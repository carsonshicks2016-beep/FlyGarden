"""Freeze, then analyze saved full-network runs. Never creates a neural model."""
import argparse
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flygarden.feedback_trace import delayed_impulses, refractory_gate
from flygarden.recorded_drive import replay_recorded_states
from flygarden.recording import atomic_json, space_check
from flygarden.route_accounting import phase_delivery, signed_totals

BASE = ROOT / 'reports/brain-integration/recovery'
PRIOR = BASE / 'local-adaptation-direction-v1'
OUT = BASE / 'sensory-steering-trace-v1'
DT = .0001
PAPER = 'https://cdn.elifesciences.org/articles/102230/elife-102230-v1.pdf'
# Exact published type labels; unavailable labels are not silently substituted.
TYPES = ['ORN_DM1', 'DM1_lPN', 'APL', 'MBON32', 'LAL170', 'LAL171',
         'LAL074', 'DNa03', 'LAL018', 'LAL010', 'PFL3', 'PFL2', 'DNa02', 'DNp09']
CLASSES = ['ALLN', 'ALPN', 'Kenyon_Cell', 'MBON', 'LHLN', 'LHCENT', 'CX']
STATE_TYPES = ['DM1_lPN', 'DNa02', 'APL', 'MBON32', 'LAL170', 'DNa03', 'LAL018']
PHASES = {'pre_1': [0, 3000], 'onset_1': [3000, 4000],
          'late_1': [4000, 8000], 'pulse_1': [3000, 8000],
          'offset_1': [8000, 11000], 'recovery_1': [25000, 30000],
          'pre_2': [30000, 33000], 'onset_2': [33000, 34000],
          'late_2': [34000, 38000], 'pulse_2': [33000, 38000],
          'offset_2': [38000, 41000], 'recovery_2': [55000, 60000]}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''):digest.update(block)
    return digest.hexdigest()


def annotations():
    ids = pd.read_csv(ROOT / 'vendor/fly-brain/data/2025_Completeness_783.csv',
                      index_col=0).index.to_numpy(dtype=np.int64)
    a = pd.read_csv(ROOT / 'data/annotations.tsv', sep='\t', dtype={'root_id': str},
                    low_memory=False).fillna('')
    assert not a.root_id.duplicated().any()
    a = a.set_index('root_id').reindex([str(x) for x in ids]).fillna('')
    return ids, a


def detail(i, ids, a):
    return dict(index=int(i), root_id=str(ids[i]),
                **{key: str(a.iloc[i][key]) for key in
                   ['cell_type', 'cell_class', 'side', 'known_nt', 'top_nt']})


def register():
    if OUT.exists() and any(OUT.iterdir()):raise FileExistsError('Preserve existing analysis; use a new version')
    OUT.mkdir(exist_ok=True);space_check(OUT, 100*1024**2)
    parent = json.loads((PRIOR / 'protocol.json').read_text())
    ids, a = annotations();populations = {}
    for field, values in [('cell_type', TYPES), ('cell_class', CLASSES)]:
        for label in values:
            for side in ['all', 'left', 'right', 'unspecified']:
                mask = a[field].eq(label).to_numpy()
                if side != 'all':mask = mask & a.side.eq('' if side == 'unspecified' else side).to_numpy()
                populations[f'{label}_{side}'] = np.flatnonzero(mask).tolist()
    # Fixed, previously monitored local targets: no selection by current results.
    for node in parent['selected_local_targets']:
        populations[f"local_{node['root_id']}"] = [node['index']]
    target_indices = np.unique(np.concatenate(
        [np.flatnonzero(a.cell_type.eq(x)) for x in STATE_TYPES]
        + [np.array([x['index'] for x in parent['selected_local_targets']])])).tolist()
    nodes = sorted(set(i for v in populations.values() for i in v))
    jobs = [f'{model}-{cue}-{seed}' for model in parent['models']
            for seed in parent['validation_seeds'] for cue in parent['cues']]
    sources = [Path(__file__), ROOT / 'flygarden/route_accounting.py',
               ROOT / 'tests/test_route_accounting.py', ROOT / 'flygarden/recorded_drive.py',
               ROOT / 'flygarden/feedback_trace.py', ROOT / 'data/annotations.tsv',
               ROOT / 'vendor/fly-brain/data/2025_Completeness_783.csv',
               ROOT / 'vendor/fly-brain/data/2025_Connectivity_783.parquet',
               PRIOR / 'protocol.json', PRIOR / 'results.json', PRIOR / 'independent-audit.json']
    sources += [PRIOR / 'trials' / job / file for job in jobs
                for file in ['manifest.json', 'rows.json']]
    coverage = {x: dict(neurons=int(a.cell_type.eq(x).sum()),
                        sides=a.loc[a.cell_type.eq(x), 'side'].value_counts().to_dict())
                for x in TYPES}
    atomic_json(OUT / 'population-roots.json',
                dict(nodes=[detail(i, ids, a) for i in nodes], populations=populations,
                     type_coverage=coverage))
    p = dict(version=1, registered_unix=time.time(),
             scope='Descriptive retrospective analysis of a fixed archive; no new qualification or fitted controller.',
             prior_package=str(PRIOR.relative_to(ROOT)), trials=jobs,
             models=parent['models'], seeds=parent['validation_seeds'], cues=parent['cues'],
             population_selection='Exact type labels in Figure 7 and functional steering discussion, plus fixed olfactory/MB/LH/CX classes and the four previously monitored locals; no score-based selection.',
             populations=populations, type_coverage=coverage, target_indices=target_indices,
             clock_s=DT, delay_ticks=18, refractory_ticks=22, phase_ticks=PHASES,
             sample_ticks=250, state_replay_max_error_mV=1e-10,
             root_manifest_sha256=sha(OUT / 'population-roots.json'),
             state_scope='Observed spikes determine resets/refractoriness. Validate g/adapt at all saved endpoints for monitored targets. Unmonitored route targets have reconstructed g only, without independent state observations; voltage is not reconstructed.',
             delivery_units='Signed voltage-equivalent synaptic increments in mV/s, not biological currents.',
             representation='Per-neuron mean rates and active fractions; individual exact-route rates. Binary/gradient pair differences and equal-reference subtraction are descriptive only. No fitted gain, significance test, classification accuracy or new pass gate.',
             motor_scope='Recorded commands from unchanged fixed descending decoder; no physics is in these neural trials.',
             limitations=['Two diagnostic seeds; phase windows are fixed before this analysis but the archive already has known failed readouts.',
                          'Soma-side annotation is not proof of peripheral receptive-field side.',
                          'Accepted drive depends on observed refractory/reset gates; attribution is not a causal intervention.',
                          'No adaptation physiology fitted to individual roots. Missing labels remain unavailable.'],
             supporting_sources=[dict(url=PAPER, doi='10.7554/eLife.102230.3',
                                      reviewed='Figure 7 and accompanying sensory/steering discussion, PDF pages 13-14; not an exact-root physiology fit.',
                                      access='Primary PDF text verified via web; article HTML blocked.', accessed='2026-10-07')],
             native_full_brain_runs=0, controller_changes=0, acceptance_criteria_changed=False,
             source_hashes={str(x.relative_to(ROOT)): sha(x) for x in sources})
    atomic_json(OUT / 'protocol.json', p)
    print('Frozen', len(jobs), 'saved trials;', len(target_indices), 'drive targets;',
          len(nodes), 'population nodes. Missing:', [k for k,v in coverage.items() if not v['neurons']], flush=True)


def save_npz(path, **arrays):
    space_check(path.parent, sum(x.nbytes for x in arrays.values()) + 1024**2)
    with path.with_suffix('.tmp').open('wb') as f:np.savez_compressed(f, **arrays)
    path.with_suffix('.tmp').replace(path)


def analyze():
    started = time.monotonic();p = json.loads((OUT / 'protocol.json').read_text())
    assert all(sha(ROOT / key) == digest for key,digest in p['source_hashes'].items())
    assert sha(OUT / 'population-roots.json') == p['root_manifest_sha256']
    if (OUT / 'results.json').exists():raise FileExistsError('Completed analysis is immutable')
    ids, a = annotations();targets = p['target_indices'];n = len(ids)
    parent = json.loads((PRIOR / 'protocol.json').read_text());selected = parent['selected']
    monitored = [j for j,t in enumerate(targets) if t in selected]
    columns = [selected.index(targets[j]) for j in monitored]
    graph = pd.read_parquet(ROOT / 'vendor/fly-brain/data/2025_Connectivity_783.parquet',
                           filters=[('Postsynaptic_Index', 'in', targets)])
    np.testing.assert_array_equal(graph.Presynaptic_ID.astype(str), ids[graph.Presynaptic_Index].astype(str))
    np.testing.assert_array_equal(graph.Postsynaptic_ID.astype(str), ids[graph.Postsynaptic_Index].astype(str))
    weights = csr_matrix((graph['Excitatory x Connectivity'].to_numpy() * .275,
                          ([targets.index(i) for i in graph.Postsynaptic_Index], graph.Presynaptic_Index)),
                         shape=(len(targets), n))
    weights.sum_duplicates();weights.sort_indices()
    info = [detail(i, ids, a) for i in targets]
    route_labels = np.asarray([str(x) for x in a.cell_type])
    classes = np.asarray([str(x) or 'unavailable' for x in a.cell_class])
    # Static anatomy describes candidate links, never evidence of transmission.
    edges = []
    for j,t in enumerate(targets):
        rows = graph[graph.Postsynaptic_Index.eq(t)]
        for cell in TYPES + ['Kenyon_Cell']:
            mask = (a.cell_class.eq(cell) if cell == 'Kenyon_Cell' else a.cell_type.eq(cell)).to_numpy()
            for side in ['left', 'right', 'unspecified']:
                members = np.flatnonzero(mask & a.side.eq('' if side == 'unspecified' else side).to_numpy())
                g = rows[rows.Presynaptic_Index.isin(members)]
                if len(g):edges.append(dict(source=cell, source_side=side, target=info[j], records=len(g),
                                             anatomical_sites=int(g.Connectivity.sum()),
                                             positive_signed_sites=float(g.loc[g['Excitatory x Connectivity'] > 0, 'Excitatory x Connectivity'].sum()),
                                             negative_signed_sites=float(-g.loc[g['Excitatory x Connectivity'] < 0, 'Excitatory x Connectivity'].sum())))
    atomic_json(OUT / 'static-route-links.json', dict(edges=edges, coverage=p['type_coverage'],
                scope='Only direct imported links into the specified targets. Absent links do not exclude longer pathways. No sign reassignment or inferred missing cell identity.'))
    populations = p['populations'];keys = list(populations)
    profile_indices = np.unique(np.concatenate([v for v in populations.values() if v])).astype(np.int32)
    single = np.unique(np.concatenate([np.flatnonzero(a.cell_type.eq(x)) for x in TYPES]
                                     + [np.array([x['index'] for x in parent['selected_local_targets']])])).astype(np.int32)
    profile_columns = np.searchsorted(profile_indices, single)
    # All population members are in the saved profile array, including classes.
    groups = [np.searchsorted(profile_indices, populations[k]) for k in keys]
    summaries = [];checks = [];profiles = {};weight_hashes = set()
    for number,name in enumerate(p['trials']):
        model, cue, seed = name.rsplit('-', 2);folder = PRIOR / 'trials' / name
        m = json.loads((folder / 'manifest.json').read_text());rows = json.loads((folder / 'rows.json').read_text())
        assert m['status'] == 'complete' and len(m['chunks']) == len(rows) == 240
        assert m['initial_weight_hash'] == m['final_weight_hash'] and m['learning_updates'] == 0
        weight_hashes.add(m['initial_weight_hash'])
        assert not set(targets) & set(m['controller']['input_indices']), 'A drive target has unaccounted external stimulation'
        assert hashlib.sha256(ids.tobytes()).hexdigest() == m['controller']['neuron_ordering_sha256']
        ii=[];ticks=[];gs=[];ads=[];vs=[];counts=[];external=[];motors=[]
        for k,(chunk,row) in enumerate(zip(m['chunks'],rows)):
            file=folder/chunk['file'];assert sha(file)==chunk['sha256']
            with np.load(file) as z:
                x=z['spike_i'];tt=np.rint(z['spike_t']/DT).astype(np.int64)
                assert np.allclose(z['spike_t'],tt*DT,atol=1e-10,rtol=0)
                assert np.all((tt>=k*250)&(tt<(k+1)*250))
                np.testing.assert_array_equal(np.bincount(x,minlength=n),z['counts'])
                ii.append(x.copy());ticks.append(tt);counts.append(z['counts'][profile_indices])
                gs.append(z['g_mV'][columns]);vs.append(z['v_mV'][columns])
                ads.append(z['adapt_mV'][columns] if 'adapt_mV' in z else np.zeros(len(columns)))
                channels=np.asarray(m['controller']['input_channels'])
                external.append(np.bincount(channels[z['external_i']],minlength=8))
                motors.append(z['motor'].copy())
                assert abs(row['end']-(k+1)*.025)<1e-9
        ii=np.concatenate(ii);ticks=np.concatenate(ticks);counts=np.asarray(counts)
        impulses=delayed_impulses(ii,ticks,weights,60000,p['delay_ticks'])
        spikes=np.zeros_like(impulses,dtype=bool)
        for j,t in enumerate(targets):spikes[ticks[ii==t],j]=True
        domain=set(parent['domains']['local_adaptive']['indices']) if model=='local_adaptive' else set()
        step=np.asarray([13.5 if t in domain else 0 for t in targets])
        g,ad,gates=replay_recorded_states(impulses,spikes,step,tau_s=.45)
        ge=float(np.max(abs(g[:,monitored]-np.asarray(gs))))
        ae=float(np.max(abs(ad[:,monitored]-np.asarray(ads))))
        assert ge<=p['state_replay_max_error_mV'] and ae<=p['state_replay_max_error_mV'],(name,ge,ae)
        for j,t in enumerate(targets):np.testing.assert_array_equal(gates[:,j],refractory_gate(ticks[ii==t],60000))
        rates=np.stack([counts[:,group].mean(1)/.025 if len(group) else np.full(240,np.nan) for group in groups],axis=1)
        for key in ['ORN_DM1_left','ORN_DM1_right','DM1_lPN_left','DM1_lPN_right','DNa02_left','DNa02_right','DNp09_left','DNp09_right']:
            np.testing.assert_allclose(rates[:,keys.index(key)],[r['population_hz'][key] for r in rows],atol=1e-12,rtol=0)
        derived=OUT/'profiles'/name;derived.parent.mkdir(exist_ok=True)
        save_npz(derived.with_suffix('.npz'),population_hz=rates,profile_indices=profile_indices,
                 counts_25ms=counts,individual_indices=single,individual_hz=counts[:,profile_columns]/.025,
                 external_counts=np.asarray(external),motor=np.asarray(motors),target_indices=np.asarray(targets),
                 reconstructed_g_mV=g,reconstructed_adapt_mV=ad,
                 recorded_state_indices=np.asarray([targets[j] for j in monitored]),
                 recorded_v_mV=np.asarray(vs),recorded_g_mV=np.asarray(gs),recorded_adapt_mV=np.asarray(ads))
        profiles[name]=dict(file=str(derived.with_suffix('.npz').relative_to(OUT)),sha256=sha(derived.with_suffix('.npz')))
        max_account_error=0.
        for phase,(lo,hi) in p['phase_ticks'].items():
            duration=(hi-lo)*DT;sl=slice(lo//250,hi//250)
            pop={key:dict(mean_hz=float(rates[sl,k].mean()),
                          active_fraction=float((counts[sl,groups[k]].sum(0)>0).mean())) if len(groups[k]) else None
                 for k,key in enumerate(keys)}
            individual=[{**detail(int(t),ids,a),'rate_hz':float(counts[sl,col].sum()/duration)}
                        for t,col in zip(single,profile_columns)]
            inputs=[]
            for j,t in enumerate(targets):
                pre,before,after=phase_delivery(ii,ticks,weights.getrow(j),gates[:,j],lo,hi)
                error=abs(after.sum()-(impulses[lo:hi,j]*gates[lo:hi,j]).sum()/duration)
                max_account_error=max(max_account_error,float(error));assert error<1e-8
                labels=np.unique(classes[pre]);by_class={label:signed_totals(after[classes[pre]==label]) for label in labels if np.any(before[classes[pre]==label])}
                by_type={label:signed_totals(after[route_labels[pre]==label]) for label in TYPES if np.any(before[route_labels[pre]==label])}
                ranking=[]
                for k in np.flatnonzero(before):
                    ranking.append({**detail(int(pre[k]),ids,a),'pregate_mV_per_s':float(before[k]),'accepted_mV_per_s':float(after[k])})
                state=dict(g_min_mV=float(g[sl,j].min()),g_max_mV=float(g[sl,j].max()),
                           adapt_mean_mV=float(ad[sl,j].mean()),independently_observed=t in selected,
                           sampling='25ms endpoints after each phase interval; not continuous extrema')
                if t in selected:
                    col=columns.index(selected.index(t));state.update(v_min_mV=float(np.asarray(vs)[sl,col].min()),v_max_mV=float(np.asarray(vs)[sl,col].max()))
                inputs.append({**info[j],'rate_hz':float(spikes[lo:hi,j].sum()/duration),
                               'accepted':signed_totals(after),'pregate':signed_totals(before),
                               'by_class':by_class,'by_route_type':by_type,'state':state,
                               'top_positive_sources':sorted([x for x in ranking if x['accepted_mV_per_s']>0],key=lambda x:-x['accepted_mV_per_s'])[:8],
                               'top_negative_sources':sorted([x for x in ranking if x['accepted_mV_per_s']<0],key=lambda x:x['accepted_mV_per_s'])[:8]})
            summaries.append(dict(trial=name,phase=phase,populations=pop,individual_rates=individual,inputs=inputs,
                                  external_counts=np.asarray(external)[sl].sum(0).tolist(),
                                  motor_mean=np.asarray(motors)[sl].mean(0).tolist()))
        checks.append(dict(trial=name,chunks=240,g_max_error_mV=ge,adapt_max_error_mV=ae,
                           independently_observed_targets=len(monitored),reconstructed_only_targets=len(targets)-len(monitored),
                           signed_accounting_max_error_mV_per_s=max_account_error,gates_exact=True))
        atomic_json(OUT/'progress.json',dict(status='running',completed=number+1,planned=len(p['trials'])))
        print(number+1,'/',len(p['trials']),name,'g error',ge,flush=True)
    assert len(weight_hashes)==1
    assert all(sha(ROOT/key)==digest for key,digest in p['source_hashes'].items())
    result=dict(status='complete',protocol_sha256=sha(OUT/'protocol.json'),native_full_brain_runs=0,
                controller_changed=False,acceptance_criteria_changed=False,trials=len(p['trials']),chunks_audited=6720,
                weights_sha256=next(iter(weight_hashes)),population_keys=keys,target_info=info,
                state_replay=checks,summaries=summaries,profiles=profiles,sources_reverified=True,
                wall_seconds=time.monotonic()-started,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    atomic_json(OUT/'results.json',result)
    atomic_json(OUT/'progress.json',dict(status='complete',completed=len(p['trials']),planned=len(p['trials'])))
    print('Completed offline analysis in',round(result['wall_seconds'],2),'seconds',flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['register','analyze'])
    args=parser.parse_args()
    (register if args.mode=='register' else analyze)()

"""Preregistered saved-run route/state audit. No new full-network runs."""
import argparse
import gc
import json
import resource
import sys
import time
from pathlib import Path

import brian2 as b
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from flygarden.feedback_trace import delayed_impulses, refractory_gate
from flygarden.recording import atomic_json, space_check
from flygarden.route_accounting import phase_delivery, signed_totals
from flygarden.route_state_audit import edge_delivery, timing_difference, json_native
from scripts.diagnose_dm1_feedforward import native_replay
from scripts.trace_sensory_steering import annotations, detail, sha

BASE=ROOT/'reports/brain-integration/recovery'
DIRECT=BASE/'recovered-mbon32-capability-v1'
ODOR=BASE/'local-adaptation-direction-v1'
TRACE=BASE/'sensory-steering-trace-v1'
OUT=BASE/'recovered-route-state-audit-v1'
GRAPH=ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet'
CONDITIONS=['intact','without_left_MBON32_edge','without_right_MBON32_edge']
DT=.0001;STEPS=60000


def write(path,value):atomic_json(path,json_native(value))


def register():
    if OUT.exists():raise FileExistsError('Keep earlier evidence; use a new version')
    d=json.loads((DIRECT/'protocol.json').read_text());o=json.loads((ODOR/'protocol.json').read_text())
    prior=json.loads((TRACE/'protocol.json').read_text());ids,a=annotations()
    dna=[d['mapping'][k][0]['index'] for k in ['DNa02_left','DNa02_right']]
    mbon=d['direct_targets'];assert dna==[92992,904] and mbon==[8333,124996]
    outgoing=pd.read_parquet(GRAPH,filters=[('Presynaptic_Index','in',mbon)])
    incoming=pd.read_parquet(GRAPH,filters=[('Postsynaptic_Index','in',dna)])
    for g in [outgoing,incoming]:
        np.testing.assert_array_equal(ids[g.Presynaptic_Index],g.Presynaptic_ID)
        np.testing.assert_array_equal(ids[g.Postsynaptic_Index],g.Postsynaptic_ID)
        np.testing.assert_array_equal(g.Connectivity*g.Excitatory,g['Excitatory x Connectivity'])
    recipients=sorted(set(outgoing.Postsynaptic_Index.astype(int)))
    relays=sorted(set(recipients)&set(incoming.Presynaptic_Index.astype(int)))
    direct=outgoing[outgoing.Postsynaptic_Index.isin(dna)]
    assert len(direct)==2 and (direct['Excitatory x Connectivity']<0).all()
    # One direct edge per exact MBON root. This inventory predates activity analysis.
    assert set(zip(direct.Presynaptic_Index,direct.Postsynaptic_Index,direct.Connectivity))=={(8333,904,40),(124996,92992,10)}
    links=[]
    for _,edge in outgoing.iterrows():
        x=edge.to_dict();x['source']=detail(int(edge.Presynaptic_Index),ids,a)
        x['target']=detail(int(edge.Postsynaptic_Index),ids,a)
        x['jump_mV']=float(edge['Excitatory x Connectivity']*.275);links.append(x)
    two_hop=[]
    for node in relays:
        two_hop.append(dict(node=detail(node,ids,a),
            from_MBON32=outgoing[outgoing.Postsynaptic_Index.eq(node)].to_dict('records'),
            into_DNa02=incoming[incoming.Presynaptic_Index.eq(node)].to_dict('records')))
    compound={label:[detail(int(i),ids,a) for i in np.flatnonzero(a.cell_type.str.split(',').map(lambda x:label in x))]
              for label in ['LAL171','LAL074']}
    paths=[Path(__file__),ROOT/'scripts/audit_recovered_route_state.py',ROOT/'scripts/plot_recovered_route_state.py',
        ROOT/'flygarden/route_state_audit.py',ROOT/'tests/test_route_state_audit.py',
        ROOT/'scripts/diagnose_dm1_feedforward.py',ROOT/'scripts/trace_sensory_steering.py',
        ROOT/'flygarden/route_accounting.py',ROOT/'flygarden/feedback_trace.py',ROOT/'flygarden/recording.py',
        ROOT/'flygarden/brain.py',ROOT/'flygarden/adaptive_neurons.py',ROOT/'flygarden/adaptive_candidate.py',
        ROOT/'flygarden/mbon_capability_candidate.py',ROOT/'flygarden/continuous_candidate.py',
        ROOT/'data/annotations.tsv',ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv',GRAPH,
        BASE/'RECOVERED_MBON_CAPABILITY_DECISION.md']
    paths += [folder/file for folder in [DIRECT,ODOR,TRACE] for file in ['protocol.json','results.json','independent-audit.json']]
    jobs=[dict(archive='direct',name=f'{cue}-{seed}',case=cue,seed=seed,model='local_adaptive')
          for seed in d['diagnostic_seeds'] for cue in d['cases']]
    jobs += [dict(archive='odor',name=f'{model}-{cue}-{seed}',case=cue,seed=seed,model=model)
             for model in o['models'] for seed in o['validation_seeds'] for cue in o['cues']]
    paths += [(DIRECT if job['archive']=='direct' else ODOR)/'trials'/job['name']/file
              for job in jobs for file in ['manifest.json','rows.json']]
    profile=sorted(set(recipients)|set(o['domains']['local_adaptive']['indices'])|
                   set(i for group in prior['populations'].values() for i in group))
    OUT.mkdir();space_check(OUT,200*1024**2)
    write(OUT/'anatomical-inventory.json',dict(MBON32=[detail(i,ids,a) for i in mbon],
        DNa02=[detail(i,ids,a) for i in dna],outgoing_records=links,
        outgoing_record_count=len(links),outgoing_anatomical_sites=int(outgoing.Connectivity.sum()),
        recipient_nodes=[detail(i,ids,a) for i in recipients],two_hop_intermediates=two_hop,
        direct_DNa02_records=direct.to_dict('records'),compound_annotations=compound,
        scope='Imported signed records only. Two-hop membership is anatomy, not transmission or unique causation. Compound labels are listed separately, never substituted for missing exact labels.'))
    p=dict(version=1,registered_before_execution=True,registered_unix=time.time(),
        question='Why does effective direct MBON32 drive yield weak/asymmetric descending rates, and which sensory-context pathways are engaged in the saved odor archive?',
        scope='Retrospective exploratory audit and fixed-source two-recipient diagnostic; not controller qualification or a recurrent-network intervention.',
        archives={'direct':str(DIRECT.relative_to(ROOT)),'odor':str(ODOR.relative_to(ROOT))},trials=jobs,
        targets=[detail(i,ids,a) for i in dna],mbon_targets=[detail(i,ids,a) for i in mbon],
        phase_ticks=prior['phase_ticks'],pulse_windows=d['pulse_windows'],recovery_windows=d['recovery_windows'],
        clock_s=DT,delay_ticks=18,refractory_ticks=22,sample_ticks=250,duration_s=6,
        receiver_parameters={'rest_mV':-52,'threshold_mV':-45,'membrane_tau_s':.020,'g_tau_s':.005,
            'reset':'v=-52mV;g=0mV','refractory_s':.0022,'method':'linear','adapt_step_mV':0},
        native_validation={'all_eight_intact_before_attribution_or_counterfactuals':True,
            'spike_ticks_counts_exact':True,'max_state_error_mV':1e-10,
            'failure_action':'Stop and preserve failure; do not interpret delivery or counterfactuals.'},
        conditions={CONDITIONS[0]:'All recorded signed incoming DNa02 events.',
            CONDITIONS[1]:'Remove only exact MBON32 left 8333 -> DNa02 right 904 inhibitory record; all source events fixed.',
            CONDITIONS[2]:'Remove only exact MBON32 right 124996 -> DNa02 left 92992 inhibitory record; all source events fixed.'},
        counterfactual_controls={'gates':'Recomputed from predicted voltage/threshold/reset; never from observed gates.',
            'untargeted_neuron_ticks_counts_exact':True,'untargeted_state_error_mV':1e-10},
        planned_intact_replays=8,planned_conditional_replays=16,full_brain_runs=0,
        attribution='Source-specific signed pre-gate/accepted mV/s on the arrival clock, with excitation and inhibition separated. Attribution uses observed 2.2ms DNa02 gates only after all intact predictions pass.',
        source_partition='Disjoint direct MBON32; exact AOTU019 types; other two-hop anatomical intermediates; remaining sources. No selection by activity.',
        populations=prior['populations'],profile_indices=profile,recipient_indices=recipients,
        relay_indices=relays,adaptation_domain=o['domains']['local_adaptive']['indices'],
        mapping_policy='Reuse frozen exact type/class groups; LAL171/LAL074 compound annotations remain unavailable for those exact biological labels.',
        state_coverage='Only saved endpoints count as observations. Unobserved relay voltages/g/adaptation unavailable; silence with inhibitory anatomical input is not evidence of subthreshold excitation. Endpoint headroom is not a continuous-voltage measurement.',
        representation='Fixed phase rates/active fractions, exact per-root recipient spike counts, matched same-seed event disagreement and symmetric nearest-event distances (not spike correspondence). No significance/threshold tuning.',
        preserved_gates={'direct':d['gates'],'odor':o['gates']},
        limitations=['Direct and odor archives use different diagnostic seeds, input contexts and MBON refractory policies; cross-archive comparison is descriptive, not matched causal evidence.',
            'Source trains in edge-removal replays cannot respond to the intervention; results are conditional, not a full-network repair.',
            'Most relay state samples are absent. Imported signs/annotations are model assumptions, not fitted exact-root physiology.',
            'Two seeds per archive; pulses not independent fly states. No learning, body, gain fitting, acceptance change or promotion.'],
        anatomy_sha256=sha(OUT/'anatomical-inventory.json'),
        source_hashes={str(path.relative_to(ROOT)):sha(path) for path in paths},
        runtime={'brian2':b.__version__,'numpy':np.__version__,'native_codegen':'cython'},
        production_controller_changed=False,acceptance_criteria_changed=False,controller_promoted=False)
    write(OUT/'protocol.json',p)
    print('Registered 36 saved trials, eight intact + 16 conditional two-recipient replays; no full-brain runs.',flush=True)


def save(path,**arrays):
    space_check(path.parent,sum(x.nbytes for x in arrays.values())+1024**2)
    with path.with_suffix('.tmp').open('wb') as stream:np.savez_compressed(stream,**arrays)
    path.with_suffix('.tmp').replace(path)


def load(job,p,ids):
    folder=ROOT/p['archives'][job['archive']]/'trials'/job['name']
    m=json.loads((folder/'manifest.json').read_text());rows=json.loads((folder/'rows.json').read_text())
    parent=json.loads((folder.parents[1]/'protocol.json').read_text())
    targets=[x['index'] for x in p['targets']];columns=[parent['selected'].index(i) for i in targets]
    assert m['status']=='complete' and len(m['chunks'])==len(rows)==240
    assert m['initial_weight_hash']==m['final_weight_hash'] and m['learning_updates']==0
    assert not set(targets)&set(m['controller']['input_indices'])
    assert not set(targets)&set(p['adaptation_domain'])
    assert m['controller']['neuron_ordering_sha256']==__import__('hashlib').sha256(ids.tobytes()).hexdigest()
    ii=[];tt=[];profiles=[];state={k:[] for k in ['v_mV','g_mV','adapt_mV']}
    whole=np.zeros(len(ids),np.int64);request=[];delivered=[]
    for k,ch in enumerate(m['chunks']):
        path=folder/ch['file'];assert sha(path)==ch['sha256']
        with np.load(path) as z:
            ticks=np.rint(z['spike_t']/DT).astype(np.int64);indices=z['spike_i']
            assert np.allclose(z['spike_t'],ticks*DT,rtol=0,atol=1e-10)
            assert np.all((ticks>=k*250)&(ticks<(k+1)*250))
            np.testing.assert_array_equal(np.bincount(indices,minlength=len(ids)),z['counts'])
            ii.append(indices.copy());tt.append(ticks);profiles.append(z['counts'][p['profile_indices']])
            whole+=z['counts']
            for key in state:state[key].append(z[key][columns] if key in z else np.zeros(2))
            if job['archive']=='direct':
                np.testing.assert_array_equal(z['mbon_i'],z['mbon_delivered_i'])
                np.testing.assert_allclose(z['mbon_t'],z['mbon_delivered_t'],atol=1e-12,rtol=0)
                request.append(np.bincount(z['mbon_i'],minlength=2));delivered.append(np.bincount(z['mbon_delivered_i'],minlength=2))
            assert abs(rows[k]['end']-(k+1)*.025)<1e-9
    ii=np.concatenate(ii);tt=np.concatenate(tt);state={k:np.asarray(v) for k,v in state.items()}
    assert not state['adapt_mV'].any()
    return dict(ii=ii,ticks=tt,counts=np.asarray(profiles),state=state,whole=whole,
        selected=parent['selected'],requested=np.asarray(request),delivered=np.asarray(delivered),manifest=m)


def replay(drive,path):
    counts,ii,tt,state=native_replay(drive,np.zeros(2,bool))
    save(path,counts_25ms=counts,spike_i=ii,spike_ticks=tt,**state)
    return dict(counts=counts,ii=ii,ticks=tt,state=state)


def analyze():
    started=time.monotonic();p=json.loads((OUT/'protocol.json').read_text())
    assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
    assert sha(OUT/'anatomical-inventory.json')==p['anatomy_sha256']
    if (OUT/'inputs').exists() or (OUT/'results.json').exists():raise FileExistsError('Preserve every attempt; use a new version')
    ids,a=annotations();targets=[x['index'] for x in p['targets']];mbon=[x['index'] for x in p['mbon_targets']]
    graph=pd.read_parquet(GRAPH,filters=[('Postsynaptic_Index','in',targets)])
    np.testing.assert_array_equal(ids[graph.Presynaptic_Index],graph.Presynaptic_ID)
    np.testing.assert_array_equal(ids[graph.Postsynaptic_Index],graph.Postsynaptic_ID)
    weights=csr_matrix((graph['Excitatory x Connectivity'].to_numpy()*.275,
        ([targets.index(int(i)) for i in graph.Postsynaptic_Index],graph.Presynaptic_Index)),shape=(2,len(ids)))
    for directory in ['inputs','replays','profiles']:(OUT/directory).mkdir()
    intact=[];replays=[];inputs=[];traces={};trial_results=[];controls=[]
    try:
        # No attribution or altered-input simulation until all intact predictions pass.
        for job in [x for x in p['trials'] if x['archive']=='direct']:
            x=load(job,p,ids);drive=delayed_impulses(x['ii'],x['ticks'],weights,STEPS,18)
            file=OUT/'inputs'/(job['name']+'.npz');save(file,arrivals_mV=drive)
            inputs.append(dict(parent=job['name'],file=str(file.relative_to(OUT)),sha256=sha(file)))
            file=OUT/'replays'/('intact--'+job['name']+'.npz');r=replay(drive,file)
            exact=all(np.array_equal(r['ticks'][r['ii']==j],x['ticks'][x['ii']==t]) for j,t in enumerate(targets))
            expected=np.zeros((240,2),np.int64)
            for j,t in enumerate(targets):expected[:,j]=x['counts'][:,p['profile_indices'].index(t)]
            exact=exact and np.array_equal(expected,r['counts'])
            errors={key:float(np.max(abs(r['state'][key]-x['state'][key]))) for key in r['state']}
            intact.append(dict(parent=job['name'],spikes_counts_exact=exact,errors_mV=errors))
            write(OUT/'native-validation.json',dict(status='running',records=intact))
            if not exact or max(errors.values())>1e-10:raise RuntimeError('Intact prediction mismatch; stopping attribution: '+str(intact[-1]))
            replays.append(dict(parent=job['name'],condition='intact',file=str(file.relative_to(OUT)),sha256=sha(file)))
            traces[job['name'],'intact']=r
            print('Intact prediction',len(intact),'/8',job['name'],errors,flush=True)
            del x,drive;gc.collect()
        write(OUT/'native-validation.json',dict(status='passed',records=intact,attribution_permitted=True))
        for job in [x for x in p['trials'] if x['archive']=='direct']:
            with np.load(OUT/'inputs'/(job['name']+'.npz')) as z:drive=z['arrivals_mV'].copy()
            x=load(job,p,ids);base=traces[job['name'],'intact']
            for k,condition in enumerate(CONDITIONS[1:]):
                mask=np.zeros(len(ids),bool);mask[mbon[k]]=True
                removed=weights.multiply(mask).tocsr()
                changed=drive-delayed_impulses(x['ii'],x['ticks'],removed,STEPS,18)
                file=OUT/'replays'/(condition+'--'+job['name']+'.npz');r=replay(changed,file)
                control=0 if k==0 else 1
                assert np.array_equal(r['counts'][:,control],base['counts'][:,control])
                assert np.array_equal(r['ticks'][r['ii']==control],base['ticks'][base['ii']==control])
                errors={key:float(np.max(abs(r['state'][key][:,control]-base['state'][key][:,control]))) for key in r['state']}
                assert max(errors.values())<=1e-10
                controls.append(dict(parent=job['name'],condition=condition,untargeted_spikes_counts_exact=True,errors_mV=errors))
                traces[job['name'],condition]=r
                replays.append(dict(parent=job['name'],condition=condition,file=str(file.relative_to(OUT)),sha256=sha(file)))
            print('Two fixed-source edge removals',job['name'],flush=True);del x,drive;gc.collect()
        groups=p['populations'];profile=p['profile_indices'];group_columns={key:np.searchsorted(profile,value) for key,value in groups.items()}
        domain_cols=np.searchsorted(profile,p['adaptation_domain']);route_cols=np.searchsorted(profile,p['recipient_indices'])
        aotu=set(np.flatnonzero(a.cell_type.eq('AOTU019')));relay=set(p['relay_indices'])-set(mbon)-aotu
        for number,job in enumerate(p['trials']):
            x=load(job,p,ids);phases=[]
            dna_ticks=[x['ticks'][x['ii']==t] for t in targets]
            for phase,(lo,hi) in p['phase_ticks'].items():
                bins=slice(lo//250,hi//250);duration=(hi-lo)*DT;pop={}
                for key,cols in group_columns.items():
                    pop[key]=(dict(neurons=len(cols),mean_hz=float(x['counts'][bins][:,cols].sum()/(len(cols)*duration)),
                        active_fraction=float(np.mean(x['counts'][bins][:,cols].sum(0)>0))) if len(cols) else
                        dict(neurons=0,mean_hz=None,active_fraction=None))
                pop['adaptation_domain']=dict(neurons=len(domain_cols),mean_hz=float(x['counts'][bins][:,domain_cols].sum()/(len(domain_cols)*duration)),
                    active_fraction=float(np.mean(x['counts'][bins][:,domain_cols].sum(0)>0)),
                    enabled=job['model']=='local_adaptive')
                delivery=[]
                for j,t in enumerate(targets):
                    source,before,accepted=phase_delivery(x['ii'],x['ticks'],weights[j],refractory_gate(dna_ticks[j],STEPS),lo,hi)
                    sets={'direct_MBON32':np.isin(source,mbon),'AOTU019':np.isin(source,list(aotu)),
                          'other_two_hop':np.isin(source,list(relay))}
                    sets['remaining']=~(sets['direct_MBON32']|sets['AOTU019']|sets['other_two_hop'])
                    partitions={key:dict(before=signed_totals(before[mask]),accepted=signed_totals(accepted[mask])) for key,mask in sets.items()}
                    direct=[]
                    for m in mbon:
                        w=float(weights[j,m])
                        if w:direct.append(dict(source_index=m,jump_mV=w,
                            **edge_delivery(x['ticks'][x['ii']==m],dna_ticks[j],w,lo,hi)))
                    v=x['state']['v_mV'][bins,j];g=x['state']['g_mV'][bins,j]
                    delivery.append(dict(target_index=t,before=signed_totals(before),accepted=signed_totals(accepted),
                        partitions=partitions,direct_edges=direct,spikes=int(np.sum((dna_ticks[j]>=lo)&(dna_ticks[j]<hi))),
                        observed_endpoint_voltage=dict(min_mV=float(v.min()),max_mV=float(v.max()),mean_mV=float(v.mean()),
                            minimum_threshold_headroom_mV=float(-45-v.max())),
                        observed_endpoint_g=dict(min_mV=float(g.min()),max_mV=float(g.max()),mean_mV=float(g.mean()))))
                route=x['counts'][bins][:,route_cols].sum(0)
                phases.append(dict(phase=phase,populations=pop,DNa02_delivery=delivery,recipient_spike_counts=route.tolist()))
            file=OUT/'profiles'/(job['archive']+'--'+job['name']+'.npz')
            save(file,counts_25ms=x['counts'],profile_indices=np.asarray(profile,np.int32),
                spike_i=x['ii'],spike_ticks=x['ticks'],recorded_v_mV=x['state']['v_mV'],recorded_g_mV=x['state']['g_mV'])
            item=dict(**job,profile_file=str(file.relative_to(OUT)),profile_sha256=sha(file),
                whole_network_spikes=int(x['whole'].sum()),whole_network_active_neurons=int(np.count_nonzero(x['whole'])),
                adaptation_domain_spikes=int(x['whole'][p['adaptation_domain']].sum()),
                state_coverage={'recorded_indices':x['selected'],
                    'recipient_observed_indices':sorted(set(x['selected'])&set(p['recipient_indices'])),
                    'recipient_unobserved_count':len(set(p['recipient_indices'])-set(x['selected'])),
                    'interpretation':'DNa02 endpoints observed; all other missing recipient states stay unavailable.'},phases=phases)
            if job['archive']=='direct':
                item['direct_input']=[dict(pulse=number,requested_events=x['requested'][lo:hi].sum(0).tolist(),
                    delivered_generator_events=x['delivered'][lo:hi].sum(0).tolist(),
                    MBON32_response_events=[int(np.sum((x['ii']==t)&(x['ticks']>=lo*250)&(x['ticks']<hi*250))) for t in mbon])
                    for number,(lo,hi) in enumerate(p['pulse_windows'],1)]
            trial_results.append(item)
            write(OUT/'progress.json',dict(status='analyzing',completed=number+1,planned=36))
            print('Recorded route/state analysis',number+1,'/36',job['archive'],job['name'],flush=True)
            del x;gc.collect()
        timing=[];conditional=[]
        direct_jobs=[x for x in p['trials'] if x['archive']=='direct']
        for job in direct_jobs:
            base=traces[f"none-{job['seed']}",'intact'];trial=traces[job['name'],'intact']
            for phase in ['pulse_1','pulse_2','recovery_1','recovery_2']:
                lo,hi=p['phase_ticks'][phase]
                def events(r,j):return r['ticks'][(r['ii']==j)&(r['ticks']>=lo)&(r['ticks']<hi)]
                if job['case']!='none':
                    timing.append(dict(parent=job['name'],seed=job['seed'],case=job['case'],phase=phase,
                        DNa02=[dict(target_index=t,**timing_difference(events(base,j),events(trial,j))) for j,t in enumerate(targets)]))
                for condition in CONDITIONS[1:]:
                    r=traces[job['name'],condition]
                    conditional.append(dict(parent=job['name'],condition=condition,phase=phase,
                        intact_hz=(trial['counts'][lo//250:hi//250].sum(0)/((hi-lo)*DT)).tolist(),
                        altered_hz=(r['counts'][lo//250:hi//250].sum(0)/((hi-lo)*DT)).tolist(),
                        DNa02=[dict(target_index=t,**timing_difference(events(trial,j),events(r,j))) for j,t in enumerate(targets)]))
        assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
        result=dict(status='complete',protocol_sha256=sha(OUT/'protocol.json'),native_validation=intact,
            replays=replays,input_files=inputs,control_checks=controls,trials=trial_results,
            matched_direct_timing=timing,fixed_source_edge_removals=conditional,sources_reverified=True,
            full_brain_runs=0,isolated_two_recipient_runs=len(replays),raw_chunks_checked=36*240,
            production_controller_changed=False,acceptance_criteria_changed=False,controller_promoted=False,
            wall_seconds=time.monotonic()-started,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            scope=p['scope'],limitations=p['limitations'])
        write(OUT/'results.json',result);write(OUT/'progress.json',dict(status='complete',completed=36,planned=36))
        print('Saved-run audit complete:',round(result['wall_seconds'],2),'s',flush=True)
    except Exception as error:
        write(OUT/'progress.json',dict(status='failed',error=repr(error),intact_validated=len(intact),recorded_trials_analyzed=len(trial_results)))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['register','analyze'])
    args=parser.parse_args();(register if args.mode=='register' else analyze)()

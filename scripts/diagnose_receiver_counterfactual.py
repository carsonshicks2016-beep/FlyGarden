"""Native isolated receivers with fixed recorded sources; no full-brain run."""
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
from flygarden.directional_metrics import opponent, gradient
from flygarden.feedback_trace import delayed_impulses
from flygarden.receiver_diagnostic import receiver_partitions
from flygarden.recording import atomic_json, space_check
from scripts.diagnose_dm1_feedforward import native_replay
from scripts.trace_sensory_steering import annotations, detail, sha

BASE=ROOT/'reports/brain-integration/recovery'
PRIOR=BASE/'local-adaptation-direction-v1'
TRACE=BASE/'sensory-steering-trace-v1'
OUT=BASE/'receiver-counterfactual-v1'
CONDITIONS=['intact','pn_dm1_only','dna_without_aotu019']
AOTU_ROOTS=['720575940633556644','720575940631517251']
KEYS=['DM1_lPN_left','DM1_lPN_right','DNa02_left','DNa02_right']


def register():
    if OUT.exists():raise FileExistsError('Preserve earlier evidence; choose a new version')
    parent=json.loads((PRIOR/'protocol.json').read_text());ids,a=annotations()
    targets=[parent['mapping'][k][0]['index'] for k in KEYS]
    assert all(len(parent['mapping'][k])==1 for k in KEYS)
    assert not set(targets)&set(parent['domains']['local_adaptive']['indices'])
    aotu=[int(np.flatnonzero(ids.astype(str)==root)[0]) for root in AOTU_ROOTS]
    assert all(a.iloc[i].cell_type=='AOTU019' and a.iloc[i].known_nt=='gaba' for i in aotu)
    orn=[n['index'] for key in ['ORN_DM1_left','ORN_DM1_right'] for n in parent['mapping'][key]]
    graph_path=ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet'
    g=pd.read_parquet(graph_path,filters=[('Presynaptic_Index','in',aotu),('Postsynaptic_Index','in',targets[2:])])
    assert len(g)==3 and int(g.Connectivity.sum())==338 and (g['Excitatory x Connectivity']<0).all()
    jobs=[f'{model}-{cue}-{seed}' for model in parent['models'] for seed in parent['validation_seeds'] for cue in parent['cues']]
    paths=[Path(__file__),ROOT/'flygarden/receiver_diagnostic.py',ROOT/'tests/test_receiver_diagnostic.py',
           ROOT/'scripts/diagnose_dm1_feedforward.py',ROOT/'scripts/trace_sensory_steering.py',
           ROOT/'flygarden/brain.py',ROOT/'flygarden/adaptive_neurons.py',ROOT/'flygarden/feedback_trace.py',
           ROOT/'flygarden/directional_metrics.py',ROOT/'data/annotations.tsv',
           ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv',graph_path,
           PRIOR/'protocol.json',PRIOR/'results.json',PRIOR/'independent-audit.json',
           TRACE/'protocol.json',TRACE/'results.json',TRACE/'independent-audit.json']
    paths += [PRIOR/'trials'/name/file for name in jobs for file in ['manifest.json','rows.json']]
    OUT.mkdir();space_check(OUT,100*1024**2)
    p=dict(version=1,registered_unix=time.time(),registered_before_execution=True,
        question='Under fixed recorded source activity, do direct receptor drive and paired AOTU019 delivery explain the tested receiver bias?',
        scope='Exploratory isolated four-unit receiver diagnostic, not a recurrent full-network intervention, deployable reduced model or independent qualification.',
        trials=jobs,models=parent['models'],seeds=parent['validation_seeds'],cues=parent['cues'],
        targets=[detail(t,ids,a) for t in targets],target_keys=KEYS,
        receptor_indices=orn,aotu_sources=[detail(t,ids,a) for t in aotu],removed_edges=g.to_dict('records'),
        conditions={'intact':'All recorded incoming signed drive into all four units.',
                    'pn_dm1_only':'For PN receivers retain only exact DM1 receptor edges; both DNa02 inputs stay intact.',
                    'dna_without_aotu019':'Remove the three exact paired AOTU019-to-DNa02 records; both PN inputs stay intact.'},
        clock_s=.0001,delay_ticks=18,duration_s=6,record_bin_s=.025,
        receiver_parameters={'rest_mV':-52,'threshold_mV':-45,'membrane_tau_s':.020,'g_tau_s':.005,
                             'reset':'v=-52mV; g=0mV','refractory_s':.0022,'method':'linear','adapt_step_mV':0},
        receiver_equation_basis='All four targets are outside the parent adaptation mask. Use the existing native baseline v/g helper; exact spike and voltage/g reconstruction required for both parent models.',
        native_validation={'all_28_parents_before_any_counterfactual':True,'spike_ticks_and_counts_exact':True,
                           'max_state_error_mV':1e-10,'adaptation_observed_zero':True,
                           'failure_action':'Stop before counterfactuals; preserve mismatch and diagnose scheduling/equations.'},
        counterfactual_controls={'untargeted_spike_ticks_counts_exact':True,'untargeted_v_g_error_mV':1e-10,
                                'gates':'Recomputed from native voltage and threshold crossings, not copied from observations.'},
        pulse_windows=parent['pulse_windows'],recovery_windows=parent['recovery_windows'],
        phase_ticks=json.loads((TRACE/'protocol.json').read_text())['phase_ticks'],gates=parent['gates'],
        metrics='Original PN Gate3/6 and separately named DNa02 direction/gradient bounds. Counterfactual criterion satisfaction is descriptive, not qualification. No offset, gain fitting, threshold relaxation, body or learning.',
        preservation='Full graph, parent recordings/checkpoints, prior acceptance criteria and live controller remain unchanged.',
        limitations=['Source trains include their parent feedback but cannot respond to the receiver intervention.',
                     'Two previously used diagnostic seeds; repeated pulses are not independent fly states.',
                     'AOTU roots selected from prior source attribution; this is a hypothesis test, not prospective held-out discovery.'],
        planned_native_validation_runs=28,planned_counterfactual_runs=56,full_brain_runs=0,
        promoted=False,source_hashes={str(path.relative_to(ROOT)):sha(path) for path in paths},
        runtime={'brian2':b.__version__,'numpy':np.__version__,'codegen':'cython'})
    atomic_json(OUT/'protocol.json',p)
    print('Frozen 28 validation + 56 conditional replays; four receivers; three removed records / 338 sites.',flush=True)


def save_arrays(path,**arrays):
    space_check(path.parent,sum(v.nbytes for v in arrays.values())+1024**2)
    with path.with_suffix('.tmp').open('wb') as f:np.savez_compressed(f,**arrays)
    path.with_suffix('.tmp').replace(path)


def load_recording(name,targets,columns):
    folder=PRIOR/'trials'/name;m=json.loads((folder/'manifest.json').read_text())
    assert m['status']=='complete' and len(m['chunks'])==240
    assert m['initial_weight_hash']==m['final_weight_hash'] and m['learning_updates']==0
    assert not set(targets)&set(m['controller']['input_indices'])
    indices=[];ticks=[];counts=[];state={k:[] for k in ['v_mV','g_mV','adapt_mV']}
    for k,ch in enumerate(m['chunks']):
        path=folder/ch['file'];assert sha(path)==ch['sha256']
        with np.load(path) as z:
            ii=z['spike_i'];tt=np.rint(z['spike_t']/.0001).astype(np.int64)
            assert np.allclose(z['spike_t'],tt*.0001,atol=1e-10,rtol=0)
            assert np.all((tt>=k*250)&(tt<(k+1)*250))
            np.testing.assert_array_equal(np.bincount(ii,minlength=138639),z['counts'])
            indices.append(ii.copy());ticks.append(tt);counts.append(z['counts'][targets])
            for key in state:state[key].append(z[key][columns] if key in z else np.zeros(len(targets)))
    assert not np.any(state['adapt_mV'])
    ii=np.concatenate(indices);tt=np.concatenate(ticks)
    expected=np.zeros((60000,len(targets)),bool)
    for j,target in enumerate(targets):expected[tt[ii==target],j]=True
    return ii,tt,np.asarray(counts),{k:np.asarray(v) for k,v in state.items()},expected


def replay_to_file(drive,path):
    counts,ii,ticks,state=native_replay(drive,np.zeros(4,dtype=bool))
    assert all(np.isfinite(v).all() for v in state.values())
    actual=np.zeros((60000,4),bool);actual[ticks,ii]=True
    save_arrays(path,counts_25ms=counts,spike_i=ii,spike_ticks=ticks,**state)
    return counts,state,actual


def evaluate(p,traces):
    contrasts=[];gradients=[];recovery=[]
    for model in p['models']:
        for condition in CONDITIONS:
            for seed in p['seeds']:
                for pulse,(lo,hi) in enumerate(p['pulse_windows'],1):
                    for label,col,minimum,grad_min in [('PN',0,p['gates']['multi_trial_contrast_hz'],p['gates']['gradient_contrast_hz']),
                                                      ('DNa02',2,p['gates']['motor_direction_contrast_hz'],p['gates']['motor_gradient_contrast_hz'])]:
                        def diff(cue):
                            t=traces[model,condition,seed,cue]
                            return float((t[lo:hi,col]-t[lo:hi,col+1]).mean())
                        identity=dict(parent_model=model,condition=condition,seed=seed,pulse=pulse,readout=label)
                        con=opponent(diff('a_left'),diff('a_right'),diff('none'),minimum)
                        grad=gradient(diff('g60'),diff('g40'),diff('equal'),grad_min)
                        con['criterion_satisfied']=con.pop('passed');grad['criterion_satisfied']=grad.pop('passed')
                        contrasts.append({**identity,**con});gradients.append({**identity,**grad})
                for cue in [x for x in p['cues'] if x!='none']:
                    t=traces[model,condition,seed,cue];none=traces[model,condition,seed,'none']
                    for pulse,(lo,hi) in enumerate(p['recovery_windows'],1):
                        difference=t[lo:hi].mean(0)-none[lo:hi].mean(0)
                        recovery.append(dict(parent_model=model,condition=condition,seed=seed,cue=cue,pulse=pulse,
                            individual_PN_difference_hz=difference[:2].tolist(),signed_DNa02_difference_hz=float(difference[2]-difference[3]),
                            receiver_PN_recovery_bound_satisfied=bool(max(abs(difference[:2]))<=p['gates']['individual_PN_and_local_recovery_difference_hz']),
                            receiver_signed_DNa02_recovery_bound_satisfied=bool(abs(difference[2]-difference[3])<=p['gates']['signed_DNa02_recovery_difference_hz'])))
    return dict(contrast=contrasts,gradient=gradients,receiver_recovery=recovery)


def run():
    started=time.monotonic();p=json.loads((OUT/'protocol.json').read_text())
    assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
    if (OUT/'results.json').exists() or (OUT/'inputs').exists():raise FileExistsError('Preserve completed or interrupted attempt; use a new version')
    targets=[x['index'] for x in p['targets']]
    parent=json.loads((PRIOR/'protocol.json').read_text());columns=[parent['selected'].index(t) for t in targets]
    graph=pd.read_parquet(ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet',
                          filters=[('Postsynaptic_Index','in',targets)])
    ids,_=annotations()
    np.testing.assert_array_equal(ids[graph.Presynaptic_Index],graph.Presynaptic_ID)
    np.testing.assert_array_equal(ids[graph.Postsynaptic_Index],graph.Postsynaptic_ID)
    w=csr_matrix((graph['Excitatory x Connectivity'].to_numpy()*.275,
                  ([targets.index(i) for i in graph.Postsynaptic_Index],graph.Presynaptic_Index)),shape=(4,138639))
    parts=receiver_partitions(w,[0,1],[2,3],p['receptor_indices'],[x['index'] for x in p['aotu_sources']])
    for directory in ['inputs','replays']:(OUT/directory).mkdir()
    validation=[];records=[];inputs=[];traces={};control_checks=[]
    try:
        # Complete all validation first. No counterfactual result exists until
        # every intact replay predicts its original spikes AND voltage/g.
        for number,name in enumerate(p['trials']):
            model,cue,seed=name.rsplit('-',2)
            ii,tt,expected_counts,expected_state,expected=load_recording(name,targets,columns)
            drives={key:delayed_impulses(ii,tt,value,60000,18) for key,value in parts.items()}
            input_path=OUT/'inputs'/(name+'.npz')
            save_arrays(input_path,**{key+'_arrivals_mV':value for key,value in drives.items()})
            inputs.append(dict(parent=name,file=str(input_path.relative_to(OUT)),sha256=sha(input_path)))
            path=OUT/'replays'/('intact--'+name+'.npz')
            counts,state,actual=replay_to_file(drives['intact'],path)
            exact=np.array_equal(actual,expected) and np.array_equal(counts,expected_counts)
            errors={key:float(np.max(abs(state[key]-expected_state[key]))) for key in state}
            item=dict(parent=name,spikes_and_counts_exact=exact,errors_mV=errors)
            validation.append(item);atomic_json(OUT/'native-validation.json',dict(status='running',records=validation))
            if not exact or max(errors.values())>p['native_validation']['max_state_error_mV']:
                raise RuntimeError('Intact native replay mismatch; no counterfactual interpretation: '+str(item))
            traces[model,'intact',int(seed),cue]=counts/.025
            records.append(dict(parent=name,condition='intact',file=str(path.relative_to(OUT)),sha256=sha(path)))
            atomic_json(OUT/'progress.json',dict(status='validating',completed=number+1,planned=84))
            print('Intact prediction passed',number+1,'/28',name,'v/g error',errors,flush=True)
            del ii,tt,expected,drives;gc.collect()
        atomic_json(OUT/'native-validation.json',dict(status='passed',records=validation,counterfactuals_launched=False))
        for number,name in enumerate(p['trials']):
            model,cue,seed=name.rsplit('-',2)
            with np.load(OUT/'replays'/('intact--'+name+'.npz')) as z:
                intact_counts=z['counts_25ms'].copy();intact_state={key:z[key].copy() for key in ['v_mV','g_mV','adapt_mV']}
                intact_spikes=np.zeros((60000,4),bool);intact_spikes[z['spike_ticks'],z['spike_i']]=True
            input_path=OUT/'inputs'/(name+'.npz');assert sha(input_path)==inputs[number]['sha256']
            with np.load(input_path) as z:
                for condition,control in [('pn_dm1_only',[2,3]),('dna_without_aotu019',[0,1])]:
                    path=OUT/'replays'/(condition+'--'+name+'.npz')
                    counts,state,actual=replay_to_file(z[condition+'_arrivals_mV'],path)
                    assert np.array_equal(counts[:,control],intact_counts[:,control])
                    assert np.array_equal(actual[:,control],intact_spikes[:,control])
                    errors={key:float(np.max(abs(state[key][:,control]-intact_state[key][:,control]))) for key in state}
                    assert max(errors.values())<=p['counterfactual_controls']['untargeted_v_g_error_mV']
                    control_checks.append(dict(parent=name,condition=condition,untargeted_spikes_and_counts_exact=True,errors_mV=errors))
                    traces[model,condition,int(seed),cue]=counts/.025
                    records.append(dict(parent=name,condition=condition,file=str(path.relative_to(OUT)),sha256=sha(path)))
                    gc.collect()
            print('Both conditional replays complete',number+1,'/28',name,flush=True)
            atomic_json(OUT/'progress.json',dict(status='counterfactuals',completed=len(records),planned=84))
        metrics=evaluate(p,traces)
        old=json.loads((PRIOR/'results.json').read_text())
        for new_key,old_key,label in [('contrast','contrast','PN'),('gradient','gradient','PN'),
                                      ('contrast','motor_contrast','DNa02'),('gradient','motor_gradient','DNa02')]:
            for row in old[old_key]:
                now=next(x for x in metrics[new_key] if x['condition']=='intact' and x['readout']==label and
                         (x['parent_model'],x['seed'],x['pulse'])==(row['model'],row['seed'],row['pulse']))
                assert all(now['criterion_satisfied' if key=='passed' else key]==value for key,value in row.items() if key not in ['model','seed','pulse'])
        assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
        result=dict(status='complete',protocol_sha256=sha(OUT/'protocol.json'),native_validation=validation,
                    control_checks=control_checks,trials=records,input_files=inputs,**metrics,
                    intact_original_metrics_exact=True,sources_reverified=True,full_brain_runs=0,
                    isolated_native_runs=len(records),production_controller_changed=False,controller_promoted=False,
                    acceptance_criteria_changed=False,wall_seconds=time.monotonic()-started,
                    peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    scope=p['scope'],limits=p['limitations'])
        atomic_json(OUT/'results.json',result);atomic_json(OUT/'progress.json',dict(status='complete',completed=84,planned=84))
        print('Completed',len(records),'isolated replays in',round(result['wall_seconds'],2),'seconds',flush=True)
    except Exception as error:
        atomic_json(OUT/'progress.json',dict(status='failed',error=repr(error),completed=len(records),planned=84))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['register','run'])
    args=parser.parse_args();(register if args.mode=='register' else run)()

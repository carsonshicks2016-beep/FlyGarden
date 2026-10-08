"""Sixteen fixed-context full-network trials with durable reconstruction."""
import argparse
import fcntl
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import psutil

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.context_capability import CONTEXTS, evaluate_contexts
from flygarden.mbon_capability import CASES
from flygarden.recording import atomic_json, space_check
from flygarden.route_state_audit import json_native
from scripts.test_recovered_mbon_capability import arrays as legacy_arrays, publish_arrays, RATE_KEYS

BASE=ROOT/'reports/brain-integration/recovery'
OUT=BASE/'sensory-context-capability-v1'
PARENT=BASE/'recovered-mbon32-capability-v1'
ROUTE=BASE/'recovered-route-state-audit-v1'
SEEDS=[12501,12502]
WEIGHT='f6f6ab9f7c49e14a906d120c705e6af7814ecdeeecaaefad8b1280bdb71e7732'


def write(path,value):atomic_json(path,json_native(value))


def prepare():
    if OUT.exists():raise FileExistsError('Preserve every attempt; choose a new version')
    parent=json.loads((PARENT/'protocol.json').read_text())
    assert all(file_sha(ROOT/k)==v for k,v in parent['sources'].items())
    files=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*protocol*.json','reports/brain-integration'],cwd=ROOT,text=True).splitlines()
    used=set()
    def integers(value):
        if isinstance(value,int):used.add(value)
        elif isinstance(value,(list,dict)):
            for item in (value.values() if isinstance(value,dict) else value):integers(item)
    def scan(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if 'seed' in key.lower():integers(item)
                scan(item)
        elif isinstance(value,list):
            for item in value:scan(item)
    for file in files:scan(json.loads((ROOT/file).read_text()))
    assert not set(SEEDS)&used
    route=json.loads((ROUTE/'protocol.json').read_text())
    sources=dict(parent['sources'])
    paths=[Path(__file__),ROOT/'scripts/audit_sensory_context_capability.py',ROOT/'scripts/plot_sensory_context_capability.py',
        ROOT/'flygarden/context_capability.py',ROOT/'flygarden/context_capability_candidate.py',
        ROOT/'flygarden/route_state_audit.py',ROOT/'tests/test_context_capability.py',
        BASE/'SENSORY_CONTEXT_COMPARISON_SPEC_V1.md',BASE/'ROUTE_STATE_DECISION.md',
        PARENT/'protocol.json',PARENT/'results.json',PARENT/'independent-audit.json',
        ROUTE/'protocol.json',ROUTE/'results.json',ROUTE/'independent-audit.json',
        PARENT/'trials/left-12401/manifest.json',PARENT/'trials/left-12401/rows.json']
    sources.update({str(path.relative_to(ROOT)):file_sha(path) for path in paths})
    p={key:parent[key] for key in ['mapping','direct_targets','direct_roots','domain','parameters','selected',
        'selected_local_targets','interval_s','neural_clock_s','duration_s','windows','pulse_windows',
        'recovery_windows','burst_windows','gates','measurements','preservation']}
    p.update(version=1,registered_before_execution=True,registered_unix=time.time(),sources=sources,
        scope='One matched engineered odor-context diagnostic. No body, learning, adaptation-disabled comparison, input-strength sweep, decoder fit or controller promotion.',
        question='Does fixed symmetric DM1 sensory engagement change direct MBON32 descending capability under unchanged input strengths and original gates?',
        diagnostic_seeds=SEEDS,seed_reservations_checked=dict(protocols=len(files),previous_seed_values=len(used)),
        contexts=list(CONTEXTS),cases=list(CASES),trials=16,model='local_adaptive',
        jobs=[dict(context=context,case=case,seed=seed,name=f'{context}-{case}-{seed}')
              for seed in SEEDS for case in CASES for context in reversed(CONTEXTS)],
        input={**parent['input'],'odor_context':{'no_odor':'Zero DM1/DM2 throughout.',
            'DM1_equal_50_50':'Both DM1 antenna concentrations0.5 during the same two pulses only; nominal25Hz per receptor. DM2/vision zero.'},
            'paired_streams':'Unchanged draws of250 × all possible candidate inputs each25ms; fixed support65Hz. Independent direct stream seed+100000. Both request and delivered-generator monitors verified.'},
        control_policy='Evaluate each context with the original evaluator against its own same-seed direct-none arm. Never pool contexts or change the hard-coded original inequalities.',
        ordinary_input_monitor='New observation-only SpikeMonitor; verify exact requested/delivered support and odor events. Historical36-window left-12401 parity before the new trials.',
        parity=dict(parent='left-12401',seed=12401,case='left',context='no_odor',windows=36,
            scope='Historical0.9s A/A validation prefix, not a seventeenth scientific trial or fresh qualification.'),
        adaptation_indices=p['domain']['indices'],relay_indices=route['relay_indices'],
        continuation='All four context/seed left arms: checkpoint after window150, fresh process reproduces151..155 and full-network v/g/adapt within1e-10mV.',
        interruption='One owned no_odor-right-12501 worker terminated after at least60 committed chunks, preserving the prefix. Reconstruct exactly from fixed initial seed before appending. Retain any other interrupted evidence.',
        scheduling={'workers':1,'baseline_available_bytes':psutil.virtual_memory().available,
            'baseline_swap_bytes':psutil.swap_memory().used,'reason':'Fixed design initially uses one worker; limited free memory and preexisting swap. No simultaneous export.'},
        recording='All modeled spikes/counts; ordinary/direct requested and delivered generator events;26 selected v/g/adapt endpoints; frozen motor commands. No body/MP4 in this neural diagnostic.',
        stop_policy='Numerical/RNG/continuation/audit failures stop interpretation. If both contexts fail original direction, no larger adaptation/direct-drive grid; deliver an explicitly scoped engineered neural readout proposal.',
        limitations=['Two diagnostic seeds; repeated pulses are not independent fly states.',
            'Both contexts retain adaptation, so this does not isolate adaptation causally.',
            'Sensory encoding and tonic support are engineered. Recruitment/timing cannot replace the original rate-based gates.'],
        production_controller_changed=False,promotion=False,acceptance_criteria_changed=False)
    assert len(p['domain']['indices'])==395 and p['parameters']=={'tau_s':.45,'step_mv':13.5}
    assert p['gates']==parent['gates'] and p['direct_targets']==[8333,124996]
    space_check(ROOT,4*1024**3);OUT.mkdir()
    write(OUT/'protocol.json',p);write(OUT/'progress.json',dict(status='prepared',planned_trials=16,completed=[],workers=1,promoted=False))
    print('Registered sixteen full-network context trials on fresh diagnostic seeds12501/12502.',flush=True)


def verify():
    p=json.loads((OUT/'protocol.json').read_text())
    assert all(file_sha(ROOT/k)==v for k,v in p['sources'].items()),'Frozen source changed'
    return p


def arrays(c,p,motor):
    data=legacy_arrays(c,p,motor)
    data.update({key:c.last[key] for key in ['input_delivered_i','input_delivered_t']})
    return data


def construct(p,context,seed):
    from flygarden.context_capability_candidate import ContextCapabilityCandidate
    c=ContextCapabilityCandidate(p['mapping'],p['domain'],p['direct_targets'],seed,context)
    assert (c.brain.n,c.brain.edges,c.brain.anatomical_synapses)==(138639,15091983,54492922)
    return c


def parity():
    p=verify();r=p['parity'];start=time.monotonic();c=construct(p,r['context'],r['seed'])
    folder=PARENT/'trials'/r['parent'];m=json.loads((folder/'manifest.json').read_text());checks=[]
    for tick in range(r['windows']):
        data=arrays(c,p,c.advance_context(r['case'],tick));ch=m['chunks'][tick];file=folder/ch['file'];assert file_sha(file)==ch['sha256']
        with np.load(file) as z:
            assert set(data)==set(z.files)|{'input_delivered_i','input_delivered_t'}
            assert all(np.array_equal(z[key],data[key]) for key in z.files)
        checks.append(ch)
    assert hashlib.sha256(np.asarray(c.brain.synapses.w[:]).tobytes()).hexdigest()==WEIGHT
    verify();write(OUT/'no-context-parity.json',dict(status='passed',parent=r['parent'],windows=r['windows'],
        historical_arrays_exact=True,new_monitor_requested_delivered_exact=True,weight_hash=WEIGHT,
        prefix=checks,wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    print('Historical no-context prefix parity passed,36 complete windows.',flush=True)


def worker(context,case,seed,continuation=False):
    from scripts.sweep_adaptive_lif import fullstate
    p=verify();assert context in CONTEXTS and case in CASES and seed in SEEDS
    folder=OUT/'trials'/f'{context}-{case}-{seed}';start=time.monotonic();c=construct(p,context,seed)
    if continuation:
        c.load(folder/'checkpoint')
        for tick in range(151,156):
            data=arrays(c,p,c.advance_context(case,tick))
            with np.load(folder/f'window-{tick:04d}.npz') as z:
                assert set(z.files)==set(data) and all(np.array_equal(z[k],v) for k,v in data.items())
        with np.load(folder/'continuation-state.npz') as z:errors={k:float(np.max(abs(v-z[k]))) for k,v in fullstate(c).items()}
        assert max(errors.values())<=p['gates']['state_precision_mV']
        write(folder/'continuation-result.json',dict(status='passed',fresh_process=True,windows=5,errors_mV=errors,
            checkpoint_integrity_sha256=file_sha(folder/'checkpoint/integrity.json'),wall_seconds=time.monotonic()-start))
        print('Fresh-process continuation passed',folder.name,errors,flush=True);return
    weight=hashlib.sha256(np.asarray(c.brain.synapses.w[:]).tobytes()).hexdigest();assert weight==WEIGHT
    if (folder/'manifest.json').exists():
        m=json.loads((folder/'manifest.json').read_text());rows=json.loads((folder/'rows.json').read_text())
        assert m['sources']==p['sources'] and m['initial_weight_hash']==weight and m['controller']==c.manifest()
        existing=len(m['chunks']);assert existing<=240 and len(rows) in (existing,existing+1)
        orphan=rows[existing] if len(rows)>existing else None;rows=rows[:existing]
    else:
        folder.mkdir(parents=True,exist_ok=False);existing=0;orphan=None;rows=[]
        m=dict(status='running',context=context,case=case,seed=seed,model='local_adaptive',controller=c.manifest(),
            sources=p['sources'],protocol_sha256=file_sha(OUT/'protocol.json'),initial_weight_hash=weight,chunks=[])
        write(folder/'manifest.json',m);write(folder/'rows.json',rows)
    run_start=time.monotonic()
    try:
        for tick in range(240):
            data=arrays(c,p,c.advance_context(case,tick));assert all(np.isfinite(v).all() for v in data.values())
            np.testing.assert_array_equal(np.bincount(data['spike_i'],minlength=138639),data['counts'])
            file=folder/f'window-{tick:04d}.npz'
            if file.exists():
                with np.load(file) as z:assert set(z.files)==set(data) and all(np.array_equal(z[k],v) for k,v in data.items()),file
                if tick<existing:assert file_sha(file)==m['chunks'][tick]['sha256']
            else:assert tick>=existing;publish_arrays(file,data)
            if tick>=existing:
                row=dict(end=c.time,population_hz=c.last['population_hz'],requested_hz=c.last['requested_hz'],motor=data['motor'].tolist())
                if tick==existing and orphan is not None:assert row==orphan
                rows.append(row);m['chunks'].append(dict(file=file.name,sha256=file_sha(file),end=c.time))
                write(folder/'rows.json',rows);write(folder/'manifest.json',m)
            write(OUT/'current-worker.json',dict(trial=folder.name,pid=os.getpid(),context=context,case=case,
                completed_windows=tick+1,reconstructed_prefix_windows=min(tick+1,existing),simulated_seconds=c.time,
                wall_seconds=time.monotonic()-start,run_wall_seconds=time.monotonic()-run_start,
                rss_bytes=psutil.Process().memory_info().rss,swap_used_bytes=psutil.swap_memory().used))
            if case=='left' and tick==150 and not (folder/'checkpoint').exists():
                staging=folder/('checkpoint-staging-'+str(time.time_ns()));c.save(staging);staging.replace(folder/'checkpoint')
            if case=='left' and tick==155:
                state=fullstate(c);file=folder/'continuation-state.npz'
                if file.exists():
                    with np.load(file) as z:assert all(np.array_equal(z[k],v) for k,v in state.items())
                else:publish_arrays(file,state)
        final=hashlib.sha256(np.asarray(c.brain.synapses.w[:]).tobytes()).hexdigest()
        assert final==weight and c.brain.plasticity.updates==0;verify()
        m.update(status='complete',final_weight_hash=final,learning_updates=0,reconstructed_windows=existing,
            wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        write(folder/'manifest.json',m);print(folder.name,'complete',round(m['wall_seconds'],1),'seconds',flush=True)
    except BaseException as error:
        m.update(status='interrupted',error=repr(error));write(folder/'manifest.json',m);raise


def controlled_interrupt(p):
    receipt=OUT/'interruption-test.json';name='no_odor-right-12501';folder=OUT/'trials'/name
    if receipt.exists():return
    if folder.exists():raise RuntimeError('Interruption target exists without receipt; preserve and inspect')
    process=subprocess.Popen([sys.executable,'-B',__file__,'worker','--context','no_odor','--case','right','--seed','12501'],cwd=ROOT)
    try:
        deadline=time.monotonic()+300
        while process.poll() is None and time.monotonic()<deadline:
            file=OUT/'current-worker.json'
            if file.exists():
                current=json.loads(file.read_text())
                if current['pid']==process.pid and current['completed_windows']>=60:
                    process.terminate();code=process.wait(timeout=30)
                    m=json.loads((folder/'manifest.json').read_text());assert 60<=len(m['chunks'])<240 and code!=0
                    m.update(status='interrupted',error='Controlled owned-worker termination for exact-prefix reconstruction');write(folder/'manifest.json',m)
                    write(receipt,dict(trial=name,owned_worker_pid=process.pid,return_code=code,complete_prefix=m['chunks'],
                        controlled_termination=True,status='prefix_preserved_pending_reconstruction'))
                    print('Preserved controlled interruption prefix',len(m['chunks']),flush=True);return
            time.sleep(.1)
        raise RuntimeError('Interruption point not reached')
    finally:
        if process.poll() is None:process.terminate();process.wait(timeout=30)


def evaluate(p):
    traces={};engagement=[];chunks=0;locals_=[x['index'] for x in p['selected_local_targets']]
    for job in p['jobs']:
        folder=OUT/'trials'/job['name'];m=json.loads((folder/'manifest.json').read_text())
        assert m['status']=='complete' and len(m['chunks'])==240 and m['initial_weight_hash']==m['final_weight_hash']==WEIGHT
        rates=[];domain=[];relays=[];total=0;active=np.zeros(138639,bool)
        for ch in m['chunks']:
            file=folder/ch['file'];assert file_sha(file)==ch['sha256']
            with np.load(file) as z:
                counts=np.bincount(z['spike_i'],minlength=138639);np.testing.assert_array_equal(counts,z['counts'])
                rates.append([float(counts[[n['index'] for n in p['mapping'][key]]].mean()/.025) for key in RATE_KEYS]+(counts[locals_]/.025).tolist())
                domain.append(counts[p['adaptation_indices']]);relays.append(counts[p['relay_indices']]);total+=int(counts.sum());active|=counts>0
            chunks+=1
        traces[job['context'],job['seed'],job['case']]=np.asarray(rates)
        engagement.append(dict(**job,whole_spikes=total,whole_active_neurons=int(active.sum()),adaptation_domain_spikes=int(np.asarray(domain).sum()),
            pulses=[dict(pulse=number,adaptation_domain_mean_hz=float(np.asarray(domain)[lo:hi].mean()/.025),
                active_adaptation_neurons=int(np.count_nonzero(np.asarray(domain)[lo:hi].sum(0))),
                active_two_hop_intermediates=int(np.count_nonzero(np.asarray(relays)[lo:hi].sum(0))))
                for number,(lo,hi) in enumerate(p['pulse_windows'],1)]))
    results=evaluate_contexts(p,traces)
    return dict(status='complete',protocol_sha256=file_sha(OUT/'protocol.json'),trials=16,chunks_audited=chunks,
        contexts=results,engagement=engagement,continuation_checks=[dict(trial=f'{context}-left-{seed}',
            **json.loads((OUT/'trials'/f'{context}-left-{seed}'/'continuation-result.json').read_text())) for context in CONTEXTS for seed in SEEDS],
        production_controller_changed=False,controller_promoted=False,acceptance_criteria_changed=False,
        navigation_validated=False,learning_validated=False)


def run():
    p=verify();start=time.monotonic();completed=[];samples=[];(ROOT/'.runtime').mkdir(exist_ok=True)
    with (ROOT/'.runtime/experiment.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if not (OUT/'no-context-parity.json').exists():subprocess.run([sys.executable,'-B',__file__,'parity'],cwd=ROOT,check=True)
        assert json.loads((OUT/'no-context-parity.json').read_text())['status']=='passed'
        for job in p['jobs']:
            folder=OUT/'trials'/job['name']
            write(OUT/'progress.json',dict(status='running',completed=completed,current=job['name'],planned_trials=16,pid=os.getpid(),workers=1,promoted=False))
            finished=(folder/'manifest.json').exists() and json.loads((folder/'manifest.json').read_text())['status']=='complete'
            args=[sys.executable,'-B',__file__,'worker','--context',job['context'],'--case',job['case'],'--seed',str(job['seed'])]
            if not finished:
                space_check(OUT,1200*1024**2)
                if job['name']=='no_odor-right-12501':controlled_interrupt(p)
                subprocess.run(args,cwd=ROOT,check=True)
            if job['case']=='left' and not (folder/'continuation-result.json').exists():subprocess.run(args+['--continuation'],cwd=ROOT,check=True)
            completed.append(job['name']);samples.append(dict(trial=job['name'],swap_used_bytes=psutil.swap_memory().used,
                swap_out_bytes=psutil.swap_memory().sout,available_memory_bytes=psutil.virtual_memory().available))
        interrupted=json.loads((OUT/'interruption-test.json').read_text());m=json.loads((OUT/'trials'/interrupted['trial']/'manifest.json').read_text())
        assert m['reconstructed_windows']>=len(interrupted['complete_prefix']) and m['chunks'][:len(interrupted['complete_prefix'])]==interrupted['complete_prefix']
        interrupted.update(status='passed',prefix_reconstructed_exactly=True);write(OUT/'interruption-test.json',interrupted)
        if not (OUT/'results.json').exists():
            result=evaluate(p);result.update(wall_seconds=time.monotonic()-start,scheduling_samples=samples);write(OUT/'results.json',result)
        if not (OUT/'independent-audit.json').exists():subprocess.run([sys.executable,'-B',str(ROOT/'scripts/audit_sensory_context_capability.py')],cwd=ROOT,check=True)
        subprocess.run([sys.executable,'-B',str(ROOT/'scripts/plot_sensory_context_capability.py')],cwd=ROOT,check=True)
        write(OUT/'progress.json',dict(status='complete',completed=completed,planned_trials=16,workers=1,promoted=False))
        print('Sixteen context trials and independent audit complete; no promotion.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','run','worker','parity'])
    parser.add_argument('--context',choices=CONTEXTS);parser.add_argument('--case',choices=CASES)
    parser.add_argument('--seed',type=int);parser.add_argument('--continuation',action='store_true');args=parser.parse_args()
    if args.mode=='prepare':prepare()
    elif args.mode=='parity':parity()
    elif args.mode=='worker':worker(args.context,args.case,args.seed,args.continuation)
    else:
        try:run()
        except BaseException as error:
            write(OUT/'progress.json',dict(status='interrupted',error=repr(error),promoted=False));raise

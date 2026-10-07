"""Eight-trial, single-setting closed-loop mechanism diagnostic.

Original graph/signs/inputs/decoder preserved. Local spiking identity and
adaptation kinetics are explicit engineering assumptions, not biological fits.
"""
import argparse, fcntl, hashlib, json, os, resource, subprocess, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import psutil

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import sweep_adaptive_lif as reference
from flygarden.recording import atomic_json, space_check
from flygarden.continuous_candidate import file_sha

BASE = ROOT/'reports/brain-integration/recovery'
OUT = BASE/'local-adaptation-closed-loop-v1'
SEEDS = [12201,12202]


def prepare():
    assert not OUT.exists(), 'Preserve existing evidence; resume without --prepare'
    OUT.mkdir();space_check(OUT,1200*1024**2)
    old = json.loads((BASE/'adaptive-parameter-sweep-v1/protocol.json').read_text())
    ids = pd.read_csv(ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv',index_col=0).index.to_numpy(dtype=np.int64)
    ann = pd.read_csv(ROOT/'data/annotations.tsv',sep='\t',dtype={'root_id':str},low_memory=False).fillna('').set_index('root_id').reindex([str(x) for x in ids])
    patchy = ann.cell_type.isin(['lLN2P_a','lLN2P_b','lLN2P_c']).to_numpy()
    mask = (ann.cell_class.eq('ALLN').to_numpy()) & ~patchy
    indices = np.flatnonzero(mask).tolist();assert len(indices)==395 and patchy.sum()==34
    domain = {'name':'nonpatchy_ALLN_spiking_engineering_hypothesis','indices':indices,'root_ids':[str(ids[i]) for i in indices],
              'description':'All395 annotated ALLNs excluding34 known nonspiking patchy types. Remaining exact-root spiking/compartment identities and adaptation kinetics are not established by the reviewed physiology.'}
    added = [str(Path(__file__).relative_to(ROOT)), 'reports/brain-integration/recovery/local-source-qualification-v1/results.json',
             'reports/brain-integration/recovery/local-recorded-drive-reference-v1/results.json',
             'reports/brain-integration/recovery/dm1-unitary-reference-v1/results.json']
    sources = {**old['sources'],**{name:file_sha(ROOT/name) for name in added}}
    protocol = {'version':1,'registered_before_execution':True,'mapping':old['mapping'],'selected':old['selected'],
                'selected_local_targets':old['selected_local_targets'],'pulse_windows':old['pulse_windows'],'recovery_windows':old['recovery_windows'],'burst_windows':old['burst_windows'],
                'models':['original','local_adaptive'],'calibration_seeds':SEEDS,'cues':['none','a_left'],
                'domains':{'local_adaptive':domain},'parameters':{'local_adaptive':{'tau_s':.45,'step_mv':13.5}},
                'design':'Eight 6s full-network trials; original vs local-only adaptation, matched no-odor/left-odor and two fresh diagnostic seeds. One fixed strongest previously registered setting; no grid, fitting, right-cue inference or held-out selection.',
                'question':'Does adaptation of local sources reduce or extinguish recurrent persistence when input changes with their output, rather than being replayed as fixed drive?',
                'gates':old['gates'],'original_inputs':old['original_inputs'],
                'mechanism_isolation':'No PN/ORN adaptation, inhibition bridge, sign correction, edge omission, encoder, support or decoder change. Learning frozen.',
                'scope':'Full139k-unit engineering mechanism diagnostic. Exact-root parameter fits and all395 local-cell spiking identities remain unqualified. Not a biological correction or deployable navigation controller.',
                'not_evaluated':['bilateral contrast','unequal gradient','body','learning','held-out performance'],
                'promotion':False,'full_qualification_possible':False,
                'continuation':'All four a_left trials: checkpoint at3.775s, fresh-process replay next5 windows; exact spikes/counts/inputs/motor and whole v/g/adapt error<=1e-10mV.',
                'scheduling':{'workers':1,'reason':'Existing swap use in current Mac session; preserve bounded memory and record fresh telemetry.'},
                'sources':sources}
    assert all(file_sha(ROOT/name)==sha for name,sha in sources.items())
    atomic_json(OUT/'protocol.json',protocol);atomic_json(OUT/'progress.json',{'status':'prepared','planned_trials':8,'completed':[],'promoted':False})


def verify():
    p = json.loads((OUT/'protocol.json').read_text())
    assert all(file_sha(ROOT/name)==sha for name,sha in p['sources'].items()), 'Pinned diagnostic sources changed'
    return p


def worker(model,cue,seed,resume=False):
    p=verify();folder=OUT/'trials'/f'{model}-{cue}-{seed}';start=time.monotonic();c=reference.construct(p,model,seed)
    if resume:
        c.load(folder/'checkpoint')
        for tick in range(151,156):
            d=reference.arrays(c,p,reference.advance(c,cue,tick))
            with np.load(folder/f'window-{tick:04d}.npz') as z: assert all(np.array_equal(z[k],v) for k,v in d.items()), ('Continuation mismatch',model,seed,tick)
        with np.load(folder/'continuation-state.npz') as z:errors={k:float(np.max(abs(v-z[k]))) for k,v in reference.fullstate(c).items()}
        assert max(errors.values())<=1e-10
        atomic_json(folder/'continuation-result.json',{'status':'passed','fresh_process':True,'windows':5,'errors_mV':errors});return
    folder.mkdir(parents=True,exist_ok=False);weight=hashlib.sha256(np.asarray(c.brain.synapses.w[:]).tobytes()).hexdigest()
    m={'status':'running','model':model,'case':cue,'seed':seed,'controller':c.manifest(),'sources':p['sources'],'initial_weight_hash':weight,'chunks':[]}
    atomic_json(folder/'manifest.json',m);rows=[]
    try:
        for tick in range(240):
            d=reference.arrays(c,p,reference.advance(c,cue,tick))
            assert all(np.isfinite(v).all() for v in d.values())
            assert np.array_equal(np.bincount(d['spike_i'],minlength=c.brain.n),d['counts'])
            space_check(folder,8*1024**2);file=folder/f'window-{tick:04d}.npz'
            with file.with_suffix('.tmp').open('wb') as f:np.savez_compressed(f,**d)
            file.with_suffix('.tmp').replace(file);m['chunks'].append({'file':file.name,'sha256':file_sha(file),'end':c.time})
            rows.append({'end':c.time,'population_hz':c.last['population_hz'],'motor':d['motor'].tolist()})
            atomic_json(folder/'manifest.json',m);atomic_json(folder/'rows.json',rows)
            atomic_json(OUT/'current-worker.json',{'trial':folder.name,'pid':os.getpid(),'completed_windows':tick+1,'planned_windows':240,'simulated_seconds':c.time,'wall_seconds':time.monotonic()-start,'rss_bytes':psutil.Process().memory_info().rss,'swap_used_bytes':psutil.swap_memory().used})
            if cue=='a_left' and tick==150:c.save(folder/'checkpoint')
            if cue=='a_left' and tick==155:np.savez_compressed(folder/'continuation-state.npz',**reference.fullstate(c))
        final=hashlib.sha256(np.asarray(c.brain.synapses.w[:]).tobytes()).hexdigest();assert weight==final and c.brain.plasticity.updates==0
        verify();m.update(status='complete',final_weight_hash=final,wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        atomic_json(folder/'manifest.json',m);print(folder.name,'complete',round(m['wall_seconds'],2),'s',flush=True)
    except BaseException as e:
        m.update(status='interrupted',error=repr(e));atomic_json(folder/'manifest.json',m);raise


def evaluate(p):
    traces={};locals={};inputs={};chunks=0
    for model in p['models']:
        for seed in SEEDS:
            for cue in p['cues']:
                folder=OUT/'trials'/f'{model}-{cue}-{seed}';m=json.loads((folder/'manifest.json').read_text());assert m['status']=='complete' and len(m['chunks'])==240 and m['initial_weight_hash']==m['final_weight_hash']
                rows=json.loads((folder/'rows.json').read_text());traces[(model,seed,cue)]={key:np.array([row['population_hz'][key] for row in rows]) for key in p['mapping']};local=[]
                for ch in m['chunks']:
                    path=folder/ch['file'];assert file_sha(path)==ch['sha256']
                    with np.load(path) as z:
                        assert np.array_equal(np.bincount(z['spike_i'],minlength=138639),z['counts'])
                        local.append(z['counts'][[x['index'] for x in p['selected_local_targets']]]/.025)
                        key=(seed,cue,ch['file']);sha=hashlib.sha256(z['external_i'].tobytes()+z['external_t'].tobytes()).hexdigest()
                        if key in inputs:assert sha==inputs[key], 'Paired input difference'
                        else:inputs[key]=sha
                    chunks+=1
                locals[(model,seed,cue)]=np.array(local)
    records=[];bursts=[];support=[];g=p['gates']
    for model in p['models']:
        for seed in SEEDS:
            none=traces[(model,seed,'none')];cue=traces[(model,seed,'a_left')]
            support.append({'model':model,'seed':seed,'passed':all(none[k].mean()>=g['walking_support_retention_fraction']*traces[('original',seed,'none')][k].mean() for k in ['DNp09_left','DNp09_right'])})
            pn=(cue['DM1_lPN_left']+cue['DM1_lPN_right'])/2;neutral=(none['DM1_lPN_left']+none['DM1_lPN_right'])/2
            for pulse,(pl,ph),(rl,rh) in zip([1,2],p['pulse_windows'],p['recovery_windows']):
                gain=float(pn[pl:ph].mean()-(neutral[pl:ph].mean() if pulse==1 else pn[100:120].mean()))
                pdiff=[float(cue[k][rl:rh].mean()-none[k][rl:rh].mean()) for k in ['DM1_lPN_left','DM1_lPN_right']]
                ldiff=locals[(model,seed,'a_left')][rl:rh].mean(0)-locals[(model,seed,'none')][rl:rh].mean(0)
                dna=float((cue['DNa02_left']-cue['DNa02_right']-none['DNa02_left']+none['DNa02_right'])[rl:rh].mean())
                records.append({'model':model,'seed':seed,'pulse':pulse,'gain_hz':gain,'pn_recovery_difference_hz':pdiff,'local_recovery_difference_hz':ldiff.tolist(),'signed_dna_recovery_difference_hz':dna,
                                'response_passed':gain>=g['response_gain_hz'],'PN_recovery_passed':max(abs(x) for x in pdiff)<=g['individual_PN_and_local_recovery_difference_hz'],
                                'local_recovery_passed':bool(np.max(abs(ldiff))<=g['individual_PN_and_local_recovery_difference_hz']),'DNa02_recovery_passed':abs(dna)<=g['signed_DNa02_recovery_difference_hz']})
            for lo,hi in p['burst_windows']:
                excess=pn-neutral;maximum=max(float(excess[i:i+4].mean()) for i in range(lo,hi-3))
                bursts.append({'model':model,'seed':seed,'window':[lo,hi],'max_100ms_PN_excess_hz':maximum,'passed':maximum<=g['burst_100ms_recovery_PN_difference_hz']})
    return {'status':'complete','chunks_audited':chunks,'paired_external_inputs_exact':True,'records':records,'bursts':bursts,'support':support,'controller_promoted':False,'full_qualification':False,'scope':'Only no-odor and left-odor mechanism checks. Bilateral/gradient/navigation/learning untested.'}


def run():
    p=verify();done=[];start=time.monotonic();samples=[]
    with (ROOT/'.runtime/experiment.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for seed in SEEDS:
            for model in p['models']:
                for cue in p['cues']:
                    name=f'{model}-{cue}-{seed}';folder=OUT/'trials'/name
                    atomic_json(OUT/'progress.json',{'status':'running','completed':done,'planned_trials':8,'current':name,'workers':1,'pid':os.getpid(),'promoted':False})
                    if (folder/'manifest.json').exists():assert json.loads((folder/'manifest.json').read_text())['status']=='complete','Interrupted trial requires checkpoint-aware recovery; complete chunks remain preserved'
                    else:
                        space_check(OUT,1200*1024**2);subprocess.run([sys.executable,'-B',__file__,'--worker','--model',model,'--cue',cue,'--seed',str(seed)],cwd=ROOT,check=True)
                    if cue=='a_left' and not (folder/'continuation-result.json').exists():subprocess.run([sys.executable,'-B',__file__,'--worker','--model',model,'--cue',cue,'--seed',str(seed),'--resume'],cwd=ROOT,check=True)
                    done.append(name);s=psutil.swap_memory();samples.append({'trial':name,'swap_used_bytes':s.used,'swap_out_bytes':s.sout,'available_bytes':psutil.virtual_memory().available})
        result=evaluate(p);result.update(trials=8,wall_seconds=time.monotonic()-start,scheduling_samples=samples)
        atomic_json(OUT/'results.json',result);atomic_json(OUT/'progress.json',{'status':'complete','completed':done,'planned_trials':8,'workers':1,'full_qualification':False,'promoted':False})
        print('Eight-trial mechanism diagnostic complete',flush=True)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--prepare',action='store_true');a.add_argument('--worker',action='store_true');a.add_argument('--resume',action='store_true');a.add_argument('--model');a.add_argument('--cue');a.add_argument('--seed',type=int);args=a.parse_args()
    if args.prepare:prepare()
    elif args.worker:worker(args.model,args.cue,args.seed,args.resume)
    else:
        try:run()
        except BaseException as e:atomic_json(OUT/'progress.json',{'status':'interrupted','error':repr(e),'promoted':False});raise

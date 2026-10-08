"""Independent raw-event/context-pairing audit; no neural evaluator imports."""
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.recording import atomic_json
OUT=ROOT/'reports/brain-integration/recovery/sensory-context-capability-v1'
KEYS=['MBON32_left','MBON32_right','DNa02_left','DNa02_right','DNp09_left','DNp09_right','DM1_lPN_left','DM1_lPN_right']


def main():
    start=time.monotonic();p=json.loads((OUT/'protocol.json').read_text());r=json.loads((OUT/'results.json').read_text())
    assert r['status']=='complete' and r['protocol_sha256']==file_sha(OUT/'protocol.json')
    assert all(file_sha(ROOT/k)==v for k,v in p['sources'].items())
    traces={};support_train={};ordinary_train={};direct_train={};chunks=0;motor_error=0.
    targets=[p['mapping'][key][0]['index'] for key in KEYS]+[x['index'] for x in p['selected_local_targets']]
    engagement={x['name']:x for x in r['engagement']}
    for job in p['jobs']:
        context=job['context'];seed=job['seed'];case=job['case'];folder=OUT/'trials'/job['name']
        m=json.loads((folder/'manifest.json').read_text());rows=json.loads((folder/'rows.json').read_text())
        assert m['status']=='complete' and len(m['chunks'])==len(rows)==240
        assert m['sources']==p['sources'] and m['protocol_sha256']==file_sha(OUT/'protocol.json')
        assert m['initial_weight_hash']==m['final_weight_hash']=='f6f6ab9f7c49e14a906d120c705e6af7814ecdeeecaaefad8b1280bdb71e7732' and m['learning_updates']==0
        assert m['controller']['direct_capability_input']['additional_zero_refractory_indices']==p['direct_targets']
        assert m['controller']['sensory_context']['context']==context and m['controller']['sensory_context']['ordinary_input_monitor']
        channels=np.asarray(m['controller']['input_channels']);rng=np.random.default_rng(seed);direct_rng=np.random.default_rng(seed+100000)
        recorded=[];domain=[];relay=[];whole=np.zeros(138639,np.int64);motor=np.zeros(2)
        for tick,ch in enumerate(m['chunks']):
            file=folder/ch['file'];assert file_sha(file)==ch['sha256']
            pulse=any(lo<=tick<hi for lo,hi in p['pulse_windows']);rates=np.zeros(8);rates[4:6]=65.
            if context=='DM1_equal_50_50' and pulse:rates[:2]=25.
            offsets,si=np.nonzero(rng.random((250,len(channels)))<rates[channels]*.0001)
            direct_rates=np.zeros(2)
            if pulse:
                if case in ['left','both']:direct_rates[0]=50.
                if case in ['right','both']:direct_rates[1]=50.
            mo,mi=np.nonzero(direct_rng.random((250,2))<direct_rates*.0001)
            with np.load(file) as z:
                counts=np.bincount(z['spike_i'],minlength=138639);np.testing.assert_array_equal(counts,z['counts'])
                st=np.rint(z['spike_t']/.0001).astype(np.int64);assert np.allclose(st*.0001,z['spike_t'],atol=1e-10,rtol=0)
                assert np.all((st>=tick*250)&(st<(tick+1)*250))
                np.testing.assert_array_equal(z['external_i'],si)
                np.testing.assert_array_equal(np.rint(z['external_t']/.0001).astype(np.int64),tick*250+offsets)
                np.testing.assert_array_equal(z['input_delivered_i'],si);np.testing.assert_allclose(z['input_delivered_t'],z['external_t'],atol=1e-12,rtol=0)
                np.testing.assert_array_equal(z['mbon_i'],mi);np.testing.assert_array_equal(np.rint(z['mbon_t']/.0001).astype(np.int64),tick*250+mo)
                np.testing.assert_array_equal(z['mbon_delivered_i'],mi);np.testing.assert_allclose(z['mbon_delivered_t'],z['mbon_t'],atol=1e-12,rtol=0)
                keep=np.isin(channels[si],[4,5]);support=np.c_[si[keep],(tick*250+offsets)[keep]].astype(np.int64)
                digest=hashlib.sha256(support.tobytes()).hexdigest()
                if (seed,tick) in support_train:assert digest==support_train[seed,tick]
                else:support_train[seed,tick]=digest
                ordinary=np.c_[si,tick*250+offsets].astype(np.int64);digest=hashlib.sha256(ordinary.tobytes()).hexdigest()
                if (context,seed,tick) in ordinary_train:assert digest==ordinary_train[context,seed,tick]
                else:ordinary_train[context,seed,tick]=digest
                for side in [0,1]:
                    if case in (['left','both'] if side==0 else ['right','both']):
                        times=np.rint(z['mbon_t'][z['mbon_i']==side]/.0001).astype(np.int64);digest=hashlib.sha256(times.tobytes()).hexdigest()
                        if (seed,tick,side) in direct_train:assert digest==direct_train[seed,tick,side]
                        else:direct_train[seed,tick,side]=digest
                expected={key:float(counts[[n['index'] for n in pop]].mean()/.025) if pop else None for key,pop in p['mapping'].items()}
                assert expected==rows[tick]['population_hz']
                assert rows[tick]['requested_hz']==dict(zip(['ORN_DM1_left','ORN_DM1_right','ORN_DM2_left','ORN_DM2_right','DNp09_left','DNp09_right','LPLC2_left','LPLC2_right'],rates.tolist()))
                forward=np.clip((expected['DNp09_left']+expected['DNp09_right'])/2/100,0,1)
                turn=np.clip((expected['DNa02_left']-expected['DNa02_right'])/100,-1,1)
                desired=np.clip([forward-.5*turn,forward+.5*turn],0,1.2)
                alpha=1-np.exp(-.025/.4481420117724551);motor=(1-alpha)*motor+alpha*desired
                motor_error=max(motor_error,float(max(abs(motor-z['motor']))))
                np.testing.assert_array_equal(motor,z['motor']);np.testing.assert_array_equal(motor,rows[tick]['motor'])
                assert all(np.isfinite(z[k]).all() for k in z.files)
                assert z['v_mV'].shape==z['g_mV'].shape==z['adapt_mV'].shape==(len(p['selected']),)
                assert not z['adapt_mV'][[p['selected'].index(i) for i in p['direct_targets']]].any()
                recorded.append(counts[targets]/.025);domain.append(counts[p['adaptation_indices']]);relay.append(counts[p['relay_indices']]);whole+=counts
            assert abs(ch['end']-(tick+1)*.025)<1e-10 and rows[tick]['end']==ch['end'];chunks+=1
        traces[context,seed,case]=np.asarray(recorded)
        observed=engagement[job['name']];assert observed['whole_spikes']==int(whole.sum()) and observed['whole_active_neurons']==int(np.count_nonzero(whole))
        assert observed['adaptation_domain_spikes']==int(np.asarray(domain).sum())
        for row,(lo,hi) in zip(observed['pulses'],p['pulse_windows']):
            assert abs(row['adaptation_domain_mean_hz']-np.asarray(domain)[lo:hi].sum()/len(p['adaptation_indices'])/(hi-lo)/.025)<1e-10
            assert row['active_adaptation_neurons']==int(np.count_nonzero(np.asarray(domain)[lo:hi].sum(0)))
            assert row['active_two_hop_intermediates']==int(np.count_nonzero(np.asarray(relay)[lo:hi].sum(0)))
        print('Independent context raw/RNG audit',job['name'],flush=True)
    checks=0
    for context,metrics in r['contexts'].items():
        def mean(seed,case,lo,hi):return traces[context,seed,case][lo:hi].sum(0)/(hi-lo)
        for row in metrics['direction']:
            seed=row['seed'];lo,hi=p['pulse_windows'][row['pulse']-1]
            contrast={c:float(mean(seed,c,lo,hi)[2]-mean(seed,c,lo,hi)[3]) for c in p['cases']}
            delta={c:contrast[c]-contrast['none'] for c in ['left','right','both']}
            flags=[delta['left']>=5,delta['right']<=-5,abs(delta['both'])<=5,
                contrast['left']-contrast['right']>=10 and contrast['left']>contrast['none'] and contrast['right']<contrast['none']]
            assert row['contrast_hz']==contrast and row['delta_from_none_hz']==delta and row['separation_hz']==contrast['left']-contrast['right']
            assert row['passed']==all(flags)
            for key,value in zip(['left_delta_at_least_5Hz','right_delta_at_most_minus_5Hz','bilateral_delta_within_5Hz','existing_descending_opponent_bound'],flags):assert row[key]==value
            checks+=1
        for row in metrics['responses']:
            lo,hi=p['pulse_windows'][row['pulse']-1];seed=row['seed'];case=row['case'];sides=row['stimulated_sides']
            t=mean(seed,case,lo,hi);n=mean(seed,'none',lo,hi);previous=n if row['pulse']==1 else mean(seed,case,100,120)
            gain=t[sides]-n[sides];renewed=t[sides]-previous[sides]
            assert row['matched_control_gain_hz']==gain.tolist() and row['gain_from_previous_recovery_hz']==renewed.tolist()
            assert row['passed']==bool(np.all(gain>=10) and np.all(renewed>=10));checks+=1
        for row in metrics['recovery']:
            lo,hi=p['recovery_windows'][row['pulse']-1];delta=mean(row['seed'],row['case'],lo,hi)-mean(row['seed'],'none',lo,hi)
            flags=[max(abs(delta[:2]))<=5,max(abs(delta[6:]))<=5,abs(delta[2]-delta[3])<=5]
            assert row['individual_difference_hz']==delta.tolist() and row['passed']==all(flags)
            for key,value in zip(['MBON_recovery_passed','PN_local_recovery_passed','signed_DNa02_recovery_passed'],flags):assert row[key]==value
            checks+=1
        for row in metrics['support_perturbation']:
            lo,hi=p['pulse_windows' if row['phase']=='pulse' else 'recovery_windows'][row['pulse']-1]
            actual=mean(row['seed'],row['case'],lo,hi)[4:6];none=mean(row['seed'],'none',lo,hi)[4:6]
            assert row['actual_hz']==actual.tolist() and row['matched_candidate_none_hz']==none.tolist()
            assert row['passed']==bool(np.all(none>0) and np.all(actual>=.8*none));checks+=1
        for row in metrics['bursts']:
            lo,hi=row['window'];excess=traces[context,row['seed'],row['case']]-traces[context,row['seed'],'none']
            sums=np.cumsum(np.vstack([np.zeros((1,12)),excess]),axis=0);moving=(sums[lo+4:hi+1]-sums[lo:hi-3])/4
            mbon=moving[:,:2].max(0).tolist();pn=float(moving[:,6:8].mean(1).max())
            assert row['MBON_100ms_excess_hz']==mbon and row['PN_100ms_excess_hz']==pn and row['passed']==(max(mbon)<=20 and pn<=20);checks+=1
        families=['direction','responses','recovery','support_perturbation','bursts']
        assert metrics['capability_neural_checks_passed']==all(row['passed'] for key in families for row in metrics[key])
    for receipt in r['continuation_checks']:
        folder=OUT/'trials'/receipt['trial'];integrity=folder/'checkpoint/integrity.json'
        assert receipt['status']=='passed' and receipt['fresh_process'] and max(receipt['errors_mV'].values())<=1e-10
        assert receipt['checkpoint_integrity_sha256']==file_sha(integrity)
        for file,digest in json.loads(integrity.read_text())['files'].items():assert file_sha(integrity.parent/file)==digest
    parity=json.loads((OUT/'no-context-parity.json').read_text());assert parity['status']=='passed' and parity['historical_arrays_exact'] and parity['windows']==36
    parent=ROOT/'reports/brain-integration/recovery/recovered-mbon32-capability-v1/trials'/parity['parent']
    for ch in parity['prefix']:assert file_sha(parent/ch['file'])==ch['sha256']
    interrupted=json.loads((OUT/'interruption-test.json').read_text());m=json.loads((OUT/'trials'/interrupted['trial']/'manifest.json').read_text())
    assert interrupted['status']=='passed' and interrupted['prefix_reconstructed_exactly'] and m['chunks'][:len(interrupted['complete_prefix'])]==interrupted['complete_prefix']
    assert all(file_sha(ROOT/k)==v for k,v in p['sources'].items())
    atomic_json(OUT/'independent-audit.json',dict(status='passed',protocol_sha256=file_sha(OUT/'protocol.json'),result_sha256=file_sha(OUT/'results.json'),
        chunks_rehashed=chunks,capability_metrics_checked=checks,raw_count_clock_motor_exact=True,maximum_motor_error=motor_error,
        support_generator_trains_identical_across_contexts_cases=True,ordinary_input_trains_identical_within_context=True,
        direct_generator_trains_identical_across_contexts_and_match_bilateral=True,all_requested_delivered_generator_events_exact=True,
        original_context_specific_controls_and_bounds_checked=True,four_checkpoint_receipts_and_hashes_valid=True,
        historical_no_context_prefix_valid=True,interrupted_prefix_reconstructed_exactly=True,sources_reverified=True,
        controller_promoted=False,wall_seconds=time.monotonic()-start))
    print('Independent audit passed',chunks,'chunks;',checks,'original capability metric rows.',flush=True)


if __name__=='__main__':main()

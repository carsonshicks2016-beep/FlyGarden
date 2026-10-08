"""Independently sum delivered events and validate derived population profiles."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from flygarden.recording import atomic_json
from scripts.trace_sensory_steering import OUT, PRIOR, sha


def main():
    p=json.loads((OUT/'protocol.json').read_text())
    r=json.loads((OUT/'results.json').read_text())
    assert r['status']=='complete' and r['protocol_sha256']==sha(OUT/'protocol.json')
    assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
    roots=json.loads((OUT/'population-roots.json').read_text())
    assert sha(OUT/'population-roots.json')==p['root_manifest_sha256']
    lookup={x['index']:x for x in roots['nodes']}
    summaries={(s['trial'],s['phase']):s for s in r['summaries']}
    target_indices=p['target_indices']
    graph=pd.read_parquet(ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet',
                          columns=['Presynaptic_Index','Postsynaptic_Index','Excitatory x Connectivity'],
                          filters=[('Postsynaptic_Index','in',target_indices)])
    dense=[np.bincount(graph.loc[graph.Postsynaptic_Index.eq(t),'Presynaptic_Index'],
                      weights=graph.loc[graph.Postsynaptic_Index.eq(t),'Excitatory x Connectivity']*.275,
                      minlength=138639) for t in target_indices]
    max_error=0.;contributions_checked=0;profiles_checked=0;phase_counts_checked=0
    external_support={};chunks=0
    for name in p['trials']:
        profile=OUT/r['profiles'][name]['file'];assert sha(profile)==r['profiles'][name]['sha256']
        with np.load(profile) as z:
            counts=z['counts_25ms'];indices=z['profile_indices'];rates=z['population_hz']
            for k,key in enumerate(r['population_keys']):
                members=np.searchsorted(indices,p['populations'][key])
                if not len(members):assert np.isnan(rates[:,k]).all();continue
                np.testing.assert_allclose(rates[:,k],counts[:,members].sum(1)/len(members)/.025,atol=1e-12,rtol=0)
            for phase,(lo,hi) in p['phase_ticks'].items():
                s=summaries[name,phase];duration=(hi-lo)*.0001
                for node in s['individual_rates']:
                    column=np.searchsorted(indices,node['index'])
                    assert lookup[node['index']]['root_id']==node['root_id']
                    assert node['rate_hz']==counts[lo//250:hi//250,column].sum()/duration
                    phase_counts_checked+=1
            profiles_checked+=1
        folder=PRIOR/'trials'/name;m=json.loads((folder/'manifest.json').read_text())
        events=[];times=[]
        for k,chunk in enumerate(m['chunks']):
            path=folder/chunk['file'];assert sha(path)==chunk['sha256']
            with np.load(path) as z:
                events.append(z['spike_i'].copy());times.append(np.rint(z['spike_t']/.0001).astype(np.int64))
                channels=np.asarray(m['controller']['input_channels'])
                support_mask=np.isin(channels[z['external_i']],[4,5])
                support_hash=hashlib.sha256(z['external_i'][support_mask].tobytes()+z['external_t'][support_mask].tobytes()).hexdigest()
                key=(m['seed'],k)
                if key in external_support:assert support_hash==external_support[key]
                else:external_support[key]=support_hash
            chunks+=1
        events=np.concatenate(events);times=np.concatenate(times);arrivals=times+18
        # Search observed spike times directly; do not call the analyzer's gate,
        # phase_delivery helper, or sparse impulse reconstruction.
        for j,target in enumerate(target_indices):
            target_times=times[events==target]
            last=np.searchsorted(target_times,arrivals,side='right')-1
            distance=np.full(len(arrivals),10**9,dtype=np.int64)
            has_last=last>=0;distance[has_last]=arrivals[has_last]-target_times[last[has_last]]
            delivered=dense[j][events]
            accepted=distance>=22
            for phase,(lo,hi) in p['phase_ticks'].items():
                mask=(arrivals>=lo)&(arrivals<hi);duration=(hi-lo)*.0001
                expected=summaries[name,phase]['inputs'][j]
                assert expected['index']==target
                for field,values in [('pregate',delivered[mask]),('accepted',delivered[mask & accepted])]:
                    positive=float(values[values>0].sum()/duration)
                    negative=float(-values[values<0].sum()/duration)
                    for key,value in [('positive_mV_per_s',positive),('negative_mV_per_s',negative),('net_mV_per_s',positive-negative)]:
                        error=abs(expected[field][key]-value);max_error=max(max_error,error)
                        assert error<1e-8,(name,phase,target,key,error)
                        contributions_checked+=1
        print(name,'independent event accounting passed',flush=True)
    assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
    atomic_json(OUT/'independent-audit.json',dict(status='passed',chunks_rehashed=chunks,
        profiles_checked=profiles_checked,individual_phase_rates_checked=phase_counts_checked,
        signed_totals_checked=contributions_checked,maximum_signed_error_mV_per_s=max_error,
        event_gate_method='Direct last-spike search at each arrival; independent of sparse replay and phase_delivery.',
        support_event_trains_identical_across_cues_and_models=True,sources_reverified=True,
        source_sha256=sha(Path(__file__)),native_full_brain_runs=0,controller_changed=False))
    print('Independent checks passed:',contributions_checked,'signed totals;',chunks,'chunks',flush=True)


if __name__=='__main__':main()

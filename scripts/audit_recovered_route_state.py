"""Independent dense-event, raw-recording and closed-form audit.

No Brian2, analysis runner, replay helper or delivery/timing helper is imported.
"""
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from flygarden.recording import atomic_json
OUT=ROOT/'reports/brain-integration/recovery/recovered-route-state-audit-v1'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()


def totals(values):
    positive=float(np.sum(values[values>0]));negative=float(-np.sum(values[values<0]))
    return {'positive_mV_per_s':positive,'negative_mV_per_s':negative,'net_mV_per_s':positive-negative}


def close(actual,expected):
    assert actual.keys()==expected.keys()
    for key in actual:
        assert abs(actual[key]-expected[key])<=1e-9,(key,actual[key],expected[key])


def timing_check(row,a,b):
    sa=set(a.tolist());sb=set(b.tolist())
    expected=dict(reference_count=len(a),changed_count=len(b),shared_ticks=len(sa&sb),
        event_disagreements=len(sa^sb),count_delta=len(b)-len(a),exact_ticks_equal=sa==sb,
        equal_counts_different_ticks=len(a)==len(b) and sa!=sb)
    assert all(row[key]==value for key,value in expected.items())
    if len(a) and len(b):
        distance=np.abs(a[:,None]-b[None,:]);nearest=np.r_[distance.min(1),distance.min(0)]*.1
        assert abs(row['symmetric_nearest_event_median_ms']-np.median(nearest))<=1e-12
        assert abs(row['symmetric_nearest_event_max_ms']-nearest.max())<=1e-12
    else:assert row['symmetric_nearest_event_median_ms'] is row['symmetric_nearest_event_max_ms'] is None


def main():
    start=time.monotonic();p=json.loads((OUT/'protocol.json').read_text());r=json.loads((OUT/'results.json').read_text())
    assert r['status']=='complete' and sha(OUT/'protocol.json')==r['protocol_sha256']
    assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
    assert sha(OUT/'anatomical-inventory.json')==p['anatomy_sha256']
    ids=pd.read_csv(ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv',index_col=0).index.to_numpy(dtype=np.int64)
    a=pd.read_csv(ROOT/'data/annotations.tsv',sep='\t',dtype={'root_id':str},low_memory=False).fillna('')
    a=a.set_index('root_id').reindex(ids.astype(str)).fillna('')
    targets=[x['index'] for x in p['targets']];mbon=[x['index'] for x in p['mbon_targets']]
    graph_path=ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet'
    incoming=pd.read_parquet(graph_path,filters=[('Postsynaptic_Index','in',targets)])
    outgoing=pd.read_parquet(graph_path,filters=[('Presynaptic_Index','in',mbon)])
    inventory=json.loads((OUT/'anatomical-inventory.json').read_text())
    assert len(outgoing)==inventory['outgoing_record_count'] and int(outgoing.Connectivity.sum())==inventory['outgoing_anatomical_sites']
    for _,edge in outgoing.iterrows():
        saved=next(x for x in inventory['outgoing_records'] if x['Presynaptic_Index']==edge.Presynaptic_Index and x['Postsynaptic_Index']==edge.Postsynaptic_Index)
        for key in outgoing.columns:assert saved[key]==edge[key]
        for key,index in [('source',int(edge.Presynaptic_Index)),('target',int(edge.Postsynaptic_Index))]:
            assert saved[key]['root_id']==str(ids[index])
            assert all(saved[key][k]==str(a.iloc[index][k]) for k in ['cell_type','cell_class','side','known_nt','top_nt'])
    assert set(p['recipient_indices'])==set(outgoing.Postsynaptic_Index)
    assert set(p['relay_indices'])==set(outgoing.Postsynaptic_Index)&set(incoming.Presynaptic_Index)
    dense=np.stack([np.bincount(incoming.loc[incoming.Postsynaptic_Index.eq(t),'Presynaptic_Index'],
        weights=incoming.loc[incoming.Postsynaptic_Index.eq(t),'Excitatory x Connectivity']*.275,minlength=len(ids)) for t in targets])
    aotu=set(np.flatnonzero(a.cell_type.eq('AOTU019')));relay=set(p['relay_indices'])-set(mbon)-aotu
    parts={'direct_MBON32':np.isin(np.arange(len(ids)),mbon),'AOTU019':np.isin(np.arange(len(ids)),list(aotu)),
           'other_two_hop':np.isin(np.arange(len(ids)),list(relay))}
    parts['remaining']=~(parts['direct_MBON32']|parts['AOTU019']|parts['other_two_hop'])
    records={(x['parent'],x['condition']):x for x in r['replays']};inputs={x['parent']:x for x in r['input_files']}
    drive=np.empty((60000,48));expected_spikes=np.zeros((60000,48),bool)
    expected_counts=np.zeros((240,48),np.int64);expected_v=np.empty((240,48));expected_g=np.empty((240,48))
    native={};chunks=0;pop_checks=0;delivery_checks=0;direct_checks=0;max_drive_error=0.;lane=0
    for number,trial in enumerate(r['trials']):
        job=p['trials'][number];assert all(job[k]==trial[k] for k in job)
        folder=ROOT/p['archives'][job['archive']]/'trials'/job['name']
        m=json.loads((folder/'manifest.json').read_text());parent=json.loads((folder.parents[1]/'protocol.json').read_text())
        selected=parent['selected'];cols=[selected.index(t) for t in targets]
        ii=[];tt=[];raw_counts=[];v=[];g=[];whole=np.zeros(len(ids),np.int64);requested=[];delivered=[]
        for k,ch in enumerate(m['chunks']):
            path=folder/ch['file'];assert sha(path)==ch['sha256']
            with np.load(path) as z:
                indices=z['spike_i'];ticks=np.rint(z['spike_t']/.0001).astype(np.int64)
                assert np.allclose(ticks*.0001,z['spike_t'],atol=1e-10,rtol=0)
                assert np.all((ticks>=k*250)&(ticks<(k+1)*250))
                np.testing.assert_array_equal(np.bincount(indices,minlength=len(ids)),z['counts'])
                whole+=z['counts'];raw_counts.append(z['counts'][p['profile_indices']]);ii.append(indices.copy());tt.append(ticks)
                v.append(z['v_mV'][cols]);g.append(z['g_mV'][cols])
                if 'adapt_mV' in z:assert not z['adapt_mV'][cols].any()
                if job['archive']=='direct':
                    requested.append(np.bincount(z['mbon_i'],minlength=2));delivered.append(np.bincount(z['mbon_delivered_i'],minlength=2))
            chunks+=1
        ii=np.concatenate(ii);tt=np.concatenate(tt);raw_counts=np.asarray(raw_counts);v=np.asarray(v);g=np.asarray(g)
        assert trial['whole_network_spikes']==int(whole.sum()) and trial['whole_network_active_neurons']==int(np.count_nonzero(whole))
        assert trial['adaptation_domain_spikes']==int(whole[p['adaptation_domain']].sum())
        f=OUT/trial['profile_file'];assert sha(f)==trial['profile_sha256']
        with np.load(f) as z:
            for key,value in [('counts_25ms',raw_counts),('profile_indices',p['profile_indices']),('spike_i',ii),('spike_ticks',tt),('recorded_v_mV',v),('recorded_g_mV',g)]:
                np.testing.assert_array_equal(z[key],value)
        routecols=np.searchsorted(p['profile_indices'],p['recipient_indices'])
        for phase in trial['phases']:
            lo,hi=p['phase_ticks'][phase['phase']];duration=(hi-lo)*.0001;bins=slice(lo//250,hi//250)
            for label,pop in phase['populations'].items():
                group=p['adaptation_domain'] if label=='adaptation_domain' else p['populations'][label]
                assert pop['neurons']==len(group)
                if group:
                    values=raw_counts[bins][:,np.searchsorted(p['profile_indices'],group)].sum(0)
                    assert abs(pop['mean_hz']-values.sum()/len(group)/duration)<1e-9
                    assert abs(pop['active_fraction']-np.count_nonzero(values)/len(group))<1e-12
                else:assert pop['mean_hz'] is pop['active_fraction'] is None
                pop_checks+=1
            np.testing.assert_array_equal(phase['recipient_spike_counts'],raw_counts[bins][:,routecols].sum(0))
            for j,node in enumerate(phase['DNa02_delivery']):
                assert node['target_index']==targets[j]
                arrival=tt+18;keep=(arrival>=lo)&(arrival<hi);src=ii[keep];times=arrival[keep]
                target_spikes=np.sort(tt[ii==targets[j]]);last=np.searchsorted(target_spikes,times,side='right')-1
                valid=np.ones(len(times),bool);observed=last>=0
                valid[observed]=times[observed]-target_spikes[last[observed]]>=22
                pre=np.bincount(src,weights=dense[j,src],minlength=len(ids))/duration
                post=np.bincount(src[valid],weights=dense[j,src[valid]],minlength=len(ids))/duration
                close(node['before'],totals(pre));close(node['accepted'],totals(post));delivery_checks+=2
                for key,mask in parts.items():
                    close(node['partitions'][key]['before'],totals(pre[mask]));close(node['partitions'][key]['accepted'],totals(post[mask]));delivery_checks+=2
                assert node['spikes']==int(np.sum((target_spikes>=lo)&(target_spikes<hi)))
                ev=v[bins,j];eg=g[bins,j]
                close(node['observed_endpoint_voltage'],dict(min_mV=float(ev.min()),max_mV=float(ev.max()),mean_mV=float(ev.mean()),minimum_threshold_headroom_mV=float(-45-ev.max())))
                close(node['observed_endpoint_g'],dict(min_mV=float(eg.min()),max_mV=float(eg.max()),mean_mV=float(eg.mean())))
                for edge in node['direct_edges']:
                    source=edge['source_index'];assert edge['jump_mV']==dense[j,source]
                    n=int(np.sum(src==source));accepted=int(np.sum((src==source)&valid))
                    assert (edge['arrivals'],edge['accepted'],edge['rejected'])==(n,accepted,n-accepted)
                    assert abs(edge['before_mV_per_s']-n*dense[j,source]/duration)<1e-9
                    assert abs(edge['accepted_mV_per_s']-accepted*dense[j,source]/duration)<1e-9
                    direct_checks+=1
        if job['archive']=='direct':
            for row,(lo,hi) in zip(trial['direct_input'],p['pulse_windows']):
                np.testing.assert_array_equal(row['requested_events'],np.asarray(requested)[lo:hi].sum(0))
                np.testing.assert_array_equal(row['delivered_generator_events'],np.asarray(delivered)[lo:hi].sum(0))
                np.testing.assert_array_equal(row['MBON32_response_events'],[int(np.sum((ii==t)&(tt>=lo*250)&(tt<hi*250))) for t in mbon])
            inp=OUT/inputs[job['name']]['file'];assert sha(inp)==inputs[job['name']]['sha256']
            arrival=tt+18;keep=arrival<60000
            with np.load(inp) as z:
                for j in range(2):
                    summed=np.bincount(arrival[keep],weights=dense[j,ii[keep]],minlength=60000)
                    err=float(np.max(abs(summed-z['arrivals_mV'][:,j])));max_drive_error=max(max_drive_error,err);assert err<=1e-10
            for condition in p['conditions']:
                record=records[job['name'],condition];f=OUT/record['file'];assert sha(f)==record['sha256']
                block=slice(lane,lane+2)
                for j in range(2):
                    weights=dense[j].copy()
                    if condition=='without_left_MBON32_edge':weights[mbon[0]]=0
                    if condition=='without_right_MBON32_edge':weights[mbon[1]]=0
                    drive[:,lane+j]=np.bincount(arrival[keep],weights=weights[ii[keep]],minlength=60000)
                with np.load(f) as z:
                    expected_spikes[z['spike_ticks'],lane+z['spike_i']]=True
                    counts=np.zeros((240,2),np.int64);np.add.at(counts,(z['spike_ticks']//250,z['spike_i']),1)
                    np.testing.assert_array_equal(counts,z['counts_25ms']);assert not z['adapt_mV'].any()
                    expected_counts[:,block]=counts;expected_v[:,block]=z['v_mV'];expected_g[:,block]=z['g_mV']
                    native[job['name'],condition]=dict(ii=z['spike_i'].copy(),ticks=z['spike_ticks'].copy(),counts=counts)
                    if condition=='intact':
                        np.testing.assert_allclose(z['v_mV'],v,atol=1e-10,rtol=0);np.testing.assert_allclose(z['g_mV'],g,atol=1e-10,rtol=0)
                        for j,t in enumerate(targets):np.testing.assert_array_equal(z['spike_ticks'][z['spike_i']==j],tt[ii==t])
                lane+=2
        print('Independent raw/event audit',number+1,'/36',job['archive'],job['name'],flush=True)
    assert chunks==8640 and lane==48
    # Independent linear closed-form integration. Gates follow these newly
    # predicted threshold crossings, not any observed or native replay spikes.
    ev=np.exp(-.0001/.020);eg=np.exp(-.0001/.005);coupling=.005/(.020-.005)*(ev-eg)
    voltage=np.full(48,-52.);conductance=np.zeros(48);last=np.full(48,-10**9,np.int64)
    counts=np.zeros_like(expected_counts);errors={'v_mV':0.,'g_mV':0.}
    for tick in range(60000):
        eligible=tick-last>=22
        voltage[eligible]=-52+(voltage[eligible]+52)*ev+conductance[eligible]*coupling;conductance[eligible]*=eg
        spikes=eligible&(voltage>-45)
        assert np.array_equal(spikes,expected_spikes[tick]),('Threshold mismatch',tick)
        conductance[eligible&~spikes]+=drive[tick,eligible&~spikes]
        voltage[spikes]=-52;conductance[spikes]=0;last[spikes]=tick;counts[tick//250]+=spikes
        if tick%250==249:
            errors['v_mV']=max(errors['v_mV'],float(np.max(abs(voltage-expected_v[tick//250]))))
            errors['g_mV']=max(errors['g_mV'],float(np.max(abs(conductance-expected_g[tick//250]))))
    np.testing.assert_array_equal(counts,expected_counts);assert max(errors.values())<=1e-10
    timing_checks=0
    for row in r['matched_direct_timing']:
        lo,hi=p['phase_ticks'][row['phase']];base=native[f"none-{row['seed']}",'intact'];changed=native[row['parent'],'intact']
        for j,target in enumerate(row['DNa02']):
            a=base['ticks'][(base['ii']==j)&(base['ticks']>=lo)&(base['ticks']<hi)]
            b=changed['ticks'][(changed['ii']==j)&(changed['ticks']>=lo)&(changed['ticks']<hi)]
            timing_check(target,a,b);timing_checks+=1
    for row in r['fixed_source_edge_removals']:
        lo,hi=p['phase_ticks'][row['phase']];base=native[row['parent'],'intact'];changed=native[row['parent'],row['condition']]
        for key,values in [('intact_hz',base),('altered_hz',changed)]:
            np.testing.assert_array_equal(row[key],values['counts'][lo//250:hi//250].sum(0)/((hi-lo)*.0001))
        for j,target in enumerate(row['DNa02']):
            a=base['ticks'][(base['ii']==j)&(base['ticks']>=lo)&(base['ticks']<hi)]
            b=changed['ticks'][(changed['ii']==j)&(changed['ticks']>=lo)&(changed['ticks']<hi)]
            timing_check(target,a,b);timing_checks+=1
    assert all(sha(ROOT/key)==value for key,value in p['source_hashes'].items())
    receipt=dict(status='passed',protocol_sha256=sha(OUT/'protocol.json'),results_sha256=sha(OUT/'results.json'),
        raw_chunks_rehashed=chunks,outgoing_records_checked=len(outgoing),population_phase_checks=pop_checks,
        signed_total_checks=delivery_checks,direct_edge_phase_checks=direct_checks,timing_checks=timing_checks,
        isolated_units_checked=48,isolated_replays_checked=24,all_predicted_spike_ticks_counts_exact=True,
        independent_closed_form_errors_mV=errors,maximum_intact_drive_error_mV=max_drive_error,
        sources_reverified=True,full_brain_runs=0,production_controller_changed=False,
        acceptance_criteria_changed=False,wall_seconds=time.monotonic()-start,
        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if (OUT/'independent-audit.json').exists():raise FileExistsError('Do not overwrite audit')
    atomic_json(OUT/'independent-audit.json',receipt);print(json.dumps(receipt,indent=2),flush=True)


if __name__=='__main__':main()

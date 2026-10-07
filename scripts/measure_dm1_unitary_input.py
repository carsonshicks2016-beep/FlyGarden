"""Measure unitary EPSPs with original weights; no compensation is fitted."""
import json, resource, sys, time
from pathlib import Path
import brian2 as b
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.recording import atomic_json, space_check

BASE = ROOT/'reports/brain-integration/recovery'
OUT = BASE/'dm1-unitary-reference-v1'


def main():
    start = time.monotonic();OUT.mkdir(exist_ok=False);space_check(OUT,20*1024**2)
    p = json.loads((BASE/'adaptive-parameter-sweep-v1/protocol.json').read_text())
    pn = [p['mapping'][k][0] for k in ['DM1_lPN_left','DM1_lPN_right']]
    orn = [x for key in ['ORN_DM1_left','ORN_DM1_right'] for x in p['mapping'][key]]
    paths = [Path(__file__), ROOT/'flygarden/brain.py', BASE/'adaptive-parameter-sweep-v1/protocol.json',
             ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet',
             ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv', ROOT/'data/annotations.tsv',
             BASE/'local-source-qualification-v1/literature/tobin-2017.xml']
    protocol = {'version':1,'registered_before_execution':True,'scope':'Isolated unitary receptor-to-projection impulse responses under original identical PN electrical properties. No biological compensation, altered readout or new fitted parameter.',
                'source_populations': ['ORN_DM1_left','ORN_DM1_right'],'targets':pn,
                'stimulus':'One arrival per exact source-target connection at20ms; each connection modeled in its own independent PN replica for100ms. Native arrival delay has already elapsed at20ms.',
                'units':{'dt_s':.0001,'duration_s':.1,'weight_mV_per_signed_site':.275,'tau_membrane_s':.02,'tau_synapse_s':.005},
                'checks':{'no_other_drive':True,'subthreshold_closed_form_voltage_error_mV':1e-10},
                'question':'Does ipsilateral preference exist within each PN while a between-PN gain difference confounds raw lateral comparison?',
                'reference_limits':'DM6 morphology/physiology literature motivates the question but supplies no fitted electrical parameters for these exact DM1 roots. No global skeleton-length or synapse-count normalization is applied.',
                'full_brain_runs':0,'promote':False,'source_hashes':{str(path.relative_to(ROOT)):file_sha(path) for path in paths}}
    atomic_json(OUT/'protocol.json',protocol)
    graph = pd.read_parquet(ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet',
                            columns=['Presynaptic_Index','Postsynaptic_Index','Connectivity','Excitatory x Connectivity'],
                            filters=[('Presynaptic_Index','in',[x['index'] for x in orn]),('Postsynaptic_Index','in',[x['index'] for x in pn])])
    sites = graph.groupby(['Presynaptic_Index','Postsynaptic_Index'])['Excitatory x Connectivity'].sum().to_dict()
    pairs = [{**source, 'target_root_id':target['root_id'],'target_index':target['index'],'target_side':target['side'],
              'signed_sites':int(sites.get((source['index'],target['index']),0))} for source in orn for target in pn]
    assert all(x['signed_sites']>=0 for x in pairs)
    b.start_scope();b.prefs.codegen.target='cython';clock=b.Clock(dt=.1*b.ms)
    cells=b.NeuronGroup(len(pairs),'''dv/dt=(-52*mV-v+g)/(20*ms):volt (unless refractory)
        dg/dt=-g/(5*ms):volt (unless refractory)
        rfc:second''',threshold='v > -45*mV',reset='v=-52*mV;g=0*mV',refractory='rfc',method='linear',clock=clock)
    cells.v=-52*b.mV;cells.rfc=2.2*b.ms
    incoming=np.zeros((1000,len(pairs)));incoming[200]=[x['signed_sites']*.275 for x in pairs]
    drive=b.TimedArray(incoming*b.mV,dt=.1*b.ms)
    injection=cells.run_regularly('g += int(not_refractory)*drive(t,i)',when='synapses')
    states=b.StateMonitor(cells,['v','g'],record=True,when='end');spikes=b.SpikeMonitor(cells)
    net=b.Network(cells,injection,states,spikes);net.run(100*b.ms,namespace={'drive':drive})
    voltage=np.asarray(states.v/b.mV)+52;g=np.asarray(states.g/b.mV)
    times=np.asarray(states.t/b.second);tt=np.maximum(times-.020,0)
    closed=np.array([x['signed_sites']*.275 for x in pairs])[:,None]/3*(np.exp(-tt/.02)-np.exp(-tt/.005))
    subthreshold=np.asarray(spikes.count)==0;err=float(np.max(abs(voltage[subthreshold]-closed[subthreshold])))
    assert err<=1e-10 and np.isfinite(voltage).all()
    for j,item in enumerate(pairs):
        item.update(peak_depolarization_mV=float(voltage[j].max()),peak_time_s=float(times[voltage[j].argmax()]),spike_count=int(spikes.count[j]))
    groups=[]
    for target in pn:
        for side in ['left','right']:
            rows=[x for x in pairs if x['target_index']==target['index'] and x['side']==side]
            groups.append({'target_root_id':target['root_id'],'target_side':target['side'],'source_side':side,'ipsilateral':side==target['side'],
                           'source_neurons':len(rows),'total_signed_sites':sum(x['signed_sites'] for x in rows),
                           'mean_sites_per_ORN':float(np.mean([x['signed_sites'] for x in rows])),
                           'mean_peak_depolarization_mV':float(np.mean([x['peak_depolarization_mV'] for x in rows]))})
    np.savez_compressed(OUT/'responses.npz',time_s=times,depolarization_mV=voltage,g_mV=g)
    assert all(file_sha(ROOT/k)==v for k,v in protocol['source_hashes'].items())
    result={'status':'complete','pairs':pairs,'group_summary':groups,'subthreshold_replicas':int(subthreshold.sum()),'closed_form_max_error_mV':err,
            'full_brain_runs':0,'production_changes':0,'weights_altered':False,'wall_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    atomic_json(OUT/'results.json',result);print('Measured',len(pairs),'unitary responses; analytic error',err,flush=True)


if __name__=='__main__':main()

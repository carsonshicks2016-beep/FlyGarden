"""Descriptive paired tables; no fitting, pass gates or controller selection."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from flygarden.recording import atomic_json
from scripts.trace_sensory_steering import OUT, TYPES


def main():
    p=json.loads((OUT/'protocol.json').read_text());r=json.loads((OUT/'results.json').read_text())
    summaries={(x['trial'],x['phase']):x for x in r['summaries']}
    comparisons=[];phase_means=[];inputs=[]
    for model in p['models']:
        for phase in p['phase_ticks']:
            for cell in TYPES:
                if not p['populations'][cell+'_left'] or not p['populations'][cell+'_right']:continue
                cues={}
                for cue in p['cues']:
                    samples=[]
                    for seed in p['seeds']:
                        s=summaries[f'{model}-{cue}-{seed}',phase]['populations']
                        samples.append([s[cell+'_left']['mean_hz'],s[cell+'_right']['mean_hz']])
                    cues[cue]=dict(mean_left_hz=float(np.mean(samples,axis=0)[0]),
                                   mean_right_hz=float(np.mean(samples,axis=0)[1]),samples_left_right_hz=samples)
                phase_means.append(dict(model=model,phase=phase,cell_type=cell,cues=cues))
        for seed in p['seeds']:
            for pulse in [1,2]:
                for period in ['onset','late','pulse']:
                    phase=f'{period}_{pulse}'
                    for cell in TYPES:
                        if not p['populations'][cell+'_left'] or not p['populations'][cell+'_right']:continue
                        cues={}
                        for cue in p['cues']:
                            pops=summaries[f'{model}-{cue}-{seed}',phase]['populations']
                            pair=[pops[cell+'_left']['mean_hz'],pops[cell+'_right']['mean_hz']]
                            cues[cue]=dict(left_hz=pair[0],right_hz=pair[1],left_minus_right_hz=pair[0]-pair[1])
                        comparisons.append(dict(model=model,seed=seed,pulse=pulse,period=period,cell_type=cell,
                            cues=cues,binary_cue_separation_hz=cues['a_left']['left_minus_right_hz']-cues['a_right']['left_minus_right_hz'],
                            gradient_separation_hz=cues['g60']['left_minus_right_hz']-cues['g40']['left_minus_right_hz'],
                            gradient_relative_equal_hz=[cues[k]['left_minus_right_hz']-cues['equal']['left_minus_right_hz'] for k in ['g60','g40']]))
        for cue in p['cues']:
            for target in r['target_info']:
                samples=[next(x for x in summaries[f'{model}-{cue}-{seed}',f'pulse_{pulse}']['inputs'] if x['index']==target['index'])
                         for seed in p['seeds'] for pulse in [1,2]]
                def mean(values):return float(np.mean(values))
                grouped={}
                for cls in sorted(set(k for s in samples for k in s['by_class'])):
                    grouped[cls]={key:mean([s['by_class'].get(cls,{}).get(key,0.) for s in samples])
                                  for key in ['positive_mV_per_s','negative_mV_per_s','net_mV_per_s']}
                by_type={}
                for cls in sorted(set(k for s in samples for k in s['by_route_type'])):
                    by_type[cls]={key:mean([s['by_route_type'].get(cls,{}).get(key,0.) for s in samples])
                                  for key in ['positive_mV_per_s','negative_mV_per_s','net_mV_per_s']}
                inputs.append(dict(model=model,cue=cue,target=target,
                                   rate_hz=mean([s['rate_hz'] for s in samples]),
                                   accepted={key:mean([s['accepted'][key] for s in samples]) for key in samples[0]['accepted']},
                                   pregate={key:mean([s['pregate'][key] for s in samples]) for key in samples[0]['pregate']},
                                   sampled_g_range_mV=[min(s['state']['g_min_mV'] for s in samples),max(s['state']['g_max_mV'] for s in samples)],
                                   sampled_v_range_mV=[min(s['state']['v_min_mV'] for s in samples),max(s['state']['v_max_mV'] for s in samples)] if samples[0]['state']['independently_observed'] else None,
                                   independent_state_observation=samples[0]['state']['independently_observed'],
                                   by_class=grouped,by_route_type=by_type))
    atomic_json(OUT/'paired-summary.json',dict(scope='Descriptive means and all paired samples from the fixed diagnostic archive. No fitted correction, significance test, qualification, or causal attribution.',
               comparisons=comparisons,phase_means=phase_means,pulse_input_means=inputs))
    print('Saved descriptive comparisons:',len(comparisons),flush=True)


if __name__=='__main__':main()

"""Fixed-route scientific figures from an audited archive; no fitting."""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.trace_sensory_steering import OUT

CUES=['none','a_left','a_right','equal','g60','g40']
LABELS=['None','Left','Right','50/50','60/40','40/60']
COLORS=['#888888','#bd5131','#386eaa','#535353','#ba8122','#29888d']


def main():
    p=json.loads((OUT/'protocol.json').read_text());r=json.loads((OUT/'results.json').read_text())
    assert json.loads((OUT/'independent-audit.json').read_text())['status']=='passed'
    keys=r['population_keys'];model='local_adaptive';seed=p['seeds'][0]
    cells=['ORN_DM1','DM1_lPN','APL','MBON32','LAL170','DNa03','LAL018','DNa02']
    fig,axes=plt.subplots(4,2,figsize=(13,12),sharex=True)
    for ax,cell in zip(axes.flat,cells):
        for cue,color,label in zip(CUES[1:],COLORS[1:],LABELS[1:]):
            profile=OUT/r['profiles'][f'{model}-{cue}-{seed}']['file']
            with np.load(profile) as z:
                diff=z['population_hz'][:,keys.index(cell+'_left')]-z['population_hz'][:,keys.index(cell+'_right')]
            ax.step(np.arange(60)*.1,diff.reshape(-1,4).mean(1),where='post',color=color,label=label,lw=1.2,alpha=.85)
        ax.set_title(cell+' left minus right');ax.set_ylabel('Hz / neuron')
        ax.axhline(0,color='#999999',lw=.7);ax.set_xlim(0,6);ax.grid(axis='y',alpha=.15)
        ax.spines[['top','right']].set_visible(False)
        for lo,hi in [(0.3,.8),(3.3,3.8)]:ax.axvspan(lo,hi,color='#d9ba5b',alpha=.16)
    axes[0,0].legend(frameon=False,ncol=3,fontsize=8)
    for ax in axes[-1]:ax.set_xlabel('Simulated time (s)')
    fig.suptitle(f'Fixed annotated route: local adaptation, seed {seed}',fontsize=15,y=.99)
    fig.text(.5,.012,'100 ms bins; yellow: odor. Raw signed rates; soma-side labels alone do not establish receptive-field side.\n'
             'One displayed seed is descriptive. No brain/controller changes, fitted readout, or behavioral qualification.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.045,1,.97]);fig.savefig(OUT/'route-timecourses.png',dpi=155);plt.close(fig)

    summaries={(x['trial'],x['phase']):x for x in r['summaries']}
    selected=['DM1_lPN','MBON32','DNa02']
    fig,axes=plt.subplots(3,2,figsize=(13,11))
    for row,cell in enumerate(selected):
        for col,side in enumerate(['left','right']):
            ax=axes[row,col];positive=[];negative=[]
            for cue in CUES:
                vals=[]
                for seed in p['seeds']:
                    for pulse in [1,2]:
                        s=summaries[f'{model}-{cue}-{seed}',f'pulse_{pulse}']
                        vals.append(next(x['accepted'] for x in s['inputs'] if x['cell_type']==cell and x['side']==side))
                positive.append([v['positive_mV_per_s'] for v in vals]);negative.append([v['negative_mV_per_s'] for v in vals])
            ax.bar(np.arange(len(CUES)),np.mean(positive,axis=1),color='#ba6b32',alpha=.6,label='Excitatory increments')
            ax.bar(np.arange(len(CUES)),-np.mean(negative,axis=1),color='#477ea5',alpha=.6,label='Inhibitory increments')
            for i in range(len(CUES)):
                ax.scatter(i+np.linspace(-.14,.14,4),positive[i],color='#9c4a17',s=13,zorder=4)
                ax.scatter(i+np.linspace(-.14,.14,4),-np.array(negative[i]),color='#245780',s=13,zorder=4)
            ax.axhline(0,color='#333333',lw=.8);ax.set_xticks(range(len(CUES)),LABELS,rotation=15)
            ax.set_title(cell+' '+side);ax.set_ylabel('Accepted increments (mV/s)')
            ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
    axes[0,0].legend(frameon=False,fontsize=8)
    fig.suptitle('Recorded signed delivery into smell, relay and steering neurons',fontsize=15,y=.99)
    fig.text(.5,.012,'Bars: descriptive mean over two seeds and two pulses; dots: all four values.\n'
             'Voltage-equivalent model increments, not measured currents. Recorded resets/refractory gates included. Attribution is not causality.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.045,1,.97]);fig.savefig(OUT/'signed-route-inputs.png',dpi=155);plt.close(fig)


if __name__=='__main__':main()

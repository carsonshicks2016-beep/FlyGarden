"""Post-analysis presentation only: enlarge two recorded spike-time clusters.

No criterion, analysis result, neural source or protocol is changed. Clusters
are selected for legibility after inspection, not as a new statistical test.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/brain-integration/recovery/recovered-route-state-audit-v1'


def main():
    r=json.loads((OUT/'results.json').read_text());events=[]
    for name in ['none-12401','right-12401']:
        trial=next(x for x in r['trials'] if x['archive']=='direct' and x['name']==name)
        with np.load(OUT/trial['profile_file']) as z:
            mask=(z['spike_i']==92992)&(z['spike_ticks']>=33000)&(z['spike_ticks']<38000)
            events.append(z['spike_ticks'][mask]*.0001)
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),sharey=True)
    for ax,bounds in zip(axes,[(3.642,3.653),(3.776,3.789)]):
        for j,(ticks,color) in enumerate(zip(events,['#457b9d','#e76f51'])):
            ax.eventplot(ticks,lineoffsets=j,linelengths=.6,colors=color,linewidths=2)
            for t in ticks[(ticks>=bounds[0])&(ticks<=bounds[1])]:
                ax.text(t,j+.34,f'{t:.4f} s',ha='center',fontsize=9,color=color)
        ax.set_xlim(*bounds);ax.set_ylim(-.5,1.6)
        ax.set_yticks([0,1],['Support only','Right MBON32 drive']);ax.set_xlabel('Simulated time (s)')
        ax.ticklabel_format(axis='x',style='plain',useOffset=False)
    fig.suptitle('DNa02-left: equal pulse counts, different exact timestamps',fontsize=13)
    fig.text(.5,.01,'Seed 12401, second pulse: two events in each recording. Enlarged clusters are presentation only; no spike identity is inferred.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.06,1,.92]);fig.savefig(OUT/'timing-detail.png',dpi=170);fig.savefig(OUT/'timing-detail.svg');plt.close(fig)


if __name__=='__main__':main()

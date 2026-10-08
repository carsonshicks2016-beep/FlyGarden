"""Plot completed fixed-context results without recomputing a brain."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/brain-integration/recovery/sensory-context-capability-v1'


def main():
    p=json.loads((OUT/'protocol.json').read_text());r=json.loads((OUT/'results.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(14,4.8));colors=['#457b9d','#e76f51']
    for k,context in enumerate(p['contexts']):
        metrics=r['contexts'][context];ax=axes[k]
        for side,color in enumerate(colors):
            values=[]
            for case in p['cases']:
                pulse=[]
                for seed in p['diagnostic_seeds']:
                    folder=OUT/'trials'/f'{context}-{case}-{seed}';rows=json.loads((folder/'rows.json').read_text())
                    key=['DNa02_left','DNa02_right'][side]
                    for lo,hi in p['pulse_windows']:pulse.append(np.mean([row['population_hz'][key] for row in rows[lo:hi]]))
                values.append(pulse)
            ax.plot(range(4),[np.mean(v) for v in values],'-o',color=color,label=['DNa02 left','DNa02 right'][side])
            for x,v in enumerate(values):ax.scatter(np.full(len(v),x)+(side-.5)*.08,v,color=color,s=18,alpha=.5)
        ax.set_xticks(range(4),['None','Left','Right','Both']);ax.set_ylabel('Pulse firing rate (Hz)')
        passed=sum(row['passed'] for row in metrics['direction'])
        ax.set_title(('No odor' if context=='no_odor' else 'Equal DM1 odor')+f' — direction {passed}/4');ax.legend(fontsize=8)
    ax=axes[2]
    for k,context in enumerate(p['contexts']):
        values=[[v['active_two_hop_intermediates'] for x in r['engagement'] if x['context']==context and x['case']==case for v in x['pulses']] for case in p['cases']]
        ax.plot(range(4),[np.mean(v) for v in values],'-o',color=colors[k],label=['No odor','Equal odor'][k])
    ax.set_xticks(range(4),['None','Left','Right','Both']);ax.set_ylabel('Active two-hop anatomical intermediates, of156');ax.set_title('Recruitment is descriptive');ax.legend(fontsize=8)
    fig.suptitle('Fixed sensory-context capability — full network; matched inputs; unchanged gates',fontsize=13)
    fig.text(.5,.012,'Two seeds × two pulses; pulses are repeated measures. Neural diagnostic only: no body, learning or controller promotion.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.05,1,.92]);fig.savefig(OUT/'context-capability.png',dpi=170);fig.savefig(OUT/'context-capability.svg');plt.close(fig)


if __name__=='__main__':main()

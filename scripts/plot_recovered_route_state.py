"""Scientific overview of the completed saved-run diagnostic; no simulation."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/brain-integration/recovery/recovered-route-state-audit-v1'


def main():
    r=json.loads((OUT/'results.json').read_text());p=json.loads((OUT/'protocol.json').read_text())
    trials={(x['archive'],x['name']):x for x in r['trials']}
    direct=[x for x in r['trials'] if x['archive']=='direct']
    fig,axes=plt.subplots(2,2,figsize=(13,8.5));colors=['#457b9d','#e76f51']
    ax=axes[0,0]
    for j,color in enumerate(colors):
        values=[]
        for cue in ['none','left','right','both']:
            values.append([phase['DNa02_delivery'][j]['spikes']/.5
                for t in direct if t['case']==cue for phase in t['phases'] if phase['phase'] in ['pulse_1','pulse_2']])
        ax.plot(range(4),[np.mean(x) for x in values],'-o',color=color,label=['DNa02 left','DNa02 right'][j])
        for k,y in enumerate(values):ax.scatter(np.full(len(y),k)+(j-.5)*.05,y,s=16,color=color,alpha=.5)
    ax.set_xticks(range(4),['None','Left MBON','Right MBON','Both']);ax.set_ylabel('Pulse rate (Hz)');ax.set_title('Unequal descending response');ax.legend()
    ax=axes[0,1]
    for j,color in enumerate(colors):
        x=[];y=[]
        for t in direct:
            for phase in t['phases']:
                if phase['phase'] not in ['pulse_1','pulse_2']:continue
                for edge in phase['DNa02_delivery'][j]['direct_edges']:
                    x.append(abs(edge['before_mV_per_s']));y.append(abs(edge['accepted_mV_per_s']))
        ax.scatter(x,y,label=['Into DNa02 left (10 sites)','Into DNa02 right (40 sites)'][j],color=color,s=36)
    ax.plot([0,700],[0,700],':',color='#999999');ax.set_xlabel('Direct inhibitory arrivals (mV/s)');ax.set_ylabel('Accepted inhibitory delivery (mV/s)');ax.set_title('Actual signals vs refractory rejection');ax.legend(fontsize=8)
    ax=axes[1,0];labels=['Adaptation domain','MBON32','DNa03','LAL170','PFL3']
    for k,(archive,model,cue) in enumerate([('direct','local_adaptive','both'),('odor','original','a_both'),('odor','local_adaptive','a_both')]):
        vals=[]
        for label in labels:
            key=label if label=='Adaptation domain' else label+'_all';key='adaptation_domain' if label=='Adaptation domain' else key
            vals.append(np.mean([phase['populations'][key]['mean_hz'] for t in r['trials'] if (t['archive'],t['model'],t['case'])==(archive,model,cue)
                for phase in t['phases'] if phase['phase'] in ['pulse_1','pulse_2']]))
        ax.bar(np.arange(len(labels))+(k-1)*.24,vals,width=.24,label=['Direct, no odor','Odor, original','Odor, local adaptive'][k])
    ax.set_xticks(range(len(labels)),labels,rotation=18,ha='right');ax.set_ylabel('Per-neuron mean pulse rate (Hz)');ax.set_title('Operating contexts (different seeds/policies)');ax.legend(fontsize=8)
    ax=axes[1,1];seed=p['trials'][0]['seed'];name='right-'+str(seed);none=trials['direct','none-'+str(seed)];right=trials['direct',name]
    for y,t in enumerate([none,right]):
        with np.load(OUT/t['profile_file']) as z:
            mask=(z['spike_i']==92992)&(z['spike_ticks']>=3000)&(z['spike_ticks']<8000)
            ax.eventplot(z['spike_ticks'][mask]*.0001,lineoffsets=y,colors=colors[y])
    ax.set_yticks([0,1],['Support only','Right MBON']);ax.set_xlim(.3,.8);ax.set_xlabel('Simulated time (s)');ax.set_title('Same pulse count can hide changed timing')
    fig.suptitle('Recovered MBON route/state audit — saved data; no controller qualification',fontsize=14)
    fig.text(.5,.008,'Each dot is one seed × pulse, not an independent fly. Inhibitory delivery is model voltage-equivalent input, not a biological current.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.03,1,.95]);fig.savefig(OUT/'route-state-audit.png',dpi=170);fig.savefig(OUT/'route-state-audit.svg');plt.close(fig)


if __name__=='__main__':main()

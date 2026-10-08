"""Render completed diagnostic summaries; never executes neural dynamics."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/brain-integration/recovery/receiver-counterfactual-v1'


def main():
    r = json.loads((OUT/'results.json').read_text())
    assert r['status'] == 'complete'
    figure, axes = plt.subplots(2, 2, figsize=(12, 8), sharex='col')
    colors = {'intact': '#555a61', 'pn_dm1_only': '#166bb3', 'dna_without_aotu019': '#bd5517'}
    labels = {'intact': 'Intact recorded input', 'pn_dm1_only': 'DM1 receptor input only',
              'dna_without_aotu019': 'Paired AOTU019 input removed'}
    for row, readout in enumerate(['PN', 'DNa02']):
        altered = 'pn_dm1_only' if readout == 'PN' else 'dna_without_aotu019'
        for col, family in enumerate(['contrast', 'gradient']):
            ax = axes[row, col]
            fields = ['right', 'none', 'left'] if family == 'contrast' else ['g40', 'equal', 'g60']
            for condition in ['intact', altered]:
                rows = [x for x in r[family] if x['parent_model'] == 'local_adaptive' and
                        x['condition'] == condition and x['readout'] == readout]
                values = np.asarray([[x[key] for key in fields] for x in rows])
                for points in values: ax.plot(range(3), points, color=colors[condition], alpha=.24, linewidth=1)
                ax.plot(range(3), values.mean(0), 'o-', color=colors[condition], linewidth=2.2,
                        label=labels[condition]+f" ({sum(x['criterion_satisfied'] for x in rows)}/4 satisfy bound)")
            ax.axhline(0, color='#a0a0a0', linewidth=.7, linestyle='--')
            ax.set_xticks(range(3), ['Right cue', 'No odor', 'Left cue'] if family == 'contrast' else
                          ['40/60 input', '50/50 input', '60/40 input'])
            ax.set_title(f'{readout}: '+('unilateral cues' if family == 'contrast' else 'unequal-intensity cues'), loc='left')
            ax.set_ylabel('Left minus right firing rate (Hz)')
            ax.spines[['top', 'right']].set_visible(False)
            ax.grid(axis='y', alpha=.15)
            ax.legend(fontsize=8, frameon=False, loc='best')
    figure.suptitle('Fixed-source tests leave reliable steering unresolved', x=.06, ha='left', fontsize=17)
    figure.text(.06, .925, 'Recovered local-adaptive parents; bold = mean, faint = each seed/pulse comparison', fontsize=10)
    figure.text(.06, .03, 'Two reused seeds × two pulses. Source neurons cannot respond to the intervention.\n'
                'These are four-unit receiver diagnostics, not full-network repairs or learning evaluations.', fontsize=10)
    figure.tight_layout(rect=[.025, .08, .99, .90])
    figure.savefig(OUT/'receiver-comparison.png', dpi=170)
    figure.savefig(OUT/'receiver-comparison.svg')
    plt.close(figure)


if __name__ == '__main__': main()

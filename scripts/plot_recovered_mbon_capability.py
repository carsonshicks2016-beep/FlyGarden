"""Plot completed downstream capability traces without any simulation."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/brain-integration/recovery/recovered-mbon32-capability-v1'


def main():
    p = json.loads((OUT/'protocol.json').read_text()); r = json.loads((OUT/'results.json').read_text())
    assert r['status'] == 'complete'
    figure, axes = plt.subplots(2, 2, figsize=(12, 8))
    colors = {'none': '#666666', 'left': '#166bb3', 'right': '#bd5517', 'both': '#27844a'}
    times = (np.arange(240)+.5)*.025
    for col, seed in enumerate(p['diagnostic_seeds']):
        for case in p['cases']:
            rows = json.loads((OUT/'trials'/f'{case}-{seed}'/'rows.json').read_text())
            activity = np.asarray([[x['population_hz'][k] for k in ['DNa02_left', 'DNa02_right', 'MBON32_left', 'MBON32_right']] for x in rows])
            # Four-window averages for visibility. Evaluation uses raw 25ms bins.
            dna = (activity[:, 0]-activity[:, 1]).reshape(60, 4).mean(1)
            mbon = activity[:, 2:4].mean(1).reshape(60, 4).mean(1)
            axes[0, col].plot(times.reshape(60, 4).mean(1), dna, color=colors[case], label=case, linewidth=1.5)
            axes[1, col].plot(times.reshape(60, 4).mean(1), mbon, color=colors[case], label=case, linewidth=1.5)
        for ax in axes[:, col]:
            for lo, hi in p['pulse_windows']: ax.axvspan(lo*.025, hi*.025, color='#9cb4cb', alpha=.16)
            for lo, hi in p['recovery_windows']: ax.axvspan(lo*.025, hi*.025, color='#b5c7ad', alpha=.16)
            ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='y', alpha=.15)
            ax.set_xlabel('Simulated time (s)'); ax.legend(frameon=False, ncol=4, fontsize=8)
        axes[0, col].set_title(f'Diagnostic seed {seed}', loc='left')
        axes[0, col].set_ylabel('DNa02 left minus right (Hz)')
        axes[1, col].set_ylabel('Mean MBON32 firing rate (Hz)')
    figure.suptitle('Intact-network direct-MBON32 capability test', x=.06, ha='left', fontsize=16)
    figure.text(.06, .925, 'Fixed local adaptation; 50 Hz direct drive; blue bands = stimulation; green bands = recovery', fontsize=10)
    figure.text(.06, .03, '100 ms display averages; all checks use raw recorded events. Two fresh seeds, two repeated pulses.\n'
                'Direct stimulation is an engineered diagnostic, not odor processing, navigation or learning.', fontsize=10)
    figure.tight_layout(rect=[.02, .08, .99, .9]); figure.savefig(OUT/'capability-traces.png', dpi=170)
    figure.savefig(OUT/'capability-traces.svg'); plt.close(figure)


if __name__ == '__main__': main()

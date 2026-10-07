"""Plot the completed local-only adaptation screen without running a brain."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/brain-integration/recovery/local-adaptation-closed-loop-v1'


def main():
    protocol = json.loads((OUT / 'protocol.json').read_text())
    seed = 12201
    local_indices = [x['index'] for x in protocol['selected_local_targets']]
    fig, axes = plt.subplots(3, 2, figsize=(12, 8.5), sharex=True, sharey='row')
    for col, model in enumerate(['original', 'local_adaptive']):
        series = {}
        for cue in ['none', 'a_left']:
            folder = OUT / 'trials' / f'{model}-{cue}-{seed}'
            manifest = json.loads((folder / 'manifest.json').read_text())
            assert manifest['status'] == 'complete' and len(manifest['chunks']) == 240
            rows = json.loads((folder / 'rows.json').read_text())
            rates = lambda key: np.array([x['population_hz'][key] for x in rows])
            pn = (rates('DM1_lPN_left') + rates('DM1_lPN_right')) / 2
            local = []
            for chunk in manifest['chunks']:
                with np.load(folder / chunk['file']) as data:
                    local.append(data['counts'][local_indices].mean() / .025)
            series[cue] = [pn, np.array(local), rates('DNa02_left') - rates('DNa02_right')]
        for row in range(3):
            ax = axes[row, col]
            for cue, color, label, style in [('a_left', '#bd4a2c', 'Left odor', '-'),
                                               ('none', '#3d6b86', 'Matched no odor', '--')]:
                binned = series[cue][row].reshape(-1, 4).mean(axis=1)
                ax.step(np.arange(60) * .1, binned, where='post', color=color,
                        linestyle=style, linewidth=1.6, label=label)
            for lo, hi in protocol['pulse_windows']:
                ax.axvspan(lo * .025, hi * .025, color='#ebb82d', alpha=.22)
            for lo, hi in protocol['recovery_windows']:
                ax.axvspan(lo * .025, hi * .025, color='#677876', alpha=.12)
            ax.axhline(0, color='#999999', linewidth=.5)
            ax.grid(axis='y', alpha=.17)
            ax.set_xlim(0, 6)
            ax.spines[['top', 'right']].set_visible(False)
    axes[0, 0].set_title('Original model: activity persists', fontsize=12)
    axes[0, 1].set_title('Local-only adaptation: recovery and renewed response', fontsize=12)
    for row, label in enumerate(['Two DM1 PNs\nmean firing rate (Hz)',
                                 'Four monitored local cells\nmean firing rate (Hz)',
                                 'DNa02 left minus right\nfiring rate (Hz)']):
        axes[row, 0].set_ylabel(label)
    for ax in axes[-1]:
        ax.set_xlabel('Simulated time (seconds)')
    axes[0, 0].legend(loc='center right', frameon=False, fontsize=9)
    fig.suptitle('Full-network mechanism screen: two repeated left-odor pulses', fontsize=15, y=.985)
    fig.text(.5, .024, '100 ms bins; seed 12201 shown. Yellow: odor; gray: registered recovery windows.\n'
             'Adaptation in 395 local cells only. Directional choice, navigation and learning are untested.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .064, 1, .955])
    fig.savefig(OUT / 'recovery-comparison.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()

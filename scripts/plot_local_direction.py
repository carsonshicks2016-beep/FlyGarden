"""Figures from completed neural-screen results; no simulations or fitting."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/brain-integration/recovery/local-adaptation-direction-v1'
COLORS = ['#bb5131', '#777777', '#386eaa', '#a180ad', '#8d8851', '#a94920', '#207e91']


def main():
    p = json.loads((OUT / 'protocol.json').read_text())
    r = json.loads((OUT / 'results.json').read_text())
    cues = ['a_left', 'none', 'a_right', 'a_both', 'equal', 'g60', 'g40']
    labels = ['Left', 'None', 'Right', 'Both 100%', '50/50', '60/40', '40/60']
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharey='col')
    for row, model in enumerate(p['models']):
        for col, (left, right, name) in enumerate([('DM1_lPN_left', 'DM1_lPN_right', 'PN left minus right'),
                                                  ('DNa02_left', 'DNa02_right', 'DNa02 left minus right')]):
            values = []
            for cue in cues:
                samples = []
                for seed in p['validation_seeds']:
                    rows = json.loads((OUT / 'trials' / f'{model}-{cue}-{seed}' / 'rows.json').read_text())
                    diff = np.array([x['population_hz'][left] - x['population_hz'][right] for x in rows])
                    samples.extend(float(diff[lo:hi].mean()) for lo, hi in p['pulse_windows'])
                values.append(samples)
            ax = axes[row, col]
            ax.bar(np.arange(7), np.mean(values, axis=1), color=COLORS, alpha=.45, width=.7)
            for i, samples in enumerate(values):ax.scatter(i + np.linspace(-.17, .17, 4), samples, color=COLORS[i], s=23, zorder=4)
            ax.axhline(0, color='#333333', linewidth=.8)
            ax.axvline(3.5, color='#bbbbbb', linestyle=':', linewidth=1)
            ax.set_xticks(range(7), labels, rotation=20)
            ax.set_title(('Original' if model == 'original' else 'Local-only adaptation') + '\n' + name)
            ax.set_ylabel('Mean difference during pulse (Hz)')
            ax.grid(axis='y', alpha=.16);ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Frozen full-network candidate: direction and unequal-intensity responses', y=.99, fontsize=14)
    fig.text(.5, .016, 'Dots: both seeds and both pulses; bars: their descriptive mean. No fitted bias subtraction.\n'
             '50/50, 60/40 and 40/60 have equal total concentration; Both 100% is a separate higher-total condition.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .07, 1, .96]);fig.savefig(OUT / 'direction-and-gradient.png', dpi=170);plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True, sharey='col')
    timeline_cues = ['a_left', 'a_right', 'equal', 'g60', 'g40']
    colors = ['#bd5131', '#386eaa', '#777777', '#ba8122', '#29888d']
    for row, model in enumerate(p['models']):
        for cue, color in zip(timeline_cues, colors):
            rows = json.loads((OUT / 'trials' / f'{model}-{cue}-{p["validation_seeds"][0]}' / 'rows.json').read_text())
            pn = np.array([(x['population_hz']['DM1_lPN_left'] + x['population_hz']['DM1_lPN_right']) / 2 for x in rows])
            dna = np.array([x['population_hz']['DNa02_left'] - x['population_hz']['DNa02_right'] for x in rows])
            for col, values in enumerate([pn, dna]):
                axes[row, col].step(np.arange(60) * .1, values.reshape(-1, 4).mean(1), where='post',
                                    label=labels[cues.index(cue)], color=color, linewidth=1.3, alpha=.8)
        for col, label in enumerate(['Mean two-PN rate (Hz)', 'DNa02 left minus right (Hz)']):
            ax = axes[row, col]
            for lo, hi in p['pulse_windows']:ax.axvspan(lo * .025, hi * .025, color='#e3ba40', alpha=.15)
            for lo, hi in p['recovery_windows']:ax.axvspan(lo * .025, hi * .025, color='#78908b', alpha=.1)
            ax.set_ylabel(label);ax.set_xlim(0, 6);ax.grid(axis='y', alpha=.16)
            ax.set_title('Original' if model == 'original' else 'Local-only adaptation')
            ax.spines[['top', 'right']].set_visible(False)
            if row == 1:ax.set_xlabel('Simulated time (seconds)')
    axes[0, 0].legend(loc='center right', frameon=False, fontsize=8)
    fig.suptitle(f'Response and recovery across cues: seed {p["validation_seeds"][0]}', y=.99, fontsize=14)
    fig.text(.5, .02, '100 ms bins; yellow: odor; gray: registered recovery. Raw signed output, no bias correction.\n'
             'These neural diagnostics do not qualify navigation, learning or biological fidelity.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .07, 1, .96]);fig.savefig(OUT / 'cue-response-timeline.png', dpi=170);plt.close(fig)


if __name__ == '__main__':main()

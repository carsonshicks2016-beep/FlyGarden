# Reproduction and sharing boundaries

The repository contains source, tests, experiment specifications and selected evidence. It is not an independently validated one-command installation. Existing macOS launchers target Carson's local `/Users/carsonhicks/FlyGarden` environment. Several scripts also depend on local artifacts omitted from Git. Static source review is available immediately; running the complete experiment requires restoring its pinned inputs.

## Upstream inputs

See `reports/provenance.json` for exact revisions and SHA-256 checksums.

- Neural model: https://github.com/eonsystemspbc/fly-brain at `a3db62f9436074e485c0278290c2164ed6150808`, locally under `vendor/fly-brain`.
- Body: https://github.com/NeLy-EPFL/flygym at `38c8ec61034cd59bc5ba0de20688d4a3c0000d60`, locally under `vendor/flygym`.
- Annotations: https://github.com/flyconnectome/flywire_annotations at `a83b2776d60d5764cef36b927f5f9679c16c47a2`. Publication attribution is retained in `data/annotations-README.md`. Standalone redistribution terms were not confirmed, so the annotation table is omitted.

Restore the graph artifacts and annotation table at their original relative paths and verify the recorded checksums. The installed environment used Python 3.12; `requirements.lock` records dependencies, including a local FlyGym installation reference that must be adjusted to the restored checkout. The test suite contains data-dependent tests and operational checks; not every test can run on this lightweight snapshot.

## Frozen protocols

Experiment protocols hash source files and input artifacts. Running a historical protocol against changed files is deliberately rejected. Do not remove those checks merely to get a run to start. Historical receipts attest to a particular local evidence package; omitted raw artifacts prevent independent verification of the entire package from Git alone.

The 153-trial adaptation sweep is complete and failed full calibration. An eight-trial local-only recovery screen succeeded, followed by28 frozen validation trials: recovery passes across all tested odor conditions, while direction and gradient criteria fail. Behavioral and learning qualification remain incomplete. Read `docs/MUSE-REVIEW.md` for the latest evidence pointers. Progress files on GitHub are historical snapshots, not live telemetry.

The new reference and recovery scripts require omitted annotations, graph artifacts and earlier raw recordings. `scripts/audit_local_recovery_diagnostic.py` independently reconstructs the local-only screen metrics from raw spikes without importing the neural evaluator. `scripts/plot_local_recovery_diagnostic.py` creates the comparison plot without running a brain. Restore the pinned local evidence package to run either; summary JSON on GitHub alone cannot reproduce the raw-spike checks.

For the directional package, `scripts/audit_local_direction.py` reconstructs raw-spike rates and motor commands, checks checkpoint/interruption receipts, and verifies exact primary-metric parity against the earlier evaluator in a separate globals dictionary. `scripts/plot_local_direction.py` renders completed results without simulation. Both require the omitted local trial archives. The pre-execution source/protocol commit is `bc0cebc`; subsequent result summaries do not retroactively change it.

The sensory-to-steering analysis was frozen in commit `4035816` before execution. Its summaries cover all 28 existing trials and create no new full-network runs. `scripts/audit_sensory_steering.py` independently checks signed delivery by searching the last recipient spike at each delayed arrival, and validates derived population/individual rates. It requires the prior raw trial archive and the new local `profiles/*.npz`; both are excluded from GitHub. The public protocol, root mapping, phase/paired summaries, figures and source support review but cannot replace these raw arrays. `scripts/trace_sensory_steering.py analyze` refuses to overwrite completed results. Preserve historical protocol/result packages when performing a revised analysis.

The receiver comparison was frozen and published in commit `b6734af` before execution. `scripts/diagnose_receiver_counterfactual.py run` requires the same 28 omitted raw parent trials and frozen sources. All 28 intact spike/voltage reconstructions must pass before counterfactuals; any failed attempt is preserved and cannot be overwritten by the runner. `scripts/audit_receiver_counterfactual.py` independently accumulates exact graph events and analytically integrates all receiver conditions without Brian2 or the native helper. It requires the new local `inputs/*.npz` and `replays/*.npz`, also excluded from GitHub. Public summaries establish the reported diagnostic scope but cannot reproduce these checks without the raw arrays. All source activity remains fixed in the altered-input arms; no recurrent full-network repair is implied. `scripts/plot_receiver_counterfactual.py` rerenders completed summaries without simulating a brain.

## Licensing and attribution

Application code is GPL-2.0-or-later, as recorded in the existing LICENSE and README. Dependencies retain their own licenses; Three.js's notice is retained in `static/vendor`. The separate published-equation diagnostic has GPL-3.0-or-later terms described in the existing learning-rule audit. Upstream datasets, model code and morphology are not claimed as original work. Omitted vendor repositories should be obtained from their upstream sources with their notices intact.

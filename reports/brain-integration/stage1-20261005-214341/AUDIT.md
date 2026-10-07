# Fly Garden — Stage 1 reference audit

Stage 1 is complete for preservation, data/import integrity, short full-network equation replay, and native upstream CPU execution. It does not establish long-run stochastic equivalence, sensory control, navigation, or learning.

## Preserved baseline

Application sources, interface, scripts, configuration and provenance are copied into `baseline/`, with hashes in `inventory.json`. Original checkpoint, recording and export files remain in place. Their JSON metadata are inventoried; this is not a new full-state checkpoint or verification of every historical payload. The paused live application was not commanded or changed. `profiles.json` distinguishes the pinned upstream source, current embodied adapter, and diagnostic variants. No production parameter or dependency was changed.

Source revision: `a3db62f9436074e485c0278290c2164ed6150808`. Whole imported network: 138,639 neurons, 15,091,983 aggregated connection records and 54,492,922 anatomical synapses. No thresholding or reduction.

## Data and mapping checks

All pinned data hashes match. Vendor checkout is clean. Every connection index maps back to its exact presynaptic and postsynaptic root ID. Counts are positive and signed weights equal connectivity multiplied by the released sign. Neuron IDs and modeled annotation IDs are unique. All listed input/output population IDs, sides and transmitter fields match the pinned annotation table.

The annotation table covers 138,625 modeled neurons; 14 are missing. Import agreement does not resolve annotation confidence or validate transmitter predictions. Missing annotations block claims about those cells, not execution of the full network.

## Reference comparisons

Rest/reset voltage -52 mV; threshold -45 mV; membrane time 20 ms; synaptic time 5 ms; ordinary refractory period 2.2 ms; connection delay 1.8 ms; signed connection scale 0.275 mV; artificial input jump 68.75 mV. These match the pinned benchmark defaults and current implementation.

Ten comparisons (five stimuli × two seeds) used 100 ms stimulation followed by 100 ms recovery, frozen learning and the full network. Spike neuron IDs, spike times and counts matched exactly. Final voltage and synaptic state matched within 1e-10 mV. Shared realized Bernoulli input isolated equations and connectivity from RNG differences. Both quiet trials emitted zero spikes.

The original pinned CPU function also ran with its original equations, reset and per-neuron PoissonInput. Only explicit experiment settings were supplied (0.1 ms clock, seed 1101, 200 ms duration and stimulation rates). These native-input checks are independent realizations, not exact or statistical equivalence tests.

| Native reference stimulus | Input Hz | Total spikes | Active neurons |
| --- | ---: | ---: | ---: |
| ORN_DM1 | 100 | 87,932 | 8,166 |
| DNp09 | 65 | 85 | 30 |

## Alteration ledger

| Component | Difference from pinned reference | Interpretation |
| --- | --- | --- |
| Reset | Application omits `w = 0` | Earlier provenance called this undefined; in Brian2 2.10.1 it is an inert local temporary, not a demonstrated execution defect. Original and omitted-reset one-cell tests agree. |
| Input RNG | Application owns a checkpointable NumPy generator and replays Bernoulli events through SpikeGeneratorGroup/Synapses; reference uses PoissonInput | Both use a per-timestep Bernoulli distribution for one input, but RNG streams and input machinery differ. Exact replay does not establish native stochastic equivalence. |
| Refractory period | Application sets zero on every possible input neuron; reference selects stimulated neurons | Detectable downstream effect in odor cases; investigate before changing production. |
| Stimulation | Synthetic odor, looming, dopamine and walking channel encodings; values clipped to 0–100 Hz | Strong activation and zero refractory on selected neurons are upstream artificial-stimulation conventions, not automatically implementation bugs or natural physiology. Original paper helper defaults to 150 Hz; pinned benchmark defaults to 100 Hz. |
| Motor output | DNp09 left/right mean rate divided by 100 Hz, clipped and smoothed | Engineered decoder into supplied leg controller; not validated natural steering. |
| Walking drive | Constant 65 Hz descending stimulation in arena loop | Can dominate output; no natural sensory decision claim. |
| Vision | Egocentric geometric threat proxy stimulates LPLC2; retinal images inspection only | Actual retinal-to-brain and obstacle pathways remain unimplemented. |
| Olfaction | Two synthetic channels use averaged antenna measurements | Bilateral sensing is not preserved in brain input. |
| Threat response | Direct motor override at threat >0.25 | Engineered escape behavior can supersede neural output. |
| Body feedback | Contact/motion feed supplied gait controller | Ascending brain mapping remains unvalidated. |
| Learning | Selected KCg→MBON01/11 plasticity; rest of weights fixed | Engineered integration; existing learning evaluation failed. Frozen throughout this audit. |
| Persistence | Neural state retained between windows, portable input RNG checkpoints, bounded spike recording | Application extensions; not biological validation. |

## Measured refractory difference

Identical stimuli and equations, changing only which input neurons have zero refractory period:

| Stimulus | Seed | Neurons with differing counts | Application spikes | Selected-input refractory spikes |
| --- | ---: | ---: | ---: | ---: |
| odor_a | 1101 | 2,839 | 87,488 | 87,124 |
| combined | 1101 | 2,926 | 87,010 | 86,624 |
| odor_a | 1102 | 2,789 | 87,467 | 87,132 |
| combined | 1102 | 3,027 | 86,666 | 85,517 |

Other six comparisons matched counts. This isolates an adapter effect; it does not establish that refractory configuration explains the persistent bright brain or that the diagnostic convention should be promoted unchanged.

## Remaining boundaries and next step

These short tests do not establish timestep convergence, multi-second/long-run equivalence, natural physiological response, complete sensory processing, useful movement or learning. Long-run stimulus dose, recovery, internal excitation/inhibition and refractory diagnostics belong to Stage 2. Preserve the reference and calibrate only a separately versioned embodied profile if evidence warrants it.

Reproduce in a fresh evidence folder: `.venv-next/bin/python scripts/audit_brain_reference.py`. Workers run sequentially. Existing evidence folders are refused. Raw diagnostic events, source identities and logs are retained alongside this report. The audit respects the existing 2 GiB storage reserve and deletes no recordings or checkpoints.

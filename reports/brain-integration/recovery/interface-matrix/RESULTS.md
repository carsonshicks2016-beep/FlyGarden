# Full-brain interface diagnosis

All28 full-network trials and28 physical command replays completed. Neural raw-data audits verify root IDs,spike-count parity,input delivery,membrane timing,population rates,decoder reconstruction,and independent signed synaptic arrivals. Physical audits verify recorded commands acting in their next eligible25ms interval,finite observations,and30Hz poses. These are diagnostics,not held-out behavioral acceptance.

Quiet inputs produce no spikes or drive. Explicit DNp09 state support produces forward commands and also recruits asymmetric steering activity. Direct left/right DNa02 stimulation produces opposite command biases. Both unilateral odor cues recruit predominantly left DNa02; sensory stimulation reaches the circuit,but the readout does not establish mirrored odor choice. Looming recruits LPLC2 and DNp01 while the selected walking outputs remain weak or inactive. Translation also activates this visual encoding,so specificity remains limited. Synthetic touch reaches its target neurons without MDN retreat output.

Nominal positive/negative synaptic increments are not physical membrane currents. Their reconstruction includes delayed presynaptic events across chunk boundaries. The body replay consumes saved commands; its movement does not feed back into these neural recordings. Touch pulses are not live contact validation. All original connections remain in the modeled network; no lesion,hidden navigator,escape override or learning is introduced in this protocol.

| Cue | Seed | External events | Physical departure mm | Heading change rad | Flipped samples |
|---|---|---|---|---|---|
| quiet | 9301 | 0 | 0.0760 | -0.0009 | 0 |
| quiet | 9302 | 0 | 0.0634 | 0.0063 | 0 |
| support | 9301 | 150 | 6.0845 | -0.0853 | 0 |
| support | 9302 | 130 | 4.8963 | -0.1482 | 0 |
| direct_left | 9301 | 177 | 6.1142 | 0.5664 | 0 |
| direct_left | 9302 | 153 | 4.9639 | 0.3902 | 0 |
| direct_right | 9301 | 172 | 5.9596 | -0.5116 | 0 |
| direct_right | 9302 | 161 | 4.8036 | -0.8431 | 0 |
| odor_left | 9301 | 883 | 0.8476 | 0.2336 | 0 |
| odor_left | 9302 | 867 | 0.7262 | 0.2215 | 0 |
| odor_right | 9301 | 853 | 0.9004 | 0.2706 | 0 |
| odor_right | 9302 | 849 | 0.7024 | 0.1969 | 0 |
| supported_odor_left | 9301 | 1033 | 5.7891 | 0.9903 | 0 |
| supported_odor_left | 9302 | 997 | 4.6409 | 1.1958 | 0 |
| supported_odor_right | 9301 | 1003 | 5.8230 | 1.0284 | 0 |
| supported_odor_right | 9302 | 979 | 4.5569 | 1.2612 | 0 |
| loom_left | 9301 | 156 | 0.0760 | -0.0009 | 0 |
| loom_left | 9302 | 160 | 0.0634 | 0.0063 | 0 |
| loom_right | 9301 | 134 | 0.0760 | -0.0009 | 0 |
| loom_right | 9302 | 126 | 0.0634 | 0.0063 | 0 |
| supported_loom_left | 9301 | 306 | 6.0845 | -0.0853 | 0 |
| supported_loom_left | 9302 | 290 | 4.9283 | -0.1622 | 0 |
| supported_loom_right | 9301 | 284 | 6.0845 | -0.0853 | 0 |
| supported_loom_right | 9302 | 256 | 4.8963 | -0.1482 | 0 |
| translation | 9301 | 338 | 0.0819 | -0.0010 | 0 |
| translation | 9302 | 397 | 0.0705 | 0.0060 | 0 |
| touch | 9301 | 50 | 0.0760 | -0.0009 | 0 |
| touch | 9302 | 53 | 0.0634 | 0.0063 | 0 |

Next: choose a separately versioned,biologically justified candidate after reviewing these results and the archived Step4 inhibitory diagnosis. Keep calibration and evaluation seeds separate. Do not promote this matrix as autonomous navigation or treat support-only motion as sensory-guided success. See ARCHITECTURE_EVIDENCE.md in the parent recovery folder for primary motor-population references.

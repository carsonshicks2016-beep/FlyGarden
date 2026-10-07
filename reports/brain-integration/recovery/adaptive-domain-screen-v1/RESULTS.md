# Fixed-point adaptive-LIF domain screen

Initial calibration: 5 controller arms, one calibration seed, 150 ms decay and 1.5 mV spike increment. This is one preregistered parameter point, not a completed parameter sweep.

| Arm | Response/recovery checks | Bilateral contrast | Burst checks | Support | Eligible |
|---|---:|---:|---:|---:|---|
| original | 0/6 | 0/2 | 0/6 | 1/1 | False |
| projection | 0/6 | 0/2 | 0/6 | 1/1 | False |
| sensory_projection | 0/6 | 0/2 | 0/6 | 1/1 | False |
| olfactory_hypothesis | 0/6 | 0/2 | 0/6 | 1/1 | False |
| global | 0/6 | 0/2 | 0/6 | 1/1 | False |

Selected calibration domain: none. Held-out evaluation run: False.

The live controller is unchanged. Local inhibition was not combined with adaptation. Uncertain local-neuron and global domains are engineering comparisons; anatomical labels do not establish their firing physiology. Passing calibration alone does not demonstrate learning, embodied navigation, or biological fidelity.

Integrity audit: 21 trials, 5040 complete chunks. Zero-adaptation regression matched baseline events and whole voltage/conductance state exactly.

Total recorded trial runtime: 1066.4 seconds. Peak measured worker memory: 2.592 GiB. This excludes parent process and operating-system overhead.

All arms retained a measurable response to both pulses, but none recovered or preserved the required bilateral contrast. Adaptation reduced persistent PN activity; even the lowest recorded individual PN recovery difference was 168 Hz, versus the 5 Hz limit. Reduced firing is not a successful recovery.

No domain passed all gates at this point. Held-out gradient evaluation was therefore not launched. The next decision is whether to preregister a wider adaptation search or investigate another mechanism; no candidate is ready for promotion.

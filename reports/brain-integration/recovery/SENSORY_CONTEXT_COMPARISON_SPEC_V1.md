# Fixed sensory-context capability comparison design, version1

Design frozen2026-10-07 after the registered saved-run audit. This is a **design specification**, not an execution-ready source preregistration or completed experiment. Publish an executable protocol with pinned sources and data before launching it. The audit's original sources and earlier trial packages must not be edited.

**Question:** With the same local-adaptation candidate and identical direct MBON32 inputs, does one fixed symmetric odor context recruit a rate-sensitive opposed DNa02 response that was absent in the odor-free operating state?

## Arms, clock and inputs

- Full138,639-unit graph; unchanged signs, synapse counts, weights,2.2ms default refractory, point equations and395-cell local adaptation (450ms/13.5mV). No body or learning.
- Exactly16 trials: two contexts (`no_odor`, `DM1_equal_50_50`) × four direct cases (`none`, `left`, `right`, `both`) × two fresh diagnostic seeds (`12501`, `12502`). Seed fields in65 existing protocol files were checked; neither seed was reserved there. Recheck source/job manifests at executable registration.
- Six simulated seconds;0.1ms neural clock,25ms recording bins. MBON pulses remain[0.3,0.8) and[3.3,3.8) seconds. Recovery remains[2.5,3.0) and[5.5,6.0). Preserve existing late100ms burst windows.
- Direct stimulation remains50Hz per selected MBON root with68.75mV external voltage jumps. Both MBON targets are zero refractory in every arm, including direct `none`. All ordinary candidate inputs retain their existing zero-refractory convention.
- During those two pulse windows only, the single odor context sets both local DM1 concentrations to0.5 using the unchanged maximum50Hz engineered receptor encoding (nominal25Hz per receptor). DM2 and vision remain zero. No-context odor is zero throughout. This context must remain labeled an engineered encoding.
- Bilateral DNp09 support remains65Hz throughout. Each seed uses matched generator draws across cases/contexts; preserve the current support/input stream and separate direct seed+100000 stream. Verify identical requested/delivered direct events and support events. Additional odor events must not advance or perturb the paired support/direct random streams.
- Ordinary trials reset physical/transient neural state and have no learned parameter updates. All arms share the same immutable initial weights. The candidate is diagnostic; no live controller changes.

## Measures and gates

Evaluate each context against **its own same-seed direct-none control**, using the original direct-capability evaluator and unchanged bounds:

- Each directional side delta at least5Hz with the required signs; descending left/right separation at least10Hz; bilateral signed delta within5Hz.
- Direct target response/renewed response gain at least10Hz; individual monitored-cell recovery differences within5Hz; signed DNa02 recovery difference within5Hz.
- Late100ms excess firing bound20Hz and matched support retention at least0.8. State precision1e-10mV.

Before execution, verify these clauses exactly match `recovered-mbon32-capability-v1/protocol.json` and its original evaluator, including half-open windows and signed inequalities. Maintain both per-context outcomes; do not pool seeds/pulses to hide an arm's failure. No new qualification gate is invented from relay recruitment or fine timing. These two diagnostic seeds are not population-level learning evidence.

Record all neuron events/counts plus exact DNa02,MBON32,AOTU019 and previously selected state endpoints; capture adaptation-domain spike counts and candidate relay activity. Report requested input, target response and descending response separately. Validate hashes, event clocks, monitor parity, fixed weights and saved/loading continuation. Check one interrupted-prefix reconstruction. Freeze an independent raw-event evaluator and retain failed/incomplete trials.

## Discrimination and stop rules

Prediction to inspect, not a replacement acceptance rule: odor may raise DNa02-left firing and make the weak right inhibitory input affect rates, while suppressing right DNa02 enough to create a left-input rate floor. Recruitment without opposed direction is a failed architecture result. Fine timing differences without rate change preserve the existing failure.

If exact pairing, delivery, continuation or evaluation fails, stop interpretation and diagnose the implementation. If neither context passes the original direction bounds, do not expand the adaptation/direct-input grid. Document the failure and move to an explicitly scoped engineered-readout proposal. If the context passes, keep it a diagnostic result and proceed to held-out sensory-to-motor and embodied sign/gradient tests before promotion. This design cannot isolate adaptation's causal role because adaptation remains enabled in both contexts.

## Resources and provenance

Use one simulation worker initially. Check fresh memory/swap/available disk before execution; preserve the2GiB disk reserve. Do not run video export concurrently. Benchmark the first engaged-context trial to update ETA, since recruited network activity can cost more than an odor-free trial. Keep every raw recording/checkpoint; publish only bounded source,protocol,summary and audit evidence to GitHub.

No run is launched by this document. The future executable protocol must pin this design, all model/source/data versions, neuron ordering, mappings, generator algorithms, evaluator, seeds and preservation rules, and be committed/published before computation.

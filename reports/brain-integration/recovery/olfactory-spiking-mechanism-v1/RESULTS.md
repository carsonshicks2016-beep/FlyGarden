# Olfactory release integration audit

Completed an isolated event-release implementation, native Brian2 validation,
and exact-root anatomical mapping. No full-brain or application controller was changed.

## Mapping

| Channel | ORNs | PNs | Cognate afferent records / anatomical synapses | Non-ORN incoming records / anatomical synapses | Two-hop PN return intermediates |
| --- | ---: | ---: | ---: | ---: | ---: |
| DM1 | 68 | 2 | 135 / 6199 | 569 / 8073 | 484 |
| DM2 | 54 | 4 | 216 / 4227 | 766 / 5979 | 400 |

The 351 exact cognate ORN–PN records represent 10,426 anatomical synapses;
they are not 351 individual biological synapses. Root IDs, positional source-row
identifiers, signs and all selected edges are retained in mapping.json. Additional
other-ORN inputs are included in the mapping summary. Two DM1 incoming non-ORN
records lack cell-type annotations. Return intermediates include paths between
members of a PN population; their existence does not prove a same-cell cycle,
positive feedback, activity, or the cause of persistent firing.

## Event checks

The event interpretation decays facilitation and replenishes available resources
between events, increases release probability at an accepted event, releases
u*x, and depletes x by the same amount. It uses generic Liu et al. 2021 parameters
U=.24, tauD=.1 s and tauF=.05 s. These are not established DM1/DM2 estimates.

- Independent event-by-event ODE calculation: maximum error 1.97e-13.
- Native Brian2 event-driven synapse versus analytic reference: maximum cumulative-release error 7.11e-15, across 300 events on a 100 μs clock.
- JSON transient-state/owned-RNG continuation and native Brian2 store/restore: exact for their respective isolated tests.
- Zero accepted events produce zero release; resources recover during silence.
- Invalid event times/probabilities and incompatible checkpoint identity are rejected; two focused tests pass.

Presynaptic inhibition is represented only by an **externally supplied event
acceptance probability** in the analytic reference. It is an engineered thinning
interpretation of effective rate pR. It has not been wired to anatomical LNs;
the Brian2 comparison deliberately tests STP alone (p=1).

An ensemble of 4,096 independent Poisson event synapses at each of 5, 20, 50 and
120 Hz differs from the published product-of-means steady expression by about
0.9–4.5% in these finite measurements. This is a descriptive discrepancy, not
an equivalence pass or a precision estimate. The event process has correlations
and noise absent from the mean-field closure. No parameters were tuned to remove
that gap. This package does not reproduce PN spike responses or paper Figures4/5;
the preceding mean-field reference package covers its specified figure checks.

## Integration decision

The existing aggregated connectome and annotations identify cognate afferent
neurons but do not establish bouton locations, presynaptic receptor effects,
LN-to-terminal efficacy, or a DM1/DM2-specific physiological parameter set.
Whole-neuron negative graph weights cannot be relabeled as terminal inhibition.
The published conductance-to-rate coefficients also are not LIF voltage weights.

Earlier full-network pulse trials showed quiet stimulated DM1 ORNs while PNs and
descending neurons continued firing. Odor-afferent adaptation could change the
onset, but cannot be assumed to cure downstream persistence. Keep this diagnosis
visible and keep navigation and learning gates failed/pending.

Next: preregister an explicitly engineered **STP-only afferent model hypothesis**,
with exact selected-edge identity, fixed first-release scaling convention,
unchanged non-selected edges/decoder, persistent per-edge state and delay queues,
and separate full checkpoint tests. Compare original versus STP-only pulse/no-odor
controls before any physical navigation evaluation. A failed recovery is a result,
not a reason to silently extend plasticity to other edges. Full published PI
integration requires a separately supported terminal/LN mapping and parameter
convention; those biological claims remain blocked by missing evidence.

## Source

[Liu et al. 2021, official article](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2021.730431/full).
The cached, hashed article and prior selected mean-field reproduction are in
../olfactory-dynamics-reference-v1/. This package is an independent implementation,
not the author's simulator. Brian2 uses NumPy code generation for this bounded
one-synapse validation. No reduction has been substituted into the application.

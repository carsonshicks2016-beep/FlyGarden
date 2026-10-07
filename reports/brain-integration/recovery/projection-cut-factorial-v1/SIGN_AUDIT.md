# Imported olfactory signs and dynamics audit

## Import integrity

Every graph endpoint matches the exact ordered root ID used by the model. Every signed connection equals anatomical count multiplied by its stored sign. No presynaptic root has mixed outgoing signs. The circuit issue is not an observed root-ordering error or a corrupted signed-weight multiplication. Hashes and all 1,114 module-neuron records are retained in sign-audit.json.

## Annotated populations

| Population | Neurons | Positive-output neurons | Negative-output neurons | Top prediction confidence below 0.5 | Disagreement with annotation top-label sign rule |
| --- | ---: | ---: | ---: | ---: | ---: |
| ALLN | 429 | 166 | 263 | 270 | 48 |
| ALPN | 685 | 474 | 211 | 0 | 0 |

The newer annotation table's top transmitter is not the original cleft-filtered, synaptic-site-majority prediction rule. Its 48 local-neuron disagreements are audit leads, not 48 demonstrated import errors. None of these disagreements has top-label confidence at least 0.8. The table does not provide postsynaptic receptor identities.

The four previously selected persistent local neurons have prediction confidence 0.286–0.323. Two lLN1_bc roots have acetylcholine known_nt annotations citing Shang et al. (2007); both are positive in the model. Excitatory local circuitry is experimentally documented, so making every local neuron inhibitory is unjustified. [Shang et al.](https://pubmed.ncbi.nlm.nih.gov/17289577/), [Huang et al.](https://pubmed.ncbi.nlm.nih.gov/20869598/)

## Specific source-supported discrepancies

| Exact root | Cell type | Model sign | Literature-linked known_nt |
| --- | --- | ---: | --- |
| 720575940623636701 | il3LN6, right | +1 | GABA |
| 720575940632403986 | il3LN6, left | +1 | GABA |
| 720575940619061662 | v2LN36, right | +1 | glutamate |
| 720575940620541349 | v2LN36, left | +1 | glutamate |

The two il3LN6 roots have GABA annotations citing Tanaka et al. (2012). Independent experiments identify this cell type as inhibitory and show that it contributes to bilateral contrast in DA1 projection neurons. They also show spatially restricted activity in its arbor. These results support testing the two roots with inhibitory output in a separate versioned candidate. They do not establish that such a change will cure DM1 persistence or navigation; DA1 evidence is not DM1 validation. The annotation joins cell types to exact model roots, rather than measuring the original animal's physiology. [Tanaka et al.](https://pubmed.ncbi.nlm.nih.gov/22592945/), [Taisz et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC10403364/)

Parsing compound marker annotations also identifies 12 lLN2P_b roots annotated “gaba, MIP; acetylcholine-negative” whose modeled output is positive. Negative acetylcholine staining is absence evidence, not an excitatory transmitter label. This brings the module total to 16 known-marker/sign-rule disagreements: 14 GABA-associated and two glutamate-associated. All exact roots and marker strings are retained in sign-audit.json. The compound strings were not resolved by the initial exact-string check; the final audit explicitly tokenizes markers and excludes negative staining.

Sizemore et al. experimentally associate antennal-lobe MIPergic patchy neurons with GABA rather than acetylcholine or glutamate. The pinned annotation assigns this evidence to the 12 lLN2P_b roots; that annotation-to-cell-type bridge still needs scrutiny before treating all twelve sign changes as equally established. MIP co-transmission also remains absent from the model. Keep this group separate from il3LN6 in subsequent tests. [Sizemore et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC10465596/)

For v2LN36, immunostaining supports glutamate. The published experiment suggests local inhibition, but transmitter identity does not establish the sign at every postsynaptic receptor. Treat this as a separate, more qualified hypothesis. [Chou et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8856614/)

## Parameter provenance and limits

The loaded local/projection neurons retain the released uniform constants: resting/reset −52mV, threshold −45mV, membrane time constant 20ms, synaptic decay 5ms, refractory period 2.2ms, delay 1.8ms and weight 0.275mV per signed synapse. Both differential equations are refractory-gated. Source comparison passed for all eight checks; these are implementation comparisons, not measured cell-specific parameter fits.

The published model assigns GABA/glutamate to inhibitory and the other predicted transmitters to positive output using a filtered site-majority rule. It also discusses the uncertainty of glutamate's sign. Our imported model inherits simplified fast transmission rather than receptor-specific or neuromodulatory kinetics. [Shiu et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11446845/)

The undefined upstream reset variable was removed; engineered stimulation uses refractory exceptions and an owned Bernoulli generator. These disclosed adapter changes are separate from local/projection cell dynamics. The present one-electrical-unit-per-neuron implementation has no dendritic compartments, cell-specific adaptation or measured synapse-specific kinetics. Parameter matching therefore does not validate odor localization.

## Decision boundary

Complete the independently audited two-by-two circuit-cut batch. Keep every cut diagnostic. The next candidate should first isolate the two source-supported il3LN6 sign changes, retaining all neurons and connections, original absolute weights, fixed encoding and decoder. Keep the original model as the control; test quiet recovery and renewed left/right odor response before any body/navigation evaluation. Do not apply blanket inhibitory conversion, loosen thresholds, or choose biological signs by whichever produces an appealing video.

Literature copies obtained from Europe PMC are hashed in literature/sources.json and literature/additional-sources.json. They support cell-type interpretation; neither exact-root electrical fits nor receptor maps were obtained. No application source was changed.

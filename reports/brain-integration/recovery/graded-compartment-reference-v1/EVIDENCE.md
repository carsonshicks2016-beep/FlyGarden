# Evidence and scope: local continuous activity

This package completes an evidence review and isolated mechanism reference. It does not change the Fly Garden application or its full-brain controller.

## Primary sources

1. Schenk and Gaudry (2023), *Nonspiking Interneurons in the Drosophila Antennal Lobe Exhibit Spatially Restricted Activity*, [eNeuro, DOI 10.1523/ENEURO.0109-22.2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9884108/). Electrophysiology supports nonspiking R32F10 patchy neurons. Spatially varying calcium responses motivate electrotonic isolation, but calcium is a proxy and does not establish release kinetics. The article reports longer calcium decay/duration in this population, so faster calcium extinction is not our acceptance criterion. Cached XML is preserved and hashed.
2. Barth-Maron, D’Alessandro and Wilson (2023), *Interactions between specialized gain control mechanisms in olfactory processing*, [Current Biology, DOI 10.1016/j.cub.2023.10.041](https://doi.org/10.1016/j.cub.2023.10.041). Experiments and modeling distinguish local postsynaptic and global presynaptic inhibition. The [authors’ model archive](https://doi.org/10.5281/zenodo.10028674) supplies a reproducible continuous-activity reference. We verified published MD5 checksums for both model archives and retained their source code. License: CC BY 4.0, according to the pinned archive metadata. No code from an unrelated search result is used.
3. Sizemore et al. (2023), [DOI 10.1038/s41467-023-41012-3](https://pmc.ncbi.nlm.nih.gov/articles/PMC10465596/), supports a GABA/MIP patchy population. Our existing exact-root annotation bridge remains qualified; it is not a physiological measurement of the connectome individual. Its prior cached XML and source hash are retained.

## Implemented equations and source conventions

The faithful 1-ms port uses `run_AL_model.m` and the parameter vector printed in `LN_activity_injection_dynamics.m`:

`b = [3835, 6.06304380373610e-6, 1004.89493761302, 30.5976478828549, 0.103245596784364, 0.11, 0.2]`.

Four recurrent variables are PN, presynaptic LN, postsynaptic local LN, and a silent fourth variable. Two ORN resource variables exist, but only the first contributes to recurrent drive. With milliseconds as time units:

- Scaled input `s = stimulus * b[2] + b[3]`.
- Presynaptic inhibition divides each input by `1 + b[4:6] * v_pre`.
- Resource dynamics: `dA/dt = -b[1] * s * A + (1-A)/b[0]`.
- ORN release proxy: `u = s * A`.
- Continuous activity: `dv/dt = (-v + W*u + M*v)/15`, with PN→local-LN drive and local-LN→PN negative feedback `-b[6] * v_local`.
- Initial resources are 0.5; initial presynaptic LN activity is 1; other activity is zero.

Source quirks are preserved: either zero presynaptic weight disables both presynaptic paths; activity is rectified; exhausted resources reset to `1/b[0]`; injection adds an increment each 1-ms sample rather than acting as a physical current. Our optional smaller-step checks scale the injection increment by step size. The original negative-postsynaptic-weight clamp is outside our domain because negative parameters are rejected. Supplying explicit parameters/injection avoids the source’s omitted-injection override of the last parameter to 0.2. These conventions are not newly inferred biology.

Continuous LN activity is neither a measured membrane voltage nor a spike rate inferred from calcium. `u` is a rate-times-resource proxy, not measured GABA vesicle release. No electrical propagation, peptide dynamics or receptor-specific currents are modeled.

## Spatial test boundary

Two independent copies of the published single-glomerulus model provide synthetic channels A/B. This lets us test bookkeeping, mirrored inputs and local feedback without global broadcast. Their exact independence is an engineered construction, not an experimental discovery of zero cross-glomerular coupling. They are not left/right antennae, mapped DM1 compartments or reconstructed branches. No FlyWire neuron is split or omitted in the actual application.

The archived MATLAB comments name LN2P_c, and its fitting script uses DC3 PN recordings. The prior full-network sign candidate contains twelve exactly joined lLN2P_b roots, and the diagnostic inputs use DM1. These are materially different mappings. The published fit must not be presented as fitted parameters for those roots, DM1, or all patchy cells. Native MATLAB execution, refitting DC3 recordings and reproduction of the complete paper’s figures have not been done; the checks establish agreement with an independent literal translation and numerical convergence.

## Requirements before a full-network candidate

1. Audit the patchy subtype inventory and supporting driver-to-cell mapping; retain ambiguous or unavailable identities explicitly.
2. Obtain glomerulus-specific input/output synapse locations or validated ROI assignments for exact version-783 roots. The imported aggregate connection table has no synapse coordinates or glomerular labels. Soma coordinates and a skeleton alone do not identify release sites.
3. Specify the conversion from incoming spikes/voltages to local continuous activity, inhibitory targets and release units. Preserve anatomical aggregate counts when distributing actual synapses across compartments; unresolved allocation cannot be filled with arbitrary channel copies.
4. Establish which kinetics can be sourced or fitted and which remain engineered assumptions. Keep calibration separate from prospective acceptance. Include mutual local-neuron inhibition and other inputs rather than treating the isolated negative-feedback model as the complete antennal lobe.
5. Validate an adapter against this reference and exact continuation before a separate full-network candidate. Retain full-network response, recovery and contrast gates; then test body direction and navigation.

Decision: the isolated rate mechanism is useful and numerically checked. Exact-root compartment physiology and a full-network integration are still pending. Do not promote it as a repaired brain or a learned controller.

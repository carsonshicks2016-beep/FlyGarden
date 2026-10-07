# Odor-to-steering interface: supported claims and missing claims

## What the literature supports

Rayshubskiy et al., *Neural circuit mechanisms for steering control in walking Drosophila*, https://elifesciences.org/articles/102230, links bilateral DNa02 firing differences to turning. Its anatomical discussion describes parallel excitation/inhibition, central-complex guidance and a proposed MBON32 pathway for appetitive versus aversive cues. The odor-attraction schematic is a pathway hypothesis; it is not proof that uniform DM1 or DM2 stimulation in a generic full-network model must produce mirrored turns. KC–MBON learned synaptic strength and competing circuit activity matter to that hypothesis. Input populations, soma sides and odor valence cannot be substituted for a validated peripheral receptive-field map.

Shiu et al., *A Drosophila computational brain model reveals sensorimotor processing*, https://www.nature.com/articles/s41586-024-07763-9, validates specific feeding/grooming predictions. Its limitations include uniform neuron properties, omitted morphology/receptor dynamics, gap junctions, non-spiking neurons, internal-state and long-range peptide effects, and zero basal firing. Its reported accuracy is specific to the tested predictions, not a navigation guarantee. The garden uses the later v783 artifact; agreement with those artifact equations is distinct from reproducing the original paper's data and experiments.

## What our evidence supports

The preserved 36-trial inhibitory intervention matrix attributes right-DNa02 suppression to negative modeled synaptic delivery. Removing negative input makes right DNa02 fire, but does not make intact odor direction useful. Removing outgoing DNa02 feedback also does not remove left-biased persistence. Those are diagnostic lesions, not authorized repairs to production anatomy.

The 40 localization and 24 lower-gain trials establish that both odor identities, unilateral/bilateral exposure, selected-input refractory policy, support removal and the tested input-rate range do not yield a qualified directional interface. Quiet and support-only controls differ; supplied walking support must remain visible and matched. The low-rate result can depend strongly on stochastic seed. These trials do not establish which neuron type causes all persistent activity.

## Current decision

Do not add a rule that converts antenna difference into steering and call it connectome control. Do not fabricate baseline activity, learning history or neuron-specific receptor dynamics to achieve the desired output. First complete the registered 4-second independent equation replay with a 3.2-second odor-free tail. If persistence is reproduced, treat it as a limitation of this network/operating-state/interface combination rather than an unverified adapter bug.

Then test the documented downstream MBON32-to-steering circuit as a capability diagnostic on exact annotated roots. Direct downstream stimulation is explicitly NOT odor navigation and must never replace the sensory interface in the application. Its purpose is to determine whether the published proposed path yields bilateral specificity and recovery in this model before investing in a physiological sensory/learning revision. Any subsequent modification needs its own source-pinned model identity and disjoint calibration; behavior remains gated until an intact local-sensing candidate qualifies.

"""Diagnostic direct input added to the unchanged local-adaptation candidate."""
import json
from pathlib import Path

import brian2 as b
import numpy as np

from .adaptive_candidate import AdaptiveCandidate
from .continuous_candidate import file_sha
from .mbon_capability import drive_events
from .recording import atomic_json


class MBONCapabilityCandidate(AdaptiveCandidate):
    def __init__(self, mapping, domain, targets, seed):
        super().__init__(mapping, domain, seed, tau_s=.45, step_mv=13.5)
        self.direct_targets = np.asarray(targets, np.int32)
        expected = [mapping[key][0]['index'] for key in ['MBON32_left', 'MBON32_right']]
        if expected != self.direct_targets.tolist() or set(targets) & set(self.targets) or set(targets) & set(domain['indices']):
            raise ValueError('Exact disjoint MBON target mapping required')
        self.direct_rng = np.random.default_rng(seed+100000)
        self.direct_generator = b.SpikeGeneratorGroup(2, [], []*b.second, clock=self.brain.clock, name='fg_mbon_capability_inputs')
        self.direct_stimulation = b.Synapses(self.direct_generator, self.brain.neurons, on_pre='v_post+=68.75*mV',
                                            clock=self.brain.clock, name='fg_mbon_capability_stimulation')
        self.direct_stimulation.connect(i=[0, 1], j=self.direct_targets)
        self.direct_monitor = b.SpikeMonitor(self.direct_generator, name='fg_mbon_capability_monitor')
        self.brain.neurons.rfc[self.direct_targets] = 0*b.ms
        self.brain.network.add(self.direct_generator, self.direct_stimulation, self.direct_monitor)
        for name in ['mbon_capability.py', 'mbon_capability_candidate.py']:
            self.source_hashes[name] = file_sha(Path(__file__).parent/name)

    def advance_capability(self, case, tick):
        if abs(self.time-tick*.025) > 1e-10: raise ValueError('Window/brain clock mismatch')
        indices, times = drive_events(self.direct_rng, case, tick)
        self.direct_generator.set_spikes(indices, times*b.second, sorted=True)
        command = self.advance(.025, np.zeros((2, 2)), [0, 0])
        actual_indices = np.asarray(self.direct_monitor.i[:], np.int32).copy()
        actual_times = np.asarray(self.direct_monitor.t[:]/b.second).copy()
        np.testing.assert_array_equal(actual_indices, indices)
        np.testing.assert_allclose(actual_times, times, atol=1e-12, rtol=0)
        self.direct_monitor.resize(0); self.direct_monitor.variables['N'].set_value(0)
        self.last.update(mbon_i=indices, mbon_t=times, mbon_delivered_i=actual_indices, mbon_delivered_t=actual_times)
        return command

    def manifest(self):
        m = super().manifest()
        m['direct_capability_input'] = dict(id='matched-direct-MBON32-v1', targets=self.direct_targets.tolist(),
            root_ids=[str(self.brain.ids[i]) for i in self.direct_targets], input_hz=50., jump_mV=68.75,
            rng_offset=100000, additional_zero_refractory_indices=self.direct_targets.tolist(),
            convention='Both MBON roots zero refractory in every case, including none; historical direct-drive convention, a change from the odor-only candidate.',
            scope='Engineering capability experiment; never a sensory or navigation controller.')
        return m

    def save(self, folder):
        super().save(folder)
        folder = Path(folder)
        atomic_json(folder/'direct-rng.json', self.direct_rng.bit_generator.state)
        atomic_json(folder/'integrity.json', {'files': {p.name: file_sha(p) for p in folder.iterdir()
                                                     if p.is_file() and p.name != 'integrity.json'}})

    def load(self, folder):
        super().load(folder)
        self.direct_rng.bit_generator.state = json.loads((Path(folder)/'direct-rng.json').read_text())

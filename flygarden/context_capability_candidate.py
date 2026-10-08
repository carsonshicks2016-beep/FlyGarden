"""Diagnostic context wrapper. No neural, weight, decoder or learning changes."""
from pathlib import Path
import brian2 as b
import numpy as np
from .continuous_candidate import file_sha
from .context_capability import CONTEXTS, context_odors
from .mbon_capability import drive_events
from .mbon_capability_candidate import MBONCapabilityCandidate


class ContextCapabilityCandidate(MBONCapabilityCandidate):
    version='fixed-sensory-context-MBON32-v1'

    def __init__(self,mapping,domain,targets,seed,context):
        if context not in CONTEXTS:raise ValueError('Unknown fixed context')
        self.context=context
        super().__init__(mapping,domain,targets,seed)
        # Observation only: ordinary inputs previously stored requests. This
        # monitor verifies actual support/odor generator output too.
        self.input_monitor=b.SpikeMonitor(self.generator,name='fg_context_input_monitor')
        self.brain.network.add(self.input_monitor)
        for name in ['context_capability.py','context_capability_candidate.py']:
            self.source_hashes[name]=file_sha(Path(__file__).parent/name)

    def advance(self,*args,**kwargs):
        motor=super().advance(*args,**kwargs)
        ii=np.asarray(self.input_monitor.i[:],np.int32).copy()
        tt=np.asarray(self.input_monitor.t[:]/b.second).copy()
        np.testing.assert_array_equal(ii,self.last['external_indices'])
        np.testing.assert_allclose(tt,self.last['external_times'],atol=1e-12,rtol=0)
        self.input_monitor.resize(0);self.input_monitor.variables['N'].set_value(0)
        self.last.update(input_delivered_i=ii,input_delivered_t=tt)
        return motor

    def advance_context(self,case,tick):
        if self.context=='no_odor':
            # Preserve the historical no-context advancement path exactly.
            return super().advance_capability(case,tick)
        if abs(self.time-tick*.025)>1e-10:raise ValueError('Window/brain clock mismatch')
        ii,tt=drive_events(self.direct_rng,case,tick)
        self.direct_generator.set_spikes(ii,tt*b.second,sorted=True)
        motor=self.advance(.025,context_odors(self.context,tick),[0,0])
        actual_i=np.asarray(self.direct_monitor.i[:],np.int32).copy()
        actual_t=np.asarray(self.direct_monitor.t[:]/b.second).copy()
        np.testing.assert_array_equal(actual_i,ii);np.testing.assert_allclose(actual_t,tt,atol=1e-12,rtol=0)
        self.direct_monitor.resize(0);self.direct_monitor.variables['N'].set_value(0)
        self.last.update(mbon_i=ii,mbon_t=tt,mbon_delivered_i=actual_i,mbon_delivered_t=actual_t)
        return motor

    def manifest(self):
        m=super().manifest()
        m['sensory_context']=dict(id='fixed-sensory-context-MBON32-v1',context=self.context,
            DM1_concentration_each_antenna=.5 if self.context=='DM1_equal_50_50' else 0.,
            odor_windows=[[12,32],[132,152]],ordinary_input_monitor=True,
            encoding='Existing engineered DM1 encoding; nominal25Hz per receptor during pulses in the odor context.',
            scope='Matched operating-context diagnostic, not a promoted navigation controller or adaptation-disabled comparison.')
        return m

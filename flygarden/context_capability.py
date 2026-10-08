"""One fixed engineered odor context; unchanged historical capability gates."""
import numpy as np
from .mbon_capability import PULSES, evaluate_capability

CONTEXTS=('no_odor','DM1_equal_50_50')


def context_odors(context,tick):
    if context not in CONTEXTS or not isinstance(tick,(int,np.integer)) or not 0<=tick<240:
        raise ValueError('Fixed context and six-second window required')
    odors=np.zeros((2,2))
    if context=='DM1_equal_50_50' and any(lo<=tick<hi for lo,hi in PULSES):odors[:,0]=.5
    return odors


def evaluate_contexts(protocol,traces):
    expected={(context,seed,case) for context in CONTEXTS for seed in protocol['diagnostic_seeds']
              for case in protocol['cases']}
    if set(traces)!=expected:raise ValueError('All sixteen context/case/seed traces required')
    return {context:evaluate_capability(protocol,{(seed,case):traces[context,seed,case]
        for seed in protocol['diagnostic_seeds'] for case in protocol['cases']}) for context in CONTEXTS}

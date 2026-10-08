import json
import numpy as np
import pytest
from flygarden.context_capability import CONTEXTS, context_odors, evaluate_contexts
from flygarden.candidate_inputs import CandidateInputs
from flygarden.mbon_capability import CASES, evaluate_capability
from flygarden.route_state_audit import json_native


def test_fixed_context_half_open_windows_and_receptor_gain():
    profile=CandidateInputs()
    for tick in range(240):
        rates=profile.rates(context_odors('DM1_equal_50_50',tick),[0,0])
        expected=25. if 12<=tick<32 or 132<=tick<152 else 0.
        assert rates['ORN_DM1_left']==rates['ORN_DM1_right']==expected
        assert rates['DNp09_left']==rates['DNp09_right']==65.
        assert rates['ORN_DM2_left']==rates['ORN_DM2_right']==rates['LPLC2_left']==rates['LPLC2_right']==0.
        assert not context_odors('no_odor',tick).any()
    with pytest.raises(ValueError):context_odors('new_context',12)
    with pytest.raises(ValueError):context_odors('no_odor',240)


def test_odor_changes_do_not_advance_support_random_stream():
    channels=np.repeat(np.arange(8),[35,33,20,20,1,1,8,8])
    rngs={context:np.random.default_rng(12501) for context in CONTEXTS};profile=CandidateInputs()
    for tick in range(240):
        support=[]
        for context in CONTEXTS:
            rates=np.asarray(list(profile.rates(context_odors(context,tick),[0,0]).values()))
            offset,ii=np.nonzero(rngs[context].random((250,len(channels)))<rates[channels]*.0001)
            keep=np.isin(channels[ii],[4,5]);support.append(np.c_[offset[keep],ii[keep]])
        np.testing.assert_array_equal(*support)


def test_context_controls_stay_separate_and_frozen_evaluator_parity():
    p=dict(diagnostic_seeds=[12501,12502],cases=list(CASES),burst_windows=[[44,132],[164,240]])
    traces={}
    for context in CONTEXTS:
        for seed in p['diagnostic_seeds']:
            for case in CASES:
                t=np.zeros((240,12));t[:,4:6]=65
                # A context's tonic left offset must subtract its own control.
                if context=='DM1_equal_50_50':t[:,2]=40
                if case!='none':
                    sides=[0] if case=='left' else [1] if case=='right' else [0,1]
                    for lo,hi in [(12,32),(132,152)]:
                        for side in sides:t[lo:hi,side]=50;t[lo:hi,2+side]+=20
                traces[context,seed,case]=t
    actual=evaluate_contexts(p,traces)
    for context in CONTEXTS:
        expected=evaluate_capability(p,{(s,c):traces[context,s,c] for s in p['diagnostic_seeds'] for c in CASES})
        assert json_native(actual[context])==json_native(expected)
        assert all(row['passed'] for row in actual[context]['direction'])
    assert json.loads(json.dumps(json_native(actual)))['no_odor']['capability_neural_checks_passed']
    traces.pop(('no_odor',12501,'none'))
    with pytest.raises(ValueError):evaluate_contexts(p,traces)


def test_no_context_dispatch_uses_original_advance(monkeypatch):
    from flygarden.context_capability_candidate import ContextCapabilityCandidate
    from flygarden.mbon_capability_candidate import MBONCapabilityCandidate
    marker=object();calls=[]
    def original(self,case,tick):calls.append((case,tick));return marker
    monkeypatch.setattr(MBONCapabilityCandidate,'advance_capability',original)
    candidate=object.__new__(ContextCapabilityCandidate);candidate.context='no_odor'
    assert candidate.advance_context('left',12) is marker and calls==[('left',12)]

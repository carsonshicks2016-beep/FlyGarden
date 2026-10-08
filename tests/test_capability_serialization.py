import json

import numpy as np

from scripts.finalize_recovered_mbon_capability import json_scalars
from flygarden.mbon_capability import evaluate_capability


def test_nested_numpy_flag_roundtrips_without_changing_value():
    original = {'rows': [{'passed': np.bool_(False), 'gain': np.float64(12.), 'count': np.int64(6)}], 'plain': True}
    converted = json_scalars(original)
    assert converted == original and type(converted['rows'][0]['passed']) is bool
    assert json.loads(json.dumps(converted)) == converted
    assert isinstance(original['rows'][0]['passed'], np.generic)


def test_frozen_evaluator_outputs_serialize_and_preserve_every_flag():
    p = dict(diagnostic_seeds=[12401, 12402], burst_windows=[[44, 132], [164, 240]])
    traces = {(s, c): np.zeros((240, 12)) for s in p['diagnostic_seeds'] for c in ['none', 'left', 'right', 'both']}
    for t in traces.values(): t[:, 4:6] = 65
    raw = evaluate_capability(p, traces); converted = json_scalars(raw)
    assert raw == converted
    assert json.loads(json.dumps(converted)) == converted
    assert not converted['capability_neural_checks_passed'] and not converted['controller_promoted']

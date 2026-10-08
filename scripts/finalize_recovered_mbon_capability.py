"""Output-only scalar serialization repair; never starts a neural simulation."""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.recording import atomic_json


def json_scalars(value):
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, dict): return {key: json_scalars(item) for key, item in value.items()}
    if isinstance(value, list): return [json_scalars(item) for item in value]
    return value


def main():
    from scripts.test_recovered_mbon_capability import OUT, verify, evaluate
    started = time.monotonic(); p = verify()
    amendment = json.loads((OUT/'serialization-amendment.json').read_text())
    assert amendment['protocol_sha256'] == file_sha(OUT/'protocol.json')
    assert all(file_sha(ROOT/key) == value for key, value in amendment['new_source_hashes'].items())
    if (OUT/'results.json').exists(): raise FileExistsError('Preserve completed results')
    manifests = []; source_files = {}
    for seed in p['diagnostic_seeds']:
        for case in p['cases']:
            path = OUT/'trials'/f'{case}-{seed}'/'manifest.json'; m = json.loads(path.read_text())
            assert m['status'] == 'complete' and len(m['chunks']) == 240
            manifests.append(m)
            for chunk in m['chunks']: source_files[str(path.parent/chunk['file'])] = chunk['sha256']
    interrupted = json.loads((OUT/'interruption-test.json').read_text())
    assert interrupted['status'] == 'passed' and interrupted['prefix_reconstructed_exactly']
    result = json_scalars(evaluate(p))
    # All measurement values/flags are unchanged. Only NumPy scalar types are
    # converted for the JSON writer. No call to run(), construct(), or worker().
    result.update(trial_worker_wall_seconds_sum=sum(m['wall_seconds'] for m in manifests),
        finalization_wall_seconds=time.monotonic()-started, main_trial_peak_rss_bytes=max(m['peak_rss_bytes'] for m in manifests),
        serialization_amendment_sha256=file_sha(OUT/'serialization-amendment.json'),
        finalization_full_brain_runs=0, immutable_parent_protocol_verified=True,
        scientific_measurement_values_and_thresholds_changed=False)
    atomic_json(OUT/'results.json', result)
    subprocess.run([sys.executable, '-B', str(ROOT/'scripts/audit_recovered_mbon_capability.py')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, '-B', str(ROOT/'scripts/plot_recovered_mbon_capability.py')], cwd=ROOT, check=True)
    assert all(file_sha(Path(path)) == value for path, value in source_files.items())
    atomic_json(OUT/'progress.json', dict(status='complete', completed=[f'{c}-{s}' for s in p['diagnostic_seeds'] for c in p['cases']],
                planned_trials=8, workers=1, promoted=False, finalized_with_output_only_serialization_amendment=True))
    atomic_json(OUT/'serialization-repair-receipt.json', dict(status='passed',
        numpy_scalar_types_converted_only=True, protocol_unchanged=True, original_pinned_sources_unchanged=True,
        recorded_chunks_unchanged=True, new_full_brain_runs=0, source_sha256=file_sha(Path(__file__)),
        wall_seconds=time.monotonic()-started))
    print('Saved-data finalization, independent audit and plot complete; no new simulation.', flush=True)


if __name__ == '__main__': main()

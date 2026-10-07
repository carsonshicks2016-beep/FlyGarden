import numpy as np
import pytest
from flygarden.recorded_drive import replay_recorded_states


def test_delay_arrivals_reset_refractory_release_and_chunk_boundary():
    drive = np.zeros((500, 1)); spikes = np.zeros_like(drive, dtype=bool)
    spikes[249, 0] = True
    drive[249, 0] = 100  # erased by reset at the end of the first chunk
    drive[250:271, 0] = 100  # ignored during refractory
    drive[271, 0] = 3  # released exactly 22 ticks after the spike
    g, adapt, gate = replay_recorded_states(drive, spikes, [13.5])
    assert g[0, 0] == 0 and adapt[0, 0] == 13.5
    assert not gate[249:271, 0].any() and gate[271, 0]
    assert g[1, 0] == pytest.approx(3*np.exp(-228*.0001/.005), rel=1e-12)
    assert adapt[1, 0] == pytest.approx(13.5*np.exp(-250*.0001/.45), rel=1e-12)


def test_signed_drive_and_unadapted_target():
    drive = np.zeros((250, 2)); spikes = np.zeros_like(drive, dtype=bool)
    drive[249] = [5, -2]; spikes[10] = True
    g, adapt, _ = replay_recorded_states(drive, spikes, [0, 1.5], tau_s=.15)
    np.testing.assert_array_equal(g, [[5, -2]])
    assert adapt[0, 0] == 0
    assert adapt[0, 1] == pytest.approx(1.5*np.exp(-239*.0001/.15), rel=1e-12)


def test_invalid_input():
    with pytest.raises(ValueError):
        replay_recorded_states(np.zeros((3, 2)), np.zeros((3, 1)), [0, 0])

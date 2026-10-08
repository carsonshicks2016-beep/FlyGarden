import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flygarden.receiver_diagnostic import receiver_partitions
from flygarden.feedback_trace import delayed_impulses


def test_partitions_preserve_signs_untargeted_rows_and_original():
    w = csr_matrix([[5., -2., 3., 0.], [4., 1., -7., 2.],
                    [8., -9., -6., 2.], [1., 0., -4., 3.]])
    original = w.toarray().copy()
    parts = receiver_partitions(w, [0, 1], [2, 3], [0, 1], [2])
    np.testing.assert_array_equal(w.toarray(), original)
    np.testing.assert_array_equal(parts['intact'].toarray(), original)
    np.testing.assert_array_equal(parts['pn_dm1_only'].toarray(),
                                   [[5, -2, 0, 0], [4, 1, 0, 0], [8, -9, -6, 2], [1, 0, -4, 3]])
    np.testing.assert_array_equal(parts['dna_without_aotu019'].toarray(),
                                   [[5, -2, 3, 0], [4, 1, -7, 2], [8, -9, 0, 2], [1, 0, 0, 3]])


def test_delayed_partition_drive_matches_directed_source_removal():
    w = csr_matrix([[2., 1., -3.], [0., 4., -5.]])
    parts = receiver_partitions(w, [0], [1], [0], [2])
    trains = {key: delayed_impulses([0, 1, 2], [0, 1, 1], value, 30, 18)
              for key, value in parts.items()}
    np.testing.assert_array_equal(trains['intact'][18:20], [[2., 0.], [-2., -1.]])
    np.testing.assert_array_equal(trains['pn_dm1_only'][18:20], [[2., 0.], [0., -1.]])
    np.testing.assert_array_equal(trains['dna_without_aotu019'][18:20], [[2., 0.], [-2., 4.]])


def test_overlapping_or_invalid_indices_block_partition():
    with pytest.raises(ValueError):receiver_partitions(csr_matrix(np.eye(2)), [0], [0], [0], [1])
    with pytest.raises(ValueError):receiver_partitions(csr_matrix(np.eye(2)), [0], [1], [2], [1])

import numpy as np
import pytest
from scipy.io import savemat

from cns_audit.physiology import canonical_ephys,load_ephys_trace
from cns_audit.download import hashes


def fixture():
    values={'voltagedata':np.array([-60.,-59.,-58.,-57.]),'legangles':np.array([90.,120.]),
            'frame_on':np.array([1,4]),'SampleRate':20000}
    metadata=dict(voltage_unit='mV',angle_unit='degree',angle_convention='extension_increases',
        cell_class='13B-alpha',genotype='fixture',sex='fixture',recording_state='fixture',
        junction_corrected=False,junction_potential_mV=-12.,unit_evidence='synthetic test only',source_sha256='fixture')
    return values,metadata


def test_camera_clock_uses_exposures_not_nominal_video_rate():
    values,meta=fixture()
    out=canonical_ephys(values,meta)
    np.testing.assert_array_equal(out['angle_time_s'],[0.,3/20000])
    np.testing.assert_array_equal(out['voltage_time_s'],np.arange(4)/20000)
    np.testing.assert_array_equal(out['voltage_mV'],[-48.,-47.,-46.,-45.])
    np.testing.assert_array_equal(values['voltagedata'],[-60.,-59.,-58.,-57.])
    assert not out['metadata']['fit_or_validation_performed']


def test_no_double_junction_correction():
    values,meta=fixture()
    out=canonical_ephys(values,meta|{'junction_corrected':True})
    np.testing.assert_array_equal(out['voltage_mV'],values['voltagedata'])
    assert not out['metadata']['junction_correction_applied']


@pytest.mark.parametrize('indices',[[0,4],[1,5],[4,1],[1,3.5]])
def test_bad_exposure_indices_block(indices):
    values,meta=fixture()
    with pytest.raises(ValueError): canonical_ephys(values|{'frame_on':np.array(indices)},meta)


def test_units_or_unknown_correction_status_cannot_be_assumed():
    values,meta=fixture()
    for altered in [meta|{'voltage_unit':'V'},meta|{'junction_corrected':'unknown'},meta|{'unit_evidence':''}]:
        with pytest.raises(ValueError): canonical_ephys(values,altered)
    del meta['sex']
    with pytest.raises(ValueError,match='metadata'): canonical_ephys(values,meta)


def test_mat_reader_verifies_source_before_loading(tmp_path):
    values,meta=fixture()
    path=tmp_path/'measured.mat'; savemat(path,values)
    with pytest.raises(ValueError,match='identity'): load_ephys_trace(path,meta)
    out=load_ephys_trace(path,meta|{'source_sha256':hashes(path)['sha256']})
    assert out['metadata']['sampling_rate_Hz']==20000

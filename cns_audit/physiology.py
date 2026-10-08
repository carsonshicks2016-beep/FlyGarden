"""Strict class-level measurement preparation, without fitting a neuron model."""
from pathlib import Path

import numpy as np
from scipy.io import loadmat

from .download import hashes


def canonical_ephys(values, metadata):
    """Keep camera and voltage clocks distinct; use acquired exposure indices.

    Metadata must be established per file, not inferred from its filename or a
    paper's mean trace. This function never maps a physiological class to roots.
    """
    required = {'voltage_unit','angle_unit','angle_convention','cell_class','genotype',
                'sex','recording_state','junction_corrected','junction_potential_mV',
                'unit_evidence','source_sha256'}
    if required-metadata.keys():
        raise ValueError(f'Missing measurement metadata: {sorted(required-metadata.keys())}')
    if metadata['voltage_unit'] != 'mV' or metadata['angle_unit'] != 'degree':
        raise ValueError('Explicit verified mV/degree units required; no silent scaling')
    if not metadata['unit_evidence'] or metadata['angle_convention'] != 'extension_increases':
        raise ValueError('Verified units and angle convention required')
    if type(metadata['junction_corrected']) is not bool:
        raise ValueError('Explicit junction-correction status required')
    voltage = np.asarray(values['voltagedata'],dtype=np.float64).squeeze()
    angles = np.asarray(values['legangles'],dtype=np.float64).squeeze()
    frame_indices = np.asarray(values['frame_on']).squeeze()
    rate = float(np.asarray(values['SampleRate']).squeeze())
    if not np.isfinite(rate) or rate<=0:
        raise ValueError('Invalid measured sampling rate')
    if voltage.ndim!=1 or angles.ndim!=1 or frame_indices.ndim!=1:
        raise ValueError('Single trace and explicit camera exposure vector required')
    if not len(voltage) or len(angles)!=len(frame_indices) or len(angles)<2:
        raise ValueError('Camera/angle count mismatch')
    if not np.isfinite(voltage).all() or not np.isfinite(angles).all():
        raise ValueError('Missing/nonfinite samples must be classified explicitly')
    if not np.isfinite(frame_indices).all() or not np.equal(frame_indices,np.floor(frame_indices)).all():
        raise ValueError('Noninteger camera exposure indices')
    if frame_indices[0]<1 or frame_indices[-1]>len(voltage) or np.any(np.diff(frame_indices)<=0):
        raise ValueError('Camera exposures out of range or nonmonotonic')
    junction=float(metadata['junction_potential_mV'])
    if not np.isfinite(junction): raise ValueError('Invalid junction potential')
    corrected=voltage.copy() if metadata['junction_corrected'] else voltage-junction
    return dict(voltage_time_s=np.arange(len(voltage),dtype=np.float64)/rate,
                voltage_mV=corrected, raw_voltage_mV=voltage.copy(),
                angle_time_s=(frame_indices.astype(np.float64)-1)/rate,
                angle_degree=angles.copy(),
                metadata=metadata | {'sampling_rate_Hz':rate,'junction_correction_applied':not metadata['junction_corrected'],
                    'camera_clock':'MATLAB one-based exposure indices, converted once',
                    'correspondence':'Physiological class only; exact BANC root unresolved',
                    'fit_or_validation_performed':False})


def load_ephys_trace(path, metadata):
    path=Path(path)
    if hashes(path)['sha256']!=metadata.get('source_sha256'):
        raise ValueError('Measurement source identity mismatch')
    # Unsupported MATLAB 7.3 files raise, rather than guessing an HDF5 layout.
    values=loadmat(path,variable_names=['voltagedata','legangles','frame_on','SampleRate'],simplify_cells=True)
    if {'voltagedata','legangles','frame_on','SampleRate'}-values.keys():
        raise ValueError('Expected author-defined fields unavailable')
    return canonical_ephys(values,metadata)

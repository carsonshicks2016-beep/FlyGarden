"""Exact-root inventory of the dominant recorded local sources; no simulation."""
import json, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.recording import atomic_json, space_check

BASE = ROOT/'reports/brain-integration/recovery'
OUT = BASE/'local-source-qualification-v1'


def main():
    started = time.monotonic(); OUT.mkdir(exist_ok=True); space_check(OUT, 10*1024**2)
    assert not (OUT/'results.json').exists(), 'Preserve the completed package; use a new version'
    paths = [Path(__file__), ROOT/'data/annotations.tsv',
             BASE/'adaptive-feedback-trace-v1/results.json',
             BASE/'projection-cut-factorial-v1/sign-audit.json',
             BASE/'projection-cut-factorial-v1/SIGN_AUDIT.md',
             BASE/'adaptive-domain-screen-v1/domain-inventory.json',
             BASE/'il3ln6-sign-full-network-v2/RESULTS.md',
             BASE/'graded-compartment-reference-v1/EVIDENCE.md',
             OUT/'literature/sources.json']
    atomic_json(OUT/'protocol.json', {'version': 1, 'scope': 'Evidence qualification, not cell-specific parameter fitting or an intervention.',
        'selection': 'Every exact root appearing among the top20 positive sources into either monitored PN, in either strongest adaptation domain, either seed, any odor recovery window. No ranking on new simulated outcomes.',
        'coverage_definition': 'Sum of listed top20 ALLN contributions divided by all accepted positive input. This is a per-row listed-source fraction, not full union coverage.',
        'qualification_rule': 'Transmitter marker, experimental population physiology, exact-root correspondence and numerical parameter fit are separate fields. Unknowns do not become convenient spiking, graded, inhibitory, electrical or adaptive assignments.',
        'source_hashes': {str(p.relative_to(ROOT)): file_sha(p) for p in paths}})
    trace = json.loads((paths[2]).read_text()); audit = json.loads((paths[3]).read_text())
    ann = pd.read_csv(ROOT/'data/annotations.tsv', sep='\t', dtype={'root_id': str}, low_memory=False).fillna('').set_index('root_id')
    neurons = {x['root_id']: x for x in audit['module_neurons']}
    scores = defaultdict(float); coverage = []
    for row in trace['summaries']:
        if not row['trial'].startswith(('projection_t450_b13p5-a_', 'sensory_projection_t450_b13p5-a_')) or not row['phase'].startswith('recovery'): continue
        for target in row['inputs'][:2]:
            listed = 0.
            for source in target['top_positive_sources']:
                scores[source['root_id']] += source['signed_accepted_mV_per_s']
                if source['cell_class'] == 'ALLN': listed += source['signed_accepted_mV_per_s']
            coverage.append({'trial': row['trial'], 'phase': row['phase'], 'target_root_id': target['root_id'],
                             'listed_top20_ALLN_fraction_of_positive_input': listed/target['positive_mV_per_s']})
    inventory = []
    for rank, (root, score) in enumerate(sorted(scores.items(), key=lambda p: (-p[1], p[0])), 1):
        item = neurons[root]; a = ann.loc[root]
        assert item['cell_type'] == a.cell_type and item['side'] == a.side
        assert item['model_outgoing_sign'] == 1, 'A listed positive source must have positive modeled output'
        sources = []
        if a.known_nt_source: sources.append(str(a.known_nt_source))
        population_notes = []
        if a.known_nt == 'acetylcholine':
            population_notes.append('Marker annotation supports cholinergic identity. Comparable experimentally identified excitatory LN populations spike and can excite PNs mainly via electrical coupling. This does not establish that this exact root has those connections or fitted adaptation kinetics.')
        if a.cell_type == 'il3LN6':
            population_notes.append('Known GABA and cell-type inhibitory/compartment-local contrast evidence; prior exact-root sign candidate already failed recovery. Do not count a repeat as a new repair.')
        if not population_notes: population_notes.append('No exact-cell spiking/graded/adaptation fit established by the reviewed evidence. Low-confidence transmitter prediction alone does not supply physiology.')
        inventory.append({**item, 'pooled_listed_source_rank': rank,
                          'pooled_listed_accepted_increment_score': score,
                          'annotation_marker_sources': sources,
                          'population_evidence_notes': population_notes,
                          'exact_root_parameter_fit_available': False,
                          'exact_electrical_connection_map_available': False,
                          'qualified_intrinsic_adaptation_parameters': None})
    by_type = {}
    for item in inventory:
        by_type.setdefault(item['cell_type'], []).append(item['root_id'])
    result = {'status': 'complete', 'source_roots': len(inventory), 'cell_types': by_type,
              'inventory': inventory, 'listed_source_coverage': coverage,
              'cell_specific_adaptive_fits_qualified': 0, 'production_changes': 0,
              'scope': 'Annotation-to-root joins are exact; experimental driver/cell-population bridges and parameters remain qualified or unavailable.',
              'wall_seconds': time.monotonic()-started}
    protocol = json.loads((OUT/'protocol.json').read_text())
    assert all(file_sha(ROOT/k)==v for k,v in protocol['source_hashes'].items())
    atomic_json(OUT/'results.json', result)
    print('Inventoried', len(inventory), 'roots in', len(by_type), 'types; no exact-root adaptation fit qualified', flush=True)


if __name__ == '__main__': main()

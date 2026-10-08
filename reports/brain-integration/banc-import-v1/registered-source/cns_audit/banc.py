"""Import-only BANC audit. Never assigns neural weights or replaces a controller."""
from __future__ import annotations

import csv
import hashlib
import json
import resource
import shutil
import sys
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.feather as feather
import pyarrow.parquet as pq

from .download import RESERVE, atomic_json, hashes, verified_download

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/brain-integration/banc-import-v1'
CACHE = ROOT / 'data/banc-import-v1'
META = ROOT / 'data/anatomy-feasibility-v1/banc_888_meta.feather'
METRICS = META.with_name('banc_888_metrics.feather')
COLUMNS = ('id pre_x pre_y pre_z post_x post_y post_z ctr_x ctr_y ctr_z size '
           'pre_supervoxel_id pre_root_id post_supervoxel_id post_root_id').split()
SOURCES = [
    dict(name='synapses_v2_human_readable.csv.gz', file_id=13916483, bytes=12257440602,
         md5='e3679e7b9cec032ed1745c7a9dfd42d8'),
    dict(name='banc_888_edgelist_simple_v2.feather', file_id=13992792, bytes=305250378,
         md5='394406f8a9bdf093c895f95aff4f6c49'),
]
for source in SOURCES:
    source['url'] = f'https://dataverse.harvard.edu/api/access/datafile/{source["file_id"]}'
DEPENDENCY_VERSION = '1.5.6'


def utc():
    return datetime.now(timezone.utc).isoformat()


def duckdb_module():
    sys.path.insert(0, str(ROOT / '.runtime/banc-import-deps'))
    import duckdb
    if duckdb.__version__ != DEPENDENCY_VERSION:
        raise ValueError('Import dependency differs from registered version')
    return duckdb


def quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def code_identities():
    paths = ['cns_audit/__init__.py', 'cns_audit/download.py', 'cns_audit/banc.py',
             'scripts/import_banc.py', 'requirements-cns-audit.lock']
    return {p: hashes(ROOT/p)['sha256'] for p in paths}


def register():
    """Refuse to rewrite a protocol after looking at graph results."""
    path = REPORT / 'protocol.json'
    if path.exists():
        raise FileExistsError('Protocol already registered; use run/resume, not overwrite')
    meta_hash = hashes(META)
    metrics_hash = hashes(METRICS)
    if meta_hash['sha256'] != '819bbcff476e52702d6f8d8604ce1f12d1d7b11942281df2f49df2a73a6f15a5':
        raise ValueError('Annotation identity differs')
    if metrics_hash['sha256'] != '737a6c0f9b4d202da8d419fb5c539e2ddceaae2594f64952298fca29f678ce08':
        raise ValueError('Metrics identity differs')
    roster = ROOT/'reports/brain-integration/banc-feasibility-v1'
    protocol = dict(schema_version=1, registered_at=utc(), purpose='Anatomical import audit only',
        dataset=dict(doi='10.7910/DVN/7WTH1N', archive_version='3.0', materialization=888,
                     synapse_version=2, license='CC BY 4.0'), sources=SOURCES,
        annotations=dict(path=str(META.relative_to(ROOT)), identity=meta_hash,
                         metrics_path=str(METRICS.relative_to(ROOT)), metrics_identity=metrics_hash,
                         primary_key='banc_888_id', ordering='ascending exact unsigned integer ID'),
        csv=dict(columns=COLUMNS, header=False, skip_rows=0, compression='gzip', strict=True,
                 ids='canonical nonnegative uint64 decimal strings; no floating conversions',
                 coordinates='finite double; retained in raw archive, not geometry-qualified',
                 size='finite nonnegative synapse footprint; units not synaptic conductance'),
        eligibility=dict(site_size_minimum=5, pair_count_minimum=None,
            raw='Retain all records, including self connections, unknown/zero endpoints and size<5',
            pairs='Count size>=5 records by ordered root pair; preserve all self/zero/unknown pairs',
            simple_comparison='size>=5, non-self, both endpoints in archived banc_888_id set',
            duplicates='Any duplicate synapse ID blocks qualification; no arbitrary first-row selection'),
        membership=dict(annotated='Known super_class excluding glia, trachea and not_a_neuron',
                        unclassified='Missing super_class, retained separately',
                        excluded='Explicit glia/trachea/not_a_neuron, retained separately',
                        conflicts='root_888 differs from release primary ID, quarantined separately',
                        outside='Endpoint not in archived annotation set; includes 0 as unassigned',
                        proofread='Quality field only, never used as a membership shortcut'),
        independent_check=dict(reader='PyArrow streaming CSV; all raw rows; exact selected root pairs',
            rosters={p: hashes(roster/p)['sha256'] for p in ['selected-identities.json', 'front-leg-identities.json']},
            predicate='size>=5, both endpoints in union of exact BANC rosters; include autapses'),
        acceptance=['Source lengths and full MD5 match archive', 'All release IDs unique and metrics sets agree',
                    'Strict parse and exact identities; all retained sizes/coordinates finite',
                    'No duplicate synapse IDs', 'All eligible sites accounted in pair sums/partitions',
                    'Independent selected-route counts exactly equal imported counts',
                    'Simple-table reconciliation reported without changing filters to fit it'],
        stop_rules=['Malformed/corrupt input', 'Disk reserve crossing', 'Source/code/roster identity drift',
                    'Duplicate IDs or invalid values stop downstream graph qualification'],
        resources=dict(workers=1, threads=1, duckdb_memory_limit='2GB',
                       spill_limit='64GB computational scratch; not archive retention cap',
                       free_space_reserve_bytes=RESERVE, simulation_launched=False),
        model_ready=False, code_sha256=code_identities(),
        unchanged='Existing FlyWire model, checkpoints and all 39 acceptance requirements/statuses')
    atomic_json(path, protocol)
    atomic_json(REPORT/'protocol-identity.json', hashes(path))
    print(json.dumps({'registered': str(path), 'sha256': hashes(path)['sha256']}, flush=True))
    return protocol


def load_protocol():
    path = REPORT/'protocol.json'
    expected = json.loads((REPORT/'protocol-identity.json').read_text())
    if hashes(path) != expected:
        raise ValueError('Registered protocol drift')
    protocol = json.loads(path.read_text())
    if protocol['code_sha256'] != code_identities():
        raise ValueError('Registered source drift; preserve evidence and register an explicit amendment')
    for p, key in [(META, 'identity'), (METRICS, 'metrics_identity')]:
        if hashes(p) != protocol['annotations'][key]:
            raise ValueError('Registered annotation drift')
    for p, digest in protocol['independent_check']['rosters'].items():
        if hashes(ROOT/'reports/brain-integration/banc-feasibility-v1'/p)['sha256'] != digest:
            raise ValueError('Registered route roster drift')
    return protocol


def membership(table):
    rows = table.to_pylist()
    output, seen = [], set()
    for row in rows:
        value = row['banc_888_id']
        if not isinstance(value, str) or not value.isdecimal() or str(int(value)) != value or not 0 < int(value) < 2**64 or value in seen:
            raise ValueError('Invalid or duplicate release ID')
        seen.add(value)
        cls = row['super_class']
        kind = ('conflict' if row['root_888'] != value else
                'excluded_non_neural' if cls in {'glia', 'trachea', 'not_a_neuron'} else
                'unclassified' if cls is None else 'annotated_neuron_candidate')
        output.append(dict(root=int(value), membership=kind, cell_type=row.get('cell_type'),
                           super_class=cls, cell_class=row.get('cell_class'),
                           cell_sub_class=row.get('cell_sub_class'), side=row.get('side'),
                           proofread=row.get('proofread'), peripheral_target_type=row.get('peripheral_target_type')))
    output.sort(key=lambda r: r['root'])
    schema = pa.schema([('root', pa.uint64())] + [(k, pa.string()) for k in output[0] if k != 'root'])
    return pa.Table.from_pylist(output, schema=schema)


class Audit:
    def __init__(self, protocol):
        self.protocol = protocol
        CACHE.mkdir(parents=True, exist_ok=True)
        self.output = CACHE/'imported'
        self.output.mkdir(exist_ok=True)
        self.con = duckdb_module().connect()
        self.con.execute("SET threads=1; SET memory_limit='2GB'; SET preserve_insertion_order=false")
        spill = CACHE/'scratch'
        spill.mkdir(exist_ok=True)
        self.con.execute(f"SET temp_directory={quote(spill)}; SET max_temp_directory_size='64GB'")
        self.started = time.monotonic()
        self.stop = threading.Event()
        self.disk_blocked = False
        self.peak_rss = 0
        self.guard = threading.Thread(target=self.watch_resources, daemon=True)
        self.guard.start()

    def watch_resources(self):
        while not self.stop.wait(.5):
            self.peak_rss = max(self.peak_rss, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            # A 256MiB headroom permits an in-flight row group and metadata to close.
            if shutil.disk_usage(CACHE).free < RESERVE + 256*2**20:
                self.disk_blocked = True
                self.con.interrupt()

    def progress(self, stage, **kwargs):
        value = dict(at=utc(), stage=stage, elapsed_seconds=time.monotonic()-self.started,
                     free_disk_bytes=shutil.disk_usage(CACHE).free, **kwargs)
        atomic_json(REPORT/'progress.json', value)
        print(json.dumps(value), flush=True)

    def publish_parquet(self, name, query):
        path = self.output/name
        receipt = path.with_suffix('.receipt.json')
        if path.exists():
            if not receipt.exists() or hashes(path) != json.loads(receipt.read_text())['identity']:
                raise ValueError(f'Existing stage has no matching receipt: {path}')
            return path
        temp = path.with_name(path.name+'.part')
        if temp.exists():
            temp.rename(temp.with_name(temp.name+f'.interrupted-{time.time_ns()}'))
        self.progress('processing', artifact=name)
        self.con.execute(f'COPY ({query}) TO {quote(temp)} (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)')
        if self.disk_blocked:
            raise OSError('Paused at disk reserve; partial stage retained')
        identity = hashes(temp)
        temp.rename(path)
        atomic_json(receipt, dict(identity=identity, protocol_sha256=hashes(REPORT/'protocol.json')['sha256']))
        return path

    def view(self, name, path):
        self.con.execute(f'CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet({quote(path)})')

    def run(self):
        try:
            if (REPORT/'audit-results.json').exists():
                raise FileExistsError('Audit finalized; preserve evidence')
            downloads = {}
            for source in SOURCES:
                last = [0]
                def progress(offset, total):
                    now = time.monotonic()
                    if now-last[0] > 15 or offset == total:
                        self.progress('download', source=source['name'], completed_bytes=offset, total_bytes=total)
                        last[0] = now
                self.progress('source_verification', source=source['name'])
                downloads[source['name']] = verified_download(source, CACHE/source['name'], progress=progress)
            atomic_json(REPORT/'source-receipts.json', downloads)
            meta = feather.read_table(META)
            mem = membership(meta)
            metric_ids = feather.read_table(METRICS, columns=['banc_888_id']).column(0).to_pylist()
            if set(metric_ids) != set(meta.column('banc_888_id').to_pylist()) or len(set(metric_ids)) != len(metric_ids):
                raise ValueError('Metrics/release-key disagreement')
            self.con.register('membership_input', mem)
            mp = self.publish_parquet('membership.parquet', 'SELECT * FROM membership_input ORDER BY root')
            self.view('membership', mp)
            columns = '{'+', '.join(f'{quote(k)}: {quote("VARCHAR")}' for k in COLUMNS)+'}'
            reader = (f'read_csv({quote(CACHE/SOURCES[0]["name"])}, columns={columns}, header=false, '
                      "auto_detect=false, delim=',', quote='', escape='', compression='gzip', parallel=false, strict_mode=true, nullstr='')")
            ids = ['id', 'pre_root_id', 'post_root_id', 'pre_supervoxel_id', 'post_supervoxel_id']
            invalid = [f"NOT coalesce(regexp_full_match({k}, '(0|[1-9][0-9]*)') AND try_cast({k} AS UBIGINT) IS NOT NULL, false)" for k in ids]
            invalid += [f'NOT coalesce(isfinite(try_cast({k} AS DOUBLE)), false)' for k in COLUMNS[1:11]]
            invalid += ['try_cast(size AS DOUBLE)<0']
            query = (f'SELECT try_cast(id AS UBIGINT) AS id, try_cast(pre_root_id AS UBIGINT) AS pre, '
                     f'try_cast(post_root_id AS UBIGINT) AS post, try_cast(size AS DOUBLE) AS size, '
                     f'({" OR ".join(invalid)}) AS invalid FROM {reader}')
            raw = self.publish_parquet('raw-sites.parquet', query)
            self.view('raw', raw)
            self.progress('integrity_and_duplicate_audit')
            keys = ['rows', 'unique_synapse_ids', 'invalid_rows', 'eligible_sites', 'eligible_self_sites', 'all_self_sites']
            values = self.con.execute('SELECT count(*), count(DISTINCT id), count(*) FILTER(WHERE invalid), '
                'count(*) FILTER(WHERE size>=5), count(*) FILTER(WHERE size>=5 AND pre=post), count(*) FILTER(WHERE pre=post) FROM raw').fetchone()
            stats = dict(zip(keys, values))
            atomic_json(REPORT/'raw-integrity.json', stats)
            if stats['invalid_rows'] or stats['unique_synapse_ids'] != stats['rows']:
                raise ValueError('Invalid or duplicate raw sites: qualification stopped; evidence retained')
            pairs = self.publish_parquet('eligible-pairs.parquet',
                 'SELECT pre, post, count(*) AS count FROM raw WHERE size>=5 GROUP BY pre,post')
            self.view('pairs', pairs)
            partition = self.con.execute("SELECT coalesce(a.membership,'outside_annotations') AS pre_class, "
                 "coalesce(b.membership,'outside_annotations') AS post_class, count(*) AS pairs, sum(p.count)::UBIGINT AS sites "
                 'FROM pairs p LEFT JOIN membership a ON a.root=p.pre LEFT JOIN membership b ON b.root=p.post GROUP BY 1,2 ORDER BY 1,2').fetchall()
            partitions = [dict(zip(['pre','post','pairs','sites'], r)) for r in partition]
            total = sum(r['sites'] for r in partitions)
            if total != stats['eligible_sites']:
                raise ValueError('Eligible sites not accounted in partition sums')
            stats['eligible_pairs'] = sum(r['pairs'] for r in partitions)
            self.publish_parquet('outside-endpoints.parquet',
                'SELECT root, count(*) AS pair_incidence, sum(count)::UBIGINT AS site_incidence FROM '
                '(SELECT pre AS root,count FROM pairs UNION ALL SELECT post AS root,count FROM pairs) e '
                'LEFT JOIN membership m USING(root) WHERE m.root IS NULL GROUP BY root')
            self.progress('simple_table_import')
            simple_path = self.output/'simple-comparison.parquet'
            if not simple_path.exists():
                temp = simple_path.with_name(simple_path.name+'.part')
                if temp.exists(): temp.rename(temp.with_name(temp.name+f'.interrupted-{time.time_ns()}'))
                reader = pa.ipc.open_file(str(CACHE/SOURCES[1]['name']))
                with pq.ParquetWriter(temp, pa.schema([('pre',pa.uint64()),('post',pa.uint64()),('count',pa.int64())]), compression='zstd') as writer:
                    for i in range(reader.num_record_batches):
                        batch = reader.get_batch(i)
                        values = [pc.cast(batch.column(batch.schema.get_field_index(k)), t, safe=True) for k,t in [('pre',pa.uint64()),('post',pa.uint64()),('count',pa.int64())]]
                        writer.write_table(pa.Table.from_arrays(values,names=['pre','post','count']))
                        if self.disk_blocked: raise OSError('Paused at disk reserve')
                identity = hashes(temp); temp.rename(simple_path)
                atomic_json(simple_path.with_suffix('.receipt.json'), dict(identity=identity, protocol_sha256=hashes(REPORT/'protocol.json')['sha256']))
            else:
                receipt = simple_path.with_suffix('.receipt.json')
                if not receipt.exists() or hashes(simple_path) != json.loads(receipt.read_text())['identity']:
                    raise ValueError('Unverified simple-table stage')
            self.view('simple', simple_path)
            simple_stats = self.con.execute('SELECT count(*), count(*) FILTER(WHERE count IS NULL OR pre IS NULL OR post IS NULL OR count<=0 OR pre=post OR pre=0 OR post=0), count(DISTINCT (pre,post)), sum(count)::UBIGINT FROM simple').fetchone()
            if simple_stats[1] or simple_stats[0] != simple_stats[2]:
                raise ValueError('Invalid/duplicate simplified graph records')
            self.con.execute('CREATE VIEW expected AS SELECT p.* FROM pairs p JOIN membership a ON a.root=p.pre JOIN membership b ON b.root=p.post WHERE p.pre<>p.post')
            difference = ('SELECT coalesce(e.pre,s.pre) AS pre, coalesce(e.post,s.post) AS post, '
                          'e.count AS raw_count,s.count AS simple_count FROM expected e FULL JOIN simple s USING(pre,post) '
                          'WHERE e.count IS DISTINCT FROM s.count')
            diff_path = self.publish_parquet('simple-differences.parquet', difference)
            self.view('differences', diff_path)
            diff_stats = dict(zip(['different_pairs','raw_only','simple_only','shared_count_mismatch'], self.con.execute(
                'SELECT count(*),count(*) FILTER(WHERE simple_count IS NULL),count(*) FILTER(WHERE raw_count IS NULL),count(*) FILTER(WHERE raw_count IS NOT NULL AND simple_count IS NOT NULL) FROM differences').fetchone()))
            comparison = dict(simple_rows=simple_stats[0], simple_sites=simple_stats[3], **diff_stats,
                              exact_match=diff_stats['different_pairs']==0,
                              filters_changed_to_fit=False)
            self.progress('independent_selected_route_scan')
            independent = self.independent_routes()
            atomic_json(REPORT/'independent-routes.json', independent)
            if independent['raw_rows'] != stats['rows'] or not independent['exact_match']:
                raise ValueError('Independent raw reader/count disagreement; qualification stopped')
            results = dict(schema_version=1, completed_at=utc(), model_ready=False,
                qualification='Anatomy audit only; no neural equations/signs/controller chosen',
                source_receipts=downloads, raw=stats, membership_rows=mem.num_rows,
                membership_counts=dict(Counter(mem.column('membership').to_pylist())),
                partitions=partitions, simple_comparison=comparison, independent_routes=independent,
                passed_integrity=independent['exact_match'],
                resources=dict(elapsed_seconds=time.monotonic()-self.started,
                    peak_process_rss_bytes=max(self.peak_rss,resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                    imported_file_bytes=sum(p.stat().st_size for p in self.output.glob('*.parquet')),
                    free_disk_bytes=shutil.disk_usage(CACHE).free, workers=1),
                omissions='Raw archive retained; all size>=5 self/unknown pairs retained; no anatomical neurons assigned electrical dynamics')
            atomic_json(REPORT/'audit-results.json', results)
            self.progress('complete', model_ready=False)
            return results
        except BaseException as exc:
            record = dict(at=utc(), error=f'{type(exc).__name__}: {exc}', disk_blocked=self.disk_blocked,
                          elapsed_seconds=time.monotonic()-self.started, evidence_preserved=True)
            try:
                atomic_json(REPORT/f'interruption-{time.time_ns()}.json',record)
                self.progress('interrupted', error=record['error'])
            except OSError: pass
            raise
        finally:
            self.stop.set(); self.guard.join(timeout=2); self.con.close()

    def independent_routes(self):
        base = ROOT/'reports/brain-integration/banc-feasibility-v1'
        rosters = [json.loads((base/p).read_text()) for p in self.protocol['independent_check']['rosters']]
        # The named roster may group rows; front-leg roster is flat.
        def collect(value):
            if isinstance(value,dict):
                if value.get('banc_888_id'): yield value['banc_888_id']
                for k,v in value.items():
                    if k != 'banc_888_id': yield from collect(v)
            elif isinstance(value,list):
                for v in value: yield from collect(v)
        selected = sorted(set(v for roster in rosters for v in collect(roster)), key=int)
        selected_array = pa.array(selected, type=pa.string())
        options = pacsv.ConvertOptions(column_types={k:pa.string() for k in COLUMNS},
            include_columns=['id','pre_root_id','post_root_id','size'], strings_can_be_null=False)
        reader = pacsv.open_csv(CACHE/SOURCES[0]['name'],
            read_options=pacsv.ReadOptions(column_names=COLUMNS,use_threads=False,block_size=16*2**20),
            parse_options=pacsv.ParseOptions(delimiter=',',quote_char=False,escape_char=False), convert_options=options)
        counter, rows, batches = Counter(), 0, 0
        for batch in reader:
            rows += batch.num_rows; batches += 1
            mask = pc.and_(pc.is_in(batch.column('pre_root_id'),value_set=selected_array),
                           pc.is_in(batch.column('post_root_id'),value_set=selected_array))
            subset = batch.filter(mask).to_pylist()
            for row in subset:
                if float(row['size']) >= 5:
                    counter[(int(row['pre_root_id']),int(row['post_root_id']))] += 1
            if self.disk_blocked: raise OSError('Paused at disk reserve')
            if batches % 128 == 0:
                self.progress('independent_selected_route_scan', raw_rows=rows, selected_pairs=len(counter))
        self.con.register('selected', pa.table({'root':pa.array([int(v) for v in selected],type=pa.uint64())}))
        imported = {(a,b):c for a,b,c in self.con.execute('SELECT p.pre,p.post,p.count FROM pairs p JOIN selected a ON a.root=p.pre JOIN selected b ON b.root=p.post').fetchall()}
        mismatch = sorted(k for k in set(counter)|set(imported) if counter[k] != imported.get(k,0))
        examples = [dict(pre=str(a),post=str(b),independent=counter[(a,b)],imported=imported.get((a,b),0)) for a,b in mismatch[:100]]
        atomic_json(REPORT/'selected-route-counts.json', [dict(pre=str(a),post=str(b),count=c) for (a,b),c in sorted(counter.items())])
        return dict(reader='Independent PyArrow raw gzip/CSV scan; all source rows', raw_rows=rows,
                    selected_roots=len(selected), pairs=len(counter), sites=sum(counter.values()),
                    mismatch_pairs=len(mismatch), mismatch_examples=examples, exact_match=not mismatch)

# Separate BANC anatomy audit

This importer validates anatomical sources. It does not start a brain, choose neural signs, transfer FlyWire weights, or change the arena.

**Current outcome:** original v1 stopped on its documented no-self expectation. A separately registered [source attribution](../banc-source-attribution-v1/RESULTS.md) completed and preserves that failure. Rerunning original v1 will repeat its failed gate; do not change its protocol to make it pass.

Run from `/Users/carsonhicks/FlyGarden`, using the existing Python 3.12 environment. The isolated dependency is pinned by wheel hash:

```sh
/opt/homebrew/bin/uv pip install --python .venv-next/bin/python --target .runtime/banc-import-deps --no-deps --require-hashes -r requirements-cns-audit.lock
.venv-next/bin/python scripts/import_banc.py run
```

That original command reproduces the import and failed source assumption. The separate continuation is `.venv-next/bin/python scripts/attribute_banc_sources.py run`; its protocol is also already registered. It reuses verified imported stages. A finalized continuation refuses rerunning over its results. `scripts/report_banc_import.py` generates both reports from completed source-attribution evidence and also refuses overwriting them.

The v1 protocol is already registered. Do not register over it. Run resumes verified source downloads and completed imported stages. A second simultaneous worker is refused by the source lock. Partial source chunks are checked before reuse; uncommitted bytes are preserved separately. A completed audit refuses overwriting its evidence. Source or protocol changes require a recorded amendment or a separate registered version.

Read `progress.json` for the current stage. Download progress reports received compressed bytes. Processing, duplicate validation, reconciliation and an independent second raw scan still follow the download; byte progress is not overall completion.

Inputs remain under `data/banc-import-v1`, with derived Parquet files in `imported`. The raw archive retains every record, including small sites, self-connections and unknown endpoints. The audited pair table uses the declared v2 size threshold of 5 and no pair-count cutoff. Every inclusion and membership partition is reported. No automatic deletion or archive cap is imposed. Free space is guarded with a 2 GiB reserve and processing headroom.

Inspect original `raw-integrity.json`, `simple-table-diagnostic.json`, and the preserved interruption. The completed continuation's `results.json`, `independent-routes.json`, and difference artifacts compare both original and inclusive source contracts. Integrity does not qualify physiology or behavior. The complete raw collection is not a runnable neural controller.

Large datasets are local and excluded from GitHub. A fresh clone must first retrieve the pinned BANC meta/metrics files listed in the original protocol and existing feasibility receipts, and recreate the cached source/import stages. Existing receipt files do not substitute for those local bytes. The supplied commands describe the verified local workspace, not a one-command fresh-machine installation.

An interrupted calculation preserves its partial artifact. On retry it is renamed for inspection; completed stages require matching receipts. This preserves evidence but may consume additional disk space. No full anatomical geometry, MaleCNS graph, synaptic-effect model or new body controller is imported by this command.

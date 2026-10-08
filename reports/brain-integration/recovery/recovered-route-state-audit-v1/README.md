# Recovered MBON32 route and state audit, version 1

Registered retrospective analysis of eight direct-drive and 28 odor recordings. No new full-network simulations, controller fitting, learning or qualification are authorized by this protocol. Every earlier acceptance gate and failed result remains intact.

First predict all eight intact DNa02 spike trains and saved voltage/g endpoints from their pre-gate source events. Stop if any prediction fails. Only then attribute signed delivery and run 16 fixed-source, two-recipient edge-removal diagnostics. These isolated diagnostics recompute threshold/reset/refractory gates; their sources cannot respond to the altered connection.

Inventory every outgoing record from the two exact MBON32 roots. The imported graph has 561 outgoing records, 4,375 anatomical sites, 512 recipients and 156 anatomical two-hop intermediates into DNa02. These counts describe connectivity, not an established functional pathway. The two direct links are inhibitory: left MBON32 -> right DNa02 has 40 represented sites; right MBON32 -> left DNa02 has 10. Both exact LAL171/LAL074 type labels remain unavailable; compound annotations are listed without selecting a substitute root.

Use the prior frozen population definitions, phase windows and root ordering. Compare operating-context engagement descriptively: the two archives differ in seeds, odor context and MBON refractory policy. Missing relay states remain unavailable. Equal average firing rates do not imply equal spike timing.

Local reproduction, with all omitted upstream inputs and parent recordings restored at their hashed paths:

```sh
.venv-next/bin/python scripts/trace_recovered_route_state.py analyze
.venv-next/bin/python scripts/audit_recovered_route_state.py
.venv-next/bin/python scripts/plot_recovered_route_state.py
```

The runner refuses to overwrite a completed or interrupted attempt. Inputs, profiles and native replay arrays remain local; public summaries and source cannot replace them for raw-data verification. Recordings and checkpoints are never deleted.

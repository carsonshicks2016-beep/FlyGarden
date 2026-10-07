# Body/decoder calibration measurement

Twenty-two three-second calibration trials completed at 25-ms command intervals. All saved commands were independently reconstructed; all 90 poses per trial match the 30-Hz sampling target within a gait step. All trial chunk and latest checkpoint hashes verify. Every trial had finite sampled positions and no flipped samples.

These are controlled body commands and artificial injected rate readouts, not full-brain trials or validated navigation. The decoder, brain and gait gains were not changed. Seeds 9101/9102 are calibration-only and must not become held-out acceptance seeds.

| Seed | Command case | Final xy displacement (mm) | Heading change (rad) | Flipped samples |
|---|---|---|---|---|
| 9101 | direct-0 | 0.046 | 0.0025 | 0 |
| 9101 | direct-0.1 | 1.468 | 0.0060 | 0 |
| 9101 | direct-0.2 | 4.661 | 0.0027 | 0 |
| 9101 | direct-0.4 | 10.956 | 0.0007 | 0 |
| 9101 | direct-0.65 | 18.726 | -0.0090 | 0 |
| 9101 | direct-0.9 | 25.653 | 0.0027 | 0 |
| 9101 | direct-left | 11.840 | 1.9617 | 0 |
| 9101 | direct-right | 11.734 | -1.9858 | 0 |
| 9101 | decoder-forward | 16.943 | 0.0015 | 0 |
| 9101 | decoder-left | 11.009 | 3.1356 | 0 |
| 9101 | decoder-right | 10.929 | -3.1206 | 0 |
| 9102 | direct-0 | 0.064 | -0.0009 | 0 |
| 9102 | direct-0.1 | 1.562 | -0.0010 | 0 |
| 9102 | direct-0.2 | 4.810 | 0.0020 | 0 |
| 9102 | direct-0.4 | 11.053 | -0.0009 | 0 |
| 9102 | direct-0.65 | 18.869 | 0.0142 | 0 |
| 9102 | direct-0.9 | 25.739 | 0.0200 | 0 |
| 9102 | direct-left | 11.767 | 2.0214 | 0 |
| 9102 | direct-right | 11.798 | -1.9959 | 0 |
| 9102 | decoder-forward | 17.061 | 0.0215 | 0 |
| 9102 | decoder-left | 10.912 | 3.1614 | 0 |
| 9102 | decoder-right | 10.835 | -3.1345 | 0 |

The physical body and fixed candidate decoder can produce substantial forward motion and mirrored turns at these tested command/rate levels. The weak movement in Step 8 is therefore not explained by an inability of this body to move when given adequate commands. This does not establish which sensory/model/readout change is justified.

The field named `contacts` in the pinned Body adapter contains the supplied controller's **stumbling contact forces**, not complete foot-ground loads. Its zero value on these open-ground trials must not be interpreted as absent ground contact or used to claim slip-free walking. Raw poses and contact fields are retained. Full contact/stance/slip observability and ten held-out 60-second trials remain required.

Physics state and decoder smoothing state are retained at each committed one-second chunk; AC-power interruption can resume at that boundary. Unit tests verify resumed command/record sequences and preserved original chunks; fresh-process native physical continuation is a separate pending acceptance check. The previous Step 7 native continuation result remains separately archived.

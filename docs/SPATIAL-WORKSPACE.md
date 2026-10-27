# Pitch-first match review

The report now starts with spatial evidence rather than explanatory paragraphs. The public
fixtures and engine outputs are unchanged. All coordinates and event IDs come from the existing
fictional records; none are fitted, mirrored, jittered or filled in.

## Try it

1. Select Atlas United–Riverside and run analysis.
2. Toggle Shots / Passes. A filled shot circle indicates a recorded Goal; hollow circles indicate
   other recorded Shots. Dashed passes have an explicit outcome field (including unresolved null).
3. Choose **View sequence** on a review priority. The whole native-membership context appears;
   this is an ordered source membership, not proof of uninterrupted ball control or a tactical pattern.
4. Step through actions with Previous / Next or the action buttons. The active source action is
   highlighted without movement interpolation. Its native endpoints and original ID are visible.
5. Open Original JSON. The exact selected ID is selected in the evidence ledger.
6. Compare both teams on identical coordinate scales. Apply a team filter and observe the other
   team's explicit exclusion message. Apply period filters through the existing shared control.
7. Select Beacon–Westhaven second half. Shots abstain; the Passes layer remains usable.

Coincident markers overlap deliberately. Counts remain visible and every event remains available
in Original evidence; no jitter invents an alternative location. Missing/non-numeric/out-of-range
points are counted and omitted. Event locations are not player positions. No physical attacking
direction, tracking, off-ball motion, intention or player ability is inferred. Shot weights remain
illustrative, uncalibrated values. The inherited review ordering has no independently established
football usefulness.

## Design decisions

The Stars audit informed a simpler hierarchy and progressive disclosure. References inspected:
[Impeccable](https://github.com/pbakaus/impeccable),
[Taste Skill](https://github.com/Leonxlnx/taste-skill),
[Diagram Design](https://github.com/cathrynlavery/diagram-design), and
[mplsoccer](https://github.com/andrewRowlinson/mplsoccer).
No third-party skill launcher was installed or executed; no runtime framework, font service,
component source or new data acquisition was added. SVG geometry is implemented locally.

The hero compacts after analysis so the working viewport gives priority to the pitch. On mobile,
the pitch precedes review priorities. Detailed interpretations, counterevidence and methods use
progressive disclosure. Team colors are consistent throughout the pitch and comparison charts.
SVG markers support keyboard activation; the action list offers larger touch targets.

## Validation

- 16 Python tests pass, including deployment contracts and 15 frozen original-engine hashes.
- 3 Node tests check coordinate boundaries, endpoint missingness, preservation and no mirroring.
- Chromium checks marker keyboard selection, source ID/JSON agreement, exact SVG endpoints,
  sequence stepping, filter exclusions, empty shot / populated pass layers, stale responses,
  catalog failure and layout widths 390, 768, 1024 and 1440 pixels. No page errors.
- Desktop/mobile screenshots are synthetic-only captures of the running application.
- The owner confirmed that the previous production version lists matches and generates a report.
  This UI revision's production browser acceptance remains distinct from local checks and CI.

## Local performance impact

Run:

```bash
uv run --frozen python tests/performance_check.py --parent 26a91dbc7db74c16ecd335d7f5faf6ca8566b92b
```

The script runs 10 paired repetitions in alternating order, each in a fresh Chromium context,
using two local servers, demo-1 and the same viewport. Page readiness ends at catalog/button
availability; analysis timing ends at the browser DOM completion status update. The browser
process and servers are shared. **This is not server cold-start or production network timing.**

| Measurement | Parent median (range), ms | Candidate median (range), ms |
|---|---:|---:|
| Page ready | 233.15 (202.1–485.6) | 280.15 (190.8–339.8) |
| Analysis to DOM status | 36.2 (16.8–51.5) | 48.25 (18.1–70.6) |

Uncompressed public assets: 16,611 → 34,149 bytes. All 20 samples and standard deviations are
retained in [the measurement artifact](performance/spatial-performance.json). Small local samples,
scheduling variability and simple fictional fixtures do not support a production speedup claim.
Independent usefulness and public production latency remain unmeasured.

The earlier run is also retained in [the initial artifact](performance/spatial-performance-initial.json).
It favored the candidate for analysis timing; the repeated run above showed the opposite.
This direction change is evidence of measurement variability, not reliable improvement.
The final artifact includes candidate asset hashes. No production cold-start claim is made.

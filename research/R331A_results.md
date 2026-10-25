# R331-A — audit scanner H1→H4 vs canonical M5→H4

**Verdict: INCOMPLETE**

- R330 cache run: 40166799441; cutoff: 2026-10-23T20:00:00+00:00.
- Evaluation labels: NY timestamp >= 2024-01-01 00:00; completed H4 bars only.
- Signal rule unchanged: close > max(high of previous 55 H4 bars); no position simulation, tuning, or rule changes.
- A uses scan.fetch_h1() and scan.to_h4() imported unchanged from scan.py; an in-memory historical position anchor extends H1 download for warm-up without touching state.json.
- B uses the unchanged R191 canonical script copied from R330 and the exact R330 M5 cache, clipped only at the locked cutoff before canonical resampling.
- OHLC differences are computed only on identical UTC instants / NY labels present and completed in both series; label-only bars are counted separately.

**Error:** AttributeError: 'numpy.ndarray' object has no attribute 'to_numpy'

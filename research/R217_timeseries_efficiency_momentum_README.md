# R217 branch mirror

This branch records the R217 time-series momentum with directional-efficiency filter experiment. The exact local execution engine, all ten discovery trade ledgers, selected forward/OOS ledgers, source hashes, and audit outputs are in the linked local execution bundle. The Python file here is a compact reproduction mirror of the same registered rules, not byte-identical to the full local runner.

- Decision: REJECT_FORWARD_GATE_FAILED.
- Selected on discovery only: Japan 225.
- Forward PF: 0.9488 @ modeled 1 bp; 0.8966 @ modeled 2 bps.
- OOS PF: 0.9409 @ modeled 1 bp; 0.9046 @ modeled 2 bps.
- All 15 full local-run checks passed, including actual truncation-prefix checks per instrument.

The engine uses raw H1 BID OHLC, no standard indicators or forward-fill. Signal thresholds are 24-hour absolute return >= 0.25% and directional efficiency >= 0.35, evaluated only at four-hour UTC closes. Entry at the next H1 open, scheduled exit after four hours with delay to first later non-flat source open when needed. Costs of 1/2 bps are modeled stresses only.

# R205 — Cross-Index Breadth Confirmation

**Verdict: REJECT.** Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38160487617

## Preregistered hypothesis

Keep the locked long-only H4 55-bar breakout, 27-bar stop and 2R target. Permit a signal only when at least 4 of at least 8 indices have a simultaneous breakout at the same completed UTC H4 close. Entry is the first non-flat M5 bar at or after signal close + 5 minutes and before the next H4 close. Exits use M5 BID OHLC, stop-first handling and gap stops at open. Modeled costs are 1 and 2 bps round-trip; these are not verified broker costs.

## Data and validation

- All ten cached Dukascopy BID H1/M5 snapshot pairs validated.
- Coverage starts in 2016 for nine instruments; Small Cap 2000 starts 2018-08-08.
- Common OOS cutoff: 2026-10-09 20:00 UTC.
- Causal/truncation gate passed for all ten instruments, checking each completed H4 prefix.
- Boundary-test and Python compilation jobs passed.
- No standard indicators; the filter uses raw price breakout states only.

## Full manual-entry ledger

All PF values are based on the indicated 1bp/2bp modeled round-trip cost.

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|
| FTSE 100 | 18 | 0.5641 | 0.5594 | 16 | 1.5415 | 1.5276 |
| US Small Cap 2000 | 19 | 1.7912 | 1.7825 | 29 | 1.0487 | 1.0448 |
| Japan 200+ | 24 | 1.4199 | 1.4114 | 30 | 1.5223 | 1.5152 |
| Australia 200 | 26 | 0.8798 | 0.8713 | 24 | 0.9855 | 0.9781 |
| EU Stocks 50 | 29 | 0.8933 | 0.8866 | 32 | 1.3585 | 1.3506 |
| France 40 | 29 | 1.2047 | 1.1956 | 39 | 0.9884 | 0.9818 |
| Dow Jones | 31 | 1.4320 | 1.4197 | 22 | 1.6252 | 1.6160 |
| USA 500 / S&P 500 | 41 | 1.8875 | 1.8704 | 34 | 1.3898 | 1.3813 |
| USA 100 Tech / Nasdaq 100 | 41 | 1.8944 | 1.8842 | 30 | 1.1534 | 1.1489 |
| Germany 40 / DAX | 44 | 0.5839 | 0.5796 | 30 | 1.5197 | 1.5101 |

## Locked selection and verdict

Selection used discovery only: among assets with at least 10 discovery closes and discovery PF >= 1.00 at 2 bps, choose the fewest discovery closes. This selected US Small Cap 2000 (19 closes, discovery PF 1.7825 at 2 bps). The forward test produced 29 closed trades, PF 1.0487 at 1 bps and 1.0448 at 2 bps; the worst eligible 2022–2025 entry-year cohort PF at 1 bps was 0.5698. It fails the minimum 30-trade gate, both PF >= 1.15 gates and the worst-cohort >= 1.00 gate. Verdict: REJECT.

Although other instruments printed stronger forward PFs, they cannot replace the locked selection after forward results are observed. Doing so would introduce forward-selection bias.

This experiment does not establish a live edge. Broker commission, real-time spread variation and live slippage remain unverified. The artifact `R205-breadth-confirmation-audit` contains machine-readable `meta.json`, per-instrument ledger, annual/cohort tables and trades.

# R251 — Final Binary Verdict

**Verdict: GAGAL.** The locked cross-pair consensus / EURUSD lag-catch-up rule fails out-of-sample and cost-adjusted expectancy gates.

Run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38521094743

## Frozen rule
- Signal uses completed H1 close-to-close returns over the previous 3 hours in GBPUSD, AUDUSD, and inverse USDCHF.
- All three peer directions must agree; their median absolute return must be at least 0.05%.
- EURUSD must lag the peer move: its signed move must be no more than 50% of the peer median and must not counter-move by more than 25%.
- Entry is the next exact shared H1 open; exit is the exact open 4 hours later. Overlapping trades are skipped.
- Long execution is ask-open to bid-open; short execution is bid-open to ask-open. Extra cost stresses are added on top of those observed quote-side costs.

## Data integrity
Four FX H1 streams span 2017-01-01 to 2026-10-13. EURUSD has both bid and ask streams; GBPUSD, AUDUSD, and USDCHF use bid bars for signals. All five streams have 85,170 rows each, zero duplicate timestamps, zero invalid OHLC rows, and zero off-grid hourly timestamps. The shared timestamp sample has 85,170 rows; no missing bars were synthesized or forward-filled.

## Performance

| Period | Trades | PF, observed bid/ask only | PF +0.5 pip | PF +1 pip | PF +2 pip |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2021 | 1,797 | 0.956 | 0.890 | 0.829 | 0.719 |
| Forward 2022–2025 | 1,499 | 1.059 | 0.991 | 0.927 | 0.813 |
| OOS 2026 through Oct 13 | 281 | 0.849 | 0.780 | 0.716 | 0.604 |

Forward expectancy was +0.430 pip/trade with observed bid/ask costs and no extra markup, but turns negative after +0.5 pip extra cost. At +1 pip, forward net was -855.1 pips and mean was -0.570 pip/trade. OOS mean at +1 pip was -1.962 pip/trade.

At +1 pip, only 2022 had annual PF slightly above 1.0 (1.105); all other forward years failed the annual PF>=1 gate. The 4-week block bootstrap on forward +1-pip trade returns estimated only 14.45% probability of positive mean; 95% interval for mean was -1.644 to +0.487 pips/trade.

## Acceptance gates
- Discovery >=100 trades: PASS
- Discovery PF >=1.05 at +1 pip: FAIL (0.829)
- Forward >=100 trades: PASS
- Forward PF >=1.10 at +1 pip: FAIL (0.927)
- Forward PF >=1.05 at +2 pip: FAIL (0.813)
- Each forward year with at least 20 trades has PF >=1 at +1 pip: FAIL
- Four-week block bootstrap supports positive expectancy at 95%: FAIL
- OOS >=30 trades: PASS
- OOS PF >=1.00 at +1 pip: FAIL (0.716)

**Final status: GAGAL.** Trade frequency was high (7.18 trades/week forward), so the failure is not caused by insufficient opportunities. The returns simply did not survive the locked forward, annual-stability, OOS, and cost requirements. Do not tune this exact signal to rescue it after seeing the forward/OOS outcomes.

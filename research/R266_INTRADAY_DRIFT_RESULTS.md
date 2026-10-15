# R266 U.S. Index Afternoon Continuation — Results

Date: 2026-10-16  
**Verdict: FAILED. No tuning; 2026 outcomes were not inspected.**

## Data and locked rules

- Inputs: GitHub-sourced BID-only M5 snapshots for USA500 and USATECH; the calculations were run locally in Python. Exact source file SHA-256 values are recorded in the JSON.
- Use complete New York RTH sessions only (78 five-minute bars from 09:30–15:55); no synthetic bars. A session qualifies when absolute 09:30 open to 12:55 bar-close return is at least 0.5× the median prior-20-session full-day range in bps, excluding the current session.
- Follow the morning direction. Enter at 13:00 ET (ideal) or 13:05 ET (+5-minute delay) and exit at the 15:55 bar close. Maximum one trade per symbol/session; no stops or overnight holding.
- Fixed cost sensitivity: +2/+4/+6 bps per trade. BID-only data means these are stress assumptions—not measured spread or verified live execution costs.
- Preregistered before test: [R266 preregistration](R266_INTRADAY_DRIFT_PREREGISTRATION.md). Evaluated splits are discovery 2016–2020, validation 2021, forward 2022–2025. The 2026 results were excluded from signal-performance calculations and not inspected.

## Combined results at +4 bps

| Entry mode | Split | Trades | PF | Net bps |
|---|---|---:|---:|---:|
| 13:00 ideal | Discovery 2016–2020 | 836 | 0.934 | -1213.5 |
| 13:00 ideal | Validation 2021 | 196 | 0.557 | -1846.1 |
| 13:00 ideal | Forward 2022–2025 | 725 | 1.145 | +2343.1 |
| 13:05 delayed | Discovery 2016–2020 | 836 | 0.887 | -2174.4 |
| 13:05 delayed | Validation 2021 | 196 | 0.599 | -1608.5 |
| 13:05 delayed | Forward 2022–2025 | 725 | 1.102 | +1638.3 |

## Forward annual stability at +4 bps

| Entry mode | Year | Trades | PF | Net bps |
|---|---:|---:|---:|---:|
| 13:00 ideal | 2022 | 174 | 1.424 | +2214.7 |
| 13:00 ideal | 2023 | 169 | 0.776 | -793.1 |
| 13:00 ideal | 2024 | 188 | 0.657 | -1464.7 |
| 13:00 ideal | 2025 | 194 | 1.760 | +2386.2 |
| 13:05 delayed | 2022 | 174 | 1.302 | +1657.0 |
| 13:05 delayed | 2023 | 169 | 0.829 | -555.1 |
| 13:05 delayed | 2024 | 188 | 0.635 | -1524.7 |
| 13:05 delayed | 2025 | 194 | 1.648 | +2061.2 |

## Forward by instrument at +4 bps (ideal entry)

| Instrument | Trades | PF | Net bps |
|---|---:|---:|---:|
| USA500 | 352 | 1.077 | +567.1 |
| USATECH | 373 | 1.203 | +1775.9 |

## Bootstrap and gate decision

Four-week circular block bootstrap over all 209 forward calendar weeks, including zero-trade weeks, 10,000 replications, primary cost +4 bps:

| Entry mode | Mean weekly net bps | Probability mean positive | 95% interval (bps/week) |
|---|---:|---:|---:|
| 13:00 ideal | +11.21 | 74.6% | [-17.89, +45.76] |
| 13:05 delayed | +7.84 | 67.6% | [-20.35, +41.48] |

The locked gates failed for both entry modes.

### Ideal
- FAIL — discovery net positive PF at least 1.10
- FAIL — validation net positive PF at least 1.10
- PASS — forward has at least 100 trades, positive net and PF at least 1.10
- FAIL — all forward years PF at least 1.00
- PASS — each instrument forward PF at least 1.00
- FAIL — entry-mode bootstrap 95% CI lower bound above zero
- FAIL — both entry modes have bootstrap lower bounds above zero

### Five-minute delay
- FAIL — discovery net positive PF at least 1.10
- FAIL — validation net positive PF at least 1.10
- PASS — forward has at least 100 trades, positive net and PF at least 1.10
- FAIL — all forward years PF at least 1.00
- PASS — each instrument forward PF at least 1.00
- FAIL — entry-mode bootstrap 95% CI lower bound above zero
- PASS — delayed forward net positive and PF at least 1.10
- FAIL — both entry modes have bootstrap lower bounds above zero

Discovery lost money at +4 bps for both modes (PF 0.934 ideal, 0.887 delayed); 2021 validation was much worse (PF 0.557 and 0.599). Forward was positive but concentrated: 2023 and 2024 were negative for both modes, and the weekly bootstrap intervals cross zero. These failures preclude using the higher 2022/2025 results as evidence of a stable edge.

**Decision: close R266 as FAILED. Do not tune this signal or inspect 2026 to rescue it.**

## Limitations

- BID-only data; ASK quotes, observed spread, broker commission and actual slippage are unavailable.
- Cost stresses are assumptions, not measured costs.
- No funded-provider timezone, DLL/MLL or Quick Strike replay was performed. A result here is not approval to trade a challenge.

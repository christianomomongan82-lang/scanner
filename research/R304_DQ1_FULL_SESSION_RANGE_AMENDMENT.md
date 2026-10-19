# R304 DQ1 — Full-session range-history definition (pre-outcome amendment)

**Committed before any R304 trade outcome calculation.**  
Amends only the historical risk-distance estimator wording in the locked R304 registration. No candidate PnL or directional outcome was inspected before this amendment.

The phrase **"prior 20 eligible full-session midpoint ranges"** means a prior local session counts toward the 20-session rolling history only if its 08:00–11:59 local interval has **exactly 240 distinct active paired M1 timestamps**, one for every minute. Partial sessions and sessions containing gaps after the registered repeated-flat filter are excluded from range history; no bars are synthesized or forward-filled. The median of the latest 20 such full-session midpoint ranges is used once at least 15 complete prior ranges exist.

Candidate entry/exit eligibility remains unchanged: first active paired quote at/after 08:05 and no later than 08:10 local, exact active 12:00 time-exit quote, and a fully contiguous observed entry-to-12:00 path. This amendment makes the implementation consistent with the registered "full-session" wording and is fixed before scoring.

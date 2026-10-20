# R305/R306 — Data and Output Manifest

## Inputs
- EURUSD ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e` (existing GitHub data artifact #11959096102, acquisition run #38697080604).
- EURUSD BID gzip SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`; ASK: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- XAUUSD ZIP SHA-256: `2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a` (existing GitHub data artifact #12031270051, collection run #38859918137).
- XAUUSD BID gzip SHA-256: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`; ASK: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`.
- Cutoff: exclude timestamps >= 2026-01-01 UTC before feature construction.

## Local output checksums

| File | SHA-256 | Bytes |
|---|---|---:|
| `r305_batch.py` | `901877fcb0ee94cb9d08e0c3dd3cec5000e2ebb782fe026d581f6ca712ad3a27` | 19,908 |
| `R305_R306_preoutcome_event_eligibility.csv` | `8774054abfe66f03eba9d991e54272f13aa4bcbfdff10b9e36d855255e7d6ff5` | 6,835,903 |
| `R305_R306_cost_delay_scorecard.csv` | `1b823d19b802eb616111fdb26352eff7253016350e5a6da8699751362703513e` | 3,326 |
| `R305_R306_period_annual_summary.csv` | `0cc940260dcdb196fc4de3826f54c2904b40f330f80698f4d9d4c7e71026a748` | 2,290 |
| `R305_R306_results_compact.json` | `3e80ca22c4ebddfdc06e2d47b19d3ded4463883025646ad45d799a612370c7bb` | 7,436 |
| `R305_trade_ledger_T10.csv` | `2fe54a7da1e232dc59d6539bb1ceb871af2099e767fa6943ee9f6588a1d66524` | 5,018,257 |
| `R305_trade_ledger_T15.csv` | `f35a28db6112d992b75070ffc283149e8bb0d129abf2468ce25e91337352544d` | 3,970,631 |
| `R306_trade_ledger_T10.csv` | `8581400c39918389657ffc85430116a74fb642e6d143a39d9b1f983623fc8ceb` | 1,384,778 |
| `R306_trade_ledger_T15.csv` | `0fbd838162354ba89099d5ad6b4af41876f25a9f6a4cff5ad0a0b98075b368d3` | 1,101,858 |
| `R305_validation_weekly_net_R.csv` | `32a77aa596b4b750a3df60107bec5c8832350b45b69613b121166cfd055e2502` | 7,968 |
| `R306_validation_weekly_net_R.csv` | `31f9f2ecf9856e60357c7cd6ee21a5985fd2f9a1a950b7d0bb20de1fd1fb594d` | 7,903 |

These are local output hashes. The exact runner and full row-level eligibility/trade CSVs are identified locally but are not yet committed as regular decoded files in the active GitHub branch. Repository-only reproduction remains a failed gate; this manifest does not imply otherwise.

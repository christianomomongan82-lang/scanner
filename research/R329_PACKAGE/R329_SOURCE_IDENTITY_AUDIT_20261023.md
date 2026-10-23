# R329 execution identity and rerun audit

- Outcome computation first recorded: 2026-10-23T03:23:30Z.
- Pinned GitHub runner blob SHA: `6abf73f4d59351424c306f3dde2b1f7b5c37cdc5`.
- Local executed runner SHA-256: `abc24c2b706e58ebc059b93b5c18f48807ebfb02df12166c4230aa428f2c842b`.
- Second local reconstruction SHA-256: `97c08cedaf01cef1da7e7a544fad2ca6a09bbd3dfadd5d004f718fd75e160129c`.
- Same local runner executed twice: all 13 generated result artifact hashes matched byte-for-byte.
- Cross-check with the second reconstruction: result JSON, scorecard, annual cohorts, full grid, row-level trade ledgers and the other economic result files matched; the sole generated-output difference was the wide weekly grid carrying an extra unused date column in the first local variant.
- Economic gates: fail. This source-identity caveat is preserved; no funded-ready result is claimed.

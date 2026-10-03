# PTime Version Manager

PTime version history is append-only and monotonic.

## Sources of truth

- `VERSION` = latest implemented/published package version.
- `VERSION.md` = human-readable status across implemented and design/spec tracks.
- `releases/Vx.y.md` = release/spec documents.
- `version/LATEST.md` = highest declared PTime design/spec version and current package version.
- `version/AGENT.md` = mandatory rules for any future version change.

## Current tracks — 2026-10-03

- Implemented package: **2.1.0**
- Highest declared design/spec version: **2.3.0**
- V2.2: Temporal Operating Layer plan.
- V2.3: Markov Chain Discrete-Time Manager spec release.

A future version must never move backward. Historical release documents must not be rewritten to make an older version appear current.

Use SemVer-style numbers to avoid ambiguous ordering.
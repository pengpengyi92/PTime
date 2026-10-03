# PTime Version Agent

This file is mandatory reading before changing PTime versions.

## Read order

1. `version/LATEST.md`
2. `VERSION`
3. `VERSION.md`
4. `CHANGELOG.md`
5. existing `releases/`
6. root `AGENT.md` and `AGENTS.md`

## Monotonic version invariant

**PTime versions never go backward.**

Before proposing a new version, find the highest version already declared anywhere in:
- implemented package metadata;
- VERSION.md;
- version/LATEST.md;
- release/spec documents.

A new version must be strictly greater than that highest declared version, unless the task is explicitly amending the same unreleased/spec version.

Never:
- set a current/latest pointer to a lower version;
- delete or rewrite history to hide a later version;
- call an older version "latest";
- mark implementation complete when release gates were not run.

## Two-track rule

PTime may have:
- **implemented package version** — reflected by `VERSION`, code metadata, tests and published release state;
- **design/spec version** — may be ahead, but must be clearly labeled SPEC / PLANNED / IMPLEMENTATION PENDING.

Do not advance `VERSION` merely because a design/spec document exists.

## Version increments

Use unambiguous SemVer-style numbering:
- PATCH: 2.3.0 -> 2.3.1
- MINOR: 2.3.0 -> 2.4.0
- MAJOR: 2.x -> 3.0.0

The version line is append-only.

## V2.3 invariant

V2.3 introduces the **Markov Chain Discrete-Time Manager**:
`T -> T+1 -> T+2` decision-state management.

Every time decision should consider both immediate value and its effect on the probability of useful next states. Recovery / sleep is a first-class transition when continuing would increase drift or sleep debt.
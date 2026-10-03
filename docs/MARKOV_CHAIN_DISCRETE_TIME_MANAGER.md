# Markov Chain Discrete-Time Manager

PTime uses a practical Markov-style model to manage sequential time decisions.

## Core equation

`S_t + A_t -> distribution over S_{t+1}`

or more explicitly:

`P(S_{t+1} | S_t, A_t)`

The state should contain enough history to make the approximation useful:
energy, attention, sleep debt, location, mission clarity, unfinished obligations and transition friction.

## Why it matters

Time leakage often propagates.

A low-value decision at `T` can make another low-value decision at `T+1` more likely, which can then degrade `T+2`.

Therefore PTime should optimize **chains**, not isolated blocks.

## Default controller

1. Identify current state.
2. Identify the best realistic next state.
3. Estimate whether the current action improves or degrades that next state.
4. If no strong next action exists, choose recovery rather than uncontrolled continuation.
5. Create a new decision boundary after recovery.

## Chain breaker

`low-value drift -> close -> sleep/recovery -> new T -> purposeful re-entry`

## Exploration controller

`question -> explore -> information gained -> saturation detected -> close / route onward`

Purposeful exploration is valid AlphaTime-supporting work. Repetition after saturation is not automatically valuable.

## PTime metric direction

Prefer:
- higher AlphaTime density;
- better next-state quality;
- faster recovery from drift;
- lower transition friction;
- explicit close decisions.

Avoid optimizing raw activity count or waking hours.
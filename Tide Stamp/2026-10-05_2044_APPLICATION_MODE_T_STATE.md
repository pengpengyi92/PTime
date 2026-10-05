# T-State Selection — Markov Principle for AlphaTime

Timestamp: 2026-10-05 20:44 HKT

## Model

Treat each AlphaTime block as a state transition problem.

Let current state be T_n.
Choose the next action that maximizes the probability of entering a higher-value, more verified state T_(n+1).

```text
T_n
-> choose action
-> transition
-> T_(n+1)
```

## Preferred transitions

```text
observe -> encode
encode -> apply
apply -> talk
talk -> interview
interview -> offer / feedback
offer / feedback -> decision
decision -> next environment
```

Bad transitions:
- observe -> observe indefinitely;
- compare -> compare indefinitely;
- browse -> browse indefinitely;
- talk -> no next action;
- recovery -> drift.

## Selective Connectivity as transition control

Connections affect transition probabilities.

```text
high-value connection
-> higher signal
-> better transition probability

high-noise connection
-> attention fragmentation
-> worse transition probability
```

Therefore:
Selective Connectivity is a T-selection principle, not just a relationship principle.

## Current mode

Current state is now:
**APPLICATION MODE**

Priority transitions:
1. select real roles / PhD routes;
2. submit;
3. enter real conversations;
4. prepare interviews;
5. use feedback to update the next T.

AlphaTime means choosing transitions that create evidence.

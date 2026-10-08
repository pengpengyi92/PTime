"""Executable SPEC examples, not an integrated PTime runtime monitor.

These synthetic tests only verify the documented Environment First decision
policy. They do not claim to observe anyone's actual state or location.
"""
from dataclasses import dataclass
from typing import Literal

Intent = Literal["Output", "Connection", "Observation", "Recovery"]
Decision = Literal["START", "CONTINUE", "RESET_10M", "SWITCH_ENV", "RECOVER", "CLOSE"]


@dataclass(frozen=True)
class SyntheticTState:
    intent: Intent = "Output"
    stalled_minutes: int = 0
    meaningful_progress: bool = False
    repeated_drift: bool = False
    completed_close: bool = False
    low_energy: bool = False
    alternative_workspace_available: bool = True


def reference_decision(state: SyntheticTState) -> Decision:
    """A deterministic policy illustration, NOT a deployed detector."""
    if state.intent == "Recovery" or state.low_energy:
        return "RECOVER"
    if state.completed_close:
        return "CLOSE"
    if state.meaningful_progress:
        return "CONTINUE"
    if state.repeated_drift or state.stalled_minutes >= 30:
        return "SWITCH_ENV" if state.alternative_workspace_available else "RESET_10M"
    if state.stalled_minutes >= 15:
        return "RESET_10M"
    return "START"


def test_T01_productive_time_stays_green():
    assert reference_decision(SyntheticTState(meaningful_progress=True)) == "CONTINUE"


def test_T02_yellow_after_15_minutes_without_start():
    assert reference_decision(SyntheticTState(stalled_minutes=15)) == "RESET_10M"


def test_T03_red_after_30_minutes_with_an_alternative():
    assert reference_decision(SyntheticTState(stalled_minutes=30)) == "SWITCH_ENV"


def test_T04_if_no_alternative_use_local_reset_not_aimless_travel():
    assert reference_decision(SyntheticTState(stalled_minutes=30, alternative_workspace_available=False)) == "RESET_10M"


def test_T05_low_energy_prioritizes_recovery_even_after_stalling():
    assert reference_decision(SyntheticTState(stalled_minutes=30, low_energy=True)) == "RECOVER"


def test_T06_intentional_recovery_is_not_false_positive_drift():
    assert reference_decision(SyntheticTState(intent="Recovery", stalled_minutes=90)) == "RECOVER"


def test_T07_completed_artifact_closes():
    assert reference_decision(SyntheticTState(completed_close=True)) == "CLOSE"


def test_T08_repeated_drift_triggers_early_action():
    assert reference_decision(SyntheticTState(stalled_minutes=8, repeated_drift=True)) == "SWITCH_ENV"


def test_T09_no_start_signal_before_threshold():
    assert reference_decision(SyntheticTState(stalled_minutes=10)) == "START"


def test_T10_progress_is_not_measured_by_file_count_alone():
    assert reference_decision(SyntheticTState(stalled_minutes=22, meaningful_progress=True)) == "CONTINUE"

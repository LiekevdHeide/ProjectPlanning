"""
Function that creates the settings used in gFunction.
Input is either the result of the argParser or an instance created in one of
the test functions (with the same arguments).
Output is the tuple with the setting, containing only hashable elements.
"""
import numpy as np

# from types import SimpleNamespace
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    Deadline: int
    LeadTime: int
    NumPhases: int
    WorkPerPhase: tuple[float]

    E_values: tuple[int]
    E_probs: tuple[float]

    shiftC: tuple[float]
    shiftC_avg: float
    overtimeC: float
    overtimeFreq: int
    phaseC: tuple[float]
    earlyC: float

    threshold_pol_basic: bool
    threshold_pol_cost: bool
    threshold_val: float


def create(args):
    work_per_phase = tuple(np.full(args.NumPhases, args.work_per_phase))
    if args.deterministic:
        epsilon_values = (1,)
        epsilon_probs = (1.0,)
    else:
        epsilon_values = (0, 1, 2)
        epsilon_probs = args.epsilon_probs  # (0.2, 0.6, 0.2))

    epsilon_probs = tuple(epsilon_probs)
    cost_var = np.full(args.Deadline + 1, args.shiftC)
    if args.overtime_freq > 0:
        cost_var[:: args.overtime_freq] = args.shiftC_overtime
    shift_costs = tuple(cost_var)
    shift_costs_avg = sum(cost_var) / (args.Deadline + 1)
    early_cost = args.earlyC
    # Set all cost of not finishing a phase and double the final cost.
    phase_costs = np.full(args.NumPhases, args.phaseC)
    phase_costs[-1] *= 5
    phase_costs = tuple(phase_costs)

    inputs = {
        "E_values": epsilon_values,
        "E_probs": epsilon_probs,
        "shiftC": shift_costs,
        "shiftC_avg": shift_costs_avg,
        "phaseC": phase_costs,
        "earlyC": early_cost,
        "WorkPerPhase": work_per_phase,
        "overtimeC": args.shiftC_overtime,
        "overtimeFreq": args.overtime_freq,
    }

    # print(args, vars(args).keys)
    inputs.update(
        {
            k: vars(args)[k]
            for k in vars(args).keys()
            & {"LeadTime", "Deadline", "NumPhases",
               "threshold_pol_basic", "threshold_pol_cost", "threshold_val"}
        }
    )
    s_class = Settings(**inputs)

    assert len(s_class.E_values) == len(s_class.E_probs), (
        "Different input size for the shift probabilities & values. "
        f"values: {s_class.E_values} and probabilities {s_class.E_probs}"
    )
    assert (
        sum(s_class.E_probs) == 1.0
    ), f"The sum of probabilities is not 1. {s_class.E_probs=}"

    assert np.inner(s_class.E_probs, s_class.E_values) == 1.0, (
        "The mean value of the productivity per day is not 1. The probability "
        f"values are {s_class.E_probs}, for respectively this number of days"
        f"output {s_class.E_values}."
    )

    assert s_class.NumPhases == len(s_class.WorkPerPhase), (
        f"Different number of phases {s_class.NumPhases} and work per phase "
        f"{s_class.WorkPerPhase}."
    )

    assert len(s_class.shiftC) == s_class.Deadline + 1, (
        f"Different length of cost per shift and number of available shifts:"
        f"{s_class.shiftC=}, {s_class.Deadline=}."
    )

    if s_class.threshold_pol_basic:
        assert s_class.threshold_val > 0, (
            "The threshold value should exceed 0 (and is an input arg)."
        )
        assert s_class.threshold_val < 1, (
            "The threshold value should be smaller than 1."
        )
    if s_class.threshold_pol_cost:
        assert s_class.threshold_val > 0, (
            "The threshold value should exceed 0 (and is an input arg)."
        )
        assert s_class.threshold_val < 1, (
            "The threshold value should be smaller than 1."
        )

    assert s_class.earlyC <= 0, (
        "The cost of being early should be non-positive (reward). "
        f"Current value: {s_class.earlyC=}."
    )

    assert not (s_class.threshold_pol_basic and s_class.threshold_pol_cost), (
        "You are trying to use two types of benchmark policies. The basic "
        f"threshold policy is {s_class.threshold_pol_basic} and the cost "
        f"threshold policy is also {s_class.threshold_pol_cost}."
    )

    assert s_class.LeadTime % 2 == 0, (
        "This only works for even lead times (then the first shift of the "
        "project is a normal shift."
    )

    return s_class

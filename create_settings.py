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
    overtimeC: float
    phaseC: tuple[float]
    earlyC: float

    threshold_pol: bool
    bench_LB: float
    bench_UB: float


def create(args):
    work_per_phase = tuple(np.full(args.NumPhases, args.work_per_phase))
    if args.deterministic:
        epsilon_values = (1,)
        epsilon_probs = (1.0,)
    else:
        epsilon_values = (0, 1, 2)
        epsilon_probs = (0.2, 0.6, 0.2)  # (1/3, 1/3, 1/3)

    cost_var = np.full(args.Deadline + 1, args.shiftC)
    if args.overtime_freq > 0:
        cost_var[:: args.overtime_freq] = args.shiftC_overtime
    shift_costs = tuple(cost_var)
    phase_costs = tuple(np.full(args.NumPhases, args.phaseC))
    early_cost = args.earlyC

    inputs = {
        "E_values": epsilon_values,
        "E_probs": epsilon_probs,
        "shiftC": shift_costs,
        "phaseC": phase_costs,
        "earlyC": early_cost,
        "WorkPerPhase": work_per_phase,
        "overtimeC": args.shiftC_overtime,
    }
    if args.threshold_pol:
        inputs.update(
            {
                "bench_LB": 0.0,
                "bench_UB": 1.0,
            }
        )
    else:
        inputs.update({"bench_LB": -10, "bench_UB": -20})
    inputs.update(
        {
            k: vars(args)[k]
            for k in vars(args).keys()
            & {"LeadTime", "Deadline", "NumPhases", "threshold_pol"}
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
    if s_class.threshold_pol:
        assert s_class.bench_LB <= s_class.bench_UB, (
            f"The lower bound of the benchmark exceeds the upper bound:"
            f"LB: {s_class.bench_LB}, UB: {s_class.bench_UB}."
        )

    return s_class

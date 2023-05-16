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
    phaseC: tuple[float]
    earlyC: float


def create(args):
    work_per_phase = tuple(np.full(args.NumPhases, 4
                                   ))

    if args.deterministic:

        epsilon_values = (1,)
        epsilon_probs = (1.0,)
    else:
        epsilon_values = (0, 1, 2)
        epsilon_probs = (0.05, 0.9, 0.05)  # (1/3, 1/3, 1/3)

    if args.cost_specified == "yes":
        shift_costs = tuple(np.full(args.Deadline + 1, args.shiftC))
        phase_costs = tuple(np.full(args.NumPhases, args.phaseC))
        early_cost = args.earlyC
    else:
        shift_costs = tuple(np.full(args.Deadline + 1, 1))
        phase_costs = tuple(
            np.full(args.NumPhases, 2 * work_per_phase[0] * shift_costs[0])
        )
        early_cost = -1  # 0

    inputs = {
        "E_values": epsilon_values,
        "E_probs": epsilon_probs,
        "shiftC": shift_costs,
        "phaseC": phase_costs,
        "earlyC": early_cost,
        "WorkPerPhase": work_per_phase,
    }

    inputs.update(
        {
            k: vars(args)[k]
            for k in vars(args).keys() & {"LeadTime", "Deadline", "NumPhases"}
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

    return s_class

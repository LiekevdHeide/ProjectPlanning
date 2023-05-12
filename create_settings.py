"""
Function that creates the settings used in gFunction.
Input is either the result of the argParser or an instance created in one of
the test functions (with the same arguments).
Output is the tuple with the setting, containing only hashable elements.
"""
import numpy as np

from types import SimpleNamespace


def create(args):
    num_shifts = args.T
    lead_time = args.L
    num_phases = args.N
    work_per_phase = tuple(np.full(num_phases, 5))
    # number_shifts = num_shifts + lead_time

    if args.deterministic:
        epsilon_values = (1,)
        epsilon_probs = (1.0,)
    else:
        epsilon_values = (0, 1, 2)
        epsilon_probs = (0.05, 0.9, 0.05)  # (1/3, 1/3, 1/3)

    if args.cost_specified == 'yes':
        shift_costs = tuple(np.full(num_shifts + 1, args.shiftC))
        phase_costs = tuple(
            np.full(num_phases, args.phaseC)
        )
        early_cost = args.earlyC
    else:
        shift_costs = tuple(np.full(num_shifts + 1, 1))
        phase_costs = tuple(
            np.full(num_phases, 2 * work_per_phase[0] * shift_costs[0])
        )
        early_cost = 0  # -1

    assert len(epsilon_values) == len(epsilon_probs), (
        "Different input size for the shift probabilities & values. "
        + f"values: {epsilon_values} and probabilities {epsilon_probs}"
    )
    assert sum(epsilon_probs) == 1.0, (
        f"The sum of probabilities is not 1. {epsilon_probs=}"
    )
    assert np.inner(epsilon_probs, epsilon_values) == 1.0, (
        "The mean value of the productivity per day is not 1. The probability"
        + f" values are {epsilon_probs}, for respectively this number of days"
          f"output {epsilon_values}."
    )

    assert num_phases == len(work_per_phase), (
        f"Different number of phases {num_phases} and work per phase "
        + f"{work_per_phase}."
    )

    # setting = (
    #     num_shifts,
    #     shift_costs,
    #     lead_time,
    #     num_phases,
    #     work_per_phase,
    #     phase_costs,
    #     epsilon_values,
    #     epsilon_probs,
    #     early_cost,
    # )

    setting = SimpleNamespace(
        Deadline=args.T, ShiftC=shift_costs,LeadTime=args.L, NumPhases=args.N,
        WorkPerPhase=work_per_phase, PhaseC=phase_costs,
        E_values=epsilon_values, E_probs=epsilon_probs, EarlyC=early_cost,
    )

    return setting

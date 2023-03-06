"""
Function that creates the settings used in gFunction.
Input is either the result of the argParser or an instance created in one of
the test functions (with the same arguments).
Output is the tuple with the setting, containing only hashable elements.
"""
import numpy as np


def create(args):
    num_shifts = args.T
    lead_time = args.L
    num_phases = args.N
    work_per_phase = (4, 3, 3, 3)
    number_shifts = num_shifts + lead_time
    shift_costs = tuple(np.full(number_shifts + 1, 2))
    epsilon_values = (0, 1, 2)
    epsilon_probs = (0.2, 0.6, 0.2)  # (1/3, 1/3, 1/3)

    assert len(epsilon_values) == len(epsilon_probs), (
        "Different input size for the shift probabilities & values. "
        + f"values: {epsilon_values} and probabilities {epsilon_probs}"
    )

    # assert num_phases == len(work_per_phase), (
    #     f"Different number of phases {num_phases} and work per phase " +
    #     f"{work_per_phase}."
    # )

    setting = (
        num_shifts,
        shift_costs,
        lead_time,
        num_phases,
        work_per_phase,
        epsilon_values,
        epsilon_probs,
    )

    return setting

"""
Uses the functions described in the second model formulation from 9-3-23.
"""
import functools
import numpy as np

import create_settings


def start_scheduling_model(args):
    # Create setting and initial parameters.
    global setting
    setting = create_settings.create(args)
    remaining_work = setting.WorkPerPhase[0]  # 4
    scheduled_shifts = tuple(np.zeros(setting.LeadTime + 1, dtype=int))
    return setting, f_func(remaining_work, scheduled_shifts, phase=0, t=1)


@functools.cache
def f_func(remaining: int, schedule: tuple[int], phase: int, t: int) -> float:
    assert t > 0, f"Error: Input time t={t} should be greater than 0."
    # Did we finish?
    # if (  # THIS BIT IS ADJUSTED FROM MODEL:
    #     t == setting.Deadline + 1
    #     and phase == setting.NumPhases - 1
    #     and remaining == 0
    # ):
    #     print(f"just in time {l_2(setting, t)}")
    #     return l_2(setting, t)
    if phase == setting.NumPhases - 1 and remaining == 0:
        # completed all phases
        return l_2(t)
    if t == setting.Deadline + 1:
        # reached the deadline
        return l_1(phase)

    # Continue scheduling
    return g_func(remaining, schedule, phase, t)[0]


@functools.cache
def g_func(remaining: int, schedule: tuple[int], phase: int, t: int
) -> (float, int):
    lead_time = setting.LeadTime
    if t > setting.Deadline - lead_time:
        return h_func(remaining, schedule, phase, t), 0

    # Create the yes/no schedules, using all previously scheduled shifts.
    schedule_yes = tuple(1 if i == lead_time else schedule[i] for i in
                         range(len(schedule)))
    schedule_no = tuple(0 if i == lead_time else schedule[i] for i in
                        range(len(schedule)))

    # array of (not scheduling, scheduling) at time t + lead time
    cost_array = (
        h_func(remaining, schedule_no, phase, t),
        setting.ShiftC[t + lead_time]
        + h_func(remaining, schedule_yes, phase, t),
    )
    return min(cost_array), cost_array.index(min(cost_array))


@functools.cache
def l_1(phase: int) -> float:
    return sum(setting.PhaseC[phase: setting.NumPhases])


@functools.cache
def l_2(time: int) -> float:
    # Finished previous time step -> time - 1
    return (setting.Deadline - (time - 1)) * setting.EarlyC


@functools.cache
def h_func(remaining: int, schedule: tuple[int], phase: int, t: int
) -> float:
    # roll the schedule to t + 1
    schedule = np.roll(schedule, -1)
    schedule = tuple(schedule)

    if schedule[-1] == 0:
        return f_func(remaining, schedule, phase, t + 1)

    return k_func(remaining, schedule, phase, t)


@functools.cache
def k_func(remaining: int, schedule: tuple[int], n: int, t: int
) -> float:
    # work on current phase, if no work remaining continue on hext phase
    # Calculate the expected remaining cost using probs & values of epsilon
    cost = 0.0
    # for all values epsilon can take
    for epsilon in range(len(setting.E_values)):
        # calculate the non-negative remaining work in case of this epsilon
        rem_non_neg = max(remaining - setting.E_values[epsilon], 0)
        if rem_non_neg == 0:
            if n < setting.NumPhases - 1:
                cost += setting.E_probs[epsilon] * (
                    f_func(
                        setting.WorkPerPhase[n + 1],
                        schedule,
                        n + 1,
                        t + 1,
                    )
                )
            else:
                cost += setting.E_probs[epsilon] * (
                    f_func(0, schedule, n, t + 1)
                )
        # calculate future cost if this epsilon indeed occurs
        else:
            cost += setting.E_probs[epsilon] * (
                f_func(rem_non_neg, schedule, n, t + 1)
            )
    return cost

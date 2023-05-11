"""
Uses the functions described in the second model formulation from 9-3-23.
"""
import functools
import numpy as np

import SettingsDictionary

sDict = SettingsDictionary.Settings


@functools.cache
def f_func(
    setting: tuple, remaining: int, schedule: tuple[int], phase: int, t: int
) -> float:
    assert t > 0, f"Error: Input time t={t} should be greater than 0."
    # Did we finish?
    # if (  # THIS BIT IS ADJUSTED FROM MODEL:
    #     t == setting[sDict.Deadline] + 1
    #     and phase == setting[sDict.NumPhases] - 1
    #     and remaining == 0
    # ):
    #     print(f"just in time {l_2(setting, t)}")
    #     return l_2(setting, t)
    if phase == setting[sDict.NumPhases] - 1 and remaining == 0:
        # completed all phases
        return l_2(setting, t)
    if t == setting[sDict.Deadline] + 1:
        # reached the deadline
        return l_1(setting, phase)


    # Continue scheduling
    return g_func(setting, remaining, schedule, phase, t)[0]


@functools.cache
def g_func(
    setting: tuple, remaining: int, schedule_no: tuple[int], phase: int, t: int
) -> (float, int):
    if t > setting[sDict.Deadline] - setting[sDict.LeadTime]:
        return h_func(setting, remaining, schedule_no, phase, t), 0

    schedule_yes = list(schedule_no)
    schedule_yes[setting[sDict.LeadTime]] = 1
    schedule_yes = tuple(schedule_yes)

    # array of (not scheduling, scheduling) at time t + lead time
    cost_array = (
        h_func(setting, remaining, schedule_no, phase, t),
        setting[sDict.ShiftC][t + setting[sDict.LeadTime]]
        + h_func(setting, remaining, schedule_yes, phase, t),
    )
    return min(cost_array), cost_array.index(min(cost_array))


@functools.cache
def l_1(setting: tuple, phase: int) -> float:
    return sum(setting[sDict.PhaseC][phase: setting[sDict.NumPhases]])


@functools.cache
def l_2(setting: tuple, time: int) -> float:
    # Finished previous time step -> time - 1
    return (setting[sDict.Deadline] - (time - 1)) * -10


@functools.cache
def h_func(
    setting: tuple, remaining: int, schedule: tuple[int], phase: int, t: int
) -> float:
    # roll the schedule to t + 1
    schedule = np.roll(schedule, -1)
    schedule = tuple(schedule)

    if schedule[-1] == 0:
        return f_func(setting, remaining, schedule, phase, t + 1)

    return k_func(setting, remaining, schedule, phase, t)


@functools.cache
def k_func(
    setting: tuple, remaining: int, schedule: tuple[int], n: int, t: int
) -> float:
    # work on current phase, if no work remaining continue on hext phase
    # Calculate the expected remaining cost using probs & values of epsilon
    cost = 0.0
    # for all values epsilon can take
    for epsilon in range(len(setting[sDict.E_values])):
        # calculate the non-negative remaining work in case of this epsilon
        rem_non_neg = max(remaining - setting[sDict.E_values][epsilon], 0)
        if rem_non_neg == 0:
            if n < setting[sDict.NumPhases] - 1:
                cost += setting[sDict.E_probs][epsilon] * (
                    f_func(
                        setting,
                        setting[sDict.WorkPerPhase][n + 1],
                        schedule,
                        n + 1,
                        t + 1,
                    )
                )
            else:
                cost += setting[sDict.E_probs][epsilon] * (
                    f_func(
                        setting,
                        0,
                        schedule,
                        n,
                        t + 1,
                    )
                )
        # calculate future cost if this epsilon indeed occurs
        else:
            cost += setting[sDict.E_probs][epsilon] * (
                f_func(
                    setting,
                    rem_non_neg,
                    schedule,
                    n,
                    t + 1,
                )
            )
    return cost

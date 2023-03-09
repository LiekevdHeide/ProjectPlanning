"""
Uses the functions described in the second model formulation from 9-3-23.
"""
import functools
import numpy as np

import SettingsDictionary

sDict = SettingsDictionary.Settings


# @functools.cache  # alternative for higher Python versions (3.9)
@functools.lru_cache(maxsize=None)
def g_func(setting, remaining, schedule_no, phase, t):
    if t > setting[sDict.Deadline] - setting[sDict.LeadTime]:
        return g_tilde(setting, remaining, schedule_no, phase, t)

    schedule_yes = schedule_no
    schedule_yes[setting[sDict.LeadTime]] = 1
    return min(g_tilde(setting, remaining, schedule_no, phase, t),
               setting[sDict.ShiftCost][t+setting[sDict.LeadTime]] +
               g_tilde(setting, remaining, schedule_yes, phase, t))


@functools.lru_cache(maxsize=None)
def g_tilde(setting, remaining, schedule, phase, t):
    if t == setting[sDict.Deadline] + 1:
        return h_1(setting, phase)
    if phase == setting[sDict.NumPhases] and remaining == 0:
        return h_2(setting, t)
    return k_func(setting, remaining, schedule, phase, t)


@functools.lru_cache(maxsize=None)
def h_1(setting, phase):
    phase_costs = 0
    for n in range(phase, setting[sDict.NumPhases]):
        phase_costs += 10
    return phase_costs


@functools.lru_cache(maxsize=None)
def h_2(setting, time):
    return setting[sDict.Deadline] - time * -10


@functools.lru_cache(maxsize=None)
def k_func(setting, remaining, schedule, phase, t):
    schedule = np.roll(schedule, -1)
    schedule = tuple(schedule)
    if schedule[0] == 0:
        return g_func(setting, remaining, schedule, phase, t + 1)

    return f_func(setting, remaining, schedule, phase, t)


@functools.lru_cache(maxsize=None)
def f_func(setting, remaining, schedule, n, t):
    # work on next phase or on current phase
    if remaining == 0:
        return expected_value(
            setting, setting[sDict.WorkPerPhase][n + 1], schedule, n + 1, t)
    return expected_value(setting, remaining, schedule, n, t)


@functools.lru_cache(maxsize=None)
def expected_value(setting, remaining, schedule, phase, t):
    # Calculate the expected remaining cost using probs & values of epsilon
    cost = 0.0
    # for all values epsilon can take
    for epsilon in range(len(setting[sDict.E_Values])):
        # calculate the non-negative remaining work in case of this epsilon
        rem_non_neg = max(remaining - setting[sDict.E_Values][epsilon], 0)

        # calculate future cost if this epsilon indeed occurs
        cost += setting[sDict.E_probs][epsilon] * g_func(
            setting, rem_non_neg, schedule, phase, t + 1,
        )
    return cost

"""
Function containing the implementation of the g(D, x, n, t) function from the
 Project planning paper. Inputs are the deadline, lead time, total number of
 phases, the vector of shift costs, the predicted remaining work (if no
 unexpected events occur), the current (rolling horizon) schedule, the current
 phase and shift.
Uses memoization to handle the recursive calculations.
"""

# function with same function as g(D, x, n, t) in paper
import functools
import numpy as np

import terminalValueFunction
import SettingsDictionary

sDict = SettingsDictionary.Settings


# @functools.cache  # alternative for higher Python versions (3.9)
@functools.lru_cache(maxsize=None)
def g_func(setting, remaining, schedule_old, phase, t):
    # if all work is finished this phase OR time until deadline is 0
    # print(f"g_func work {remaining} at {t} phase {phase}")
    if remaining == 0 or t == setting[sDict.Deadline]:
        return terminalValueFunction.final_costs(
            setting, schedule_old, phase, t), 0

    # if the project is not finished, define costs + future schedules
    cost_no = 0.0
    schedule_no = np.roll(schedule_old, -1)
    schedule_no[-1] = 0
    schedule_no = tuple(schedule_no)
    # if shift t+L is not scheduled:
    # if current shift is implemented
    if schedule_old[0] == 1:
        # calculate expected value of not scheduling shift t+L
        cost_no = expected_value(setting, remaining, schedule_no, phase, t + 1)
    # if current shift is not scheduled x'(0)
    else:
        cost_no += g_func(setting, remaining, schedule_no, phase, t + 1)[0]

    # check if possible to schedule shift t+L
    if t + setting[sDict.LeadTime] > setting[sDict.Deadline]:
        # no additional shifts can be scheduled => choose no
        return cost_no, 0
    else:
        assert t + setting[sDict.LeadTime] <= setting[sDict.Deadline], (
            f"Schedule after deadline time {t} "
            + f"plus lead time {setting[sDict.LeadTime]},"
            + f"deadline {setting[sDict.Deadline]}"
        )
        assert t + setting[sDict.LeadTime] < len(setting[sDict.ShiftCost]), (
            f"Error, out of bounds {t} + {setting[sDict.LeadTime]} >="
            + f" {len(setting[sDict.ShiftCost])}"
        )
        cost_yes = setting[sDict.ShiftCost][t + setting[sDict.LeadTime]]
        schedule_yes = np.roll(schedule_old, -1)
        schedule_yes[-1] = 1
        schedule_yes = tuple(schedule_yes)

        # if current shift is implemented
        if schedule_old[0] == 1:
            # add expected value of continuing with x'(1)
            cost_yes = expected_value(
                setting, remaining, schedule_yes, phase, t + 1
            )
        else:
            cost_yes += g_func(setting, remaining, schedule_yes, phase, t + 1,)[0]

        cost_array = (cost_no, cost_yes)
        print(t, remaining, schedule_old, cost_array)
        return min(cost_array), cost_array.index(min(cost_array))


def expected_value(setting, remaining, schedule, phase, t):
    cost = 0.0
    # for all values epsilon can take
    for epsilon in range(len(setting[sDict.E_Values])):
        # calculate the non-negative remaining work in case of this epsilon
        rem_non_neg = max(remaining - setting[sDict.E_Values][epsilon], 0)

        # calculate future cost if this epsilon indeed occurs
        g_c = g_func(setting, rem_non_neg, schedule, phase, t,)[0]
        print("g_c", g_c)
        cost += setting[sDict.E_probs][epsilon] * g_c
    return cost

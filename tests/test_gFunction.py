"""
Test function for the gFunction.
"""
import numpy as np

import gFunction
import SettingsDictionary

sDict = SettingsDictionary.Settings


def create_setting(input_type):
    setting = [0, 0, 0]
    if input_type == "zero":
        setting[sDict.Deadline] = 1
        setting[sDict.NumPhases] = 1
        setting[sDict.LeadTime] = 1
    else:
        setting[sDict.Deadline] = 5
        setting[sDict.NumPhases] = 1
        setting[sDict.LeadTime] = 1
    setting = tuple(setting)
    return setting


def test_shift_cost():
    setting = create_setting("basic")
    shift_c_zero = tuple(
        np.full(setting[sDict.Deadline] + setting[sDict.LeadTime] + 1, 0.0)
    )
    shift_c_one = tuple(
        np.full(setting[sDict.Deadline] + setting[sDict.LeadTime] + 1, 1.0)
    )
    setting0 = setting + shift_c_zero
    setting1 = setting + shift_c_one
    remaining = 5
    phase = 0
    t = 0
    schedule = tuple(np.zeros(setting[sDict.LeadTime] + 1))
    cost_zero = gFunction.g_func(setting0, remaining, schedule, phase, t)
    cost_one = gFunction.g_func(setting1, remaining, schedule, phase, t)
    assert cost_zero < cost_one, (
        "Final costs not zero if zero costs"
        + f"zero cost {cost_zero}"
        + f"nonzero cost {cost_one}"
    )


"""
TO ADD: - test if increasing lead time increases the cost.
        - test if increasing the deadline reduces cost (if same work).
"""

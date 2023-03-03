"""
The function final_costs represents the terminal value function for the paper.
It returns the final costs if the final phase is completed, dependent on the
amount of time remaining until the deadline.
It returns the final costs if the deadline is reached, dependent on the
remaining phases that still need to be completed.
For all other cases, it returns to the g_function for the next phase.
"""
import gFunction

import SettingsDictionary


def final_costs(setting, schedule, phase, time):
    sDict = SettingsDictionary.Settings
    print(
        f"Terminal value function:{setting[sDict.Deadline] - time}"
        + f"current phase {phase}"
    )

    # if project is completed OR deadline is reached
    if phase == setting[sDict.NumPhases]:
        return setting[sDict.Deadline] - time * -10
    if time == setting[sDict.Deadline]:
        # costs
        phase_costs = 0
        for n in range(phase, setting[sDict.NumPhases]):
            phase_costs += 10
        return phase_costs

    # otherwise: continue to next phase
    return gFunction.g_func(setting, 3, schedule, phase + 1, time)

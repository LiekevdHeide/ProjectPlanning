import numpy as np

import modelForm2
import create_settings
import SettingsDictionary
sDict = SettingsDictionary.Settings


def test_choice():
    # Create input
    input = Input()
    setting = create_settings.create(input)
    setting[sDict.E_values] = (1,)
    setting[sDict.E_probs] = (1.0,)

    plan_all = np.zeros(
        (
            setting[sDict.LeadTime] + 1,
            setting[sDict.NumPhases],
            setting[sDict.WorkPerPhase][0],
            setting[sDict.Deadline],
        ),
        # dtype=int,
    )
    cost_no = np.zeros(
        (
            setting[sDict.LeadTime] + 1,
            setting[sDict.NumPhases],
            setting[sDict.WorkPerPhase][0],
            setting[sDict.Deadline],
        )
    )
    cost_yes = np.copy(cost_no)
    cost_as_returned = np.copy(cost_no)

    plan = np.zeros(setting[sDict.Deadline], dtype=int)
    cost = np.zeros(setting[sDict.Deadline])
    for l in range(setting[sDict.LeadTime] + 1):
        # this works for leadtime  = 1, otherwise need 2^L
        schedule_no = np.zeros(setting[sDict.LeadTime] + 1, dtype=int)
        schedule_no[0:l] = 1  # change this if L>1
        schedule_yes = np.copy(schedule_no)
        schedule_yes[setting[sDict.LeadTime]] = 1
        schedule_no = tuple(schedule_no)
        schedule_yes = tuple(schedule_yes)
        for phase in range(setting[sDict.NumPhases]):
            for r in range(setting[sDict.WorkPerPhase][phase]):
                for t in range(setting[sDict.Deadline]):
                    cost[t], plan[t] = modelForm2.g_func(
                        setting, r + 1, schedule_no, phase, t + 1
                    )
                    plan_all[l, phase, r, t] = plan[t]
                    cost_as_returned[l, phase, r, t] = cost[t]
                    cost_no[l, phase, r, t] = modelForm2.h_func(setting, r + 1, schedule_no, phase, t + 1)
                    if t < setting[sDict.Deadline] - setting[sDict.LeadTime]:
                        cost_yes[l, phase, r, t] = setting[sDict.ShiftC][t + setting[sDict.LeadTime]]
                        cost_yes[l, phase, r, t] += modelForm2.h_func(setting, r + 1, schedule_yes, phase, t + 1)
                    else:
                        # not allowed to schedule, so increase costs
                        cost_yes[l, phase, r, t] = cost_no[l, phase, r, t] + 1

                    # check if the costs are correct
                    assert cost[t] == min(cost_no[l, phase, r, t], cost_yes[l, phase, r, t]), (
                        f"Incorrect costs: {l=} {phase=} {r=} {t=}"
                        f" actual costs {cost[t]} schedule? {plan[t]} cost yes {cost_yes[l, phase, r, t]}"
                        f"cost no: {cost_no[l, phase, r, t]}"
                    )
                    # Check if the schedule is correct
                    assert plan[t] == np.argmin((cost_no[l, phase, r, t], cost_yes[l, phase, r, t])), (
                        f"Incorrect scheduling choice: schedule {plan[t]}, cost yes{cost_yes[l, phase, r, t]}"
                        f"cost no {cost_no[l, phase, r, t]}."
                    )
                    # Change the plan to show if there is a difference in costs:
                    if cost_no[l, phase, r, t] == cost_yes[l, phase, r, t]:
                        plan_all[l, phase, r, t] = 0.5


class Input:
    def __init__(self):
        self.L = 1
        self.N = 2
        self.T = 10
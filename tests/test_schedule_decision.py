import numpy as np

import modelForm2


def test_choice():
    # Create input
    input_class = Input()
    setting, cost = modelForm2.start_scheduling_model(input_class)

    plan_all = np.zeros(
        (
            setting.LeadTime + 1,
            setting.NumPhases,
            setting.WorkPerPhase[0],
            setting.Deadline,
        ),
    )
    cost_no = np.zeros(
        (
            setting.LeadTime + 1,
            setting.NumPhases,
            setting.WorkPerPhase[0],
            setting.Deadline,
        )
    )
    cost_yes = np.copy(cost_no)
    cost_as_returned = np.copy(cost_no)

    plan = np.zeros(setting.Deadline, dtype=int)
    cost = np.zeros(setting.Deadline)
    for l in range(setting.LeadTime + 1):
        # this works for leadtime  = 1, otherwise need 2^L
        schedule_no = np.zeros(setting.LeadTime + 1, dtype=int)
        schedule_no[0:l] = 1  # change this if L>1
        schedule_yes = np.copy(schedule_no)
        schedule_yes[setting.LeadTime] = 1
        schedule_no = tuple(schedule_no)
        schedule_yes = tuple(schedule_yes)
        for phase in range(setting.NumPhases):
            for r in range(setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline):
                    cost[t], plan[t] = modelForm2.g_func(
                        setting, r + 1, schedule_no, phase, t + 1
                    )
                    plan_all[l, phase, r, t] = plan[t]
                    cost_as_returned[l, phase, r, t] = cost[t]
                    cost_no[l, phase, r, t] = modelForm2.h_func(
                        setting, r + 1, schedule_no, phase, t + 1
                    )
                    if t < setting.Deadline - setting.LeadTime:
                        cost_yes[l, phase, r, t] = setting.shiftC[
                            t + setting.LeadTime
                        ]
                        cost_yes[l, phase, r, t] += modelForm2.h_func(
                            setting, r + 1, schedule_yes, phase, t + 1
                        )
                    else:
                        # not allowed to schedule, so increase costs
                        cost_yes[l, phase, r, t] = cost_no[l, phase, r, t] + 1

                    # check if the costs are correct
                    assert cost[t] == min(
                        cost_no[l, phase, r, t], cost_yes[l, phase, r, t]
                    ), (
                        f"Incorrect costs: {l=} {phase=} {r=} {t=}"
                        f" actual costs {cost[t]} schedule? {plan[t]}"
                        f" cost yes {cost_yes[l, phase, r, t]}"
                        f"cost no: {cost_no[l, phase, r, t]}"
                    )
                    # Check if the schedule is correct
                    assert plan[t] == np.argmin(
                        (cost_no[l, phase, r, t], cost_yes[l, phase, r, t])
                    ), (
                        f"Incorrect scheduling choice: schedule {plan[t]},"
                        f" cost yes{cost_yes[l, phase, r, t]}"
                        f"cost no {cost_no[l, phase, r, t]}."
                    )
                    # Change plan to show if there is no difference in costs:
                    if cost_no[l, phase, r, t] == cost_yes[l, phase, r, t]:
                        plan_all[l, phase, r, t] = 0.5


class Input:
    def __init__(self):
        self.LeadTime = 1
        self.NumPhases = 2
        self.Deadline = 10
        self.deterministic = True
        self.cost_specified = "no"

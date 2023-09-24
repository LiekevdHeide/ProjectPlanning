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
    for shift_hist in range(setting.LeadTime + 1):
        # this works for leadtime  = 1, otherwise need 2^L
        schedule_no = np.zeros(setting.LeadTime + 1, dtype=int)
        schedule_no[0:shift_hist] = 1  # change this if L>1
        schedule_yes = np.copy(schedule_no)
        schedule_yes[setting.LeadTime] = 1
        schedule_no = tuple(schedule_no)
        schedule_yes = tuple(schedule_yes)
        for phase in range(setting.NumPhases):
            for r in range(setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline):
                    cost[t], plan[t] = modelForm2.g_func(r + 1, schedule_no, phase, t + 1)
                    plan_all[shift_hist, phase, r, t] = plan[t]
                    cost_as_returned[shift_hist, phase, r, t] = cost[t]
                    cost_no[shift_hist, phase, r, t] = modelForm2.h_func(r + 1, schedule_no, phase, t + 1)
                    if t < setting.Deadline - setting.LeadTime:
                        cost_yes[shift_hist, phase, r, t] = setting.shiftC[
                            t + setting.LeadTime + 1
                        ]
                        cost_yes[shift_hist, phase, r, t] += modelForm2.h_func(r + 1, schedule_yes, phase, t + 1)
                    else:
                        # not allowed to schedule, so increase costs
                        cost_yes[shift_hist, phase, r, t] = (
                            cost_no[shift_hist, phase, r, t] + 1
                        )

                    # check if the costs are correct
                    assert cost[t] == min(
                        cost_no[shift_hist, phase, r, t],
                        cost_yes[shift_hist, phase, r, t],
                    ), (
                        f"Incorrect costs: {shift_hist=} {phase=} {r=} {t=}"
                        f" actual costs {cost[t]} schedule? {plan[t]}"
                        f" cost yes {cost_yes[shift_hist, phase, r, t]}"
                        f"cost no: {cost_no[shift_hist, phase, r, t]}"
                    )
                    # Check if the schedule is correct
                    assert plan[t] == np.argmin(
                        (
                            cost_no[shift_hist, phase, r, t],
                            cost_yes[shift_hist, phase, r, t],
                        )
                    ), (
                        f"Incorrect scheduling choice: schedule {plan[t]},"
                        f" cost yes{cost_yes[shift_hist, phase, r, t]}"
                        f"cost no {cost_no[shift_hist, phase, r, t]}."
                    )
                    # Change plan to show if there is no difference in costs:
                    if (
                        cost_no[shift_hist, phase, r, t]
                        == cost_yes[shift_hist, phase, r, t]
                    ):
                        plan_all[shift_hist, phase, r, t] = 0.5


class Input:
    def __init__(self):
        self.LeadTime = 1
        self.NumPhases = 2
        self.work_per_phase = 5
        self.Deadline = 10
        self.deterministic = True
        self.threshold_pol = False
        self.shiftC = 1
        self.shiftC_overtime = 2
        self.overtime_freq = 2
        self.phaseC = 10
        self.earlyC = -1

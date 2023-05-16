"""
Test function to verify correct costs and decisions for the deterministic special case.
"""
import numpy as np

import modelForm2


def test_deterministic():
    input_class = Input()
    setting, cost = modelForm2.start_scheduling_model(input_class)
    # create
    correct_no = np.zeros(
        (
            setting.NumPhases,
            setting.WorkPerPhase[0],
            setting.Deadline,
        ),
        dtype=int,
    )
    correct_yes = np.copy(correct_no)
    if setting.LeadTime == 1:
        # check if yes/no costs correct, assumes current schedule is empty
        for phase in range(setting.NumPhases):
            for r in range(setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline - 1):
                    # calculates cost of choosing yes/no for current settings
                    cost_y = modelForm2.h_func(
                        setting, r + 1, (0, 1), phase, t + 1
                    )
                    cost_y += setting.shiftC[t + setting.LeadTime]
                    cost_n = modelForm2.h_func(
                        setting, r + 1, (0, 0), phase, t + 1
                    )
                    min_cost_y, trash = modelForm2.g_func(
                        setting, r + 1, (1, 0), phase, t + 2
                    )
                    min_cost_y += setting.shiftC[t + setting.LeadTime]
                    min_cost_n, trash = modelForm2.g_func(
                        setting, r + 1, (0, 0), phase, t + 2
                    )
                    # min_cost_y = cost_as_returned[1, phase, r, t + 1]
                    # min_cost_y += setting.ShiftC][t + setting.LeadTime]]
                    print(phase, r, t, cost_y, min_cost_y)

                    # min_cost_n = cost_as_returned[0, phase, r, t + 1]

                    assert cost_n == min_cost_n, (
                        f"Cost if don't schedule now, not equal to cost "
                        f"if this is chosen {phase=} {r=} {t=} "
                        f"cost no {cost_n} cost next t {min_cost_n}"
                    )

                    assert cost_y == min_cost_y, (
                        f"Cost of schedule now, not equal to cost if "
                        f"this is chosen {phase=} {r=} {t=} "
                        f"cost yes {cost_y} "
                        f"cost next t {min_cost_y}"
                    )

                    correct_yes[phase, r, t] = cost_y == min_cost_y
                    correct_no[phase, r, t] = cost_n == min_cost_n
        print(correct_yes)


class Input:
    def __init__(self):
        self.LeadTime = 1
        self.NumPhases = 2
        self.Deadline = 10
        self.deterministic = True
        self.cost_specified = "no"

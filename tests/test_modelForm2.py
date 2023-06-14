"""
Test function for the gFunction.
"""

import modelForm2


def test_shift_cost():
    input_class_zero = Input(0.0)
    print(input_class_zero)
    setting_zero, cost_zero = modelForm2.start_scheduling_model(
        input_class_zero
    )
    print(setting_zero)

    input_class_one = Input(1)
    setting_one, cost_one = modelForm2.start_scheduling_model(input_class_one)
    print(setting_one)

    assert cost_zero < cost_one, (
        "Final costs not zero if zero costs " f"{cost_zero=} " f"{cost_one=}."
    )


"""
TO ADD: - test if increasing lead time increases the cost.
        - test if increasing the deadline reduces cost (if same work).
"""


class Input:
    def __init__(self, cost):
        self.LeadTime = 1
        self.NumPhases = 2
        self.work_per_phase = 5
        self.Deadline = 10
        self.deterministic = True
        self.shiftC = cost
        self.shiftC_overtime = 2 * cost
        self.overtime_freq = 2
        self.phaseC = 20
        self.earlyC = 10
        self.threshold_pol = False

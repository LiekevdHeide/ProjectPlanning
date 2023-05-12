"""
Test function for the gFunction.
"""

import modelForm2


def test_shift_cost():
    input_class_zero = Input(0)
    setting_zero, cost_zero = modelForm2.start_scheduling_model(
        input_class_zero)
    print(setting_zero)

    input_class_one = Input(5)
    setting_one, cost_one = modelForm2.start_scheduling_model(
        input_class_one)
    print(setting_one)

    assert cost_zero < cost_one, (
        "Final costs not zero if zero costs "
        + f"zero cost {cost_zero} "
        + f"nonzero cost {cost_one}."
    )


"""
TO ADD: - test if increasing lead time increases the cost.
        - test if increasing the deadline reduces cost (if same work).
"""


class Input:
    def __init__(self, cost):
        self.L = 1
        self.N = 2
        self.T = 10
        self.deterministic = False
        self.cost_specified = 'yes'
        self.shiftC = cost
        self.phaseC = cost
        self.earlyC = 0

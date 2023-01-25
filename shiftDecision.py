"""
Includes potential strategies for deciding whether to schedule a shift in leadtime L
inputs can be:
current schedule, shift_cost this shift, remaining_work,
"""


def every_other_shift(schedule, shift_cost):
    # current schedule is: plan every other shift
    schedule[-1] = 1 - schedule[-2]
    return schedule[-1] * shift_cost

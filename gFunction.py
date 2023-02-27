# function with same function as g(D, x, n, t) in paper
import functools
import numpy as np

import terminalValueFunction


@functools.cache  # alternative for lower Python versions: .lru_cache
def g_function(lead_time, remaining, schedule, phase, t):
    # if all work is finished this phase OR time until deadline is 0
    if remaining == 0 or t == 0:
        return terminalValueFunction.final_costs(schedule, phase, t)

    # if the project is not finished, but we have fewer remaining shifts than the lead time
    # we cannot schedule any future shifts
    if t <= lead_time:
        # !! check moment of roll + size of schedule (L or L+1)
        schedule = np.roll(schedule, -1)
        schedule[-1] = 0

        # return: expected value of all possible outcomes this shift IF implemented
        return g_function(remaining, )

    # Otherwise: choose if we schedule a shift at t+L

    return

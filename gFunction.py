# function with same function as g(D, x, n, t) in paper
import functools
import numpy as np

import terminalValueFunction


# Custom Decorator function
# def listToTuple(function):
#     def wrapper(*args):
#         args = [tuple(x) if type(x) == np.ndarray else x for x in args]
#         result = function(*args)
#         result = tuple(result) if type(result) == np.ndarray else result
#         return result
#     print("wrap")
#     return wrapper


# @functools.cache  # alternative for lower Python versions: .lru_cache
# @listToTuple  # change the np.array to a tuple (which is hashable..)
@functools.lru_cache(maxsize=None)
def g_function(deadline, lead_time, num_phases, shift_cost, remaining, schedule, phase, t):
    # if all work is finished this phase OR time until deadline is 0
    print(f"g_func work {remaining} at {t} phase {phase}")
    if remaining == 0 or t == deadline:
        return terminalValueFunction.final_costs(deadline, lead_time, shift_cost, num_phases, schedule, phase, t)

    # if the project is not finished, define costs + future schedules
    cost_if_not_schedule = 0.0
    schedule_no = np.roll(schedule, -1)
    schedule_no[-1] = 0
    schedule_no = tuple(schedule_no)
    # if don't schedule shift t+L:
    # if current shift is implemented
    if schedule[0] == 1:
        for epsilon in range(0, 2):
            cost_if_not_schedule += (1/3) * g_function(deadline, lead_time, num_phases, shift_cost,
                                                       max(remaining - epsilon, 0), schedule_no, phase, t + 1)
    # if current shift is not scheduled x'(0)
    else:
        cost_if_not_schedule += g_function(deadline, lead_time, num_phases, shift_cost,
                                           remaining, schedule_no, phase, t + 1)

    # if possible to schedule shift t+L
    if t + lead_time > deadline:
        return cost_if_not_schedule
    else:
        assert t + lead_time <= deadline, (f"Schedule after deadline time {t} " +
                                           f"plus lead time {lead_time}, deadline {deadline}")
        cost_if_scheduled = shift_cost[t + lead_time]
        schedule_yes = np.roll(schedule, -1)
        schedule_yes[-1] = 1
        schedule_yes = tuple(schedule_yes)

        # add expected value of continuing with x'(1)
        if schedule[0] == 1:
            for epsilon in range(0, 2):
                cost_if_scheduled += (1/3) * g_function(deadline, lead_time, num_phases, shift_cost,
                                                        max(remaining - epsilon, 0), schedule_yes, phase, t + 1)
        else:
            cost_if_scheduled += g_function(deadline, lead_time, num_phases, shift_cost,
                                            remaining, schedule_yes, phase, t + 1)

        return min(cost_if_scheduled, cost_if_not_schedule)
    assert f"After final case in g_function. Shift {t}, remaining work={remaining}, schedule={schedule}"


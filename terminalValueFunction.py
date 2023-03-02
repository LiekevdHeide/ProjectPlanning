"""
Terminal value functions added cost at:
(1) Deadline
(2) Project finished (before deadline)
"""
import gFunction


def final_costs(deadline, lead_time, shift_cost, num_phases, shift_schedule, phase, time):
    print("Terminal value function:", deadline - time, "current phase", phase)

    # if project is completed OR deadline is reached
    if phase == num_phases:
        return deadline - time * -10
    if time == deadline:
        # costs
        phase_costs = 0
        for n in range(phase, num_phases):
            phase_costs += 10
        return phase_costs

    # otherwise: continue to next phase
    return gFunction.g_function(deadline, lead_time, num_phases, shift_cost, 3, shift_schedule, phase + 1, time)

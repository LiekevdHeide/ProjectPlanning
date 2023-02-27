"""
Terminal value functions added cost at:
(1) Deadline
(2) Project finished (before deadline)
"""
import gFunction


def final_costs(num_phases, shift_schedule, phase, time_until_deadline):
    print("before deadline:", time_until_deadline, "current phase", phase)

    # if project is completed OR deadline is reached
    if phase == num_phases and time_until_deadline == 0:
        # costs
        phase_costs = 0
        for n in range(phase, num_phases):
            phase_costs += 10
        return phase_costs + time_until_deadline * -10

    # otherwise: continue to next phase
    return gFunction(10, shift_schedule, phase+1, time_until_deadline)

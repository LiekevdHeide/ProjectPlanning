"""
Uses the functions described in the second model formulation from 9-3-23.
"""
import functools
import numpy as np

import create_settings
import calc_threshold


def start_scheduling_model(args):
    # Create setting and initial parameters.
    # global setting
    global g_setting
    setting = create_settings.create(args)
    g_setting = setting

    remaining_work = setting.WorkPerPhase[0]  # 4
    scheduled_shifts = tuple(np.zeros(setting.LeadTime + 1, dtype=int))
    # if f_func.cache_info().currsize > 0:
    #     f_func.cache_clear()
    #     g_func.cache_clear()
    #     l_1.cache_clear()
    #     l_2.cache_clear()
    #     h_func.cache_clear()
    #     k_func.cache_clear()
    return setting, f_func(
        remaining_work, scheduled_shifts, phase=0, t=1
    )


def start_large_scheduling(args):
    # Should be used for large leadtimes!
    # Create setting and initial parameters.
    # global setting
    global g_setting
    setting = create_settings.create(args)
    g_setting = setting

    # remaining_work = setting.WorkPerPhase[0]  # 4
    # scheduled_shifts = tuple(np.zeros(setting.LeadTime + 1, dtype=int))
    for t in reversed(range(2, g_setting.Deadline + 1)):
        for s in range(2**g_setting.LeadTime):
            # create schedule, can end in 0 since will be changed anyway
            str_sched = f"{s:0{setting.LeadTime}b}"[::-1] + "0"
            schedule = tuple([int(s) for s in str_sched])
            for phase in range(g_setting.NumPhases):
                for r in range(g_setting.WorkPerPhase[phase]):
                    f_func(r, schedule, phase=phase, t=t)

    return setting, f_func(
        setting.WorkPerPhase[0],
        tuple(np.zeros(setting.LeadTime + 1, dtype=int)), phase=0, t=1
    )


@functools.lru_cache(maxsize=2000000)
def f_func(
    remaining: int, schedule: tuple[int], phase: int, t: int
) -> float:
    assert t > 0, f"Error: Input time t={t} should be greater than 0."
    # Did we finish?
    # if (  # THIS BIT IS ADJUSTED FROM MODEL:
    #     t == setting.Deadline + 1
    #     and phase == setting.NumPhases - 1
    #     and remaining == 0
    # ):
    #     print(f"just in time {l_2(setting, t)}")
    #     return l_2(setting, t)
    if phase == g_setting.NumPhases - 1 and remaining == 0:
        # completed all phases
        return l_2(t)
    if t == g_setting.Deadline + 1:
        # reached the deadline
        return l_1(phase)

    # Continue scheduling
    return g_func(remaining, schedule, phase, t)[0]


@functools.lru_cache(maxsize=2000000)
def g_func(remaining: int, schedule: tuple[int], phase: int, t: int) -> (float, int):
    lead_time = g_setting.LeadTime
    if t > g_setting.Deadline - lead_time:
        return h_func(remaining, schedule, phase, t), 0

    # Create the yes/no schedules, using all previously scheduled shifts.
    schedule_yes = tuple(
        1 if i == lead_time else schedule[i] for i in range(len(schedule))
    )
    schedule_no = tuple(
        0 if i == lead_time else schedule[i] for i in range(len(schedule))
    )

    if not (g_setting.threshold_pol_basic or g_setting.threshold_pol_cost):
        cost_no = h_func(remaining, schedule_no, phase, t)
        if g_setting.shiftC[t + lead_time] > g_setting.shiftC_avg:
            cost_yes = np.array([0, g_setting.shiftC[t + lead_time], 0, 0])
        else:
            cost_yes = np.array([g_setting.shiftC[t + lead_time], 0, 0, 0])
        cost_yes += h_func(remaining, schedule_yes, phase, t)
        if sum(cost_yes) < sum(cost_no):
            return cost_yes, 1
        else:
            return cost_no, 0

    # Calculate threshold measure
    threshold_schedule_decision = calc_threshold.measure(
        g_setting, remaining, schedule, phase, t
    )

    if threshold_schedule_decision:
        if g_setting.shiftC[t + lead_time] > g_setting.shiftC_avg:
            return (
                [0, g_setting.shiftC[t + lead_time], 0, 0]
                + h_func(remaining, schedule_yes, phase, t),
                1,
            )
        else:
            return (
                [g_setting.shiftC[t + lead_time], 0, 0, 0]
                + h_func(remaining, schedule_yes, phase, t),
                1,
            )

    return h_func(remaining, schedule_no, phase, t), 0


# @functools.cache
def l_1(phase: int) -> float:
    return np.array([0.0, 0.0, sum(g_setting.phaseC[phase: g_setting.NumPhases]), 0.0])


# @functools.cache
def l_2(time: int) -> float:
    # Finished previous time step -> time - 1
    return np.array([0.0, 0.0, 0.0, (g_setting.Deadline - (time - 1)) * g_setting.earlyC])


@functools.lru_cache(maxsize=2000000)
def h_func(remaining: int, schedule: tuple[int], phase: int, t: int) -> float:
    # roll the schedule to t + 1
    schedule = np.roll(schedule, -1)
    schedule = tuple(schedule)

    if schedule[-1] == 0:
        return f_func(remaining, schedule, phase, t + 1)

    return k_func(remaining, schedule, phase, t)


@functools.lru_cache(maxsize=2000000)
def k_func(remaining: int, schedule: tuple[int], n: int, t: int) -> float:
    # work on current phase, if no work remaining continue on hext phase
    # Calculate the expected remaining cost using probs & values of epsilon
    cost = np.array([0.0, 0.0, 0.0, 0.0])
    # for all values epsilon can take
    for epsilon in range(len(g_setting.E_values)):
        # calculate the non-negative remaining work in case of this epsilon
        rem_non_neg = max(remaining - g_setting.E_values[epsilon], 0)
        if rem_non_neg == 0:
            if n < g_setting.NumPhases - 1:
                cost += [g_setting.E_probs[epsilon] * x for x in f_func(
                        g_setting.WorkPerPhase[n + 1],
                        schedule,
                        n + 1,
                        t + 1,
                    )]
            else:
                cost += [g_setting.E_probs[epsilon] * x for x in f_func(0, schedule, n, t + 1)]
        # calculate future cost if this epsilon indeed occurs
        else:
            cost += [g_setting.E_probs[epsilon] * x for x in f_func(rem_non_neg, schedule, n, t + 1)]
    return cost

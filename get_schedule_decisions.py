import numpy as np

import modelForm2
import calc_threshold


def current(setting):
    # get scheduling decision for each time, remaining work, current schedule
    # for the benchmark schedule choices OR the optimal choice from the MDP
    if setting.threshold_pol_basic or setting.threshold_pol_cost:
        return benchmark(setting)
    else:
        return optimal(setting)


def optimal(setting):
    """
    Get scheduling decision for each time, remaining work, current schedule
        using the optimal MDP scheduling choices.
    Only works for lead time <= 1.
    :param setting:
    :return: array(leadTime + 1, num phases, remaining work, time)
    """
    lead_time = setting.LeadTime
    plan_all = np.zeros(
        (
            max(1, 2 ** lead_time),
            setting.NumPhases,
            setting.WorkPerPhase[0],
            setting.Deadline,
        ),
    )
    cost_as_returned = np.copy(plan_all)

    for already in range(max(1, 2 ** lead_time)):
        # Create binary form of number, fill with zeros and reverse order
        str_sched_no = f"{already:0{lead_time}b}"[::-1] + "0"
        str_sched_yes = f"{already:0{lead_time}b}"[::-1] + "1"
        schedule_no = tuple([int(s) for s in str_sched_no])
        schedule_yes = tuple([int(s) for s in str_sched_yes])

        for phase in range(setting.NumPhases):
            # Ignore r = 0, since it is never reached except in phase N
            for r in range(setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline):
                    cost, plan = modelForm2.g_func(r + 1, schedule_no, phase, t + 1)
                    plan_all[already, phase, r, t] = plan

                    # Remainder only useful if include indifferent
                    # OR when we want to check if plan is correct given the costs.
                    cost = sum(cost)
                    cost_as_returned[already, phase, r, t] = cost
                    cost_no = sum(modelForm2.h_func(r + 1, schedule_no, phase, t + 1))

                    if t < setting.Deadline - lead_time:
                        cost_yes = setting.shiftC[t + lead_time]
                        cost_yes += sum(modelForm2.h_func(r + 1, schedule_yes, phase, t + 1))
                    else:
                        # not allowed to schedule, so increase costs
                        cost_yes = cost_no + 1

                    # Change the plan to show indifference between
                    # scheduling and not scheduling.
                    # if cost_no == cost_yes:
                    #     plan_all[already, phase, r, t] = 0.5

    return plan_all


def benchmark(setting):
    """
    Get scheduling decision for each time, remaining work, current schedule
        if the benchmark/threshold strategy is used.
    only works for lead time <= 1.
    :param setting:
    :return: array(leadTime + 1, NumPhases, remaining work, T)
    """
    plan_all = np.zeros(
        (
            max(1, 2**setting.LeadTime),
            setting.NumPhases,
            setting.WorkPerPhase[0],
            setting.Deadline,
        ),
    )
    measure_val = plan_all.copy()
    for already in range(max(1, 2**setting.LeadTime)):  # setting.LeadTime + 1)
        prev_sched = f"{already:0{setting.LeadTime}b}"[::-1]
        prev_sched = [int(s) for s in prev_sched]
        for phase in range(setting.NumPhases):
            # Ignore r = 0, since it is never reached except in phase N
            for r in range(0, setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline - setting.LeadTime):
                    # if t < setting.Deadline - setting.LeadTime:
                    # Calculate the threshold measure
                    # (already,)
                    schedule_choice = calc_threshold.measure(
                            setting, r + 1, prev_sched, phase, t + 1
                    )
                    measure_val[already, phase, r, t] = schedule_choice
                    # What does the threshold policy say?
                    if schedule_choice:
                        plan_all[already, phase, r, t] = 1.0
                    # if (measure == setting.bench_LB
                    #         or measure == setting.bench_UB):
                    #     plan_all[already, phase, r, t] = 0.5

    return plan_all

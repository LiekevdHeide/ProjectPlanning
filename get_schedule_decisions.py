import numpy as np

import modelForm2
import calc_threshold


def current(setting):
    lead_time = setting.LeadTime
    plan_all = np.zeros(
        (
            lead_time + 1,
            setting.NumPhases,
            setting.WorkPerPhase[0],
            setting.Deadline,
        ),
    )
    cost_as_returned = np.copy(plan_all)

    for already_scheduled in range(lead_time + 1):
        # this works for leadtime  = 1, otherwise need 2^L
        schedule_no = np.zeros(lead_time + 1, dtype=int)
        schedule_no[0:already_scheduled] = 1  # change this if L>1
        schedule_yes = np.copy(schedule_no)
        schedule_yes[lead_time] = 1
        schedule_no = tuple(schedule_no)
        schedule_yes = tuple(schedule_yes)

        for phase in range(setting.NumPhases):
            # Ignore r = 0, since it is never reached except in phase N
            for r in range(setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline):
                    cost, plan = modelForm2.g_func(
                        setting, r + 1, schedule_no, phase, t + 1
                    )
                    plan_all[already_scheduled, phase, r, t] = plan
                    cost_as_returned[already_scheduled, phase, r, t] = cost
                    cost_no = modelForm2.h_func(
                        setting, r + 1, schedule_no, phase, t + 1
                    )

                    if t < setting.Deadline - lead_time:
                        cost_yes = setting.shiftC[t + lead_time]
                        cost_yes += modelForm2.h_func(
                            setting, r + 1, schedule_yes, phase, t + 1
                        )
                    else:
                        # not allowed to schedule, so increase costs
                        cost_yes = cost_no + 1

                    # Change the plan to show indifference between
                    # scheduling and not scheduling.
                    if cost_no == cost_yes:
                        plan_all[already_scheduled, phase, r, t] = 0.5

    return plan_all


def benchmark(setting):
    # only works for lead time == 1.
    plan_all = np.zeros(
        (
            setting.LeadTime + 1,
            setting.NumPhases,
            setting.WorkPerPhase[0],
            setting.Deadline,
        ),
    )
    measure_val = plan_all.copy()
    for already in range(setting.LeadTime + 1):
        for phase in range(setting.NumPhases):
            # Ignore r = 0, since it is never reached except in phase N
            for r in range(0, setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline - setting.LeadTime):
                    # if t < setting.Deadline - setting.LeadTime:
                    # Calculate the threshold measure
                    schedule_choice = calc_threshold.measure(
                            setting, r + 1, (already,), phase, t + 1
                    )
                    measure_val[already, phase, r, t] = schedule_choice
                    # What does the threshold policy say?
                    if schedule_choice:
                        plan_all[already, phase, r, t] = 1.0
                    # if (measure == setting.bench_LB
                    #         or measure == setting.bench_UB):
                    #     plan_all[already, phase, r, t] = 0.5

    # print(measure_val)
    return plan_all

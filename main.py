# -*- coding: utf-8 -*-
"""
Created 25-1
The main() function imports the specific settings we use in the experiments.
Then, we use the recursive g_function with these settings as inputs to
calculate the overall optimal costs of scheduling shifts with uncertainty and
a lead time $L$.
Inputs of the form: -T 20 -L 2 -N 5
"""
import numpy as np
import timeit
import argparse

# own functions
import create_settings
import SettingsDictionary
import modelForm2
import plot_planning

sDict = SettingsDictionary.Settings


# np.set_printoptions(threshold=np.inf)


def main():
    # get experiment setting
    args = parse_inputs()
    stopwatch_start = timeit.default_timer()

    # create setting and initial parameters
    setting = create_settings.create(args)
    remaining_work = setting[sDict.WorkPerPhase][0]  # 4
    scheduled_shifts = tuple(np.zeros(setting[sDict.LeadTime] + 1, dtype=int))

    # run algorithm
    opt_cost = modelForm2.f_func(
        setting, remaining_work, scheduled_shifts, phase=0, t=1
    )

    plan_all = np.zeros(
        (
            setting[sDict.LeadTime] + 1,
            setting[sDict.NumPhases],
            setting[sDict.WorkPerPhase][0],
            setting[sDict.Deadline],
        ),
        # dtype=int,
    )
    cost_as_returned = np.copy(plan_all)

    for l in range(setting[sDict.LeadTime] + 1):
        # this works for leadtime  = 1, otherwise need 2^L
        schedule_no = np.zeros(setting[sDict.LeadTime] + 1, dtype=int)
        schedule_no[0:l] = 1  # change this if L>1
        schedule_yes = np.copy(schedule_no)
        schedule_yes[setting[sDict.LeadTime]] = 1
        schedule_no = tuple(schedule_no)
        schedule_yes = tuple(schedule_yes)

        for phase in range(setting[sDict.NumPhases]):
            for r in range(setting[sDict.WorkPerPhase][phase]):
                for t in range(setting[sDict.Deadline]):
                    cost, plan = modelForm2.g_func(
                        setting, r + 1, schedule_no, phase, t + 1
                    )
                    plan_all[l, phase, r, t] = plan
                    cost_as_returned[l, phase, r, t] = cost
                    cost_no = modelForm2.h_func(setting, r + 1, schedule_no, phase, t + 1)

                    if t < setting[sDict.Deadline] - setting[sDict.LeadTime]:
                        cost_yes = setting[sDict.ShiftC][t + setting[sDict.LeadTime]]
                        cost_yes += modelForm2.h_func(setting, r + 1, schedule_yes, phase, t + 1)
                    else:
                        # not allowed to schedule, so increase costs
                        cost_yes = cost_no + 1

                    # Change the plan to show if there is a difference in costs:
                    if cost_no == cost_yes:
                        plan_all[l, phase, r, t] = 0.5

    plot_planning.create(setting, plan_all)

    runtime = timeit.default_timer() - stopwatch_start
    print(f"Overall costs {opt_cost} and runtime {runtime}")


def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-T", help="Number of shifts available", type=int, required=True
    )
    parser.add_argument("-L", help="Lead time", type=int, required=True)
    parser.add_argument("-N", help="Number of phases", type=int, required=True)
    args = parser.parse_args()
    return args


# execute main() function
if __name__ == "__main__":
    main()

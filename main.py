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
            setting[sDict.NumPhases],
            setting[sDict.WorkPerPhase][0],
            setting[sDict.Deadline],
        ),
        dtype=int,
    )
    cost_no = np.copy(plan_all)
    cost_yes = np.copy(plan_all)
    correct_no = np.copy(plan_all)
    correct_yes = np.copy(plan_all)

    # Look at the weird no schedule blocks:
    schedule_no = scheduled_shifts
    schedule_yes = list(scheduled_shifts)
    schedule_yes[setting[sDict.LeadTime]] = 1
    schedule_yes = tuple(schedule_yes)

    for phase in range(setting[sDict.NumPhases]):
        for r in range(1, setting[sDict.WorkPerPhase][phase] + 1):
            plan = np.zeros(setting[sDict.Deadline], dtype=int)
            cost = np.zeros(setting[sDict.Deadline])
            for t in range(1, setting[sDict.Deadline] + 1):
                cost[t - 1], plan[t - 1] = modelForm2.g_func(
                    setting, r, scheduled_shifts, phase, t
                )
                plan_all[phase, r - 1, t - 1] = plan[t - 1]
                cost_no[phase, r - 1, t - 1] = modelForm2.h_func(setting, r, schedule_no, phase, t)
                cost_yes[phase, r - 1, t - 1] = setting[sDict.ShiftC][t + setting[sDict.LeadTime]]
                cost_yes[phase, r - 1, t - 1] += modelForm2.h_func(setting, r, schedule_yes, phase, t)
            print(f"phase:{phase + 1} work remaining: {r - 1}", plan, cost)

    for phase in range(setting[sDict.NumPhases]):
        for r in range(2, setting[sDict.WorkPerPhase][phase] + 1):
            for t in range(1, setting[sDict.Deadline]):
                # check if yes/no costs correct:
                if cost_yes[phase, r - 1, t - 1] != min(cost_yes[phase, r - 2, t], cost_no[phase, r - 2, t]):
                    print(f"phase {phase} rem. {r - 1} t {t - 1} costY={cost_yes[phase, r - 1, t - 1]}" +
                          f" at rem. {r - 2}, t {t} yes: {cost_yes[phase, r - 2, t]} no: {cost_no[phase, r - 2, t]} ")
                if cost_no[phase, r - 1, t - 1] != min(cost_yes[phase, r - 1, t], cost_no[phase, r - 1, t]):
                    print(f"phase {phase} rem. {r - 1} t {t - 1} costN={cost_no[phase, r - 1, t - 1]}" +
                          f" at rem. {r - 1}, t {t} yes: {cost_yes[phase, r - 1, t]} no: {cost_no[phase, r - 1, t]} ")

                correct_yes[phase, r - 1, t - 1] = cost_yes[phase, r - 1, t - 1] == min(cost_yes[phase, r - 2, t],
                                                             cost_no[phase, r - 2, t])
                correct_no[phase, r - 1, t - 1] = cost_no[phase, r - 1, t - 1] == min(cost_yes[phase, r - 1, t],
                                                             cost_no[phase, r - 1, t])
    print(correct_no)
    print(correct_yes)

    # for phase in range(0, 1):  # setting[sDict.NumPhases]):
    #    for r in range(1, setting[sDict.WorkPerPhase][phase] + 1):
    #        for t in range(1, setting[sDict.Deadline] + 1):
    #            no_sched = modelForm2.h_func(setting, r, schedule_no, phase, t)
    #            sched = setting[sDict.ShiftC][t + setting[sDict.LeadTime]]
    #            sched += modelForm2.h_func(setting, r, schedule_yes, phase, t)
    #            print(phase + 1, r, t, no_sched, sched, no_sched == sched)

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

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
import modelForm2
import plot_planning


def main():
    # Get experiment setting.
    args = parse_inputs()
    stopwatch_start = timeit.default_timer()

    # Run algorithm.
    setting, opt_cost = modelForm2.start_scheduling_model(args)
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
            for r in range(0, setting.WorkPerPhase[phase]):
                for t in range(setting.Deadline):
                    cost, plan = modelForm2.g_func(
                        r + 1, schedule_no, phase, t + 1
                    )
                    plan_all[already_scheduled, phase, r, t] = plan
                    cost_as_returned[already_scheduled, phase, r, t] = cost
                    cost_no = modelForm2.h_func(
                        r + 1, schedule_no, phase, t + 1
                    )

                    if t < setting.Deadline - lead_time:
                        cost_yes = setting.ShiftC[t + lead_time]
                        cost_yes += modelForm2.h_func(
                            r + 1, schedule_yes, phase, t + 1)
                    else:
                        # not allowed to schedule, so increase costs
                        cost_yes = cost_no + 1

                    # Change the plan to show indifference between
                    # scheduling and not scheduling.
                    if cost_no == cost_yes:
                        plan_all[already_scheduled, phase, r, t] = 0.5

    if setting.NumPhases == 1:
        print(plan_all)
    else:
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
    parser.add_argument(
        "-deterministic", help="Is this the deterministic special case?",
        action="store_true")
    subparsers = parser.add_subparsers(help='Specify cost or default',
                                       dest='cost_specified')
    parser_specify_cost = subparsers.add_parser("yes", help="Specify cost")
    parser_specify_cost.add_argument("-shiftC", type=float, required=True)
    parser_specify_cost.add_argument("-phaseC", type=float, required=True)
    parser_specify_cost.add_argument("-earlyC", type=float, required=True)

    return parser.parse_args()


# execute main() function
if __name__ == "__main__":
    main()

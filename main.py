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

import create_settings
# own functions
import SettingsDictionary
import modelForm2

sDict = SettingsDictionary.Settings
# np.set_printoptions(threshold=np.inf)


def main():
    # get experiment setting
    args = parse_inputs()
    stopwatch_start = timeit.default_timer()

    # create settings and initial parameters
    settings = create_settings.create(args)
    remaining_work = settings[sDict.WorkPerPhase][0]  # 4
    scheduled_shifts = tuple(
        np.zeros(settings[sDict.LeadTime] + 1, dtype=int))

    # run algorithm
    opt_cost = modelForm2.g_func(
        settings, remaining_work, scheduled_shifts, phase=0, t=0
    )

    for phase in range(settings[sDict.NumPhases]):
        for t in range(settings[sDict.Deadline]):
            plan = np.zeros(settings[sDict.WorkPerPhase][phase], dtype=int)
            cost = np.zeros(settings[sDict.WorkPerPhase][phase])
            for r in range(settings[sDict.WorkPerPhase][phase]):
                cost[r], plan[r] = modelForm2.g_func(
                        settings, r, scheduled_shifts, phase, t
                        )
            print(phase, t, plan, cost)

    runtime = timeit.default_timer() - stopwatch_start
    print(f"Overall costs new method {opt_cost}")
    print("Runtime new", runtime)


def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-T", help="Number of shifts available", type=int, required=True
    )
    parser.add_argument("-L", help="Lead time", type=int, required=True)
    parser.add_argument("-N", help="Number of phases", type=int, required=True)
    args = parser.parse_args()
    assert args.L > 0, "Error: input argument lead time is non-positive."
    return args


# execute main() function
if __name__ == "__main__":
    main()

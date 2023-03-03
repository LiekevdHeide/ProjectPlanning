# -*- coding: utf-8 -*-
"""
Created 25-1
The main() function imports the specific settings we use in the experiments.
Then, we use the recursive g_function with these settings as inputs to
calculate the overall optimal costs of scheduling shifts with uncertainty and
a lead time $L$.
"""
import numpy as np
import timeit
import argparse

# own functions
import gFunction

# np.set_printoptions(threshold=np.inf)


def main():
    # get experiment setting
    args = parse_inputs()
    number_shifts = args.T
    lead_time = args.L
    num_phases = args.N
    number_shifts = number_shifts + lead_time
    stopwatch_start = timeit.default_timer()

    # run algorithm
    shift_costs = tuple(np.full(number_shifts + 1, 2))
    remaining_work = 4  # int((number_shifts - lead_time) / 2)

    scheduled_shifts = tuple(np.zeros(lead_time + 1, dtype=int))

    settings = (number_shifts, lead_time, num_phases, shift_costs)
    opt_cost = gFunction.g_func(
        settings, remaining_work, scheduled_shifts, phase=0, t=0
    )
    runtime = timeit.default_timer() - stopwatch_start
    print(f"Overall costs {opt_cost}")
    print("runtime", runtime)


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

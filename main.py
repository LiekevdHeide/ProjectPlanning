# -*- coding: utf-8 -*-
"""
Created 25-1
Contains: startup of algorithm.
"""
import numpy as np
import timeit
import argparse

# own functions
import shiftDecision
import terminalValueFunction

np.set_printoptions(threshold=np.inf)


def main():
    # get experiment setting
    # parse_inputs()
    number_shifts = 30
    lead_time = 4

    number_shifts = number_shifts + lead_time
    stopwatch_start = timeit.default_timer()

    # run algorithm
    shift_costs = np.full(number_shifts, 2)
    scheduled_shifts = np.zeros(lead_time, dtype=int)
    remaining_work = int((number_shifts - lead_time) / 2)

    costs = 0.0
    time_until_deadline = 0
    worked_shifts = np.zeros(number_shifts, dtype=int)
    rng = np.random.default_rng(2023)
    random_work = rng.choice([-1, 0, 1], size=number_shifts, p=[0.2, 0.6, 0.2])
    print(random_work)

    for shift in range(number_shifts):
        if scheduled_shifts[0] == 1:
            worked_shifts[shift] = 1
            # work has been scheduled this epoch
            # decrease work remaining by STOCHASTIC amount
            remaining_work -= 1 + random_work[shift]
        print(shift, scheduled_shifts[0], remaining_work)

        # If work is completed: end program
        if remaining_work <= 0:
            time_until_deadline = number_shifts - shift
            break

        # roll the schedule so all elements one earlier, use element 0 next shift
        scheduled_shifts = np.roll(scheduled_shifts, -1)
        scheduled_shifts[-1] = 0

        # decide on shift in lead time L (and add corresponding costs)
        costs += shiftDecision.every_other_shift(scheduled_shifts, shift_costs[shift])

    costs += terminalValueFunction.final_costs(time_until_deadline, remaining_work)
    runtime = timeit.default_timer() - stopwatch_start
    print(f"Worked shifts (binary): {worked_shifts}")
    print(f"Costs of every other shift: {costs}")

    print("runtime", runtime)


# def parse_inputs():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "-T", "--totalShifts", help="Total number of shifts", type=int,
#         required=True
#     )
#     args = parser.parse_args()
#     return args


# execute main() function
if __name__ == "__main__":
    main()

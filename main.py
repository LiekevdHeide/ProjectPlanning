# -*- coding: utf-8 -*-
"""
Created 25-1
The main() function imports the specific settings we use in the experiments.
Then, we use the function modelForm2.start_scheduling_model(args) to
 start the recursive process with these settings as inputs to calculate the
 overall optimal costs of scheduling shifts with uncertainty and a lead time.
Inputs of the form: -Deadline 10 -LeadTime 1 -NumPhases 2
     with optional: -benchmark -bench_LB 0.0 -bench_UB 1.0
"""
import timeit
import argparse
import sys

# own functions
import modelForm2
import plot_planning
import get_schedule_decisions


def main():
    # Get experiment setting.
    args = parse_inputs()
    stopwatch_start = timeit.default_timer()

    # print(sys.getrecursionlimit()) 1000
    sys.setrecursionlimit(3000)  # sufficient for T=200

    # Run algorithm.
    setting, opt_cost = modelForm2.start_scheduling_model(args)
    runtime = timeit.default_timer() - stopwatch_start
    print(
        f"Overall costs {opt_cost} and runtime {runtime}"
        f", {setting.threshold_pol=}"
    )

    # Print the current plan, or create a graph.
    if setting.NumPhases == 1:
        # get scheduling decisions
        plan_all = get_schedule_decisions.current(setting)
        print(plan_all)
    else:
        if setting.LeadTime <= 1:
            # get scheduling decisions
            plan_all = get_schedule_decisions.current(setting)
            plot_planning.create(setting, plan_all)


def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--Deadline",
        help="Number of shifts available",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--LeadTime", help="Lead time", type=int, required=True
    )
    parser.add_argument(
        "--NumPhases", help="Number of phases", type=int, required=True
    )
    parser.add_argument(
        "--work_per_phase",
        help="Amount of work per phase (equal for all phases",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--deterministic",
        help="Is this the deterministic special case?",
        action="store_true",
    )
    parser.add_argument(
        "--threshold_pol",
        help="Use the threshold benchmark",
        action="store_true",
    )

    parser.add_argument("--shiftC", type=float, default=1)
    parser.add_argument("--shiftC_overtime", type=float, default=2)
    parser.add_argument("--overtime_freq", type=int, default=0)
    parser.add_argument("--phaseC", type=float, default=10)
    parser.add_argument("--earlyC", type=float, default=-1)

    return parser.parse_args()


# execute main() function
if __name__ == "__main__":
    main()

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

# own functions
import modelForm2
import plot_planning
import get_schedule_decisions


def main():
    # Get experiment setting.
    args = parse_inputs()
    stopwatch_start = timeit.default_timer()

    # Run algorithm.
    setting, opt_cost = modelForm2.start_scheduling_model(args)
    runtime = timeit.default_timer() - stopwatch_start
    print(f"Overall costs {opt_cost} and runtime {runtime}, {setting.bench=}")

    # get scheduling decision for each time, remaining work, current schedule:
    if not setting.bench:
        plan_all = get_schedule_decisions.current(setting)
    else:
        plan_all = get_schedule_decisions.benchmark(setting)

    # Print the current plan, or create a graph.
    if setting.NumPhases == 1:
        print(plan_all)

    else:
        plot_planning.create(setting, plan_all)


def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-Deadline", help="Number of shifts available", type=int, required=True
    )
    parser.add_argument("-LeadTime", help="Lead time", type=int, required=True)
    parser.add_argument(
        "-NumPhases", help="Number of phases", type=int, required=True
    )
    parser.add_argument(
        "-deterministic",
        help="Is this the deterministic special case?",
        action="store_true",
    )
    parser.add_argument(
        "-benchmark", help="Use the threshold benchmark", action="store_true"
    )
    parser.add_argument(
        "-bench_LB", help="Lower bound threshold policy", type=float
    )
    parser.add_argument(
        "-bench_UB", help="Upper bound threshold policy", type=float
    )

    subparsers = parser.add_subparsers(
        help="Specify cost or default", dest="cost_specified"
    )
    parser_specify_cost = subparsers.add_parser("yes", help="Specify cost")
    parser_specify_cost.add_argument("-shiftC", type=float, required=True)
    parser_specify_cost.add_argument("-shiftC_overtime", type=float, required=True)
    parser_specify_cost.add_argument("-phaseC", type=float, required=True)
    parser_specify_cost.add_argument("-earlyC", type=float, required=True)

    return parser.parse_args()


# execute main() function
if __name__ == "__main__":
    main()

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
# import plot_planning
# import get_schedule_decisions
import print_output


def main():
    # Get experiment setting.
    args = parse_inputs()

    # print(sys.getrecursionlimit()) 1000
    sys.setrecursionlimit(3000)  # sufficient for T=200
    output_name = args.output_name
    print(args.epsilon_probs)

    if args.threshold_pol_basic or args.threshold_pol_cost:
        opt_cost_all = float('inf')
        for th in range(1, 25):
            th /= 50  # th=0.14
            args.threshold_val = th

            stopwatch_start = timeit.default_timer()

            # Run algorithm.
            setting, opt_cost = modelForm2.start_scheduling_model(args)
            runtime = timeit.default_timer() - stopwatch_start
            current_output = (
                f"Overall costs {opt_cost:.3f} and runtime {runtime:.2f}"
                f", {setting.threshold_pol_basic=}, "
                f"{setting.threshold_pol_cost=}, "
                f"{setting.threshold_val=}"
            )

            if opt_cost < opt_cost_all:
                opt_output = current_output
                opt_cost_all = opt_cost
                best_setting = setting
    else:
        stopwatch_start = timeit.default_timer()
        best_setting, opt_cost_all = modelForm2.start_scheduling_model(args)
        runtime = timeit.default_timer() - stopwatch_start
        opt_output = (
            f"Overall cost {opt_cost_all:.3f} and runtime {runtime:.2f}"
            f", {best_setting.threshold_pol_basic=}, "
            f"{best_setting.threshold_pol_cost=}, "
            f"{best_setting.threshold_val=}"
        )

    print(opt_output, args)

    # print output to csv
    print_output.write_setting(
        output_name, best_setting, opt_cost_all, runtime
    )

    # Print the current plan, or create a graph.
    # if args.show_plot:
    #     if best_setting.NumPhases == 1:
    #         # get scheduling decisions
    #         plan_all = get_schedule_decisions.current(best_setting)
    #         print(plan_all)
    #     else:
    #         # if setting.LeadTime <= 1:
    #         # get scheduling decisions
    #         plan_all = get_schedule_decisions.current(best_setting)
    #         plot_planning.create(best_setting, plan_all)

    # Combine all output files in output_dir and combine in 1 file with name
    # print_output.combine_files(output_dir, "Combined/combi_all1")


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
        "--epsilon_probs",
        nargs='+', type=float,
        help="Array with probabilities of epsilon: (0, 1, 2) resp.",
    )
    parser.add_argument(
        "--threshold_pol_basic",
        help="Use the basic threshold benchmark",
        action="store_true",
    )
    parser.add_argument(
        "--threshold_pol_cost",
        help="Use the cost-based threshold benchmark",
        action="store_true",
    )
    parser.add_argument(
        "--threshold_val",
        help="Threshold value if the threshold benchmark is used.",
        type=float, default=-1
    )

    parser.add_argument("--shiftC", type=float, default=1)
    parser.add_argument("--shiftC_overtime", type=float, default=2)
    parser.add_argument("--overtime_freq", type=int, default=0)
    parser.add_argument("--phaseC", type=float, default=10)
    parser.add_argument("--earlyC", type=float, default=-1)

    parser.add_argument(
        "--show_plot", action="store_true", help="Show schedule plot."
    )
    parser.add_argument(
        "--output_name", required=True,
        help="Name of output file, including directory."
    )

    return parser.parse_args()


# execute main() function
if __name__ == "__main__":
    main()

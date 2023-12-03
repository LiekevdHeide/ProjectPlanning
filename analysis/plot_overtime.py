import argparse
import pandas as pd
import matplotlib.pyplot as plt

import clean_output_files

from matplotlib import rc

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)


def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Input file, .csv with all overtime output",
        required=True,
    )
    parser.add_argument(
        "--savePlot",
        help="Boolean if the plots should be saved as pdf.",
        action="store_true",
    )
    args = parser.parse_args()
    return args


# get input file containing all experiments
parser = parse_inputs()

# -------------check completeness of experiments-------------------------------
fileToRead = parser.file
output_og = pd.read_csv(fileToRead, header="infer", sep=";")
output = clean_output_files.clean(output_og)
# -----------------------------------------------------------------------------
# Overall differences:

cost_columns = [
    "solution_cost_o", "solution_cost_b", "solution_cost_c"
]
cost_column_labels = [
    "Optimal", "Basic", "Shift-based"
]

leadTimes = output["LeadTime"].unique()

# Plot overtimes
for idx_l in range(0, leadTimes.size, 1):
    plotOvertime = output[(output["LeadTime"] == leadTimes[idx_l])]
    plotOvertime = plotOvertime.sort_values(by=["overtimeC"])
    print(output["overtimeC"].unique())

    fig, ax = plt.subplots()
    for idx_c in range(0, 3, 1):
        ax.scatter(x=plotOvertime["overtimeC"], y=plotOvertime[cost_columns[idx_c]],
                   label=f"{cost_column_labels[idx_c]}")

    # set locations and names of the labels
    plt.xticks([1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6])
    plt.ylim(bottom=28, top=50)
    plt.xlabel("Overtime cost")
    plt.ylabel("Cost")
    plt.legend(frameon=False, loc="upper left")

    if parser.savePlot:
        plt.savefig(
            f"Impact overtime cost lead time {leadTimes[idx_l]}.pdf"
        )
    else:
        plt.title(f"Impact of overtime cost for lead time {leadTimes[idx_l]}")

    fig.tight_layout()
    plt.show()

    # plotOvertime.plot(x="overtimeC", y=cost_columns, kind="line")
    # plt.title(f"Impact of overtime cost for lead time {leadTimes[idx_l]} ")
    # fig.tight_layout()
    # plt.show()

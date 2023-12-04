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
        help="Input file, .csv with all uncertainty output",
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
# Group columns:
cost_columns = [
    "solution_cost_o", "solution_cost_b", "solution_cost_c"
]
cost_column_labels = [
    "Optimal", "Basic", "Shift-based"
]

# Split the uncertainties column
output = pd.concat([output, output["E_probs"].str.split(', ', expand=True)], axis=1)
output.rename({1: "Uncertainty"}, axis=1, inplace=True)
output["Uncertainty"] = 1 - pd.to_numeric(output["Uncertainty"])

# Make plots of impact of uncertainty:
leadTimes = output["LeadTime"].unique()
for idx_l in range(0, leadTimes.size, 1):
    plotUncertainty = output[(output["LeadTime"] == leadTimes[idx_l])]
    plotUncertainty = plotUncertainty.sort_values(by=["Uncertainty"], ascending=False)
    print(plotUncertainty['Uncertainty'].unique())

    fig, ax = plt.subplots()
    markerStyles = ["o", "s", "^"]
    for idx_c in range(0, 3, 1):
        ax.scatter(x=plotUncertainty["Uncertainty"], y=plotUncertainty[cost_columns[idx_c]],
                   label=f"{cost_column_labels[idx_c]}",
                   edgecolor="black", facecolor='none', marker=markerStyles[idx_c])

    # set locations and names of the labels
    plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4])
    plt.ylim(bottom=28, top=40)
    plt.xlabel("Uncertainty")
    plt.ylabel("Cost")
    plt.legend(frameon=False, loc="upper left")

    if parser.savePlot:
        plt.savefig(
              f"Impact uncertainty lead time {leadTimes[idx_l]}.pdf"
        )
    else:
        plt.title(f"Impact of uncertainty for lead time {leadTimes[idx_l]}")

    fig.tight_layout()
    plt.show()

    # fig, ax = plt.subplots()
    # plotUncertainty.plot(ax=ax, x="Uncertainty", y=cost_columns, kind="line")
    # plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4])
    # plt.title(f"Lead time {leadTimes[idx_l]}")
    # fig.tight_layout()
    # plt.show()

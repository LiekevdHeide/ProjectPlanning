import argparse
import pandas as pd
import matplotlib.pyplot as plt

import clean_output_files

from matplotlib import rc

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)
rc('font', **{'size': 18})


def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-fu",
        "--uncertaintyFile",
        help="Input file, .csv with all uncertainty output",
        required=True,
    )
    parser.add_argument(
        "-fo",
        "--overtimeFile",
        help="Input file, .csv with all overtime output",
        required=True,
    )
    parser.add_argument(
        "-fd",
        "--deadlineFile",
        help="Input file, .csv with all deadline output",
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

filesToRead = [parser.uncertaintyFile, parser.overtimeFile, parser.deadlineFile]
columnsToRead = ["Uncertainty", "overtimeC", "Deadline"]
labelsToRead = ["Uncertainty", "Overtime cost", "Deadline"]

for files in range(3):
    # -------------check completeness of experiments-------------------------------
    fileToRead = filesToRead[files]
    output_og = pd.read_csv(fileToRead, header="infer", sep=";")
    if files < 2:
        output = clean_output_files.clean(output_og, True)
    else:
        output = clean_output_files.clean(output_og, False)

    # -----------------------------------------------------------------------------
    # Group columns:
    column_labels = [
        "Lead time 0", "Lead time 2", "Lead time 14"
    ]
    if files == 0:
        # Split the uncertainties column
        output = pd.concat([output, output["E_probs"].str.split(', ', expand=True)], axis=1)
        output.rename({1: "Uncertainty"}, axis=1, inplace=True)
        output["Uncertainty"] = 1 - pd.to_numeric(output["Uncertainty"])
    if files == 2:
        # Remove lead time from deadline
        output["Deadline"] = output["Deadline"] - output["LeadTime"]

    print(output["solution_cost_o"])

    # Make plots of impact of uncertainty:
    leadTimes = output["LeadTime"].unique()

    fig, ax = plt.subplots()
    markerStyles = ["o", "s", "^"]
    for idx_l in range(leadTimes.size):
        plot = output[(output["LeadTime"] == leadTimes[idx_l])]
        plot = plot.sort_values(by=columnsToRead[files], ascending=False)
        ax.scatter(x=plot[columnsToRead[files]], y=plot["solution_cost_o"],
                   label=f"{column_labels[idx_l]}",
                   edgecolor="black", facecolor='none', marker=markerStyles[idx_l])

    # set locations and names of the labels
    if files == 0:
        plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4])
    if files == 1:
        plt.xticks([1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6])
    if files == 2:
        plt.xticks([40, 45, 50, 55, 60, 65, 70, 75, 80])

    plt.ylim(bottom=28, top=50)
    plt.xlabel(labelsToRead[files])
    plt.ylabel("Cost")
    if files != 2:
        plt.legend(frameon=False, loc="upper left")
    else:
        plt.legend(frameon=False, loc="upper right")
    fig.set_size_inches(6, 4.8)
    fig.tight_layout()

    if parser.savePlot:
        plt.savefig(
              f"Impact of {columnsToRead[files]}.pdf"
        )
    else:
        plt.title(f"Impact of {columnsToRead[files]}")

    plt.show()

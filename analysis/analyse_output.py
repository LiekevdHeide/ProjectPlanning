"""
Function to analyse the output of the experiments.
Input: -f file name (including directory)
"""
import argparse
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats

matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["font.family"] = "Helvetica"
matplotlib.rcParams["font.size"] = 10
matplotlib.rcParams["axes.titlesize"] = "large"
matplotlib.rcParams["xtick.labelsize"] = "small"
matplotlib.rcParams["ytick.labelsize"] = "small"
matplotlib.rcParams["legend.fontsize"] = "small"
# matplotlib.rcParams["lines.linewidth"] = np.sqrt(16)

plt.rcParams["figure.figsize"] = (3.2, 2.4)


def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Input file, .csv with stylized net output",
        required=True,
    )
    args = parser.parse_args()
    return args


# get input file containing all experiments
parser = parse_inputs()

# -------------check completeness of experiments-------------------------------
fileToRead = parser.file
output = pd.read_csv(fileToRead, header="infer", sep=";")

print("num rows ", len(output), "num cols ", len(output.columns))
output.dropna(inplace=True)

output.drop_duplicates(
    subset=[
        "Deadline",
        "LeadTime",
        "NumPhases",
        "WorkPerPhase",
        "E_values",
        "E_probs",
        "shiftC",
        "overtimeC",
        "phaseC",
        "earlyC",
        "threshold_pol_basic",
        "threshold_pol_cost",
    ],
    inplace=True,
)
print("num rows ", len(output), "num cols ", len(output.columns))

# check NaN entries
print("Any empty entries in dataframe? ", output.isnull().values.any())
print("Number of empty entries in output:", output.isnull().sum().sum())

output["optimal_pol"] = (output["threshold_pol_basic"] == False) & (
    output["threshold_pol_cost"] == False
)

print(output)
checkRuns = (
    output[["LeadTime", "E_probs", "overtimeC"]]
    .groupby(["LeadTime", "E_probs"])
    .count()
)
print(checkRuns)

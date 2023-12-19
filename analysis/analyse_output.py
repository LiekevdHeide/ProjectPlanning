"""
Function to analyse the output of the experiments.
Input: -f file name (including directory)
"""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

import clean_output_files

# import matplotlib
# matplotlib.rcParams["text.usetex"] = True
# matplotlib.rcParams["font.family"] = "Helvetica"
# matplotlib.rcParams["font.size"] = 10
# matplotlib.rcParams["axes.titlesize"] = "large"
# matplotlib.rcParams["xtick.labelsize"] = "small"
# matplotlib.rcParams["ytick.labelsize"] = "small"
# matplotlib.rcParams["legend.fontsize"] = "small"
# # matplotlib.rcParams["lines.linewidth"] = np.sqrt(16)

# plt.rcParams["figure.figsize"] = (3.2, 2.4)


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
output_og = pd.read_csv(fileToRead, header="infer", sep=";")
output = clean_output_files.clean(output_og)

# For paper output:
output = output[output['E_probs'] != "(0.005, 0.99, 0.005)"]
output = output[output['E_probs'] != "(0.025, 0.95, 0.025)"]
output = output[output['E_probs'] != "(0.15, 0.7, 0.15)"]

# -----------------------------------------------------------------------------
# Overall differences:
basic_cols = ['solution_cost_b', "split_shiftC_b",
              "split_overtimeC_b", "split_earlyC_b",
              "split_phaseC_b"]
opt_cols = ['solution_cost_o', "split_shiftC_o",
            "split_overtimeC_o", "split_earlyC_o",
            "split_phaseC_o"]
cost_cols = ['solution_cost_c', "split_shiftC_c",
             "split_overtimeC_c", "split_earlyC_c",
             "split_phaseC_c"]

for i in range(len(basic_cols)):
    costVopt = stats.ttest_rel(
        output[basic_cols[i]], output[opt_cols[i]],
        alternative='greater'
    )
    basicVopt = stats.ttest_rel(
        output[cost_cols[i]], output[opt_cols[i]],
        alternative='greater'
    )
    print(
        f"T tests for differences in costs {basic_cols[i]} result in: "
        f"Basic greater than optimal? pval {basicVopt.pvalue} "
        f"Cost greater than optimal? pval {costVopt.pvalue}, "
    )

basicVcost = stats.ttest_rel(
        output['basic_perc'], output['cost_perc'],
        alternative='greater'
    )
f"And the t-test of all cost relative/percentage difference is: {basicVcost} "

# -----------------------------------------------------------------------------
cost_columns = [
    "solution_cost_o", "solution_cost_b", "solution_cost_c"
]
perc_columns = ["basic_perc", "cost_perc"]
cost_perc_columns = ["solution_cost_o", "basic_perc", "cost_perc"]
# Averages:
mean_costs = output[cost_columns].mean()
print(f"The mean cost are (opt, basic, cost):\n{mean_costs}")

mean_perc = output[["basic_perc", "cost_perc"]].mean()
print(f"The mean percentage differences are (basic, cost):\n{mean_perc}")

# Averages only for overtimeCost = 2:
print("Cost and percentage difference for overtimeCost 2:")
print(output.groupby("overtimeC")[cost_columns].mean().to_latex(
        float_format="{:.2f}".format))
print(output.groupby("overtimeC")[perc_columns].mean().to_latex(
        float_format="{:.2f}".format))

# For different parameter levels:
# ? deadline? freq?
parameter_columns = ["LeadTime", "E_probs", "alpha", "overtimeC", "earlyC"]
threshold_columns = ["threshold_val_b", "threshold_val_c"]
print(output.groupby(parameter_columns)[cost_columns].count())
par_levels = output.groupby(parameter_columns)[cost_columns].mean()
print(par_levels)
for c in range(len(parameter_columns)):
    print(output.groupby(parameter_columns[c])[cost_columns].mean().to_latex(
        float_format="{:.2f}".format))

print("Output cost, then percentage increases:")
for c in range(len(parameter_columns)):
    print(output.groupby(parameter_columns[c])[cost_perc_columns].mean().to_latex(
        float_format="{:.2f}%".format))

for c in range(len(parameter_columns)):
    print(output.groupby(parameter_columns[c])[perc_columns].mean().to_latex(
        float_format="{:.2f}%".format))

for c in range(len(parameter_columns)):
    print(output.groupby(parameter_columns[c])[threshold_columns].mean().to_latex(
        float_format="{:.2f}".format))

output.columns = output.columns.str.removeprefix("split_")
split_cost_columns = [
    "shiftC_o", "shiftC_b", "shiftC_c",
    "overtimeC_o", "overtimeC_b", "overtimeC_c",
    "earlyC_o", "earlyC_b", "earlyC_c",
    "phaseC_o", "phaseC_b", "phaseC_c",
]
for c in range(len(parameter_columns)):
    print(output.groupby(
        parameter_columns[c])[split_cost_columns].mean().to_latex(
        float_format="{:.2f}".format)
    )

# -----------------------------------------------------------------------------------------------------------
# Split the uncertainties column
output = pd.concat([output, output["E_probs"].str.split(', ', expand=True)], axis=1)
output.rename({1: "Uncertainty"}, axis=1, inplace=True)
output["Uncertainty"] = 1 - pd.to_numeric(output["Uncertainty"])
print(output["Uncertainty"])

# Make plots of impact of uncertainty:
leadTimes = output["LeadTime"].unique()
for idx_l in range(0, leadTimes.size, 1):
    plotUncertainty = output[(output["LeadTime"] == leadTimes[idx_l]) & (output["alpha"] == 60) & (output["overtimeC"] == 1.5)]
    plotUncertainty = plotUncertainty.sort_values(by=["Uncertainty"], ascending=False)

    fig, ax = plt.subplots()
    plotUncertainty.plot(ax=ax, x="Uncertainty", y=cost_columns, kind="line")
    plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4])
    plt.title(f"Impact of uncertainty for Lead time {leadTimes[idx_l]}")
    plt.show()

# Plot overtimes
for idx_l in range(0, leadTimes.size, 1):
    plotOvertime = output[(output["LeadTime"] == leadTimes[idx_l]) & (output["alpha"] == 60) & (0.199 < output["Uncertainty"]) & (output["Uncertainty"] < 0.201)]
    plotOvertime = plotOvertime.sort_values(by=["overtimeC"])
    plotOvertime.plot(x="overtimeC", y=cost_columns, kind="line")
    plt.title(f"Impact of overtime cost for lead time {leadTimes[idx_l]} ")
    plt.show()

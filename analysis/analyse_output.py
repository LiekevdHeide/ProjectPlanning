"""
Function to analyse the output of the experiments.
Input: -f file name (including directory)
"""
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from matplotlib import rc

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)
rc('font', **{'size': 10})

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
output = clean_output_files.clean(output_og, True)

# For paper output:
output = output[output['E_probs'] != "(0.005, 0.99, 0.005)"]
output = output[output['E_probs'] != "(0.025, 0.95, 0.025)"]
output = output[output['E_probs'] != "(0.15, 0.7, 0.15)"]

output = output[output['overtimeC'] != 1.25]
output = output[output['overtimeC'] != 1.75]

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
    print(output.groupby(parameter_columns[c])[cost_perc_columns].aggregate(['min','mean', 'max']).to_latex(
        float_format="{:.2f}%".format))

# for c in range(len(parameter_columns)):
#     print(output.groupby(parameter_columns[c])[perc_columns].mean().to_latex(
#         float_format="{:.2f}%".format))

# for c in range(len(parameter_columns)):
#     print(output.groupby(parameter_columns[c])[threshold_columns].mean().to_latex(
#         float_format="{:.2f}".format))

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

# ------------------------------------------------------------------------------------------------------------
# Plot bar chart with cost split
print("Plot bar chart")

labels = ("Optimal", "Basic", "Shift-based")

fig, ax = plt.subplots()
per_split = {
        "Day shift": np.array(output[["shiftC_o", "shiftC_b", "shiftC_c"]].mean()),
        "Night shift": np.array(output[["overtimeC_o", "overtimeC_b", "overtimeC_c"]].mean()),
        # "Early reward": np.hstack((np.array(output[output["LeadTime"] == 0][["earlyC_o", "earlyC_b", "earlyC_c"]].mean()),
        #                            np.array(output[output["LeadTime"] == 2][["earlyC_o", "earlyC_b", "earlyC_c"]].mean()),
        #                            np.array(output[output["LeadTime"] == 14][["earlyC_o", "earlyC_b", "earlyC_c"]].mean()))).ravel(),
        "Unfinished cost": np.array(output[["phaseC_o", "phaseC_b", "phaseC_c"]].mean())
}
print(per_split.items())
colors = ("black", "gray", "lightgray")
bottom = np.zeros(3)
c = 0
for name, split in per_split.items():
    p = ax.barh(labels, split, 0.5, label=name, left=bottom, color=colors[c])
    c += 1
    bottom += split

ax.invert_yaxis()
ax.set_xlim(0, 40)
# ax.set_ylim(-0.3, 2.5)
ax.set_xlabel("Cost")
# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
# Put a legend to the right of the current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.17), ncol=3, frameon=False)
fig.set_size_inches(5, 2.2)
plt.subplots_adjust(left=0.16, right=0.95, top=0.9, bottom=0.2)
# plt.tight_layout
plt.savefig("Cost_split_all.pdf")
plt.show()

# ------------------------------------------------------------------
# Lead time

labels = ("Optimal L=0", "Optimal L=2", "Optimal L=14")

fig, ax = plt.subplots()
per_split = {
        "Day shift": np.hstack((np.array(output[output["LeadTime"] == 0][["shiftC_o"]].mean()),  # ), "shiftC_b", "shiftC_c"]].mean()),
                                np.array(output[output["LeadTime"] == 2][["shiftC_o"]].mean()),  # , "shiftC_b", "shiftC_c"]].mean()),
                                np.array(output[output["LeadTime"] == 14][["shiftC_o"]].mean()))).ravel(),  # , "shiftC_b", "shiftC_c"]].mean()))).ravel(),
        "Night shift": np.hstack((np.array(output[output["LeadTime"] == 0][["overtimeC_o"]].mean()),  # , "overtimeC_b", "overtimeC_c"]].mean()),
                                  np.array(output[output["LeadTime"] == 2][["overtimeC_o"]].mean()),  # , "overtimeC_b", "overtimeC_c"]].mean()),
                                  np.array(output[output["LeadTime"] == 14][["overtimeC_o"]].mean()))).ravel(),  # , "overtimeC_b", "overtimeC_c"]].mean()))).ravel(),
        # "Early reward": np.hstack((np.array(output[output["LeadTime"] == 0][["earlyC_o", "earlyC_b", "earlyC_c"]].mean()),
        #                            np.array(output[output["LeadTime"] == 2][["earlyC_o", "earlyC_b", "earlyC_c"]].mean()),
        #                            np.array(output[output["LeadTime"] == 14][["earlyC_o", "earlyC_b", "earlyC_c"]].mean()))).ravel(),
        "Unfinished cost": np.hstack((np.array(output[output["LeadTime"] == 0][["phaseC_o"]].mean()),  # , "phaseC_b", "phaseC_c"]].mean()),
                                      np.array(output[output["LeadTime"] == 2][["phaseC_o"]].mean()),  # , "phaseC_b", "phaseC_c"]].mean()),
                                      np.array(output[output["LeadTime"] == 14][["phaseC_o"]].mean()))).ravel()  # , "phaseC_b", "phaseC_c"]].mean()))).ravel()
}
colors = ("black", "gray", "lightgray")
bottom = np.zeros(3)
c = 0
print(per_split.items)

for name, split in per_split.items():
    p = ax.barh(labels, split, 0.5, label=name, left=bottom, color=colors[c])
    c += 1
    bottom += split

ax.invert_yaxis()
ax.set_xlim(0, 55)
ax.set_xlabel("Cost")
ax.legend(loc="upper right", frameon=False)
fig.set_size_inches(6, 2.3)
plt.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)
# plt.tight_layout
plt.savefig("Cost_split_Leadtime_opt.pdf")
plt.show()

# ----------------------
# Plot cost split for uncertainty


labels = ("Optimal deterministic", "Optimal low uncertainty", "Optimal medium uncertainty", "Optimal high uncertainty")

fig, ax = plt.subplots()
per_split = {
        "Day shift": np.hstack((np.array(output[output["E_probs"] == "(0.0, 1.0, 0.0)"][["shiftC_o"]].mean()),
                                np.array(output[output["E_probs"] == "(0.05, 0.9, 0.05)"][["shiftC_o"]].mean()),
                                np.array(output[output["E_probs"] == "(0.1, 0.8, 0.1)"][["shiftC_o"]].mean()),
                                np.array(output[output["E_probs"] == "(0.2, 0.6, 0.2)"][["shiftC_o"]].mean()))).ravel(),
        "Night shift": np.hstack((np.array(output[output["E_probs"] == "(0.0, 1.0, 0.0)"][["overtimeC_o"]].mean()),
                                  np.array(output[output["E_probs"] == "(0.05, 0.9, 0.05)"][["overtimeC_o"]].mean()),
                                  np.array(output[output["E_probs"] == "(0.1, 0.8, 0.1)"][["overtimeC_o"]].mean()),
                                  np.array(output[output["E_probs"] == "(0.2, 0.6, 0.2)"][["overtimeC_o"]].mean()))).ravel(),
        "Unfinished cost": np.hstack((np.array(output[output["E_probs"] == "(0.0, 1.0, 0.0)"][["phaseC_o"]].mean()),
                                      np.array(output[output["E_probs"] == "(0.05, 0.9, 0.05)"][["phaseC_o"]].mean()),
                                      np.array(output[output["E_probs"] == "(0.1, 0.8, 0.1)"][["phaseC_o"]].mean()),
                                      np.array(output[output["E_probs"] == "(0.2, 0.6, 0.2)"][["phaseC_o"]].mean()))).ravel()
}

# per_split = {
#         "Day shift": np.hstack((np.array(output[output["Uncertainty"] == 0.0][["shiftC_o", "shiftC_b", "shiftC_c"]].mean()),
#                                 np.array(output[output["Uncertainty"] == 0.1][["shiftC_o", "shiftC_b", "shiftC_c"]].mean()),
#                                 np.array(output[output["Uncertainty"] == 0.2][["shiftC_o", "shiftC_b", "shiftC_c"]].mean()),
#                                 np.array(output[output["Uncertainty"] == 0.4][["shiftC_o", "shiftC_b", "shiftC_c"]].mean()))).ravel(),
#         "Night shift": np.hstack((np.array(output[output["Uncertainty"] == 0.0][["overtimeC_o", "overtimeC_b", "overtimeC_c"]].mean()),
#                                   np.array(output[output["Uncertainty"] == 0.1][["overtimeC_o", "overtimeC_b", "overtimeC_c"]].mean()),
#                                   np.array(output[output["Uncertainty"] == 0.2][["overtimeC_o", "overtimeC_b", "overtimeC_c"]].mean()),
#                                   np.array(output[output["Uncertainty"] == 0.4][["overtimeC_o", "overtimeC_b", "overtimeC_c"]].mean()))).ravel(),
#         "Unfinished cost": np.hstack((np.array(output[output["Uncertainty"] == 0.0][["phaseC_o", "phaseC_b", "phaseC_c"]].mean()),
#                                       np.array(output[output["Uncertainty"] == 0.1][["phaseC_o", "phaseC_b", "phaseC_c"]].mean()),
#                                       np.array(output[output["Uncertainty"] == 0.2][["phaseC_o", "phaseC_b", "phaseC_c"]].mean()),
#                                       np.array(output[output["Uncertainty"] == 0.4][["phaseC_o", "phaseC_b", "phaseC_c"]].mean()))).ravel()
# }

colors = ("black", "gray", "lightgray")
bottom = np.zeros(4)
c = 0
for name, split in per_split.items():
    p = ax.barh(labels, split, 0.5, label=name, left=bottom, color=colors[c])
    c += 1
    bottom += split

ax.invert_yaxis()
ax.set_xlim(0, 55)
ax.set_xlabel("Cost")
ax.legend(loc="upper right", frameon=False)
fig.set_size_inches(6, 2.3)
plt.subplots_adjust(left=0.35, right=0.98, top=0.9, bottom=0.1)
# plt.tight_layout
plt.savefig("Cost_split_Uncertainty_opt.pdf")
plt.show()

# -----------------------------------------------------------------------
# Deadline

labels = ("Optimal T=50", "Optimal T=60", "Optimal T=70")

fig, ax = plt.subplots()
per_split = {
        "Day shift": np.hstack((np.array(output[output["alpha"] == 50][["shiftC_o"]].mean()),
                                np.array(output[output["alpha"] == 60][["shiftC_o"]].mean()),
                                np.array(output[output["alpha"] == 70][["shiftC_o"]].mean()))).ravel(),
        "Night shift": np.hstack((np.array(output[output["alpha"] == 50][["overtimeC_o"]].mean()),
                                  np.array(output[output["alpha"] == 60][["overtimeC_o"]].mean()),
                                  np.array(output[output["alpha"] == 70][["overtimeC_o"]].mean()))).ravel(),
        "Unfinished cost": np.hstack((np.array(output[output["alpha"] == 50][["phaseC_o"]].mean()),
                                      np.array(output[output["alpha"] == 60][["phaseC_o"]].mean()),
                                      np.array(output[output["alpha"] == 70][["phaseC_o"]].mean()))).ravel()
}
colors = ("black", "gray", "lightgray")
bottom = np.zeros(3)
c = 0
for name, split in per_split.items():
    p = ax.barh(labels, split, 0.5, label=name, left=bottom, color=colors[c])
    c += 1
    bottom += split

ax.invert_yaxis()
ax.set_xlim(0, 58)
ax.set_xlabel("Cost")
ax.legend(loc="upper right", frameon=False)
fig.set_size_inches(6, 2.3)
plt.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)
# plt.tight_layout
plt.savefig("Cost_split_Deadline_opt.pdf")
plt.show()

# ------------------------------------
# Overtime cost

labels = ("Optimal c=1.5", "Optimal c=2", "Optimal c=2.5")

fig, ax = plt.subplots()
per_split = {
        "Day shift": np.hstack((np.array(output[output["overtimeC"] == 1.5][["shiftC_o"]].mean()),
                                np.array(output[output["overtimeC"] == 2.0][["shiftC_o"]].mean()),
                                np.array(output[output["overtimeC"] == 2.5][["shiftC_o"]].mean()))).ravel(),
        "Night shift": np.hstack((np.array(output[output["overtimeC"] == 1.5][["overtimeC_o"]].mean()),
                                  np.array(output[output["overtimeC"] == 2.0][["overtimeC_o"]].mean()),
                                  np.array(output[output["overtimeC"] == 2.5][["overtimeC_o"]].mean()))).ravel(),
        "Unfinished cost": np.hstack((np.array(output[output["overtimeC"] == 1.5][["phaseC_o"]].mean()),
                                      np.array(output[output["overtimeC"] == 2.0][["phaseC_o"]].mean()),
                                      np.array(output[output["overtimeC"] == 2.5][["phaseC_o"]].mean()))).ravel()
}
print("OvertimeC")
print(per_split)
colors = ("black", "gray", "lightgray")
bottom = np.zeros(3)
c = 0
for name, split in per_split.items():
    p = ax.barh(labels, split, 0.5, label=name, left=bottom, color=colors[c])
    c += 1
    bottom += split

ax.invert_yaxis()
ax.set_xlim(0, 55)
ax.set_xlabel("Cost")
ax.legend(loc="upper right", frameon=False)
fig.set_size_inches(6, 2.3)
plt.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)
# plt.tight_layout
plt.savefig("Cost_split_OvertimeCost_opt.pdf")
plt.show()

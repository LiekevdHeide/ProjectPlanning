"""
Function to analyse the output of the experiments.
Input: -f file name (including directory)
"""
import argparse
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats


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

print("num rows ", len(output_og), "num cols ", len(output_og.columns))
output_og.dropna(inplace=True)

output_og.drop_duplicates(
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
print("num rows ", len(output_og), "num cols ", len(output_og.columns))

# check NaN entries
print("Any empty entries in dataframe? ", output_og.isnull().values.any())
print("Number of empty entries in output:", output_og.isnull().sum().sum())

output_og["optimal_pol"] = (output_og["threshold_pol_basic"] == False) & (
        output_og["threshold_pol_cost"] == False
)

output_og["alpha"] = output_og["Deadline"] - output_og["LeadTime"]
# output_og["alpha"] -= (output_og["NumPhases"] * 5 * 2)

print(output_og)

checkRuns = (
    output_og[["LeadTime", "E_probs", "overtimeC"]]
    .groupby(["LeadTime", "E_probs"])
    .count()
)
print(checkRuns)

check_pol = (
    output_og[["optimal_pol", "LeadTime", "E_probs", "overtimeC"]]
    .groupby(["optimal_pol", "LeadTime", "E_probs"])
    .count()
)
print(check_pol)

# Separate into different tables dependent on policy
output_opt = output_og.loc[output_og["optimal_pol"]]
output_basic = output_og.loc[output_og["threshold_pol_basic"]]
output_cost = output_og.loc[output_og["threshold_pol_cost"]]

output_opt = output_opt.drop(columns=[
    "threshold_pol_basic", "threshold_pol_cost", "optimal_pol", "threshold_val"
])
output_basic = output_basic.drop(columns=[
    "threshold_pol_basic", "threshold_pol_cost", "optimal_pol"
])
output_cost = output_cost.drop(columns=[
    "threshold_pol_basic", "threshold_pol_cost", "optimal_pol"
])

print(
    "Lengths of tables:", "opt:", len(output_opt.index),
    "basic:", len(output_basic.index),
    "cost:", len(output_cost.index)
)

assert len(output_opt.index) == len(output_basic.index), (
    f"Number of optimal experiments differs from basic threshold:"
    f"Optimal: {len(output_opt.index)} basic: {len(output_basic.index)}"
)

assert len(output_opt.index) == len(output_cost.index), (
    f"Number of optimal experiments differs from cost threshold:"
    f"Optimal: {len(output_opt.index)} basic: {len(output_cost.index)}"
)

# Add basic threshold solution as a column
output = pd.merge(output_opt, output_basic,  # .reset_index(),
                  on=["Deadline", "LeadTime", "NumPhases", "WorkPerPhase",
                      "E_values", "E_probs", "shiftC",
                      "shiftC_avg", "overtimeC", "phaseC", "earlyC", "alpha"],
                  validate="one_to_one", suffixes=("_o", "_b"))

# Add cost threshold solution as a column
output = pd.merge(output, output_cost,  # .reset_index(),
                  on=["Deadline", "LeadTime", "NumPhases", "WorkPerPhase",
                      "E_values", "E_probs", "shiftC",
                      "shiftC_avg", "overtimeC", "phaseC", "earlyC", "alpha"],
                  validate="one_to_one", suffixes=("", "_c"))

# Add the cost suffix to all columns from the cost threshold policy
cols = ["Filename", "solution_cost", "runtime",
        "split_shiftC", "split_overtimeC", "split_phaseC", "split_earlyC"]
output.rename(
    columns={c: c + '_c' for c in output.columns if c in cols}, inplace=True
)
output.rename(
    columns={"threshold_val": "threshold_val_b"}, inplace=True
)

print(output.columns)

output['basic_perc'] = output['solution_cost_b']
output['basic_perc'] -= output['solution_cost_o']
output['basic_perc'] /= output['solution_cost_o']
output['basic_perc'] *= 100
output['cost_perc'] = output['solution_cost_c']
output['cost_perc'] -= output['solution_cost_o']
output['cost_perc'] /= output['solution_cost_o']
output['cost_perc'] *= 100
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
    for idx_c in range(0, 3, 1):
        ax.scatter(x=plotUncertainty["Uncertainty"], y=plotUncertainty[cost_columns[idx_c]])

    # set locations and names of the labels
    plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4])
    plt.title(f"Impact of uncertainty for lead time {leadTimes[idx_l]}")
    # plt.show()

    fig, ax = plt.subplots()
    plotUncertainty.plot(ax=ax, x="Uncertainty", y=cost_columns, kind="line")
    plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4])
    plt.title(f"Lead time {leadTimes[idx_l]}")
    plt.show()

# Plot overtimes
for idx_l in range(0, leadTimes.size, 1):
    plotOvertime = output[(output["LeadTime"] == leadTimes[idx_l]) & (output["alpha"] == 60) & (0.199 < output["Uncertainty"]) & (output["Uncertainty"] < 0.201)]
    plotOvertime = plotOvertime.sort_values(by=["overtimeC"])
    plotOvertime.plot(x="overtimeC", y=cost_columns, kind="line")
    plt.title(f"Impact of overtime cost for lead time {leadTimes[idx_l]} ")
    plt.show()

"""
Function to analyse the output of the experiments.
Input: -f file name (including directory)
"""
import argparse
import pandas as pd
# import matplotlib
# import matplotlib.pyplot as plt
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

output_og = output_og[output_og["LeadTime"] <= 14]

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

output_opt = output_opt.drop(columns=["threshold_pol_basic", "threshold_pol_cost", "optimal_pol", "threshold_val"])
output_basic = output_basic.drop(columns=["threshold_pol_basic", "threshold_pol_cost", "optimal_pol"])
output_cost = output_cost.drop(columns=["threshold_pol_basic", "threshold_pol_cost", "optimal_pol"])

print("Lengths of tables:", "opt:", len(output_opt.index), "basic:", len(output_basic.index), "cost:",
      len(output_cost.index))

assert len(output_opt.index) == len(output_basic.index), (f"Number of optimal experiments differs from basic threshold:"
                                                          f"Optimal: {len(output_opt.index)} basic: {len(output_basic.index)}")

assert len(output_opt.index) == len(output_cost.index), (f"Number of optimal experiments differs from cost threshold:"
                                                         f"Optimal: {len(output_opt.index)} basic: {len(output_cost.index)}")

output = pd.merge(output_opt, output_basic,  # .reset_index(),
                  on=["Deadline", "LeadTime", "NumPhases", "WorkPerPhase", "E_values", "E_probs", "shiftC",
                      "shiftC_avg", "overtimeC", "phaseC", "earlyC"],
                  validate="one_to_one", suffixes=("_opt", "_basic"))

output = pd.merge(output, output_cost,  # .reset_index(),
                  on=["Deadline", "LeadTime", "NumPhases", "WorkPerPhase", "E_values", "E_probs", "shiftC",
                      "shiftC_avg", "overtimeC", "phaseC", "earlyC"],
                  validate="one_to_one", suffixes=("", "_cost"))
cols = ["Filename", "solution_cost", "runtime"]
output.rename(columns={c: c+'_cost' for c in output.columns if c in cols}, inplace=True)
output.rename(columns={"threshold_val": "threshold_val_basic"}, inplace=True)

print(output.columns)

output['basic_perc'] = output['solution_cost_basic'] - output['solution_cost_opt']
output['basic_perc'] /= output['solution_cost_opt']
output['basic_perc'] *= 100
output['cost_perc'] = output['solution_cost_cost'] - output['solution_cost_opt']
output['cost_perc'] /= output['solution_cost_opt']
output['cost_perc'] *= 100
# --------------------------------------------------------------------------------------------------------------------
# Overall differences:
costVopt = stats.ttest_rel(output['solution_cost_basic'], output['solution_cost_opt'], alternative='greater')
basicVopt = stats.ttest_rel(output['solution_cost_cost'], output['solution_cost_opt'], alternative='greater')
basicVcost = stats.ttest_rel(output['basic_perc'], output['cost_perc'], alternative='greater')

print(f"T tests for differences in costs and in percentage difference result in: "
      f"Cost versus optimal: {costVopt}, basic versus optimal: {basicVopt} "
      f"And the relative/percentage difference is: {basicVcost} ")

cost_columns = ["solution_cost_opt", "solution_cost_basic", "solution_cost_cost"]
perc_columns = ["basic_perc", "cost_perc"]
# Averages:
mean_costs = output[cost_columns].mean()
print(f"The mean cost are (opt, basic, cost):\n{mean_costs}")

mean_perc = output[["basic_perc", "cost_perc"]].mean()
print(f"The mean percentage differences are (basic, cost):\n{mean_perc}")

# For different parameter levels:
# ? deadline? freq?
parameter_columns = ["Deadline", "LeadTime", "E_probs", "overtimeC", "earlyC"]
print(output.groupby(parameter_columns)[cost_columns].count())
par_levels = output.groupby(parameter_columns)[cost_columns].mean()
print(par_levels)
for c in range(len(parameter_columns)):
    print(output.groupby(parameter_columns[c])[cost_columns].mean().to_latex(float_format="{:.2f}".format))

for c in range(len(parameter_columns)):
    print(output.groupby(parameter_columns[c])[perc_columns].mean().to_latex(float_format="{:.2f}".format))

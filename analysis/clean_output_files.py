import pandas as pd


def clean(output_og):
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

    return output

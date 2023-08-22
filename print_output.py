"""
Function to print the output of the experiment.
Inputs: Current setting (including optimal/benchmark).
Outputs: .csv file with the results (and setting) with a relevant name.
"""
import os
import pandas as pd
import sys


def write_setting(file_name, setting, solution_cost, runtime):
    file_name += '.csv'
    # check if file already exists
    # df = pd.DataFrame.from_dict(vars(setting), orient='index')
    # print(df)

    with open(file_name, 'a', newline='') as csvfile:
        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            print("This file already exists and is non-empty.")
        else:
            # write header
            csvfile.write("Filename;")
            csvfile.write(";".join(vars(setting).keys()))
            csvfile.write(";" + "solution_cost;runtime" + "\n")

        # write values
        csvfile.write(f"{file_name};")
        csvfile.write(";".join(f'{value}' for key, value in vars(setting).items()))
        csvfile.write(f";{solution_cost};{runtime}\n")


def combine_files(path, output_name):
    combination = pd.DataFrame()
    print("Combine the following files:")
    for x in os.listdir(path):
        if x.endswith(".csv"):
            print(x)
            current_file = pd.read_csv(path + x, sep=';', header=0)
            combination = pd.concat([combination, current_file],
                                    ignore_index=True, sort=False)

        # allFiles.drop_duplicates(subset=[])
        # allFiles['excSeed'].value_counts()
        # allFiles.loc[allFiles['excSeed'] == 400]['simulSeed'].value_counts()

        combination.to_csv(path + output_name + '.csv',
                           index=False, sep=';', decimal='.')


if __name__ == "__main__":
    combine_files(*sys.argv[1:])

"""
Function to print the output of the experiment.
Inputs: Current setting (including optimal/benchmark).
Outputs: .csv file with the results (and setting) with a relevant name.
"""


def write_header(file_name, setting):
    print(vars(setting))
    # {'kids': 0, 'name': 'Dog', 'color': 'Spotted', 'age': 10, 'legs': 2, 'smell': 'Alot'}
    # now dump this in some way or another
    # attrs = vars(an)
    print(', '.join("%s: %s" % item for item in vars(setting).items()))

    with open(file_name, "a") as output_header:
        output_header.write(
            ""
        )

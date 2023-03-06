"""
Test function for the terminalValueFunction.
"""
import terminalValueFunction
import SettingsDictionary

sDict = SettingsDictionary.Settings


def create_setting(input_type):
    setting = [0, 0, 0]
    if input_type == "basic":
        setting[sDict.Deadline] = 0
        setting[sDict.NumPhases] = 0
        setting[sDict.LeadTime] = 0
    else:
        setting[sDict.Deadline] = 0
        setting[sDict.NumPhases] = 1
        setting[sDict.LeadTime] = 0
    setting = tuple(setting)
    return setting


def test_answer():
    cost = terminalValueFunction.final_costs(
        create_setting("basic"), shift_cost=0, schedule=(0,), phase=0, time=0,
    )
    assert cost == 0, "Final costs not zero if zero costs"


"""
TO ADD: - test if work remaining costlier than no work remaining
        - test if in final phase less costly than in previous phase
        - test if cost is as expected for a very simple example
        - test if t=T cost correct
"""

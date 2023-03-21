"""
The SettingsDictionary contains the standard settings for one run of the
gFunction optimal shift decision calculations. It contains the location
of the deadline, lead time, total number of phases and the tuple of the shift
costs in the tuple used as input to the g_function.
"""

from enum import IntEnum


class Settings(IntEnum):
    Deadline = 0
    ShiftCost = 1
    LeadTime = 2
    NumPhases = 3
    WorkPerPhase = 4
    E_Values = 5
    E_probs = 6
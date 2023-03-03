"""
The SettingsDictionary contains the standard settings for one run of the
gFunction optimal shift decision calculations. It contains the location
of the deadline, lead time, total number of phases and the tuple of the shift
costs in the tuple used as input to the g_function.
"""

from enum import IntEnum


class Settings(IntEnum):
    Deadline = 0
    LeadTime = 1
    NumPhases = 2
    ShiftCost = 3

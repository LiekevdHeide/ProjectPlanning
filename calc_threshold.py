"""
Function to calculate if we would schedule using the upper and lower threshold values.
Calculates the measure to compare against the thresholds for all phases.
!ONLY WORKS FOR 2 PHASES!
inputs: setting, remaining work, current schedule, current phase, current time
output: scheduling decision y/n
"""


def measure(
        setting, remaining: int, schedule: tuple[int], phase: int, t: int
) -> bool:

    # Works very well for 1 shiftC type
    # If multiple, needs a diff threshold for each phase.
    # for p in range(phase, setting.NumPhases):
    #     val = remaining + sum(setting.WorkPerPhase[phase:p])
    #     val -= sum(schedule[:setting.LeadTime])
    #     val /= setting.Deadline - (t + setting.LeadTime - 1)
    # # # #     # val *= setting.shiftC[t + setting.LeadTime] does the opposite of what we want
    # # # #     # val /= setting.shiftC[t + setting.LeadTime] does not help: still > 0
    # # # #     # Only do expensive shift if REALLY need it -> near UB
    # # #     if setting.bench_LB < val <= setting.bench_UB:
    # # #         return True
    #     if setting.shiftC[t + setting.LeadTime] == setting.overtimeC:
    #         # val -= 0.2
    #         if 0.1 + setting.bench_LB < val <= setting.bench_UB:
    #             return True
    #     else:
    #         if setting.bench_LB < val <= setting.bench_UB:
    #             return True

    # B:
    # val = remaining + sum(setting.WorkPerPhase[phase:setting.NumPhases - 1])
    # val -= sum(schedule[:setting.LeadTime])
    # val /= (setting.Deadline - (t + setting.LeadTime - 1))
    # val /= setting.shiftC[t + setting.LeadTime] ** 2
    # if val > 0.1:
    #     return True

    # new idea:
    val_this_phase = remaining - sum(schedule[:setting.LeadTime])
    val_this_phase /= setting.Deadline - (t + setting.LeadTime - 1)
    if val_this_phase > 1.0:  # or val_this_phase <= 0.0:
        return False
    if setting.shiftC[t + setting.LeadTime] < setting.overtimeC:
        # print(val_this_phase)
        return True
    elif val_this_phase > 0.3:  # frequency == 2 -> 0.5?, frequency == 3 -> 0.6/0.7 f==4 -> 0.6
        return True

    return False
    # return True

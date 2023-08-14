"""
Function to calculate if we would schedule using a threshold value.
Calculates the measure to compare against the thresholds for all phases.
Uses either the basic policy, or the cost-based threshold policy
!ONLY WORKS FOR 2 PHASES!
inputs: setting, remaining work, current schedule, current phase, current time
output: scheduling decision y/n
"""


def measure(
        setting, remaining: int, schedule: tuple[int], phase: int, t: int
) -> bool:
    if setting.threshold_pol_basic:
        return measure_basic(setting, remaining, schedule, phase, t)
    elif setting.threshold_pol_cost:
        return measure_cost(setting, remaining, schedule, phase, t)

    assert False, (
        "You are using the benchmark policy, but no threshold policy is True."
    )


def measure_basic(
        setting, remaining: int, schedule: tuple[int], phase: int, t: int
) -> bool:

    # B:
    val = remaining + sum(setting.WorkPerPhase[phase:setting.NumPhases - 1])
    val -= sum(schedule[:setting.LeadTime])
    val /= (setting.Deadline - (t + setting.LeadTime - 1))
    if val > setting.threshold_val:
        return True

    return False


def measure_cost(
        setting, remaining: int, schedule: tuple[int], phase: int, t: int
) -> bool:
    val = remaining + sum(setting.WorkPerPhase[phase:setting.NumPhases - 1])
    val -= sum(schedule[:setting.LeadTime])
    val /= (setting.Deadline - (t + setting.LeadTime - 1))
    val /= (setting.shiftC[t + setting.LeadTime] / setting.shiftC_avg)
    if val > setting.threshold_val:
        return True

    return False

    # Include costs in threshold policy.

    # val_this_phase = remaining - sum(schedule[:setting.LeadTime])
    # val_this_phase /= setting.Deadline - (t + setting.LeadTime - 1)
    # if val_this_phase > 1.0:  # or val_this_phase <= 0.0:
    #     return False
    # if setting.shiftC[t + setting.LeadTime] < setting.overtimeC:
    #     # print(val_this_phase)
    #     return True
    # elif val_this_phase > 0.3:
    #     # frequency == 2 -> 0.5?, frequency == 3 -> 0.6/0.7 f==4 -> 0.6
    #     return True
    #
    # return False

    # Works very well for 1 shiftC type
    # If multiple, needs a diff threshold for each phase.
    # for p in range(phase, setting.NumPhases):
    #     val = remaining + sum(setting.WorkPerPhase[phase:p])
    #     val -= sum(schedule[:setting.LeadTime])
    #     val /= setting.Deadline - (t + setting.LeadTime - 1)
    # # # #     # val *= setting.shiftC[t + setting.LeadTime]
    # does the opposite of what we want
    # # # #     # val /= setting.shiftC[t + setting.LeadTime]
    # does not help: still > 0
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

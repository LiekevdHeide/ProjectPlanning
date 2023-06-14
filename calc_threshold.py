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
    for p in range(phase, setting.NumPhases):
        val = remaining + sum(setting.WorkPerPhase[phase:p])
        val -= sum(schedule[:setting.LeadTime])
        val /= setting.Deadline - (t + setting.LeadTime - 1)
        if setting.shiftC[t + setting.LeadTime] == setting.overtimeC:
            if 0.1 + setting.bench_LB < val <= 0.3 * setting.bench_UB:
                return True
        else:
            if setting.bench_LB < val <= setting.bench_UB:
                return True

    # Brams:
    # val = remaining + sum(setting.WorkPerPhase[phase:setting.NumPhases - 1])
    # val -= sum(schedule[:setting.LeadTime])
    # val /= (setting.Deadline - (t + setting.LeadTime - 1))
    # val /= setting.shiftC[t + setting.LeadTime]
    # if val > 0.1:
    #     return True

    return False

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
    for p in range(phase, setting.NumPhases):
        val = remaining + sum(setting.WorkPerPhase[phase:p])
        val -= sum(schedule[:setting.LeadTime])
        val /= setting.Deadline - (t + setting.LeadTime - 1)
        if setting.bench_LB < val <= setting.bench_UB:
            return True

    return False

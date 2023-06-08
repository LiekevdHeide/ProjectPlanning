
def measure(
        setting, remaining: int, schedule: tuple[int], phase: int, t: int
) -> float:
    val = remaining + sum(setting.WorkPerPhase[phase + 1:])
    val -= sum(schedule[:setting.LeadTime - 1])
    val /= setting.Deadline - (t + setting.LeadTime - 1)
    return val

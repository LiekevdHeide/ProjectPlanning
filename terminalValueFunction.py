"""
Terminal value functions added cost at:
(1) Deadline
(2) Project finished (before deadline)
"""


def final_costs(time_until_deadline, remaining_work):
    print("before deadline:", time_until_deadline, "remaining work", remaining_work)
    # if before deadline: -10 per shift, if after deadline 10*remaining shifts
    return time_until_deadline * -10 + max(remaining_work, 0) * 10

"""
Plot the planning (as given by the model) per phase, current time
and remaining work.
Input: schedule for each phase, time and remaining work:
        Do we schedule the shift at time+L?
Output: plot with colors to indicate if we schedule in lead time L
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["font.family"] = "Helvetica"


def create(setting, planning):
    if setting.LeadTime > 3:
        "This instance is too large to plot."
        return
    # Create figure with subplots: numPhases x leadTime
    fig, axarr = plt.subplots(
        setting.NumPhases, max(1, 2**setting.LeadTime)
    )  # , sharex=True
    # size of figure based on number of columns
    fig.set_size_inches(2.5 * max(1, 2**setting.LeadTime),
                        0.5 + 1.8 * setting.NumPhases)
    # Create title for combined plot.
    title = f"Schedule for each phase leadtime {setting.LeadTime}"
    if setting.threshold_pol_basic:
        title += ", benchmark_b"
    elif setting.threshold_pol_cost:
        title += ", benchmark_c"
    fig.suptitle(title, fontsize=16)

    # if lead time = 0: only one column -> index is 1 value
    if setting.LeadTime == 0:
        index = 0
    else:
        index = (0, 0)
    # create one plot with name, so we can use its colors
    im = axarr[index].imshow(
        planning[0, 0], cmap=plt.cm.Purples, interpolation="none"
    )
    for i in range(setting.NumPhases):
        for j in range(max(1, 2**setting.LeadTime)):
            # if lead time = 0: only one column -> index is 1 value
            if setting.LeadTime == 0:
                index = (i,)
            else:
                index = (i, j)
            if sum(index) != 0:
                axarr[index].imshow(
                    planning[j, i], cmap=plt.cm.Purples, interpolation="none"
                )

    for i in range(setting.NumPhases):
        for j in range(max(1, 2**setting.LeadTime)):
            # Index = location of subplot [x, y] coordinate
            if setting.LeadTime == 0:
                index = i
            else:
                index = (i, j)
            if j == 0:
                axarr[index].set_ylabel("Remaining work")
            axarr[index].set_xlabel("Time")
            if setting.LeadTime == 0:
                axarr[index].set_title(f"Phase {i + 1}")
            if setting.LeadTime > 1:
                plan = f"{j:0{setting.LeadTime}b}"[::-1]
                axarr[index].set_title(
                    f"Phase {i + 1}, plan {plan}?"
                )
            axarr[index].invert_yaxis()

            # x labels
            # Major ticks for the axis labels
            axarr[index].xaxis.set_major_locator(
                mticker.MaxNLocator(min(10, setting.Deadline), integer=True)
            )
            # x label values
            ticks_loc = axarr[index].get_xticks().tolist()
            axarr[index].xaxis.set_major_locator(
                mticker.FixedLocator(ticks_loc)
            )
            axarr[index].set_xticklabels([int(x + 1) for x in ticks_loc])

            # y labels
            # make sure it's not too cluttered
            axarr[index].yaxis.set_major_locator(
                mticker.MaxNLocator(
                    min(5, setting.WorkPerPhase[i]), integer=True
                )
            )
            # y label values
            ticks_loc = axarr[index].get_yticks().tolist()
            axarr[index].yaxis.set_major_locator(
                mticker.FixedLocator(ticks_loc)
            )
            axarr[index].set_yticklabels([int(y + 1) for y in ticks_loc])

            # Minor ticks to add the gridlines
            axarr[index].set_yticks(
                np.arange(0.5, setting.WorkPerPhase[i] - 1), minor=True
            )
            axarr[index].set_xticks(
                np.arange(0.5, setting.Deadline - 1), minor=True
            )
            # Gridlines based on minor ticks
            axarr[index].grid(
                which="minor", color="w", linestyle="-", linewidth=1.5
            )
            # Remove minor ticks
            axarr[index].tick_params(
                which="minor", bottom=False, top=False, left=False
            )

    # Get the colors of the values, according to the
    # colormap used by imshow, used in plot[0,0]
    colors = [im.cmap(im.norm(value)) for value in [0, 1]]
    # Create a patch (proxy artist) for every color.
    patches = [
        mpatches.Patch(color=colors[0], label="Don't schedule".format()),
        mpatches.Patch(color=colors[1], label="Schedule".format()),
    ]
    # Put those patched as legend-handles into the legend
    plt.figlegend(
        handles=patches,
        loc="upper right",
        ncol=3,
        bbox_to_anchor=(0.99, 0.965),
        frameon=False,
    )
    plt.tight_layout()
    # fig.subplots_adjust(top=0.88) # in combination with tight_layout
    # plt.savefig(
    #     f"Plot_schedule_{setting.WorkPerPhase[0]}{setting.LeadTime}.pdf"
    # )
    plt.show()
    plt.close()

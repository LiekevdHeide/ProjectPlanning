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
import SettingsDictionary

matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["font.family"] = "Helvetica"
sDict = SettingsDictionary.Settings


def create(setting, planning):
    fig, axarr = plt.subplots(setting[sDict.NumPhases], setting[sDict.LeadTime] + 1)  # , sharex=True
    fig.set_size_inches(5, 2.5 * setting[sDict.NumPhases])
    fig.suptitle(
        f"Schedule for each phase leadtime {setting[sDict.LeadTime]}",
        fontsize=16,
    )
    if setting[sDict.LeadTime] == 0:
        index = 0
    else:
        index = (0, 0)
    im = axarr[index].imshow(planning[0, 0], cmap=plt.cm.autumn, interpolation="none")
    for i in range(setting[sDict.NumPhases]):
        for j in range(setting[sDict.LeadTime] + 1):
            if setting[sDict.LeadTime] == 0:
                index = (i,)
            else:
                index = (i, j)
            if sum(index) != 0:
                axarr[index].imshow(planning[j, i], cmap=plt.cm.autumn, interpolation="none")

    for i in range(setting[sDict.NumPhases]):
        for j in range(setting[sDict.LeadTime] + 1):
            if setting[sDict.LeadTime] == 0:
                index = i
            else:
                index = (i, j)
            axarr[index].set_ylabel("Remaining work")
            axarr[index].set_xlabel("Time")
            if setting[sDict.LeadTime] == 0:
                axarr[index].set_title(f"Phase {i + 1}")
            if setting[sDict.LeadTime] == 1:
                axarr[index].set_title(f"Phase {i + 1}, plan ({j},?)")
            axarr[index].invert_yaxis()
            #    # Major ticks
            axarr[index].xaxis.set_major_locator(
                mticker.MaxNLocator(min(10, setting[sDict.Deadline]), integer=True)
            )
            ticks_loc = axarr[index].get_xticks().tolist()
            axarr[index].xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
            axarr[index].set_xticklabels([int(x + 1) for x in ticks_loc])

            axarr[index].yaxis.set_major_locator(
                mticker.MaxNLocator(
                    min(5, setting[sDict.WorkPerPhase][i]), integer=True
                )
            )
            ticks_loc = axarr[index].get_yticks().tolist()
            axarr[index].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
            axarr[index].set_yticklabels([int(y + 1) for y in ticks_loc])

            # Minor ticks
            axarr[index].set_yticks(
                np.arange(0.5, setting[sDict.WorkPerPhase][i] - 1), minor=True
            )
            axarr[index].set_xticks(
                np.arange(0.5, setting[sDict.Deadline] - 1), minor=True
            )

            # Gridlines based on minor ticks
            axarr[index].grid(which="minor", color="w", linestyle="-", linewidth=1.5)
            # Remove minor ticks
            axarr[index].tick_params(
                which="minor", bottom=False, top=False, left=False
            )

    # get the colors of the values, according to the
    # colormap used by imshow
    colors = [im.cmap(im.norm(value)) for value in [0, 0.5, 1]]
    # create a patch (proxy artist) for every color
    patches = [
        mpatches.Patch(color=colors[0], label="Don't schedule".format()),
        mpatches.Patch(color=colors[1], label="Indifferent".format()),
        mpatches.Patch(color=colors[2], label="Schedule".format()),
    ]
    # put those patched as legend-handles into the legend
    plt.figlegend(
        handles=patches,
        loc="upper right",
        ncol=3,
        bbox_to_anchor=(0.99, 0.965),
        frameon=False,
    )
    plt.tight_layout()
    # fig.subplots_adjust(top=0.88) # in combination with tight_layout
    # plt.savefig(f"Plot_schedule_{setting[sDict.WorkPerPhase][0]}_{setting[sDict.LeadTime]}.pdf")
    plt.show()
    plt.close()

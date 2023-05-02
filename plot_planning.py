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
    fig, axarr = plt.subplots(setting[sDict.NumPhases], 1)
    fig.set_size_inches(5, 2.5 * setting[sDict.NumPhases])
    fig.suptitle(f"Schedule for each phase leadtime {setting[sDict.LeadTime]}",
                 fontsize=16)
    im = axarr[0].imshow(planning[0], cmap=plt.cm.autumn, interpolation='none')
    for i in range(1, setting[sDict.NumPhases]):
        axarr[i].imshow(planning[i], cmap=plt.cm.autumn, interpolation='none')

    for i in range(setting[sDict.NumPhases]):
        axarr[i].set_ylabel("Remaining work")
        axarr[i].set_xlabel("Time")
        axarr[i].set_title(f'Phase {i + 1}')
        axarr[i].invert_yaxis()
    #    # Major ticks
        axarr[i].xaxis.set_major_locator(
            mticker.MaxNLocator(min(10, setting[sDict.Deadline]),
                                integer=True))
        ticks_loc = axarr[i].get_xticks().tolist()
        axarr[i].xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        axarr[i].set_xticklabels([int(x) for x in ticks_loc])

        axarr[i].yaxis.set_major_locator(
            mticker.MaxNLocator(min(5, setting[sDict.WorkPerPhase][i]),
                                integer=True))
        ticks_loc = axarr[i].get_yticks().tolist()
        axarr[i].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        axarr[i].set_yticklabels([int(y + 1) for y in ticks_loc])

        # Minor ticks
        axarr[i].set_yticks(
            np.arange(0.5, setting[sDict.WorkPerPhase][i] - 1), minor=True
        )
        axarr[i].set_xticks(
            np.arange(0.5, setting[sDict.Deadline] - 1), minor=True
        )

        # Gridlines based on minor ticks
        axarr[i].grid(which='minor', color='w', linestyle='-', linewidth=1.5)
        # Remove minor ticks
        axarr[i].tick_params(
            which='minor', bottom=False, top=False, left=False
        )

    # get the colors of the values, according to the
    # colormap used by imshow
    colors = [im.cmap(im.norm(value)) for value in [0, 1]]
    # create a patch (proxy artist) for every color
    patches = [
        mpatches.Patch(color=colors[0], label="Don't schedule".format()),
        mpatches.Patch(color=colors[1], label="Schedule".format())
    ]
    # put those patched as legend-handles into the legend
    plt.figlegend(handles=patches, loc='upper right', ncol=2,
                  bbox_to_anchor=(0.99, 0.965), frameon=False)
    plt.tight_layout()
    # fig.subplots_adjust(top=0.88) # in combination with tight_layout
    plt.savefig(f"Plot_schedule_{setting[sDict.WorkPerPhase][0]}.pdf")
    plt.show()
    plt.close()

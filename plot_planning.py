"""
Plot the planning (as given by the model) per phase, current time and remaining work.
Input: schedule for each phase, time and remaining work: Do we schedule the shift at time+L?
Output: plot with colors to indicate if we schedule in lead time L
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import SettingsDictionary

matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["font.family"] = "Helvetica"
sDict = SettingsDictionary.Settings


def create(setting, planning):
    extent = 1, setting[sDict.WorkPerPhase][0], 0, setting[sDict.Deadline]
    fig, axarr = plt.subplots(1, 3)  # , figsize=(12, 6))  # , frameon=False)
    fig.set_size_inches(6, 4)
    im = axarr[0].imshow(planning[0], cmap=plt.cm.autumn, interpolation='none',
                    extent=extent)
    axarr[1].imshow(planning[1], cmap=plt.cm.autumn, interpolation='none',
                    extent=extent)
    axarr[2].imshow(planning[2], cmap=plt.cm.autumn, interpolation='none',
                    extent=extent)

    for i in range(3):
        axarr[i].set_xlabel("Remaining work")
        axarr[i].set_ylabel("Time remaining")
        axarr[i].set_title(f'Phase {i}')
        axarr[i].invert_yaxis()
        # Major ticks
        axarr[i].set_xticks(np.arange(1, setting[sDict.WorkPerPhase][0] + 1))
        axarr[i].set_yticks(np.arange(0, setting[sDict.Deadline] + 1))
        # Minor ticks
        step_size = setting[sDict.WorkPerPhase][0] - 1
        step_size /= setting[sDict.WorkPerPhase][0]
        axarr[i].set_xticks(
            np.arange(1, setting[sDict.WorkPerPhase][0], step_size), minor=True)

        # Gridlines based on minor ticks
        axarr[i].grid(which='minor', color='w', linestyle='-', linewidth=2, axis='x')
        axarr[i].grid(which='major', color='w', linestyle='-', linewidth=2, axis='y')
        # Remove minor ticks
        axarr[i].tick_params(which='minor', bottom=False, left=False)

    # get the colors of the values, according to the
    # colormap used by imshow
    colors = [im.cmap(im.norm(value)) for value in [0, 1]]
    # create a patch (proxy artist) for every color
    patches = [mpatches.Patch(color=colors[0], label="Don't schedule".format(l=0)),
               mpatches.Patch(color=colors[1], label="Schedule".format(l=0))]
    # put those patched as legend-handles into the legend
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.tight_layout()
    plt.show()
    plt.close()

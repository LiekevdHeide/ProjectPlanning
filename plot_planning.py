"""
Plot the planning (as given by the model) per phase, current time
and remaining work.
Input: schedule for each phase, time and remaining work:
        Do we schedule the shift at time+L?
Output: plot with colors to indicate if we schedule in lead time L
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

from matplotlib import rc

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)
rc('font', **{'size': 10})


def create(setting, planning):
    if setting.LeadTime > 3:
        "This instance is too large to plot."
        return
    # Create figure with subplots: numPhases x leadTime
    fig, axarr = plt.subplots(
        max(1, 2**setting.LeadTime), setting.NumPhases, sharex=True, sharey=True
    )
    print(planning)
    # , sharex=True
    # size of figure based on number of columns
    # fig.set_size_inches(2.6 * max(1, 2**setting.LeadTime),
    #                     0.5 + 1.5 * setting.NumPhases)
    # fig.set_size_inches(6, 5)

    # Create title for combined plot.
    title = f"Schedule for each phase leadtime {setting.LeadTime}"
    if setting.threshold_pol_basic:
        title += ", basic threshold policy"
    elif setting.threshold_pol_cost:
        title += ", shift-based threshold policy"
    # fig.suptitle(title, fontsize=16)

    # if lead time = 0: only one column -> index is 1 value
    if setting.LeadTime == 0:
        index = 0
    else:
        index = (0, 0)
    # create one plot with name, so we can use its colors
    im = axarr[index].imshow(
        planning[0, 0], cmap=plt.cm.Greys, interpolation="none"
    )

    for i in range(max(1, 2**setting.LeadTime)):
        for j in range(setting.NumPhases):
            # if lead time = 0: only one column -> index is 1 value
            if setting.LeadTime == 0:
                index = (j,)
            else:
                index = (i, j)
            if sum(index) != 0:
                axarr[index].imshow(
                    planning[i, j], cmap=plt.cm.Greys, interpolation="none"
                )
            if setting.LeadTime == 2:
                axarr[index].axvline(x=1.5, color='red')

    for i in range(max(1, 2**setting.LeadTime)):
        for j in range(setting.NumPhases):
            # Index = location of subplot [x, y] coordinate
            if setting.LeadTime == 0:
                index = (j,)
            else:
                index = (i, j)
            if j == 0:
                axarr[index].set_ylabel("Work")  # "Remaining work")
            axarr[index].set_xlabel("Shift")

            # if setting.LeadTime == 0:
            #     axarr[index].set_title(f"Phase {j + 1}")
            # if setting.LeadTime > 1:
            #     plan = f"{i:0{setting.LeadTime}b}"[::-1]
            #     axarr[index].set_title(
            #         f"Phase {j + 1}, plan {plan}?"
            #     )

            # x labels
            # Major ticks for the axis labels
            axarr[index].xaxis.set_major_locator(
                mticker.MaxNLocator((setting.Deadline + setting.LeadTime) / 2, integer=True)
            )

            # x label values
            ticks_loc = axarr[index].get_xticks().tolist()
            # axarr[index].xaxis.set_major_locator(
            #     mticker.FixedLocator(ticks_loc)
            # )
            if setting.LeadTime == 0:
                axarr[index].set_xticks(ticks_loc)
                ticks_loc = [int(x + 1) for x in ticks_loc]
                axarr[index].set_xlim(left=-1, right=20)
            if setting.LeadTime == 1:
                ticks_loc = ticks_loc[setting.LeadTime + 1:]
                ticks_loc = ticks_loc[:-1]
                axarr[index].set_xticks(ticks_loc)
                ticks_loc = [int(x) for x in ticks_loc]
                # axarr[index].set_xlim(left=0, right=21)
            if setting.LeadTime == 2:
                ticks_loc = ticks_loc[setting.LeadTime:]  # No labels for all events before start project
                ticks_loc = ticks_loc[:-1]
                axarr[index].set_xticks(ticks_loc)
                ticks_loc = [int(x - 1) for x in ticks_loc]
            axarr[index].set_xticklabels(ticks_loc)  # [int(x + 1) for x in ticks_loc])
            # x_labels = [0, 0, 0, 0, 0] + list(range(1, setting.Deadline + 2))
            # axarr[index].set_xticklabels([0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19])

            # y labels
            # make sure it's not too cluttered
            axarr[index].yaxis.set_major_locator(
                mticker.MaxNLocator(
                    min(3, setting.WorkPerPhase[j]), integer=True
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
                np.arange(0.5, setting.WorkPerPhase[j] - 1), minor=True
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
    axarr[index].invert_yaxis()

    # Add caption only to top row:
    for j in range(setting.NumPhases):
        if setting.LeadTime == 0:
            axarr[j].set_title(f"Phase {j + 1}")
        else:
            axarr[(0, j)].set_title(f"Phase {j + 1}")
    for i in range(max(1, 2**setting.LeadTime)):
        if setting.LeadTime == 0:
            plan = f"{i:0{setting.LeadTime}b}"[::-1]
            # axarr[0].annotate(f"x=(.)", (-0.5, 0.5), xycoords='axes fraction',
            #                   rotation=0, va='center', fontsize=12)
        else:
            plan = f"{i:0{setting.LeadTime}b}"[::-1]
            if setting.LeadTime == 1:
                axarr[(i, 0)].annotate(f"x=({plan[0]})", (-0.5, 0.5), xycoords='axes fraction',
                                       rotation=0, va='center', fontsize=12)
            if setting.LeadTime == 2:
                axarr[(i, 0)].annotate(f"x=({plan[0]},{plan[1]})", (-0.5, 0.5), xycoords='axes fraction',
                                       rotation=0, va='center', fontsize=12)

    # Get the colors of the values, according to the
    # colormap used by imshow, used in plot[0,0]
    colors = [im.cmap(im.norm(value)) for value in [0, 1]]
    # Create a patch (proxy artist) for every color.
    patches = [
        mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[1], edgecolor='black', label="Schedule".format()),
        mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[0], edgecolor='black', label="Don't schedule".format()),
    ]

    # Put those patched as legend-handles into the legend
    if setting.LeadTime == 0:
        location = "upper left"
    if setting.LeadTime == 2:
        location = "lower left"
    plt.figlegend(
        handles=patches,
        loc=location,
        # ncol=2,
        # bbox_to_anchor=(0.99, 0.9999),  # 85),
        frameon=False,
    )

    # Hide x labels and tick labels for all but left or top most plots
    for ax in fig.get_axes():
        ax.label_outer()

    if setting.LeadTime == 0:
        fig.set_size_inches(6, 1.6)
    if setting.LeadTime == 2:
        fig.set_size_inches(6, 3.3)
    plt.tight_layout()
    # fig.subplots_adjust(top=0.88) # in combination with tight_layout
    pdf_title = f"vertical_Plot_"
    if setting.threshold_pol_basic:
        pdf_title += "ThresholdBasic_"
    if setting.threshold_pol_cost:
        pdf_title += "ThresholdShift_"
    if not setting.threshold_pol_basic and not setting.threshold_pol_cost:
        pdf_title += "OPT_"
    plt.savefig(
         pdf_title + f"_{setting.LeadTime}_{setting.E_probs}.pdf"
    )
    print(pdf_title)
    plt.show()
    plt.close()

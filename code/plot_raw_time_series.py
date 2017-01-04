from __future__ import division, print_function, absolute_import

import numpy as np
import matplotlib.pyplot as plt

from econtools import save_cli

from util.env import out_path
from util.style import navy, maroon
from clean.gather import data_clean


def plot_raw_timeseries(midterm=False, save=False, standalone=False):
    df = data_clean(midterm=midterm)
    df['low_white'] = df['pct_white'] < 50

    var = 'had_vra'
    avg_vra = df[df[var]].groupby('year')['turnout_vap'].mean()
    avg_oth = df[~df[var]].groupby('year')['turnout_vap'].mean()

    fig, ax = plt.subplots()
    ax.plot(avg_oth.index, avg_oth.values, linestyle='-',
            marker='o', color=navy, label='Non-VRA counties')
    ax.plot(avg_vra.index, avg_vra.values, linestyle='-',
            marker='^', color=maroon, label='VRA counties')

    # VRA start and finish lines
    vra_y0, vra_yT = 1965, 2014.75
    ax.axvline(vra_y0, linestyle='-', color='k')
    ax.axvline(vra_yT, linestyle='-', color='k')

    # VRA Period Lines
    if midterm:
        ylevel = .17
    else:
        ylevel = .35
    vra_y0, vra_yT = 1965, 2014.75
    ax.annotate("VRA In Force", xy=((vra_y0 + vra_yT)/2 - 2, ylevel),
                xytext=(-11, 0),
                textcoords='offset points')
    ax.annotate('',
                xy=((vra_y0, ylevel - .005)),
                xytext=((vra_yT, ylevel - .005)),
                arrowprops=dict(facecolor='r', arrowstyle='<->'))

    ticks = np.arange(df['year'].min(), df['year'].max() + 1, 8) + 4

    # Axes formatting
    ax.set_xticks(ticks)

    ax.margins(x=0.05)
    ax.grid(True, alpha=.2, color=navy, linestyle='-')
    ax.tick_params(top='off', bottom='off', left='off', right='off')

    ax.set_ylabel("Mean Voter Turnout")

    if standalone:
        fig.suptitle("The Voting Rights Act in North Carolina", fontsize=14)

    plt.legend(loc=4)

    if save:
        filepath = _set_filepath(midterm)
        fig.savefig(filepath, bbox_inches='tight')
    else:
        plt.show()

def _set_filepath(midterm):
    filepath = out_path('ts_had_vra_mean')
    if midterm:
        filepath += '_midterm'
    filepath += '.pdf'

    return filepath


if __name__ == '__main__':
    save = save_cli()
    if save:
        plot_raw_timeseries(midterm=True, save=save)
        plot_raw_timeseries(midterm=False, save=save)
    else:
        plot_raw_timeseries(save=save)

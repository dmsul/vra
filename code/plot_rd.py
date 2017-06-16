from __future__ import division, print_function, absolute_import

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import econtools.metrics as mt
from econtools import save_cli

from util.env import out_path
from util.style import navy, maroon
from analysis.rd import rd_data

bad_c = ('Stokes', 'Gaston', 'Cleveland')


def main_many_plots(save=False):
    pairs = (
        (2000, 2004),
        (2004, 2008),
        (2008, 2012),
        (2012, 2016),
    )
    for p in pairs:
        fig = plot_frd(*p)
        if save:
            filepath = out_path('plot_rd_{}_{}.pdf').format(*p)
            fig.savefig(filepath, bbox_inches='tight')


def main_old_plot(save=False):
    plot_frd(1964, 1968)


def plot_frd(year0, yearT):

    plot_df = rd_data(year0, yearT)

    diff_mean = plot_df['diff'].mean()
    plot_df['diff'] -= diff_mean

    res1 = mt.reg(plot_df, 'diff', ['run', 'low', 'run_low'],
                  addcons=True, vce_type='robust')
    print(res1.summary)

    x = np.linspace(plot_df['turnout_vap'].min(), plot_df['turnout_vap'].max(),
                    num=100)
    X = pd.DataFrame(x, columns=['run'])
    X['run'] -= .5  # cutoff
    X['low'] = (X['run'] < 0).astype(int)
    # X['mid'] = ((X['run'] >= 0) & (X['run'] < .1)).astype(int)
    X['run_low'] = X['run'] * X['low']
    # X['run_mid'] = X['run'] * X['mid']
    X['_cons'] = 1

    fig, ax = plt.subplots()
    if yearT == 2016:
        plot_df = plot_df[~plot_df['county_name'].isin(bad_c[:1])]
    actual_diff = plot_df['diff'] + diff_mean
    ax.scatter(plot_df['run'], actual_diff, color=navy)
    # ax.axvline(0, linestyle='--', color='r')

    XB = X.values.dot(res1.beta.values)
    XB += diff_mean  # Was de-meaned for regression
    ax.plot(x[x < 0], XB[x < 0], color=maroon)
    ax.plot(x[x >= 0], XB[x >= 0], color=maroon)

    ax.yaxis.grid(True, alpha=.2, color=navy, linestyle='-')
    ax.tick_params(left='off', right='off')
    ax.set_xlabel("Difference between 1964 Turnout and VRA Threshold")
    ax.set_ylabel("Change in Turnout")

    plt.show()

    return fig


if __name__ == "__main__":
    save = save_cli()
    # main_old_plot(save=save)
    plot_frd(2008, 2012)

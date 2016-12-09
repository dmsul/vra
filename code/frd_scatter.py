from __future__ import division, print_function, absolute_import

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import econtools.metrics as mt
from econtools import save_cli

from util.env import out_path
from util.style import navy, maroon
from clean.gather import data_clean, vra_counties

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
    plot_frd(2008, 2012)


def plot_frd(year0, yearT):
    bad_c = ('Stokes', 'Gaston', 'Cleveland')
    df = data_clean(midterm=False)
    pre_years = [1948, 1952, 1956, 1960]
    pre_years = [year0]
    post_years = [yearT]  # 1976, 1980, 1984, 1988]
    df['t'] = np.nan
    df.loc[df['year'].isin(pre_years), 't'] = 0
    df.loc[df['year'].isin(post_years), 't'] = 1

    collapsed = df.groupby(['county_name', 't'])['turnout_vap'].mean()
    collapsed = collapsed.sort_index()
    diff = collapsed.groupby(level='county_name').diff().dropna()
    diff.index = diff.index.droplevel('t')

    dfidx = df.set_index('county_name')
    white_16 = dfidx.loc[dfidx['year'] == 2016, 'pct_white']
    diff = diff.to_frame('diff').join(white_16)

    vra_years = df['year'].isin([1964])
    plot_df = df[vra_years].groupby('county_name')['turnout_vap'].min()
    plot_df = plot_df.reset_index().join(diff, on='county_name')
    vra_names = vra_counties()
    plot_df['had_vra'] = plot_df['county_name'].isin(vra_names)

    cutoff = .5
    plot_df['run'] = plot_df['turnout_vap'] - cutoff
    plot_df['low'] = (plot_df['turnout_vap'] < cutoff).astype(int)
    plot_df['mid'] = (
        (plot_df['turnout_vap'] >= cutoff) &
        (plot_df['turnout_vap'] < cutoff + .1)
    ).astype(int)
    plot_df['run_low'] = plot_df['run'] * plot_df['low']
    plot_df['run_mid'] = plot_df['run'] * plot_df['mid']
    plot_df['white_low'] = plot_df['pct_white'] * plot_df['low']
    plot_df['white_run'] = plot_df['pct_white'] * plot_df['run']

    diff_mean = plot_df['diff'].mean()
    plot_df['diff'] -= diff_mean

    res1 = mt.reg(plot_df, 'diff', ['run', 'low', 'run_low'],
                  addcons=True, vce_type='robust')
    print(res1.summary)

    x = np.linspace(plot_df['turnout_vap'].min(), plot_df['turnout_vap'].max(),
                    num=100)
    X = pd.DataFrame(x, columns=['run'])
    X['run'] -= cutoff
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

    ax.set_xlabel("Difference between 1964 Turnout and VRA Threshold")
    ax.set_ylabel("Change in Turnout")

    # fig2, ax2 = plt.subplots()
    # bx, by = binscatter(plot_df['turnout_vap'], plot_df['diff'], n=30)
    # ax2.scatter(bx, by)

    plt.show()

    return fig


if __name__ == "__main__":
    save = save_cli()
    main_many_plots(save=save)

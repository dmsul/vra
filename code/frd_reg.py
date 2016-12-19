from __future__ import division, print_function, absolute_import

import numpy as np

import econtools.metrics as mt
from econtools import save_cli

from util.env import out_path
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
    plot_frd(1960, 1964)


def plot_frd(year0, yearT):
    bad_c = ('Stokes', 'Gaston', 'Cleveland')
    df = data_clean(midterm=False)
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

    res1 = mt.reg(plot_df, 'diff', ['run', 'low', 'run_low', 'pct_white'],
                  addcons=True, vce_type='robust')
    print(res1.summary)

    return plot_df


if __name__ == "__main__":
    save = save_cli()
    main_old_plot(save=save)

from __future__ import division, print_function, absolute_import

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from econtools import save_cli, legend_below, outreg, table_statrow
from econtools.util.to_latex import eol
import econtools.metrics as mt

from util.env import out_path
from util.style import navy, maroon
from analysis.rd import rd_data


def main():
    save = save_cli()
    year_pairs = (
        (1964, 1968),
        (2004, 2008),
        (2008, 2012),
        (2012, 2016),
    )
    for year0, yearT in year_pairs:
        if yearT == 2016:
            plot_change_on_race(year0, yearT, save=save)
        reg_plot_change_on_race(year0, yearT, save=save)


def plot_change_on_race(year0, yearT, save=False):
    """ Scatter "change in turnout" on "pct white" by VRA status """
    df = data_prep(year0, yearT)

    df = df[df['diff'] < .2]    # Exclude crazy outlier

    fig, ax = plt.subplots()
    tmp = df[df['vra']]
    line_vra = ax.plot(tmp['pct_white'], tmp['diff'], color=navy,
                       linestyle='', marker='o', label='Had VRA')
    tmp = df[~df['vra']]
    line_novra = ax.plot(tmp['pct_white'], tmp['diff'], color=maroon,
                         linestyle='', marker='s', label='Never VRA')

    ax.yaxis.grid(True, alpha=.2, color=navy, linestyle='-')
    ax.set_xlabel("Percent White ({})".format(year0))
    ax.set_ylabel("Change in Turnout ({}-{})".format(year0, yearT))

    lines = line_vra + line_novra
    legend_below(ax, handles=lines, shrink=True, ncol=2, numpoints=1)

    if save:
        filepath = out_path('cond_on_race_{}_{}_fullsamp.pdf').format(year0,
                                                                      yearT)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def reg_plot_change_on_race(year0, yearT, save=False):
    plot_interact = True
    df = data_prep(year0, yearT)
    df = df[(df['pct_white'] > 50) & (df['pct_white'] < 85)].copy()

    # Once without VRA-white interaction
    reg1 = mt.reg(df, 'diff', ['vra', 'pct_white'], addcons=True,
                  cluster='county_name')
    print(reg1.summary)
    fig1, ax1 = _reg_plot(df, reg1, year0, yearT)

    # Once with VRA-white interact
    reg2 = mt.reg(df, 'diff', ['vra', 'pct_white', 'vra_white'], addcons=True,
                  cluster='county_name')
    print(reg2.summary)

    if plot_interact:
        fig2, ax2 = _reg_plot(df, reg2, year0, yearT)

    # Do it all again with 'pct_65plus'
    reg3 = mt.reg(df, 'diff', ['vra', 'pct_white', 'pct_65plus'], addcons=True,
                  cluster='county_name')
    print(reg3.summary)

    reg4 = mt.reg(df, 'diff', ['vra', 'pct_white', 'vra_white', 'pct_65plus'],
                  addcons=True,
                  cluster='county_name')
    print(reg4.summary)

    # Put regs in table
    var_names = ('vra', 'pct_white', 'pct_65plus', 'vra_white', '_cons')
    var_labels = ("Had VRA", "Percent White", "Percent over 65",
                  "Had VRA$\\times$Percent White",
                  "Constant")
    regs = (reg1, reg2, reg3, reg4)
    table_str = outreg(regs, var_names, var_labels)
    table_str += eol
    table_str += table_statrow("R$^2$", [reg.r2 for reg in regs], digits=3)
    print(table_str)

    # Save everything
    if save:
        table_path = out_path('cond_on_race_{}_{}.tex').format(year0, yearT)
        with open(table_path, 'w') as f:
            f.write(table_str)
        fig_path = out_path('cond_on_race_{}_{}.pdf').format(year0, yearT)
        fig1.savefig(fig_path, bbox_inches='tight')
        if plot_interact:
            fig_path = out_path('cond_on_race_{}_{}_interact.pdf')
            fig_path = fig_path.format(year0, yearT)
            fig2.savefig(fig_path, bbox_inches='tight')

        plt.close()
    else:
        plt.show()

def _reg_plot(df, reg, year0, yearT):
    yhat = __gen_fitted_values(df, reg)

    # Plot
    fig, ax = plt.subplots()
    df = df.sort_values('pct_white')
    vra_scat = ax.plot(df.loc[df['vra'], 'pct_white'],
                       df.loc[df['vra'], 'diff'],
                       linestyle='', marker='o', color=navy,
                       label="Had VRA")
    novra_scat = ax.plot(df.loc[~df['vra'], 'pct_white'],
                         df.loc[~df['vra'], 'diff'],
                         linestyle='', marker='s', color=maroon,
                         label="Never VRA")
    vra_fit = ax.plot(yhat.index.values, yhat[1].values,
                      linestyle='-', marker=None, color=navy,
                      label="Had VRA Fitted Values")
    novra_fit = ax.plot(yhat.index.values, yhat[0].values,
                        linestyle='-', marker=None, color=maroon,
                        label="Never VRA Fitted Values")

    ax.yaxis.grid(True, alpha=.2, color=navy, linestyle='-')
    ax.set_xlabel("Percent White ({})".format(year0))
    ax.set_ylabel("Change in Turnout ({}-{})".format(year0, yearT))

    lines = vra_scat + novra_scat + vra_fit + novra_fit
    legend_below(ax, handles=lines, shrink=True, ncol=2, numpoints=1)

    return fig, ax

def __gen_fitted_values(df, reg):
    """ Output is DataFrame with 'pct_white' index and vra {0,1} columns """
    n = 50
    x = np.linspace(df['pct_white'].min(), df['pct_white'].max(), num=n)
    fake_df = pd.DataFrame(x, columns=['pct_white'])
    fake_df = (fake_df.append(fake_df)          # Double for VRA status
                      .reset_index(drop=True))
    fake_df['vra'] = 0
    fake_df.loc[:(n-1), 'vra'] = 1
    fake_df['_cons'] = 1

    if 'vra_white' in reg.beta:   # For VRA-white interaction
        fake_df['vra_white'] = fake_df.eval('vra * pct_white')
        keep_vars = ['pct_white', 'vra', 'vra_white', '_cons']
    else:
        keep_vars = ['pct_white', 'vra', '_cons']

    betas = reg.beta[keep_vars].copy()
    yhat = fake_df.dot(betas).to_frame('yhat')
    yhat['vra'] = fake_df['vra']
    yhat['pct_white'] = fake_df['pct_white']
    yhat = yhat.pivot(index='pct_white', columns='vra', values='yhat')

    return yhat


def data_prep(year0, yearT):
    df = rd_data(year0, yearT)

    df['vra'] = df['run'] < 0
    df['vra_white'] = df['vra'] * df['pct_white']

    return df


if __name__ == '__main__':
    main()

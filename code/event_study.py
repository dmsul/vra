from __future__ import division, print_function, absolute_import

import numpy as np
import matplotlib.pyplot as plt

import econtools.metrics as mt

from util.env import out_path
from util.style import navy
from clean.gather import data_clean


def es_differential(midterm=False, use_controls=False, standalone=False,
                    save=False):
    df = data_clean(midterm=midterm)

    # Yearly interactions
    years = df['year'].unique()
    year0 = years[0]
    for y in years:
        df['vra_{}'.format(y)] = (
            (df['had_vra']) & (df['year'] == y)).astype(int)
        if y == year0:
            continue
        df['_Iyear_{}'.format(y)] = (df['year'] == y).astype(int)

    df = df.sort_index(axis=1)

    vra_vars = df.filter(like='vra_').columns.tolist()
    _I = df.filter(like='_I').columns.tolist()

    # Regression
    controls = []
    if use_controls:
        controls += ['pct_white', 'pct_65plus']
    if midterm is not False:
        controls.append('uncontested')
    reg = mt.reg(df, 'turnout_vap', vra_vars + _I + controls,
                 addcons=True, cluster='county_name')
    print(reg.summary)

    diff = parse_vra_coeff(reg.beta)
    ci_low = parse_vra_coeff(reg.summary['CI_low'])
    band = diff - ci_low

    fig, ax = plt.subplots()

    ax.errorbar(diff.index, diff.values, yerr=band.values,
                linestyle='-', fmt='o', capsize=0, color=navy)

    # ax.axhline(0, color='0.5', linestyle='-')
    vra_y0, vra_yT = 1965, 2014.75
    ax.axvline(vra_y0, linestyle='-', color='g')
    ax.axvline(vra_yT, linestyle='-', color='r')

    ticks = np.arange(df['year'].min(), df['year'].max() + 1, 8) + 4
    ax.set_xticks(ticks)
    ax.margins(x=0.05)

    ax.grid(True, alpha=.2, color=navy, linestyle='-')
    ax.tick_params(top='off', bottom='off', left='off', right='off')

    ax.set_ylabel("Differential Between VRA and non-VRA Counties")

    if standalone:
        fig.suptitle(
            "The Voting Rights Act and Voter Turnout in North Carolina",
            fontsize=14)

    if controls and standalone:
        control_labels = {
            'uncontested': '"uncontested"',
            'pct_white': '"percent white"',
            'pct_65plus': '"percent over 65"',
        }
        note = 'Note: Controls for '
        for col in controls:
            note += control_labels[col] + ', '
        note = note[:-2] + '.'
        plt.annotate(note, (-0.07, 0.01), (0, -40), xycoords='axes fraction',
                     textcoords='offset points')

    # VRA start and finish lines
    if midterm:
        ylevel = -.195
    elif midterm is False:
        if use_controls:
            ylevel = -.195
        else:
            ylevel = -.195
    else:
        ylevel = -.195
    ax.annotate("VRA In Force", xy=((vra_y0 + vra_yT)/2 - 2, ylevel),
                xytext=(-11, 0),
                textcoords='offset points')
    ax.annotate('',
                xy=((vra_y0, ylevel - .005)),
                xytext=((vra_yT, ylevel - .005)),
                arrowprops=dict(facecolor='r', arrowstyle='<->'))

    if save:
        filepath = _set_figure_path(midterm, use_controls)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

    return df

def _set_figure_path(midterm, use_controls, standalone):
    filepath = out_path('es_plot{}.pdf')
    infix = ''
    if midterm:
        infix += '_midterm'
    elif midterm is None:
        infix += '_all'
    else:
        infix += '_pres'

    if use_controls:
        infix += '_controls'

    if standalone:
        infix += '_standalone'

    return filepath.format(infix)


def parse_vra_coeff(s):
    match = 'vra_'
    vra_vars = s.filter(like=match)
    vra_vars = vra_vars.rename(index=lambda x: int(x.replace(match, '')))
    return vra_vars


def plot_raw_timeseries():
    df = data_clean(midterm=False)
    df['low_white'] = df['pct_white'] < 50

    avg_vra = df[df['low_white']].groupby('year')['turnout_vap'].mean()
    avg_oth = df[~df['low_white']].groupby('year')['turnout_vap'].mean()

    fig, ax = plt.subplots()
    ax.plot(avg_oth.index, avg_oth.values, '-o', label='Non-VRA counties')
    ax.plot(avg_vra.index, avg_vra.values, '-o', label='VRA counties')
    ax.axvline(1965, color='k')
    ax.axvline(2013, color='k')

    ylevel = .17
    ax.annotate("VRA In Force", xy=((2013 + 1965)/2 - 2, ylevel),
                xytext=(-7, 0),
                textcoords='offset points')
    ax.annotate('',
                xy=((1965, ylevel - .01)),
                xytext=((2013, ylevel - .01)),
                arrowprops=dict(facecolor='r', arrowstyle='<->'))

    ax.set_xticks(np.arange(df['year'].min(), df['year'].max() + 1, 8))
    ax.margins(x=0.05)
    ax.grid(True, alpha=.5)
    ax.set_ylabel("Voter Turnout (Median across Counties)")
    fig.suptitle("The Voting Rights Act in North Carolina", fontsize=14)

    plt.legend(loc=4)
    # plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    if 0:
        for midterm in (True, False):
            for control in (True, False):
                es_differential(midterm=midterm, use_controls=control,
                                save=True)
    es_differential(midterm=None)
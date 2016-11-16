from __future__ import division, print_function, absolute_import

import numpy as np
import matplotlib.pyplot as plt

import econtools.metrics as mt

from clean.gather import data_clean


def differential_pres():
    df = data_clean(midterm=False)

    years = df['year'].unique()
    year0 = years[0]
    df['high_black'] = df['pct_white'] < 50
    for y in years:
        df['vra_{}'.format(y)] = (
            (df['had_vra']) & (df['year'] == y)).astype(int)
        if y == year0:
            continue
        df['_Iyear_{}'.format(y)] = (df['year'] == y).astype(int)

    df = df.sort_index(axis=1)

    vra_vars = df.filter(like='vra_').columns.tolist()
    _I = df.filter(like='_I').columns.tolist()
    pct_vars = []
    reg = mt.reg(df, 'turnout_vap', vra_vars + _I + pct_vars,
                 addcons=True, cluster='county_name')
    print(reg.summary)

    diff = parse_vra_coeff(reg.beta)
    ci_low = parse_vra_coeff(reg.summary['CI_low'])
    band = diff - ci_low

    fig, ax = plt.subplots()

    ax.errorbar(diff.index, diff.values, yerr=band.values,
                linestyle='-', fmt='o', capsize=0)
    # ax.plot(diff.index, diff.values, '-o')

    ax.axhline(0, color='0.5', linestyle='-')
    ax.axvline(1965, linestyle='-', color='g')
    ax.axvline(2013, linestyle='-', color='r')

    ticks = np.arange(df['year'].min(), df['year'].max() + 1, 8) + 4
    ax.set_xticks(ticks)
    ax.margins(x=0.05)

    ax.grid(True, alpha=.5)

    ax.set_ylabel("Differential Between VRA and non-VRA Counties")
    fig.suptitle("The Voting Rights Act and Voter Turnout in North Carolina",
                 fontsize=14)

    note = (
        'Note: Controls for '
        '"percent white", and "percent over 65"'
    )
    plt.annotate(note, (-0.07, 0.01), (0, -40), xycoords='axes fraction',
                 textcoords='offset points')

    ylevel = -.17
    ax.annotate("VRA In Force", xy=((2013 + 1965)/2 - 2, ylevel),
                xytext=(-11, 0),
                textcoords='offset points')
    ax.annotate('',
                xy=((1965, ylevel - .01)),
                xytext=((2013, ylevel - .01)),
                arrowprops=dict(facecolor='r', arrowstyle='<->'))

    plt.show()
    return df


def differential_midterm():
    df = data_clean(midterm=True)

    df = df.sort_values(['county_name', 'year'])

    for y in range(1950, 2014 + 1, 4):
        df['vra_{}'.format(y)] = (
            (df['had_vra']) & (df['year'] == y)).astype(int)
        if y == 1950:
            continue
        else:
            df['_Iyear_{}'.format(y)] = (df['year'] == y).astype(int)
    vra_vars = df.filter(like='vra_').columns.tolist()
    _I = df.filter(like='_I').columns.tolist()
    reg = mt.reg(df, 'turnout_vap', vra_vars + _I +
                 ['uncontested', 'pct_white', 'pct_65plus'],
                 addcons=True, cluster='county_name')
    print(reg.summary)

    coeffs = reg.beta.filter(like='vra_').values

    fig, ax = plt.subplots()

    ax.plot(range(1950, 2014 + 1, 4), coeffs, '-o')

    ax.set_xticks(np.arange(df['year'].min(), df['year'].max() + 1, 8))
    ax.margins(x=0.05)
    ax.grid(True, alpha=.5)
    ax.axhline(0, color='k')

    ax.set_ylabel("Differential Between VRA and non-VRA Counties")
    fig.suptitle("The Voting Rights Act and Voter Turnout in North Carolina",
                 fontsize=14)

    note = (
        'Note: Controls for "uncontested", '
        '"percent white", and "percent over 65"'
    )
    plt.annotate(note, (-0.07, 0.01), (0, -40), xycoords='axes fraction',
                 textcoords='offset points')

    plt.show()

    return reg


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
    differential_pres()

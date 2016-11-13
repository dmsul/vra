from __future__ import division, print_function

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import econtools.metrics as mt


def differential_pres():
    df = data_prep_president()

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
    pct_vars = ['pct_white', 'pct_65plus']
    reg = mt.reg(df, 'turnout_vap', vra_vars + _I + pct_vars,
                 addcons=True, cluster='county_name')
    print(reg.summary)

    diff = parse_vra_coeff(reg.beta)
    ci_low = parse_vra_coeff(reg.summary['CI_low'])
    ci_high = parse_vra_coeff(reg.summary['CI_high'])
    band = diff - ci_low

    fig, ax = plt.subplots()


    ax.errorbar(diff.index, diff.values, yerr=band.values,
                linestyle='-', fmt='o', capsize=0)
    # ax.plot(diff.index, diff.values, '-o')
    # ax.scatter(ci_low.index, ci_low.values, marker='s', color='r', alpha=.5)
    # ax.scatter(ci_high.index, ci_high.values, marker='s', color='r', alpha=.5)

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


def parse_vra_coeff(s):
    match = 'vra_'
    vra_vars = s.filter(like=match)
    vra_vars = vra_vars.rename(index=lambda x: int(x.replace(match, '')))
    return vra_vars


def differential_midterm():
    df = data_prep_midterm()

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


def main():
    df = data_prep_president()

    avg_vra = df[df['had_vra']].groupby('year')['turnout_vap'].mean()
    avg_oth = df[~df['had_vra']].groupby('year')['turnout_vap'].mean()

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


def data_all():
    df = data_prep_midterm()
    df['midterm'] = 1

    df2 = data_prep_president()
    df = df.append(df2, ignore_index=True)
    df['midterm'] = df['midterm'].fillna(0)

    df = df.sort_values(['county_name', 'year'])
    df = df.reset_index(drop=True)

    df['uncontested'] = df['uncontested'].fillna(0)

    return df


def data_prep_midterm():
    df = prep_early()
    df2 = prep_2014()
    df = df.append(df2, ignore_index=True)

    df.loc[df['turnout_vap'] > 1, 'turnout_vap'] = np.nan

    df['year'] = df['year'].astype(int)

    df = df[df['state_abbrev'] == 'NC'].copy()
    vra = vra_counties()
    df['had_vra'] = df['county_name'].isin(vra)

    # Fill missings
    df['uncontested'] = df['uncontested'].fillna(0)
    df = df.sort_values(['county_name', 'year'])
    for col in ('pct_white', 'pct_65plus'):
        df[col] = df[col].fillna(method='ffill')

    return df

def data_prep_president():
    df = prep_early_pres()
    df = df.rename(columns={
        'abbreviation': 'state_abbrev',
        'statename': 'state_name',
        'fipscounty': 'county_fips',
        'countyname': 'county_name'
    })
    df = df[df['state_abbrev'] == 'NC'].copy()

    df2 = prep_2016()
    df = df.append(df2, ignore_index=True)

    had_vra = vra_counties()
    df['had_vra'] = df['county_name'].isin(had_vra)

    df['year'] = df['year'].astype(int)

    for col in ('pct_white', 'pct_65plus'):
        df[col] = df[col].fillna(method='ffill')

    return df

def prep_early_pres():
    df = pd.read_stata(data_path('merged_vote_rain.dta'))

    rain_vars = df.filter(regex='rain').columns
    df = df.drop(rain_vars, axis=1)

    df = df.rename(columns={
        'countyname': 'county_name',
        'turnout': 'turnout_vap',
    })

    df['turnout_vap'] /= 100

    return df

def prep_early():
    df = pd.read_stata(data_path('merged_vote_rain_midterm.dta'))
    df = df.drop(df.filter(regex='rain').columns, axis=1)
    df = df.rename(columns={
        'abbreviation': 'state_abbrev',
        'statename': 'state_name',
        'fipscounty': 'county_fips',
        'countyname': 'county_name'
    })

    df['turnout_vap'] = df['vote'] / df['elig']

    df['county_fips'] = df['county_fips'].astype(int).astype(str).str.zfill(5)

    return df

def prep_2014():
    df = pd.read_stata(data_path('county_turnout_just_2014.dta'))
    fips = (
        df['state_fips'].astype(str).str.zfill(2) +
        df['county_fips'].astype(str).str.zfill(3)
    )
    df['county_fips'] = fips
    df['year'] = df['year'].astype(np.int64)

    return df

def prep_2016():
    filepath = data_path('NC_2016.csv')
    df = pd.read_csv(filepath)
    df = df.rename(columns={
        'COUNTY': 'county_name',
    })

    df = df[df['county_name'].notnull()]

    df['county_name'] = df['county_name'].str.title()
    df.loc[df['county_name'] == 'Mcdowell', 'county_name'] = 'McDowell'

    df['turnout_vap'] = df['VOTED'] / df['TOTAL']

    df = df[['county_name', 'turnout_vap']].copy()

    df['year'] = 2016
    df['state_abbrev'] = 'NC'

    return df

def vra_counties():
    county_name = (
        'Anson',
        'Beaufort',
        'Bertie',
        'Bladen',
        'Camden',
        'Caswell',
        'Chowan',
        'Cleveland',
        'Craven',
        'Cumberland',
        'Edgecombe',
        'Franklin',
        'Gaston',
        'Gates',
        'Granville',
        'Greene',
        'Guilford',
        'Halifax',
        'Harnett',
        'Hertford',
        'Hoke',
        'Jackson',
        'Lee',
        'Lenoir',
        'Martin',
        'Nash',
        'Northampton',
        'Onslow',
        'Pasquotank',
        'Perquimans',
        'Person',
        'Pitt',
        'Robeson',
        'Rockingham',
        'Scotland',
        'Union',
        'Vance',
        'Washington',
        'Wayne',
        'Wilson',
    )
    return county_name


def data_path(*args):
    return os.path.expanduser(
        os.path.join('~', 'research', 'vra', 'data', *args))


if __name__ == '__main__':
    differential_pres()

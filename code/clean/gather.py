from __future__ import division, print_function, absolute_import

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import econtools.metrics as mt

from clean.fmv import prep_early_pres, prep_early
from clean.other import prep_2014, prep_2016, vra_counties


def extrapolate_elig():
    df = data_combine()
    year0 = 1980
    yearT = 2016
    df = df[(df['year'] <= yearT) & (df['year'] >= year0)].copy()
    df['t'] = df['year'] - 1980
    df['t2'] = df['t'] ** 2
    df['t3'] = df['t'] ** 3

    counties = df.county_name.unique().tolist()
    new_elig = pd.DataFrame(np.zeros((len(counties), 2)),
                            columns=[2014, 2016],
                            index=counties)

    extrap_X = np.array(
        [[x - 1980, 1] for x in (2014, 2016)]
    )

    X = range(year0, yearT + 1, 2)
    full_X = np.array(
        [[x - 1980, 1] for x in X]
    )

    for county in counties:
        this_df = df[df['county_name'] == county].copy()
        reg = mt.reg(this_df, 'elig', ['t'], addcons=True)
        new_elig.loc[county, :] = extrap_X.dot(reg.beta.values)
        # Show fit
        fig, ax = plt.subplots()
        ax.scatter(this_df['year'], this_df['elig'], color='b')
        ax.plot(X, full_X.dot(reg.beta.values), '-r')
        plt.show()

    return new_elig


def data_clean(midterm=None):
    df = data_combine()
    for col in ('elig', 'pct_white', 'pct_65plus'):
        df = _extrap_col(df, col)

    df['turnout_vap'] = df['vote'] / df['elig']

    if midterm is None:
        return df
    elif midterm:
        return df[df['midterm']].copy()
    else:
        return df[~df['midterm']].copy()

def _extrap_col(df, col):
    df = df.set_index(['county_name', 'year']).sort_index()
    extrapolated = _extrap(df, col).stack('year')
    df.loc[extrapolated.index, col] = extrapolated
    df = df.reset_index()
    return df

def _extrap(df, col):
    s = df.loc[pd.IndexSlice[:, [2000, 2010]], col]
    s = s.unstack('year')
    annual_change = (s[2010] - s[2000]) / 10

    new_years = [2012, 2014, 2016]
    new_df = pd.DataFrame(np.zeros((len(annual_change), len(new_years))),
                          columns=new_years,
                          index=annual_change.index)
    new_df.columns.name = 'year'

    for year in new_years:
        new_df.loc[:, year] = s[2010] + annual_change * (year - 2010)

    return new_df


def data_combine():
    """ Append presidential and midterm election data """
    df = combine_midterm()
    df2 = combine_president()
    df = df.append(df2, ignore_index=True)

    df = df.sort_values(['county_name', 'year'])
    df = df.reset_index(drop=True)

    df['uncontested'] = df['uncontested'].fillna(0)

    vra = vra_counties()
    df['had_vra'] = df['county_name'].isin(vra)

    return df


def combine_midterm():
    df = prep_early()
    df2 = prep_2014()
    df = df.append(df2, ignore_index=True)

    df.loc[df['turnout_vap'] > 1, 'turnout_vap'] = np.nan

    df['year'] = df['year'].astype(int)

    df = df[df['state_abbrev'] == 'NC'].copy()

    # Fill missings
    df['uncontested'] = df['uncontested'].fillna(0)
    df = df.sort_values(['county_name', 'year'])
    for col in ('pct_white', 'pct_65plus'):
        df[col] = df[col].fillna(method='ffill')

    df['midterm'] = True

    return df


def combine_president():
    df = prep_early_pres()
    df2 = prep_2016()
    df = df.append(df2, ignore_index=True)

    df['midterm'] = False

    return df


if __name__ == '__main__':
    df = data_clean()

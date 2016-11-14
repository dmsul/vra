from __future__ import division, print_function, absolute_import

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import econtools.metrics as mt

from clean.fmv import prep_early_pres, prep_early
from clean.other import prep_2014, prep_2016, vra_counties


def extrapolate_elig():
    df = data_all()
    year0 = 2008
    yearT = 2014
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


if __name__ == '__main__':
    df = extrapolate_elig()

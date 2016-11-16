from __future__ import division, print_function, absolute_import

import pandas as pd

from util.env import data_path


def prep_early_pres():
    df = pd.read_stata(data_path('merged_vote_rain.dta'))

    rain_vars = df.filter(regex='rain').columns
    df = df.drop(rain_vars, axis=1)

    df = df.rename(columns={
        'abbreviation': 'state_abbrev',
        'statename': 'state_name',
        'turnout': 'turnout_vap',
        'fipscounty': 'county_fips',
        'countyname': 'county_name'
    })

    df['turnout_vap'] /= 100
    df['vote'] = df['turnout_vap'] * df['elig']

    df['year'] = df['year'].astype(int)

    df = df[df['state_abbrev'] == 'NC'].copy()

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

    df['year'] = df['year'].astype(int)

    df = df[df['state_abbrev'] == 'NC'].copy()

    df['midterm'] = True

    return df

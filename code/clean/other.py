from __future__ import division, print_function, absolute_import

import pandas as pd

from util.env import data_path


def prep_2014():
    df = pd.read_stata(data_path('county_turnout_just_2014.dta'))
    fips = (
        df['state_fips'].astype(str).str.zfill(2) +
        df['county_fips'].astype(str).str.zfill(3)
    )
    df['county_fips'] = fips
    df['year'] = df['year'].astype(int)

    df = df.rename(columns={
        'cvap_est': 'elig',
    })

    return df


def prep_2016():
    filepath = data_path('NC_2016.csv')
    df = pd.read_csv(filepath)
    df = df.rename(columns={
        'COUNTY': 'county_name',
        'TOTAL': 'registered',
        'VOTED': 'voted',
    })

    df = df[df['county_name'].notnull()]

    df['county_name'] = df['county_name'].str.title()
    df.loc[df['county_name'] == 'Mcdowell', 'county_name'] = 'McDowell'

    df['turnout_vap'] = df['voted'] / df['registered']

    df = df[['county_name', 'turnout_vap', 'voted', 'registered']].copy()

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

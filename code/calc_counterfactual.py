from __future__ import division, print_function, absolute_import

import pandas as pd

from clean.precinct import load_precinct
from clean.gather import data_clean


def get_county_data():
    df = data_clean()
    cols = ['county_name', 'turnout_vap', 'had_vra']
    df = df.loc[df['year'] == 2016, cols].copy()

    df['county'] = df['county_name'].str.upper()
    df = df.drop('county_name', axis=1)

    df = df.set_index('county')

    return df


if __name__ == "__main__":
    ALL_DEM = True
    VRA_SCALE = .02    # To get Clinton to win, .0675
    df = load_precinct(2016)

    races = ('US PRESIDENT', 'NC GOVERNOR', 'US SENATE')

    prez = df[df['contest'] == races[0]].copy()

    vote_cats = ['total', 'onestop', 'absentee', 'electionday']
    vote_county = prez.groupby(['county', 'choice'])[vote_cats].sum()
    county_data = get_county_data()

    vote_county = vote_county.join(county_data)['total']
    county_votes_cast = vote_county.groupby(level='county').sum()
    bal_county = vote_county.divide(county_votes_cast)
    if ALL_DEM:
        bal_county.loc[:] = 0
        bal_county.loc[pd.IndexSlice[:, 'Hillary Clinton']] = 1

    new_votes = county_votes_cast.mul(
        county_data['had_vra'] * VRA_SCALE /
        county_data['turnout_vap']
    )

    new_cand_votes = bal_county.mul(new_votes)

    new_vote_county = vote_county + new_cand_votes

    old_results = vote_county.groupby(level='choice').sum()
    new_results = new_vote_county.groupby(level='choice').sum()
    print(old_results / old_results.sum())
    print(new_results / new_results.sum())

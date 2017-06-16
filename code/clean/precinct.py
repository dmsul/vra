from __future__ import division, print_function, absolute_import

import subprocess
import os

import pandas as pd

from util.env import data_path


def load_precinct(year=2016):

    clean_from_zip(year)
    filepath = txt_path_by_year(year)

    df = pd.read_table(filepath, header=0)

    df = df.rename(columns=lambda x: x.lower())
    rename = {
        'contest name': 'contest',
        'total votes': 'total',
        'one stop': 'onestop',
        'absentee by mail': 'absentee',
        'election day': 'electionday',
    }
    df = df.rename(columns=rename)

    return df


def clean_from_zip(year):
    # If it's already on disk, assume it's fine
    if os.path.isfile(txt_path_by_year(year)):
        return

    # Unzip
    zip_path = zip_path_by_year(year)
    dest_folder = data_path('precinct')
    subprocess.call(['7z', 'e', zip_path, '-o' + dest_folder])

    # Get rid of ASCII null character
    txt_path = txt_path_by_year(year)
    with open(txt_path, 'r') as f:
        contents = f.read()

    contents = contents.replace('\x00', '')

    with open(txt_path, 'w') as f:
        f.write(contents)


def zip_path_by_year(year):
    if year == 2014:
        filepath = data_path('precinct', 'resultsPCT20141104.zip')
    elif year == 2016:
        filepath = data_path('precinct', 'resultsPCT20161108.zip')
    else:
        raise ValueError

    return filepath


def txt_path_by_year(year):
    if year == 2014:
        filepath = data_path('precinct', 'resultsPCT20141104.txt')
    elif year == 2016:
        filepath = data_path('precinct', 'resultsPCT20161108.txt')
    else:
        raise ValueError

    return filepath


def load_xwalk():
    """
    The precinct data already have county, so this is pointless. But it's done
    so I'm keeping it.
    """
    filepath = data_path('xwalk_precinct_county.csv')

    df = pd.read_csv(filepath, header=0, skiprows=[1])

    # Drop allocation factor (should be 1; VTD subset of county)
    assert (df['afact'].min() == df['afact'].max()) & (df['afact'].max() == 1)
    df = df.drop('afact', axis=1)

    df['fips'] = df['county']
    df['county'] = df['cntyname'].str.replace(' NC', '').str.upper()
    df = df.drop('cntyname', axis=1)

    # Re-order columns
    df = df[['fips', 'county', 'vtd', 'vtdname', 'pop10']]

    return df


def _process(df):
    bad = ('ABSENTEE BY MAIL', 'ABSENTEE MAIL', 'ONESTOP', 'PROVISIONAL',
           'MAIL ABSENTEE', 'SPRING HOPE OS', 'MT PLEASANT OS', 'NASHVILLE OS',
           'ROCKY MOUNT OS',
           'ABSENTEE', 'TRANSFER', 'CURBSIDE', 'ONE STOP', '???')
    df = df[~df['precinct'].isin(bad)]
    bad2 = ('ONE STOP', 'OS', 'ABSENTEE', 'PROVISIONAL', 'TRANSFER',
            'ABSEN ', 'PROVI ', 'TRANS ', 'CURBSIDE',
            'ABS/PROV', 'ABS/CURB', 'ONE-STOP')
    for bad in bad2:
        l = len(bad)
        is_bad = df['precinct'].str[:l] == bad
        df = df[~is_bad].copy()

    return df


if __name__ == "__main__":
    pre = load_precinct(2014)
    pre['year'] = 1
    post = load_precinct(2016)
    post['year'] = 2

    pre = _process(pre)
    post = _process(post)

    cols = ['county', 'precinct', 'year']
    pre = pre[cols].drop_duplicates().set_index(cols[:2]).sort_index().squeeze()
    post = post[cols].drop_duplicates().set_index(cols[:2]).sort_index().squeeze()

    df = pre.add(post, fill_value=0)

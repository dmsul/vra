from __future__ import division, print_function, absolute_import

import numpy as np

from util.env import out_path
from clean.gather import data_clean


if __name__ == '__main__':
    # draft of "prep_data"
    df = data_clean()
    had_vra = (
        df[['county_name', 'had_vra']]
        .drop_duplicates()
        .set_index('county_name')
    )
    df = df.set_index(['county_name', 'year'])

    df['pct_nonwhite'] = 100 - df['pct_white']
    cols = ['turnout_vap', 'pct_nonwhite']
    df = df[cols].unstack('year')

    # Re-scale turnout (before re-naming)
    df['turnout_vap'] *= 100

    col_years = [
        ('turnout_vap', 1960),
        ('turnout_vap', 1964),
        ('turnout_vap', 1968),
        ('turnout_vap', 1972),
        ('pct_nonwhite', 1964),
        ('pct_nonwhite', 2010),
        ('pct_nonwhite', 2016),
    ]
    df = df[col_years]
    df = df.join(had_vra)

    df['vra'] = np.where(df['had_vra'], 'X', '')
    df = df.drop('had_vra', axis=1)

    cols = df.columns
    newcols = cols[-1:] | cols[:-1]
    df = df[newcols].copy()

    table_str = df.to_latex(float_format=lambda x: '{:2.1f}'.format(x))
    table_str = table_str.split('midrule\n', 1)[1]
    table_str = table_str.split('\n\\bottomrule', 1)[0]

    with open(out_path('full_county_list.tex'), 'w') as f:
        f.write(table_str)

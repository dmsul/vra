from __future__ import division, print_function, absolute_import

import pandas as pd

from util.env import data_path


def voter_demogs_2016():
    filepath = data_path('NCGA', 'rptVTDVap.xlsx')
    df = pd.read_excel(filepath, skiprows=[0])

    frac_cols = df.filter(regex='%').columns
    df = df.drop(frac_cols, axis=1)

    return df


if __name__ == '__main__':
    df = voter_demogs_2016()

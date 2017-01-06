from __future__ import division, print_function, absolute_import

import econtools.metrics as mt
from econtools import save_cli

from frd_scatter import frd_data


def plot_frd(year0, yearT):
    df = frd_data(year0, yearT)

    diff_mean = df['diff'].mean()
    df['diff'] -= diff_mean

    res1 = mt.reg(df, 'diff', ['run', 'low', 'run_low'],
                  addcons=True, vce_type='robust')
    print(res1.summary)

    return df


if __name__ == "__main__":
    save = save_cli()
    plot_frd(1960, 1968)

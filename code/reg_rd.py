from __future__ import division, print_function, absolute_import

import econtools.metrics as mt
from econtools import save_cli

from plot_rd import frd_data


def plot_frd(year0, yearT):
    df = frd_data(year0, yearT)

    diff_mean = df['diff'].mean()
    df['diff'] -= diff_mean

    res = mt.reg(df, 'diff', ['low', 'run', 'run_low', 'pct_white'],
                 addcons=True, vce_type='robust')
    print(res.summary)

    return res


if __name__ == "__main__":
    save = save_cli()
    plot_frd(2012, 2016)

from __future__ import division, print_function, absolute_import

import econtools.metrics as mt
from econtools import save_cli

from analysis.rd import rd_data


def reg_rd(year0, yearT):
    df = rd_data(year0, yearT)

    diff_mean = df['diff'].mean()
    df['diff'] -= diff_mean

    res = mt.reg(df, 'diff', ['low', 'run', 'run_low', 'pct_white'],
                 addcons=True, vce_type='robust')
    print(res.summary)

    return res


if __name__ == "__main__":
    save = save_cli()
    reg_rd(2012, 2016)

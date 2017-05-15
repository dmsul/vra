from __future__ import division, print_function, absolute_import

from econtools import save_cli, outreg, table_statrow
from econtools.util.to_latex import eol
import econtools.metrics as mt

from util.env import out_path
from analysis.rd import rd_data


def rd_table_main():
    save = save_cli()
    year_sets = (
        (1960, 1968),
        (1960, 1964),
        (1964, 1968),
        (2004, 2008),
        (2008, 2012),
        (2012, 2016),
    )
    for year0, yearT in year_sets:
        regs = reg_rd(year0, yearT)
        print("{}-{}".format(year0, yearT))
        rd_table(regs, year0=year0, yearT=yearT, save=save)


def rd_table(regs, year0=None, yearT=None, save=False):
    var_names = ('low', 'run', 'run_low', 'pct_white', 'pct_65plus', '_cons')
    var_labels = ("Discontinuity at VRA Threshold", "Turnout in 1964",
                  "Turnout in 1964$\\times$Threshold", "Fraction White",
                  "Fraction Over 65", "Constant")

    table_str = outreg(regs, var_names, var_labels)

    table_str += eol

    # table_str += table_statrow("N", [reg.N for reg in regs])
    table_str += table_statrow("R$^2", [reg.r2 for reg in regs], digits=3)

    print(table_str)

    if save:
        year_str = "{}-{}".format(year0, yearT)
        filename = out_path("reg_rd_{}.tex".format(year_str))
        with open(filename, 'w') as f:
            f.write(table_str)

    return table_str


def reg_rd(year0, yearT):
    df = rd_data(year0, yearT)

    diff_mean = df['diff'].mean()
    df['diff'] -= diff_mean

    reg_raw = mt.reg(df, 'diff', ['low', 'run', 'run_low'],
                     addcons=True, vce_type='robust')
    print(reg_raw.summary)

    reg_race = mt.reg(df, 'diff', ['low', 'run', 'run_low', 'pct_white'],
                      addcons=True, vce_type='robust')
    print(reg_race.summary)

    reg_race_age = mt.reg(df, 'diff', ['low', 'run', 'run_low', 'pct_white',
                                       'pct_65plus'],
                          addcons=True, vce_type='robust')
    print(reg_race_age.summary)

    return reg_raw, reg_race, reg_race_age


if __name__ == "__main__":
    rd_table_main()

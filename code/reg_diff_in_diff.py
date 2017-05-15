from __future__ import division, print_function, absolute_import

from econtools import save_cli, outreg, table_statrow, force_list
from econtools.util.to_latex import eol
import econtools.metrics as mt

from util.env import out_path

from clean.gather import data_clean


def table_main():
    save = save_cli()
    year_sets = (
        ([1956, 1960], [1968, 1972]),
        ([1956, 1960, 1964], [1968, 1972]),
        ([1960], [1968]),
        ([1964], [1968]),
        ([2012], [2016]),
        ([2008, 2012], [2016]),
        ([2004, 2008, 2012], [2016]),
    )
    for year0, yearT in year_sets:
        fe, lag = reg_dd(year0, yearT)
        dd_table(fe, lag, year0=year0, yearT=yearT, save=save)

def dd_table(fe_results, lag_results, year0=None, yearT=None, save=False):
    regs = [fe_results, lag_results]
    var_names = ('post_vra', 'lagged_turnout', 'pct_white', 'pct_65plus',
                 '_cons')
    var_labels = ("VRA$\\times$post", "Turnout$_{t-4}$", "Fraction White",
                  "Fraction Over 65", "Constant")
    table_str = outreg(regs, var_names, var_labels)

    table_str += eol

    table_str += table_statrow("N", [reg.N for reg in regs])
    table_str += table_statrow("R$^2$", [reg.r2 for reg in regs], digits=3)
    table_str += table_statrow("County Effects", ["Yes", "No"])

    pre_string = period_string(year0)
    post_string = period_string(yearT)

    table_str += table_statrow("Pre-period", [pre_string] * 2)
    table_str += table_statrow("Post-period", [post_string]*2)

    if save:
        filename = out_path("reg_dd_{}_{}.tex".format(pre_string, post_string))
        filename = filename.replace('--', '-')  # Latex en-dash to dash
        with open(filename, 'w') as f:
            f.write(table_str)

    print(table_str)

    return table_str

def period_string(years):
    if len(years) == 1:
        pre_string = "{}".format(min(years))
    else:
        pre_string = "{}--{}".format(min(years), max(years))

    return pre_string


def reg_dd(year0, yearT, quiet=False):
    df = prep_pre_post(year0, yearT)
    df['post_vra'] = df['had_vra'] * df['post']
    _I = df.filter(like='_I').columns.tolist()
    lag_controls = ['post_vra', 'lagged_turnout', 'pct_white', 'pct_65plus']
    controls = ['post_vra', 'pct_white', 'pct_65plus']
    fe_reg = mt.reg(df,
                    'turnout_vap',
                    controls + _I,
                    a_name='county_name',
                    vce_type='robust')
    lag_reg = mt.reg(df,
                     'turnout_vap',
                     lag_controls + _I,
                     addcons=True,
                     vce_type='robust')
    if not quiet:
        print(fe_reg.summary.iloc[:, :4])
        print(lag_reg.summary.iloc[:, :4])
    return fe_reg, lag_reg


def prep_pre_post(year0, yearT):
    df = data_clean(midterm=False)
    pre_years = force_list(year0)
    post_years = force_list(yearT)

    c_y = ['county_name', 'year']
    df = df.sort_values(c_y).set_index(c_y)
    lagged = df.groupby(level='county_name')['turnout_vap'].shift(1)
    df = df.join(lagged.to_frame('lagged_turnout'))
    df = df.reset_index()

    df = df[df['year'].isin(pre_years + post_years)].copy()
    df['post'] = df['year'].isin(post_years)

    for idx, y in enumerate(df['year'].unique()):
        if idx == 0:
            continue
        df['_Iyear_{}'.format(y)] = df['year'] == y

    return df


if __name__ == '__main__':
    table_main()

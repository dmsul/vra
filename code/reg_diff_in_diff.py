from __future__ import division, print_function, absolute_import

from econtools import force_list
import econtools.metrics as mt

from clean.gather import data_clean


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
    fe_res, lag_res = reg_dd(1960, 1968)

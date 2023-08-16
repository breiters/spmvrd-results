import warnings
import sys
import argparse
from numpy.lib.arraysetops import isin, unique
import pandas as pd
import matplotlib.pyplot as plt
import re
import math

# matrix,l1ways,l2ways,region,threads,EFFECTIVE_INST_SPEC,CPU_CYCLES,FP_DP_FIXED_OPS_SPEC,FP_DP_SCALE_OPS_SPEC,
# L2D_CACHE_REFILL,L2D_CACHE_WB,L2D_SWAP_DM,L2D_CACHE_MIBMCH_PRF,L1D_CACHE_REFILL,CPI ,Frequency ,
# L1D cache miss rate ,L2D cache miss rate ,L2-Memory Bandwidth ,DP (FP) ,DP (FP+SVE512) ,Computational Intensity (FP+SVE512) ,time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-f", "--file", type=str, default=None, help="csv file")
    parser.add_argument("-w", "--ways", type=int, default=None, help="l2 ways")
    args = parser.parse_args()

    meas = 'meas-1.8-20230617.csv'

    df_pred = pd.read_csv(args.file)
    df_meas = pd.read_csv(meas)
    

    # A64FX L2 miss correction terms
    df_meas['L2D_CACHE_REFILL'] = df_meas['L2D_CACHE_REFILL'] - df_meas['L2D_SWAP_DM'] - df_meas['L2D_CACHE_MIBMCH_PRF']

    l1ways = 0
    # l2ways = 5
    l2ways = args.ways

    df_meas_nosc = df_meas.loc[(df_meas['l1ways'] == 0) & (df_meas['l2ways'] == 0)]
    df_meas_sc   = df_meas.loc[(df_meas['l1ways'] == l1ways) & (df_meas['l2ways'] == l2ways)]

    rep_meas = 100
    rep_pred = 1

    df_pred['l1miss_sc'] = df_pred['l1miss_sc'] / rep_pred
    df_pred['l2miss_sc'] = df_pred['l2miss_sc'] / rep_pred
    df_pred['l1miss_nosc'] = df_pred['l1miss'] / rep_pred
    df_pred['l2miss_nosc'] = df_pred['l2miss'] / rep_pred
    df_pred['matrix'] = df_pred['matrix'].apply(lambda x: x.split('.')[0])

    df_pred = df_pred.drop(columns=['rep', 'threads', 'l1miss', 'l2miss'])

    # df_dup = df_meas_sc.loc[df_meas_sc.duplicated(subset=['matrix'])]
    # print('df dup sc', df_dup['matrix'])
    # df_dup = df_meas_nosc.loc[df_meas_nosc.duplicated(subset=['matrix'])]
    # print('df dup nosc', df_dup['matrix'])
    # print('pred', len(df_pred.index))
    # print('meas_sc', len(df_meas_sc.index))
    # print('meas_nosc', len(df_meas_nosc.index))

    def summarize_threads(df):
        dfg = df.groupby(['matrix', 'l1ways', 'l2ways'])
        df_summ = pd.DataFrame()
        df_summ['l1miss'] = dfg['L1D_CACHE_REFILL'].sum() / rep_meas
        df_summ['l2miss'] = dfg['L2D_CACHE_REFILL'].sum() / rep_meas
        # df_summ['flops'] = dfg['DP (FP+SVE512) '].mean()
        return df_summ

    df_meas_nosc = summarize_threads(df_meas_nosc).reset_index()
    df_meas_sc = summarize_threads(df_meas_sc).reset_index()

    # print('pred', len(df_pred.index))
    # print('meas_sc', len(df_meas_sc.index))
    # print('meas_nosc', len(df_meas_nosc.index))

    df_meas = pd.merge(df_meas_nosc, df_meas_sc, on='matrix', suffixes=('_nosc', '_sc'))

    # absolute reduction:
    df_meas['l1red'] = (df_meas['l1miss_nosc'] - df_meas['l1miss_sc'])
    df_meas['l2red'] = (df_meas['l2miss_nosc'] - df_meas['l2miss_sc'])

    # percentage reduction:
    df_meas['l1red_ratio'] = (df_meas['l1miss_nosc'] - df_meas['l1miss_sc']) / df_meas['l1miss_nosc'] * 100
    df_meas['l2red_ratio'] = (df_meas['l2miss_nosc'] - df_meas['l2miss_sc']) / df_meas['l2miss_nosc'] * 100

    df_pred['l1red'] = (df_pred['l1miss_nosc'] - df_pred['l1miss_sc'])
    df_pred['l2red'] = (df_pred['l2miss_nosc'] - df_pred['l2miss_sc'])

    df_pred['l1red_ratio'] = (df_pred['l1miss_nosc'] - df_pred['l1miss_sc']) / df_pred['l1miss_nosc'] * 100
    df_pred['l2red_ratio'] = (df_pred['l2miss_nosc'] - df_pred['l2miss_sc']) / df_pred['l2miss_nosc'] * 100


    # df_meas = df_meas.loc[(df_meas['l1red'] > 0) | (df_meas['l2red'] > 0)]
    # df_meas = df_meas.loc[(df_meas['flops_sc'] > 0.95 * df_meas['flops_nosc'])]
    df = pd.merge(df_meas, df_pred, on='matrix', suffixes=('_meas', '_pred'))
    print('df len', len(df))

    df = df.drop(columns=['l1ways_sc', 'l2ways_sc', 'l1ways_nosc', 'l2ways_nosc'])

    df['nnz_per_row'] = df['nnz'] / df['rows']

    df_variance = pd.read_csv('variance.csv')
    df_variance = df_variance.drop(columns=['mean_variance'])
    df_variance['matrix'] = df_variance['matrix'].apply(lambda x: x.split('.')[0])
    df_variance['matrix'] = df_variance['matrix'].apply(lambda x: x.split('/')[-1])
    df = pd.merge(df, df_variance, on='matrix')
    # coefficient of variation
    df['nnz_per_row_var_coeff'] = df['variance'].apply(lambda x: math.sqrt(x)) / (df['nnz_per_row'])
    # print(df)

    # print(df.corr(numeric_only=True))

    df['l1ape_sc']   = abs((df['l1miss_sc_meas'] - df['l1miss_sc_pred']) / df['l1miss_sc_meas']) * 100
    df['l2ape_sc']   = abs((df['l2miss_sc_meas'] - df['l2miss_sc_pred']) / df['l2miss_sc_meas']) * 100
    df['l1ape_nosc'] = abs((df['l1miss_nosc_meas'] - df['l1miss_nosc_pred']) / df['l1miss_nosc_meas']) * 100
    df['l2ape_nosc'] = abs((df['l2miss_nosc_meas'] - df['l2miss_nosc_pred']) / df['l2miss_nosc_meas']) * 100
    
    df['l1ape_red']  = abs((df['l1red_meas'] - df['l1red_pred']) / df['l1red_meas'] * 100)
    df['l2ape_red']  = abs((df['l2red_meas'] - df['l2red_pred']) / df['l2red_meas'] * 100)

    df['l1ape_red_ratio']  = abs((df['l1red_ratio_meas'] - df['l1red_ratio_pred']) / df['l1red_ratio_meas'] * 100)
    df['l2ape_red_ratio']  = abs((df['l2red_ratio_meas'] - df['l2red_ratio_pred']) / df['l2red_ratio_meas'] * 100)

    # print(df[['matrix', 'nnz']])


    # use only matrices > L2 size
    # df = df.loc[df['nnz'] * 12 + (16 + 4 * 8) * df['rows'] > 32 * 1024 * 1024]
    # df = df.loc[df['nnz'] * 12 + (16 + 1 * 8) * df['rows'] > 32 * 1024 * 1024]
    # df = df.loc[df['nnz'] * 12 > 32 * 1024 * 1024]
    df = df.loc[df['nnz'] * 12 > 8 * 1024 * 1024]
    print('matrices:', len(df.index))

    # use only matrices where vectors don't fit L2
    # df = df.loc[(16 + 4 * 8) * df['rows'] > 32 * 1024 * 1024]
    # df = df.loc[(16 + 1 * 8) * df['rows'] > 32 * 1024 * 1024] # makes sense ?!

    #df = df.loc[df['nnz'] * 24 > 32 * 1024 * 1024]
    # df = df.loc[df['nnz'] * 12 + 12 > 32 * 1024 * 1024]

    # use only matrices with positive predicted reduction
    # df = df.loc[(df['l1red_pred'] > 0) | (df['l2red_pred'] > 0)]
    # df = df.loc[(df['l2red_pred'] > 0) & (df['l2red_meas'] > 0)]
    

    


    plt.style.use('ggplot')
    rmin = 2
    rmax = 21
    mape_sc = []
    mape_nosc = []
    std_sc = []
    std_nosc = []
    count = []
    nnz_range = range(rmin, rmax, 2)
    min_size = []
    avg_size = []

    # dfbar = pd.DataFrame()
    for i in nnz_range:
        df2 = df.loc[df['nnz_per_row'] >= i]
        # df2 = df.loc[(df['nnz_per_row'] >= i) & (df['nnz_per_row'] < i + 1)]
        count.append(len(df2.index))
        min_size.append(int(12 * df2['nnz'].min() / 1024 / 1024))
        avg_size.append(int(12 * df2['nnz'].mean() / 1024 / 1024))
        if True:
            mape_sc.append(df2['l2ape_sc'].mean())
            std_sc.append(df2['l2ape_sc'].std())
            mape_nosc.append(df2['l2ape_nosc'].mean())
            std_nosc.append(df2['l2ape_nosc'].std())
        else:
            mape_sc.append(df2['l1ape_sc'].mean())
            std_sc.append(df2['l1ape_sc'].std())
            mape_nosc.append(df2['l1ape_nosc'].mean())
            std_nosc.append(df2['l1ape_nosc'].std())

    # std_sc = list(map(float, std_sc))
    # std_nosc = list(map(float, std_nosc))

    x = [i for i in nnz_range]
    d = {'nnz_per_row' : x,
        'MAPE_SC' : mape_sc,
        'MAPE_NOSC' : mape_nosc,
        'err_sc' : std_sc,
        'err_nosc' : std_nosc
        }

    fig, ax = plt.subplots(figsize=(3.5, 3))
    dfbar = pd.DataFrame(d)
    # print(dfbar)
    # dfbar.to_csv('bar.csv')
    # dfbar.plot.bar(x='nnz_per_row', y=['MAPE_SC', 'MAPE_NOSC'], ax=ax, rot=0)
    # ax.legend(['5 L2 Ways', 'NO SC'], ncol=2)
    dfbar.plot.bar(x='nnz_per_row', y=['MAPE_SC', 'MAPE_NOSC'], ax=ax, rot=0, legend=False)
    ax.yaxis.grid(color='gray', linestyle='dashed')
    # ax.set_axisbelow(True)
    ax.set_ylabel('MAPE [%]')
    ax.set_xlabel('min. avg. NNZs per row')
    # ax.set_ylim((0, 7))


    # for i in range(0, int((rmax-rmin) / 2) + 1):
        # ax.annotate(str(count[i]), (i - 0.18, 0.2), color='darkslategray', fontsize=10.0, rotation=90)
        # ax.annotate('min=' + str(min_size[i]) + ' avg=' +  str(avg_size[i]) + ' count=' + str(count[i]), (i - 0.18, 0.05), color='darkslategray', fontsize=10.0, rotation=90)

    plt.tight_layout(pad=0.2)
    # plt.savefig('fig.pdf')
    # ax.bar_label(count)
    # for p in ax.patches:
        # ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
    # dfbar.plot.bar(x='nnz_per_row', y='MAPE_SC', yerr='err_sc', ax=ax, color='blue')
    # dfbar.plot.bar(x='nnz_per_row', y='MAPE_NOSC', yerr='err_nosc', ax=ax, color='orange')

    # ax = fig.add_axes([0,0,1,1])
    # ax.bar(x, mape_sc)
    # plt.show()

    # matrices where a reduction is predicted but the opposite is the case or vice versa
    # df_bad = df.loc[((df['l2red_meas'] > 0) & (df['l2red_pred'] < 0)) | ((df['l2red_meas'] < 0) & (df['l2red_pred'] > 0))]
    # df_bad = df_bad.loc[abs(df_bad['l2red_meas'] / df_bad['l2miss_nosc_meas']) > 0.005]
    df_bad = df.loc[df['l2red_pred'] < 0]
    # print('fail:')
    # print(df_bad[['matrix', 'rows', 'nnz', 'nnz_per_row', 'l2miss_nosc_meas', 'l2miss_sc_meas', 'l2red_meas', 'l2red_pred']])

    # df = df.loc[(df['l2red_meas'] > 10000) | (df['l2red_meas'] < -10000)]
    df_2 = df.loc[abs(df['l2red_meas']) / df['l2miss_nosc_meas'] > 0.10]

    df['diff'] = (df['l2miss_nosc_meas'] - df['l2miss_nosc_pred']) / df['l2miss_nosc_meas']
    # print(df[['nnz', 'diff']])

    # df = df.loc[(df['nnz_per_row'] >= 8) & (df['nnz_per_row_var_coeff'] <= 1.0)]
    # df = df.loc[(df['nnz_per_row'] < 8) & (df['nnz_per_row_var_coeff'] > 1.0)]
    # print(df[['l2ape_sc', 'l2ape_nosc']])

    df1 = df.loc[df['diff'] < 0]
    print('diff < 0', df1['diff'].min())
    print(df1[['matrix', 'nnz', 'nnz_per_row', 'rows', 'l2miss_nosc_meas', 'diff', 'nnz_per_row_var_coeff']])

    df1 = df.loc[df['diff'] >= 0]
    print('diff >= 0', df1['diff'].max())
    print(df1[['matrix', 'nnz', 'nnz_per_row', 'rows', 'l2miss_nosc_meas', 'diff', 'nnz_per_row_var_coeff']])

    df1 = df.loc[df['diff'] > 0.1]
    print(df1[['matrix', 'nnz', 'nnz_per_row', 'rows', 'l2miss_nosc_meas', 'diff', 'nnz_per_row_var_coeff']])

    df1 = df.loc[df['l2ape_nosc'] > 15]
    print('ape no sc > 15')
    print(df1[['matrix', 'nnz', 'nnz_per_row', 'rows', 'l2ape_nosc', 'variance', 'nnz_per_row_var_coeff']])

    df1 = df.loc[df['l2ape_sc'] > 15]
    print('ape sc > 15')
    print(df1[['matrix', 'nnz', 'nnz_per_row', 'rows', 'l2ape_sc', 'variance', 'nnz_per_row_var_coeff']])

    print('mean var coeff', df['nnz_per_row_var_coeff'].mean())
    print('median var coeff', df['nnz_per_row_var_coeff'].median())
    # df = df.loc[df['nnz_per_row_var_coeff'] < 1.0]
    # df = df.loc[df['nnz_per_row'] >= 8]
    print(len(df))

    # print('df2:')
    # print(df_2)

    # print(df[['l2red_meas', 'l2red_pred']])
    # print((df['l2red_meas'] - df['l2red_pred']) / df['l2red_meas'])
    # print((df['l2red_meas'] - df['l2red_pred']) / df['l2red_meas'])

    print('MAPE L1    sc = {:.2f} pm {:.2f}'.format(df["l1ape_sc"].mean(), df['l1ape_sc'].std()))
    print('MAPE L2    sc = {:.2f} pm {:.2f}'.format(df['l2ape_sc'].mean(), df['l2ape_sc'].std()))
    print('MAPE L1 no sc = {:.2f} pm {:.2f}'.format(df['l1ape_nosc'].mean(), df['l1ape_nosc'].std()))
    print('MAPE L2 no sc = {:.2f} pm {:.2f}'.format(df['l2ape_nosc'].mean(), df['l2ape_nosc'].std()))
    # print('MAPE L1   red = {:.2f} pm {:.2f}'.format(df['l1ape_red'].mean(), df['l1ape_red'].std()))
    # print('MAPE L2   red = {:.2f} pm {:.2f}'.format(df['l2ape_red'].mean(), df['l2ape_red'].std()))

    # print('MAPE L1   red = {:.2f} pm {:.2f}'.format(df_1['l1ape_red'].mean(), df_1['l1ape_red'].std()))
    # print('MAPE L2   red = {:.2f} pm {:.2f}'.format(df_2['l2ape_red'].mean(), df_2['l2ape_red'].std()))
    # print('MAPE L2 red r = {:.2f} pm {:.2f}'.format(df_2['l2ape_red_ratio'].mean(), df_2['l2ape_red_ratio'].std()))

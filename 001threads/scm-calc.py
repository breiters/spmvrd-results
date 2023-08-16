import warnings
import sys
import argparse
from numpy.lib.arraysetops import isin, unique
import pandas as pd
import re

pd.options.mode.chained_assignment = None  # default='warn'

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

MEMBLOCKLEN = 256

INF_BUCKET = 18446744073709551615

L1capacity = 64
L2capacity = 8192

L1ways = 4
L2ways = 16

l1ways = 0
l2ways = 0

mins_l1 = [c * L1capacity / L1ways for c in range(L1ways)]
mins_l2 = [c * L2capacity / L2ways for c in range(L2ways)]

# matrix,cache_id,shared,mindist,count

def misses(df, sc):
    # rescale buckets to KiB
    df['mindist'] = df['mindist'] * MEMBLOCKLEN // 1024
    # df['matrix'] = df['matrix'].apply(lambda x: x.split('/')[-1])

    df_private = df.loc[df['shared'] == 0]
    df_shared  = df.loc[df['shared'] == 1]

    min_dist_l1 = 0
    min_dist_l2 = 0
    if sc:
        min_dist_l1 = int(64 * (4-l1ways) / 4)
        min_dist_l2 = int(8 * 1024 * (16-l2ways) / 16)
    else:
        min_dist_l1 = int(64)
        min_dist_l2 = int(8 * 1024)

    def miss_x(df, min_dist):
        return df[df['mindist'] >= min_dist].groupby(['cache_id']).sum('count')['count']

    miss_x_l1 = miss_x(df_private, min_dist_l1)
    miss_x_l2 = miss_x(df_shared, min_dist_l2)

    return miss_x_l1, miss_x_l2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-f", "--file", type=str, default=None, help="csv file")
    parser.add_argument("-i", "--l1ways", type=int, default=None, help="l1ways")
    parser.add_argument("-j", "--l2ways", type=int, default=None, help="l2ways")
    args = parser.parse_args()

    df = pd.read_csv(args.file)

    l1ways = args.l1ways
    l2ways = args.l2ways

    df_sc = pd.read_csv(args.file)
    df_nosc = pd.read_csv(args.file.replace('/sc/', '/nosc/'))

    matrix = args.file.split('/')[-1].split('.mtx')[0]
    df_sc['matrix'] = matrix
    df_nosc['matrix'] = matrix

    pattern = re.compile('[0-9]+threads.csv')
    m = pattern.search(args.file)
    num_threads = int(m.group().split('threads')[0])

    verbose = False
    csv = True

    rep = 1

    nnz  = df_sc['nnz'].unique()[0]
    nrow = df_sc['nrows'].unique()[0]

    miss_a      = rep * 8 * nnz / MEMBLOCKLEN
    miss_colidx = rep * 4 * nnz / MEMBLOCKLEN

    miss_others_l1 = 0
    miss_others_l2 = 0

    if l1ways > 0:
        if nnz * 12 > int(64 * l1ways / 4):
            miss_others_l1 = miss_a + miss_colidx
    else:
        if nnz * 12 + (8 + 8) * nrow + 8 * (nrow + 1) > int(64):
            miss_others_l1 = miss_a + miss_colidx

    if num_threads == 1:
        if nnz * 12 > 1 * 8 * 1024 * l2ways / 16:
            miss_others_l2 = miss_a + miss_colidx
    else:
        if nnz * 12 > 4 * 8 * 1024 * l2ways / 16:
            miss_others_l2 = miss_a + miss_colidx

    miss_x_l1_sc, miss_x_l2_sc = misses(df_sc, True)
    miss_x_l1_nosc, miss_x_l2_nosc = misses(df_nosc, False)

    red_l1 = 0
    red_l2 = 0
    if sum(miss_x_l1_nosc) > 0 :
        red_l1 = (sum(miss_x_l1_nosc) - sum(miss_x_l1_sc) - miss_others_l1) / (sum(miss_x_l1_nosc)) * 100

    if sum(miss_x_l2_nosc) > 0:
        red_l2 = (sum(miss_x_l2_nosc) - sum(miss_x_l2_sc) - miss_others_l2) / (sum(miss_x_l2_nosc)) * 100

    # matrix,threads,nnz,rows,rep,l1miss,l2miss,l1miss_sc,l2miss_sc,l1red,l2red
    print(
        df_sc['matrix'][0],
        num_threads,
        df_sc['nnz'][0],
        df_sc['nrows'][0],
        rep,
        sum(miss_x_l1_nosc),
        sum(miss_x_l2_nosc),
        sum(miss_x_l1_sc) + miss_others_l1,
        sum(miss_x_l2_sc) + miss_others_l2,
        red_l1,
        red_l2,
        sep=',')
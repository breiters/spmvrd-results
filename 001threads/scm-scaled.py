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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-f", "--file", type=str, default=None, help="csv file")
    parser.add_argument("-i", "--l1ways", type=int, default=None, help="l1ways")
    parser.add_argument("-j", "--l2ways", type=int, default=None, help="l2ways")
    args = parser.parse_args()

    df = pd.read_csv(args.file)

    l1ways = args.l1ways
    l2ways = args.l2ways

    matrix = args.file.split('/')[-1].split('.mtx')[0]
    df['matrix'] = matrix

    csv = True
    verbose = False

    # rescale buckets to KiB
    df['mindist'] = df['mindist'] * MEMBLOCKLEN // 1024
    # print(df['mindist'].head(30))

    # df['matrix'] = df['matrix'].apply(lambda x: x.split('/')[-1])

    pattern = re.compile('[0-9]+threads.csv')
    m = pattern.search(args.file)
    num_threads = int(m.group().split('threads')[0])
    
    # print(num_threads)
    # print(df['matrix'][0])

    df_private = df.loc[df['shared'] == 0]
    df_shared  = df.loc[df['shared'] == 1]

    nnz = df['nnz'].unique()[0]
    nrow = df['nrows'].unique()[0]
    rep = 1

    scale_nosc = 8.0 / (16.0 * nrow / nnz + 20.0)
    scale_sc   = 8.0 / (16.0 * nrow / nnz + 8.0)

    min_dist_for_l1_miss_nosc = int(64 * scale_nosc)
    min_dist_for_l2_miss_nosc = int(8 * 1024 * scale_nosc)

    min_dist_for_l1_miss_sc = int(64 * scale_sc * (4-l1ways) / 4)
    min_dist_for_l2_miss_sc = int(8 * 1024 * scale_sc * (16-l2ways) / 16)

    miss_a      = 8 * nnz / MEMBLOCKLEN
    miss_colidx = 4 * nnz / MEMBLOCKLEN
    miss_y      = 8 * nrow / MEMBLOCKLEN
    miss_rowptr = 8 * (nrow + 1) / MEMBLOCKLEN

    def miss_x(df, min_dist):
        return df[df['mindist'] >= min_dist].groupby(['cache_id']).sum('count')['count']

    miss_x_l1_nosc = sum(miss_x(df_private, min_dist_for_l1_miss_nosc))
    miss_x_l2_nosc = sum(miss_x(df_shared, min_dist_for_l2_miss_nosc))
    miss_x_l1_sc = sum(miss_x(df_private, min_dist_for_l1_miss_sc))
    miss_x_l2_sc = sum(miss_x(df_shared, min_dist_for_l2_miss_sc))

    miss_l1_nosc = 1
    miss_l2_nosc = 1
    miss_l1_sc = 1
    miss_l2_sc = 1

    size_a = nnz * 8
    size_colidx = nnz * 4
    size_x = nrow * 8
    size_y = nrow * 8
    size_rowptr = (nrow + 1) * 8

    size_l1 = 1 * 64 * 1024
    size_l2 = 1 * 8 * 1024 * 1024

    # set l1 cache misses
    if size_a + size_colidx + size_y + size_rowptr + size_x < size_l1:
        miss_l1_nosc = 1
    else:
        miss_l1_nosc = (size_a + size_colidx + size_y + size_rowptr) / MEMBLOCKLEN + miss_x_l1_nosc

    if size_a + size_colidx < l1ways * size_l1 / 4:
        if size_y + size_rowptr + size_x < (4 - l1ways) * size_l1 / 4:
            miss_l1_sc = 1
        else:
            miss_l1_sc = (size_y + size_rowptr) / MEMBLOCKLEN + miss_x_l1_sc
    else:
        if size_y + size_rowptr + size_x < (4 - l1ways) * size_l1 / 4:
            miss_l1_sc = (size_a + size_colidx) / MEMBLOCKLEN
        else:
            miss_l1_sc = (size_a + size_colidx + size_y + size_rowptr) / MEMBLOCKLEN + miss_x_l1_sc

    # set l2 cache misses
    if size_a + size_colidx + size_y + size_rowptr + size_x < size_l2:
        miss_l2_nosc = 1
    else:
        miss_l2_nosc = (size_a + size_colidx + size_y + size_rowptr) / MEMBLOCKLEN + miss_x_l2_nosc

    if size_a + size_colidx < l2ways * size_l2 / 16:
        if size_y + size_rowptr + size_x < (16 - l2ways) * size_l2 / 16:
            miss_l2_sc = 1
        else:
            miss_l2_sc = (size_y + size_rowptr) / MEMBLOCKLEN + miss_x_l2_sc
    else:
        if size_y + size_rowptr + size_x < (16 - l2ways) * size_l2 / 16:
            miss_l2_sc = (size_a + size_colidx) / MEMBLOCKLEN
        else:
            miss_l2_sc = (size_a + size_colidx + size_y + size_rowptr) / MEMBLOCKLEN + miss_x_l2_sc

    # matrix,threads,nnz,rows,rep,l1miss,l2miss,l1miss_sc,l2miss_sc,l1red,l2red
    print(
        df['matrix'][0],
        num_threads,
        df['nnz'][0],
        df['nrows'][0],
        rep,
        miss_l1_nosc,
        miss_l2_nosc,
        miss_l1_sc,
        miss_l2_sc,
        (miss_l1_nosc - miss_l1_sc) / miss_l1_nosc * 100,
        (miss_l2_nosc - miss_l2_sc) / miss_l2_nosc * 100,
        sep=',')

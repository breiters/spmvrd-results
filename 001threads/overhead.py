import warnings
import sys
import argparse
from numpy.lib.arraysetops import isin, unique
import pandas as pd
import matplotlib.pyplot as plt
import re

if __name__ == '__main__':
    df_scaled = pd.read_csv('scaled/overhead001t.csv')
    df_calc_sc = pd.read_csv('calc/sc/overhead001t.csv')
    df_calc_nosc = pd.read_csv('calc/nosc/overhead001t.csv')

    df_scaled = df_scaled.groupby('matrix').mean().reset_index()
    df_calc_sc = df_calc_sc.groupby('matrix').mean().reset_index()
    df_calc_nosc = df_calc_nosc.groupby('matrix').mean().reset_index()
    # print(df_calc_sc)

    df_calc = pd.DataFrame()

    df_calc['matrix'] = df_calc_sc['matrix']
    df_calc['time'] = df_calc_sc['time'] + df_calc_nosc['time']

    df_calc['overhead'] = df_calc['time'] / df_scaled['time']

    print(df_calc)

    print('mean: ', df_calc['overhead'].mean())
    print('min: ', df_calc['overhead'].min())
    print('max: ', df_calc['overhead'].max())

    print('calc time max: ', df_calc['time'].max())
    print('scaled time max: ', df_scaled['time'].max())

    print('calc time mean: ', df_calc['time'].mean())
    print('scaled time mean: ', df_scaled['time'].mean())
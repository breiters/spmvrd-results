#!/usr/bin/env gnuplot
# SparCity - A64FX Sector Cache
#
# Copyright (C) 2023 Simula Research Laboratory
#
# Authors: James D. Trotter <james@simula.no>
#
# Date: 2023-05-04

set terminal pngcairo size 1024,1024
set output '02a-csr-speedup-vs-nonzeros.png'

# set terminal epslatex size 8,8 standalone font 'phv,8pt' header "\\usepackage[cm]{sfmath}"
# set output '02a-csr-speedup-vs-nonzeros.tex'

set title 'Speedup versus nonzeros for CSR SpMV with sector cache on Fujitsu A64FX (L2 ways: 2)'

set key noautotitle horizontal top left
# unset key

# set xlabel 'L2 ways'
# set xtics 0,1 nomirror
# set xrange [1.5:6.5]

set xlabel 'matrix nonzeros (millions)'
set xtics nomirror
set logscale x
# set xrange [0.5:2000]

set ylabel 'speedup'
set ytics nomirror
# set logscale y
# set yrange [0:1.5]

# horizontal line for speedup=1
set arrow from graph 0,first 1 to graph 1,first 1 nohead dashtype "."

# # vertical arrow at L1 cache capacity (48*64 KiB = 3072 KiB; 3072 KiB / 12 B = 262 144)
# set arrow from 1e-6*262144, graph 0 to 1e-6*262144, graph 1 nohead dashtype "--"
# # vertical arrow at 1 out of 4 ways of L1 cache capacity (0.25*3072 KiB / 12 B = 65 536)
# set arrow from 1e-6*65536, graph 0 to 1e-6*65536, graph 1 nohead dashtype "--"
# # vertical arrow at 2 out of 4 ways of L1 cache capacity (0.5*3072 KiB / 12 B = 131 072)
# set arrow from 1e-6*131072, graph 0 to 1e-6*131072, graph 1 nohead dashtype "--"
# # vertical arrow at 2 out of 4 ways of L1 cache capacity (0.75*3072 KiB / 12 B = 196 608)
# set arrow from 1e-6*196608, graph 0 to 1e-6*196608, graph 1 nohead dashtype "--"

# vertical arrow at L2 cache capacity (4*8 MiB = 32 MiB; 32 MiB / 12 B = 2 796 203)
set arrow from 1e-6*2796203, graph 0 to 1e-6*2796203, graph 1 nohead dashtype "--"
# set label "L2" at 1e-6*2796203, graph 1 offset character -1, character -2 rotate right
# vertical arrow at 14 out of 16 ways of L2 cache capacity (14/16*32 MiB / 12 B = 2 446 677)
set arrow from 1e-6*2446677, graph 0 to 1e-6*2446677, graph 1 nohead dashtype "--"
set label "14 of 16 L2 ways" at 1e-6*2446677, graph 1 offset character -1.5, character -5 rotate right

plot '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-20230505.txt' using ($5*1e-6):($29/$12) linecolor '#d95f02' title 'L1 ways: none', \
#     '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-1-l1ways-20230505.txt' using ($5*1e-6):($29/$12) linecolor '#7570b3' title 'L1 ways: 1', \
#     '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-2-l1ways-20230505.txt' using ($5*1e-6):($29/$12) linecolor '#e7298a' title 'L1 ways: 2', \
#     '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-3-l1ways-20230505.txt' using ($5*1e-6):($29/$12) linecolor '#66a61e' title 'L1 ways: 3', \

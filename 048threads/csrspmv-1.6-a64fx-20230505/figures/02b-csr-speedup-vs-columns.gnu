#!/usr/bin/env gnuplot
# SparCity - A64FX Sector Cache
#
# Copyright (C) 2023 Simula Research Laboratory
#
# Authors: James D. Trotter <james@simula.no>
#
# Date: 2023-05-04

set terminal pngcairo size 1024,1024
set output '02b-csr-speedup-vs-columns.png'

# set terminal epslatex size 8,8 standalone font 'phv,8pt' header "\\usepackage[cm]{sfmath}"
# set output '02b-csr-speedup-vs-columns.tex'

set title 'Speedup versus columns for CSR SpMV with sector cache on Fujitsu A64FX (L2 ways: 2)'

set key noautotitle horizontal top left
# unset key

# set xlabel 'L2 ways'
# set xtics 0,1 nomirror
# set xrange [1.5:6.5]

set xlabel 'matrix columns (millions)'
set xtics nomirror
set logscale x
# set xrange [0.5:2000]

set ylabel 'speedup'
set ytics nomirror
# set logscale y
# set yrange [0:1.5]

# horizontal line for speedup=1
set arrow from graph 0,first 1 to graph 1,first 1 nohead dashtype "."

# vertical arrow at L1 cache capacity (48*64 KiB = 3072 KiB; 3072 KiB / 8 B = 393 216)
set arrow from 1e-6*393216, graph 0 to 1e-6*393216, graph 1 nohead dashtype "--"
set label "L1" at 1e-6*393216, graph 0 offset character -1, character 1 right
# # vertical arrow at 1 out of 4 ways of L1 cache capacity (0.25*3072 KiB / 8 B = 98 304)
# set arrow from 1e-6*98304, graph 0 to 1e-6*98304, graph 1 nohead dashtype "--"
# # vertical arrow at 2 out of 4 ways of L1 cache capacity (0.5*3072 KiB / 8 B = 196 608)
# set arrow from 1e-6*196608, graph 0 to 1e-6*196608, graph 1 nohead dashtype "--"
# # vertical arrow at 2 out of 4 ways of L1 cache capacity (0.75*3072 KiB / 8 B = 294 912)
# set arrow from 1e-6*294912, graph 0 to 1e-6*294912, graph 1 nohead dashtype "--"

# # vertical arrow at L2 cache capacity (4*8 MiB = 32 MiB; 32 MiB / 8 B = 4 194 304)
# set arrow from 1e-6*4194304, graph 0 to 1e-6*4194304, graph 1 nohead dashtype "--"
# vertical arrow at 14 out of 16 ways of L2 cache capacity (14/16*32 MiB / 8 B = 3 670 016)
set arrow from 1e-6*3670016, graph 0 to 1e-6*3670016, graph 1 nohead dashtype "--"
set label "L2" at 1e-6*3670016, graph 0 offset character -1, character 1 right

plot '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-20230505.txt' using ($4*1e-6):($29/$12) linecolor '#d95f02' title 'L1 ways: none', \
#     '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-1-l1ways-20230505.txt' using ($4*1e-6):($29/$12) linecolor '#7570b3' title 'L1 ways: 1', \
#     '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-2-l1ways-20230505.txt' using ($4*1e-6):($29/$12) linecolor '#e7298a' title 'L1 ways: 2', \
#     '< paste ../summary/01a-csrspmv-1.6-a64fx-nosc-20230505.txt ../summary/01a-csrspmv-1.6-a64fx-sc-02-l2ways-3-l1ways-20230505.txt' using ($4*1e-6):($29/$12) linecolor '#66a61e' title 'L1 ways: 3', \

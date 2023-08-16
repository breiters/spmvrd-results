#!/bin/bash
# SparCity - SuiteSparse Matrix Collection
# Copyright (C) 2023 James D. Trotter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# authors: James D. Trotter <james@simula.no>
#
# This script runs performance benchmarks for parallel sparse
# matrix-vector multiply using the compressed sparse row storage
# format with matrices from SuiteSparse. Note that the program
# 'csrspmv' must be in PATH. Alternatively, the environment variable
# CSRSPMV can be set to point to the csrspm program.
#
# Example usage:
#
#  $ pjsub scripts/01a-csrspmv-1.6-a64fx-sc-10-l2ways_48-threads.sh --verbose
#
# ChangeLog:
#
#  2023-05-05: update to csrspmv-1.6
#  2023-04-16: initial version
#

#PJM -N csrspmv-1.6-a64fx-sc-10-l2ways_48-threads
#PJM -g jh180024o
#PJM -L rscgrp=regular-o
#PJM -L node=1
#PJM --mpi proc=1
#PJM --omp thread=48
#PJM -L elapse=12:00:00
#PJM -o logs/01a-csrspmv-1.6-a64fx-sc-10-l2ways_48-threads-stdout.txt
#PJM -e logs/01a-csrspmv-1.6-a64fx-sc-10-l2ways_48-threads-stderr.txt

export LC_ALL=C
export OMP_PROC_BIND=close
export OMP_PLACES=cores
export OMP_WAIT_POLICY=active
export OMP_DISPLAY_ENV=true

export FLIB_HPCFUNC=TRUE
export FLIB_SCCR_CNTL=TRUE
export FLIB_L1_SCCR_CNTL=FALSE
export XOS_MMM_L_HPAGE_TYPE=hugetlbfs
export XOS_MMM_L_PAGING_POLICY=demand:demand:demand

echo "FLIB_HPCFUNC=${FLIB_HPCFUNC}" >&2
echo "FLIB_SCCR_CNTL=${FLIB_SCCR_CNTL}" >&2
echo "FLIB_L1_SCCR_CNTL=${FLIB_L1_SCCR_CNTL}" >&2
echo "XOS_MMM_L_HPAGE_TYPE=${XOS_MMM_L_HPAGE_TYPE}" >&2
echo "XOS_MMM_L_PAGING_POLICY=${XOS_MMM_L_PAGING_POLICY}" >&2

export CSRSPMV=bin/csrspmv-1.6-a64fx-sc-10-l2ways
./scripts/01a-csrspmv.sh \
    --verbose \
    --index=mtx/original489.txt \
    --papi-event-file=share/papi_util_a64fx_memdp.txt \
    --papi-event-format=csv \
    --papi-event-per-thread \
    --papi-event-summary \
    --repeat=100 \
    --outdir=results/01a-csrspmv-1.6-a64fx-sc-10-l2ways-$(date +%Y%m%d)

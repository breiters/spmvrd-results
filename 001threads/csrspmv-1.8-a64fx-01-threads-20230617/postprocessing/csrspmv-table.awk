#!/usr/bin/awk -f
BEGIN {
    n = 0;
    mintime = 0;
    maxperf = 0;
    meanperf = 0;
    L1miss = 0;
    L2miss = 0;
}
$1 == "csr_from_coo:" {
    rows=$4;
    columns=$6;
    nonzeros=$8;
    threads=$16;
    rowsperthreadmin=$18;
    rowsperthreadmax=$20;
    nzperthreadmin=$24;
    nzperthreadmax=$26;
    nzperthreadmean=$8/$16;
    imbalancefactor=$26/($8/$16);
}
$1 == "gemv:" {
    if (n == 0) { mintime = $2 } else if (mintime > $2) { mintime = $2 };
    if (maxperf < $6) { maxperf = $6 };
    if (n > 3) { meanperf += $6 };
    n = n + 1;
}
$0 ~ "^gemv," {
    # 1 region,
    # 2 threads,
    # 3 EFFECTIVE_INST_SPEC,
    # 4 CPU_CYCLES,
    # 5 FP_DP_FIXED_OPS_SPEC,
    # 6 FP_DP_SCALE_OPS_SPEC,
    # 7 L2D_CACHE_REFILL,
    # 8 L2D_CACHE_WB,
    # 9 L2D_SWAP_DM,
    # 10 L2D_CACHE_MIBMCH_PRF,
    # 11 L1D_CACHE_REFILL,
    # 12 CPI ,
    # 13 Frequency ,
    # 14 L1D cache miss rate ,
    # 15 L2D cache miss rate ,
    # 16 L2-Memory Bandwidth ,
    # 17 DP (FP) ,
    # 18 DP (FP+SVE512) ,
    # 19 Computational Intensity (FP+SVE512) ,
    # 20 time
    m = split($0, a, ",");
    L1miss += a[11] / n;
    L2miss += (a[7]-a[9]-a[10]) / n;
}
END {
    meanperf = meanperf / (n-3);
    printf "  %9d   %9d   %10d   %7d   %9d   %9d   %9.0f   %9.3f   %11.6f   %9.3f   %9.3f   %9d   %9d   %6.1f   %6.1f", \
	rows, columns, nonzeros, \
	threads, nzperthreadmin,  nzperthreadmax,  nzperthreadmean, imbalancefactor, \
	mintime, maxperf, meanperf, L1miss, L2miss, 1e-9*256*L1miss/mintime, 1e-9*256*L2miss/mintime
}

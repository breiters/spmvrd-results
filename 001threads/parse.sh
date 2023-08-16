#!/bin/bash

VERS=1.8
DATE=20230617
OUT_FILE=meas-${VERS}-${DATE}.csv

#HEADER=$(grep region csrspmv-${VERS}-a64fx-${DATE}/results/01a-csrspmv-${VERS}-a64fx-sc-02-l2ways-1-l1ways-${DATE}/AG-Monien/debr-stderr.txt)
HEADER=$(grep region, csrspmv-1.8-a64fx-01-threads-20230617/results/01a-csrspmv-1.8-a64fx-sc-11-l2ways-1-l1ways-20230617/AG-Monien/debr-stderr.txt)

echo matrix,l1ways,l2ways,${HEADER} > ${OUT_FILE}

for f in csrspmv-${VERS}-a64fx-01-threads-${DATE}/results/01a-csrspmv-${VERS}-a64fx-nosc-${DATE}/*/*stderr.txt; do
	FILE=${f%-stderr.txt*}
	FILE=${FILE##*/}
	grep region, $f -A1 | grep -v region | awk -v file=${FILE} '{print file ",0,0," $1}' >> ${OUT_FILE}; 
done

# 01a-csrspmv-1.5-a64fx-sc-02-l2ways-1-l1ways-${DATE}/
# 01a-csrspmv-1.5-a64fx-sc-02-l2ways-${DATE}/

for l2 in 02 03 04 05 06 07 08 09 10 11 12 13 14; do
	for f in csrspmv-${VERS}-a64fx-01-threads-${DATE}/results/01a-csrspmv-${VERS}-a64fx-sc-$l2-l2ways-${DATE}/*/*stderr.txt; do
			FILE=${f%-stderr.txt*}
			FILE=${FILE##*/}
        	grep region, $f -A1 | grep -v region | awk -v L2=$l2 -v file=${FILE} '{print file ",0," L2 "," $1}' >> ${OUT_FILE};
	done;
	for l1 in 1 2 3; do
		for f in csrspmv-${VERS}-a64fx-01-threads-${DATE}/results/01a-csrspmv-${VERS}-a64fx-sc-$l2-l2ways-$l1-l1ways-${DATE}/*/*stderr.txt; do
				FILE=${f%-stderr.txt*}
				FILE=${FILE##*/}
        		grep region, $f -A1 | grep -v region | awk -v L1=$l1 -v L2=$l2 -v file=${FILE} '{print file "," L1 "," L2 "," $1}' >> ${OUT_FILE};
		done;
	done
done


#!/bin/bash

l1=$1
l2=$2
VERS=1.6
DATE=20230505
OUT_FILE=result-${l1}l1-${l2}l2-calc.csv

echo matrix,threads,nnz,rows,rep,l1miss,l2miss,l1miss_sc,l2miss_sc,l1red,l2red > ${OUT_FILE}
for f in calc/sc/*threads.csv; do echo $f; python3 scm-calc.py -f $f -i $l1 -j $l2 >> ${OUT_FILE}; done

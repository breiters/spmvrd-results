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
# Print a table to summarise performance results for parallel
# matrix-vector multiply with matrices in compressed sparse row
# format.
#
# Example usage:
#
#  $ csrspmv-table.sh --verbose results/csrspmv-rome16q-002-threads/HB/arc130-stderr.txt
#
#
# ChangeLog:
#
#  2023-03-14: print average performance in addition to max
#  2023-03-03: format changed to include min/max rows per thread
#  2023-02-28: initial version
#

program_name=csrspmv-table.sh
program_version=1.0.0

function help()
{
    printf "Usage: ${0} [OPTION].. FILE..\n"
    printf " summarise parallel sparse matrix-vector multiply results\n"
    printf "\n"
    printf " Options are:\n"
    printf "  %-20s\t%s\n" "-v, --verbose" "be more verbose"
    printf "  %-20s\t%s\n" "-h, --help" "display this help and exit"
    printf "  %-20s\t%s\n" "--version" "display version information and exit"
    printf "\n"
    printf " Any additional options are ignored.\n"
    printf "\n"
    printf " Report bugs to: <james@simula.no>.\n"
}

function version()
{
    printf "%s %s\n" "${program_name}" "${program_version}"
    printf "Copyright (C) 2023 James D. Trotter\n"
    printf "License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>\n"
    printf "This is free software: you are free to change and redistribute it.\n"
    printf "There is NO WARRANTY, to the extent permitted by law.\n"
}

function parse_program_options()
{
    FILES=()
    while [ "$#" -gt 0 ]; do
	case "${1}" in
	    -h | --help) help; exit 0;;
	    --version) version; exit 0;;
	    -v | --verbose) VERBOSE=1; shift 1;;
	    --) shift; break;;
	    *) FILES+=("${1}"); shift; continue;;
	esac
    done
    set -- "${FILES[@]}"
    return 0
}

function main ()
{
    if ! parse_program_options "$@"; then
        return 1
    fi

    printf "                                                                                               nonzeros per thread                                           max.        mean                                                 \n"
    printf "                                                                                              -----------------------------------  imbalance                 perf.       perf.           .                   L1 BW    L2 BW   \n"
    printf "  group                  matrix                 rows        columns     nonzeros     threads   min         max         mean        factor      time [s]      [Gflop/s]   [Gflop/s]   L1 misses   L2 misses   [GB/s]   [GB/s]  \n"
    printf " ---------------------- ---------------------- ----------- ----------- ------------ --------- ----------- ----------- ----------- ----------- ------------- ----------- ----------- ----------- ----------- -------- -------- \n"
    for i in $(seq 0 1 $((${#FILES[@]}-1))); do
        local FILE="${FILES[i]}"
	if [ ! -e "${FILE}" ]; then
	    echo "${program_name}: ${FILE}: no such file or directory" >&2
	    continue
	fi

	#
	# Example output:
	#
	# $ cat results/06a-csrspmv-partnz-all-20230302b/partnz-rome16q-016-threads/HB/arc130-stderr.txt
	# mtxfile_read: 0.001047 seconds (26.4 MB/s)
	# csr_from_coo: 0.000407 seconds, 130 rows, 130 columns, 1282 nonzeros, 1 to 124 nonzeros per row, 16 threads, 0 to 16 rows per thread, 80 to 81 nonzeros per thread
	# gemv: 0.000002 seconds (0.651 Gnz/s, 1.302 Gflop/s, 9.4 to 14.1 GB/s)
	# gemv: 0.000000 seconds (4.421 Gnz/s, 8.841 Gflop/s, 63.8 to 95.6 GB/s)
	# gemv: 0.000000 seconds (4.421 Gnz/s, 8.841 Gflop/s, 63.8 to 95.6 GB/s)
	# gemv: 0.000000 seconds (2.849 Gnz/s, 5.698 Gflop/s, 41.1 to 61.6 GB/s)
	# gemv: 0.000001 seconds (1.709 Gnz/s, 3.419 Gflop/s, 24.7 to 37.0 GB/s)
	# ...

	local name=$(basename "${FILE/-stderr.txt}")
	# local name=$([ ${#name} -gt 20 ] && echo "${name:0:18}.." || echo "${name}")
	local group=$(basename $(dirname "${FILE}"))
	printf "  %-20s   %-20s " "${group}" "${name}"
	./csrspmv-table.awk "${FILE}"
	printf " \n"
    done
}

main "$@"

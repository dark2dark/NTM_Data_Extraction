#!/bin/bash
#   xxx!/bin/sh
# Run this script from the command line, capture the stderr output into a file
#		./NTM_build_data_attr.sh 2> build_attr.txt
#
#	The data analysis pipe line:
#		1. 	Using multi_per_patient_diagnosed.csv and CO_only_per_patient.csv
#			generate a list of attr for cases in each ZCTA.
#
# Copyright (2011-2015) University of Colorado
# All Rights Reserved
# Author: David Knox
#
PYTHON="python2.7"

OUT_DIR=$1
: ${OUT_DIR:="Results"}
LABEL=$2
: ${LABEL:="ALL"}
SOURCE=$3
: ${SOURCE:=$OUT_DIR/multi_per_patient_diagnosed.csv}


echo [$SOURCE] used to create files with [$LABEL] label in output directory [$OUT_DIR] >&2

# Function that prints the command line to stderr and performs the command
# This is used to record the parameters being used in the output of the script
#
function Run_Command() { CMD=$* ; echo '###' $CMD >&2 ; echo " " >&2; $CMD ; }

if [ ! -d "$OUT_DIR" ]; then
# Create directory
Run_Command mkdir $OUT_DIR
fi

echo " " >&2
echo "Creating copy of this script in output directory [$OUT_DIR/script_for_attrs.sh]" >&2
Run_Command cp NTM_build_data_attr.sh $OUT_DIR/script_for_attrs.sh

echo " " >&2
echo "Generate the case counts, using file: $SOURCE" >&2

echo " " >&2
echo "Generate the case counts for species in any category (RAPID or SLOW) for each ZCTA [$SOURCE] ==> "$OUT_DIR/$LABEL"_any_data.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_data.py -a -h -s RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_any_data.csv"

echo " " >&2
echo "Generate the case counts for species in category RAPID for each ZCTA [$SOURCE] ==> "$OUT_DIR/$LABEL"_rapid_data.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_data.py -h -c 1 -s RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_rapid_data.csv"

echo " " >&2
echo "Generate the case counts for species in category RAPID for each ZCTA [$SOURCE] ==> "$OUT_DIR/$LABEL"_slow_data.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_data.py -h -c 2 -s RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_slow_data.csv"



echo " " >&2
echo "Generate the case attributes, using file: $SOURCE" >&2

echo " " >&2
echo "Generate the case attributes for species in any category (RAPID or SLOW) for each ZCTA [$SOURCE] ==> "$OUT_DIR/$LABEL"_any_attr.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_data3.py -a -h -s RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_any_attr.csv"

echo " " >&2
echo "Generate the case attributes for species in category RAPID for each ZCTA [$SOURCE] ==> "$OUT_DIR/$LABEL"_rapid_attr.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_data3.py -h -c 1 -s RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_rapid_attr.csv"

echo " " >&2
echo "Generate the case attributes for species in category RAPID for each ZCTA [$SOURCE] ==> "$OUT_DIR/$LABEL"_slow_attr.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_data3.py -h -c 2 -s RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_slow_attr.csv"


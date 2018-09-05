#!/bin/bash
# Run this script from the command line, capture the stderr output into a file
#		./NTM_build_datasets.sh 2> build.txt
#
#	The data analysis pipe line:
#
#		1.	Using the extracted species_per_patient data,
#			Count the occurrences of patients in each ZTCA region within the data 
#			Create counts for number of patients with each category of species diagnosis.
#			This can be used to count multiple different species in category 
#			or count individual species.
#			
#		2.	Using the extracted species_per_patient data,
#			combine the individual species data for each patient into a single entry.
#			For each patient, write a single record with value for each of given species.
#			The value is an indicator there was at least one diagnosis for that species.
#			
# Copyright (2011-2015) University of Colorado
# All Rights Reserved
# Author: David Knox
#
#
PYTHON="python2.7"

OUT_DIR=$1
: ${OUT_DIR:="Results"}

LABEL=$2
: ${LABEL:="ALL"}

SOURCE=$3
: ${SOURCE:=$OUT_DIR/multi_per_patient_diagnosed.csv}

OPTIONS=$4
: ${OPTIONS:="-h"}

# Function that prints the command line to stderr and performs the command
# This is used to record the parameters being used in the output of the script
function Run_Command() { CMD=$* ; echo '###' $CMD >&2 ; echo " " >&2; $CMD ; }

if [ ! -d "$OUT_DIR" ]; then
# Create directory
Run_Command mkdir $OUT_DIR
fi

echo " " >&2
echo "Creating copy of this script in output directory [$OUT_DIR/script_for_counts.sh]" >&2
Run_Command cp NTM_build_data_counts.sh $OUT_DIR/script_for_counts.sh

#
# Count the number of patients in each ZCTA with given diagnosis 
#

# Using RAPID_SLOW_CATEGORIES.txt
echo " " >&2
echo "Creating ZCTA counts for category ANY in RAPID_SLOW_CATEGORIES.txt ==> "$OUT_DIR/$LABEL"_ANY_RAPID_SLOW.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_counts.py $OPTIONS -a -C RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_ANY_RAPID_SLOW.csv"

echo " " >&2
echo "Creating ZCTA counts for category OTHER in RAPID_SLOW_CATEGORIES.txt ==> "$OUT_DIR/$LABEL"_OTHER_THAN_RAPID_SLOW.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_counts.py $OPTIONS -o -C RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_OTHER_THAN_RAPID_SLOW.csv"

echo " " >&2
echo "Creating ZCTA counts for category 1 in RAPID_SLOW_CATEGORIES.txt ==> "$OUT_DIR/$LABEL"_RAPID.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_counts.py $OPTIONS -c 1 -C RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_RAPID.csv"

echo " " >&2
echo "Creating ZCTA counts for category 2 in RAPID_SLOW_CATEGORIES.txt ==> "$OUT_DIR/$LABEL"_SLOW.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_counts.py $OPTIONS -c 2 -C RAPID_SLOW_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_SLOW.csv"

#
# Using INDIVIDUAL_CATEGORIES.txt
#
echo " " >&2
echo "Creating ZCTA counts for category ANY in INDIVIDUAL_CATEGORIES.txt ==> "$OUT_DIR/$LABEL"_ANY_INDIVIDUAL.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_counts.py $OPTIONS -a -C INDIVIDUAL_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_ANY_INDIVIDUAL.csv"

echo " " >&2
echo "Creating ZCTA counts for category OTHER in INDIVIDUAL_CATEGORIES.txt ==> "$OUT_DIR/$LABEL"_OTHER_THAN_INDIVIDUAL.csv" >&2
Run_Command $PYTHON NTM_ZCTA_category_counts.py $OPTIONS -o -C INDIVIDUAL_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_OTHER_THAN_INDIVIDUAL.csv"

#
# Loop thru the SPECIES to generate individual count files
#
SPECIES_ID=1
for SPECIES in ABSCESSUS AVIUM AVIUM_COMPLEX INTRACELLULARE CHIMAERA CHELONAE FORTUITUM SIMIAE GORDONAE KANSASII MASSILIENSE MUCOGENICUM PEREGRINUM 
	do
	echo " " >&2
	echo "Creating ZCTA counts for category $SPECIES_ID in INDIVIDUAL_CATEGORIES.txt ==> "$OUT_DIR/$LABEL"_"$SPECIES".csv" >&2
	Run_Command Run_Command $PYTHON NTM_ZCTA_category_counts.py $OPTIONS -c $SPECIES_ID -C INDIVIDUAL_CATEGORIES.txt $SOURCE > $OUT_DIR/$LABEL"_"$SPECIES.csv
	echo "Created individual species file of counts for:" $((SPECIES_ID++)) $SPECIES "==> "$OUT_DIR/$LABEL"_"$SPECIES".csv" >&2
	done

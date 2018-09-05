#!/bin/sh
# Run this script from the command line, capture the stderr output into a file
#		./NTM_build_datasets.sh 2> build.txt
#
#
# Copyright (2011-2015) University of Colorado
# All Rights Reserved
# Author: David Knox
#
OUT_DIR=Results
INPUT_FILE=NTM_wfixes.csv
SUMMARY=summary.txt
UNDIAGNOSED=multi_per_patient_undiagnosed.csv
DIAGNOSED=multi_per_patient_diagnosed.csv
PATIENT_SPECIES=species_freq.csv

# Function that prints the command line to stderr and performs the command
# This is used to record the parameters being used in the output of the script
function Run_Command() { CMD=$* ; echo '###' $CMD >&2 ; echo " " >&2; $CMD ; }

if [ ! -d "$OUT_DIR" ]; then
# Create directory
Run_Command mkdir $OUT_DIR
fi

echo " " >&2
echo "Creating copy of this script in output directory [$OUT_DIR/script_used.sh]" >&2
Run_Command cp NTM_build_datasets.sh $OUT_DIR/script_used.sh

# Extract diagnosis and method from patient records and write summary
echo " " >&2
echo "Creating summary of the input file [$INPUT_FILE] ==> $OUT_DIR/$SUMMARY" >&2
Run_Command python NTM_species_summary.py -s -m $INPUT_FILE > $OUT_DIR/$SUMMARY

# Extract diagnosis and method from patient records
echo " " >&2
echo "Creating list of species found for each patient [$INPUT_FILE] ==> $OUT_DIR/$DIAGNOSED" >&2
Run_Command python NTM_species_per_patient.py -r $INPUT_FILE > $OUT_DIR/$DIAGNOSED

# Extract undiagnosed patients
echo " " >&2
echo "Creating list of both diagnosed and undiagnosed patients [$INPUT_FILE] ==> $OUT_DIR/$UNDIAGNOSED" >&2
Run_Command python NTM_species_per_patient.py -r -u $INPUT_FILE > $OUT_DIR/$UNDIAGNOSED

#
# Count the number of patients in each ZCTA with given diagnosis 
#

# Using RAPID_SLOW_CATEGORIES.txt
echo " " >&2
echo "Creating ZCTA counts for category ANY in RAPID_SLOW_CATEGORIES.txt ==> $OUT_DIR/ANY_RAPID_SLOW.csv" >&2
Run_Command python NTM_ZCTA_category_counts.py -h -a -C RAPID_SLOW_CATEGORIES.txt $OUT_DIR/$DIAGNOSED > $OUT_DIR/ANY_RAPID_SLOW.csv

echo " " >&2
echo "Creating ZCTA counts for category OTHER in RAPID_SLOW_CATEGORIES.txt ==> $OUT_DIR/OTHER_THAN_RAPID_SLOW.csv" >&2
Run_Command python NTM_ZCTA_category_counts.py -h -o -C RAPID_SLOW_CATEGORIES.txt $OUT_DIR/$DIAGNOSED > $OUT_DIR/OTHER_THAN_RAPID_SLOW.csv

echo " " >&2
echo "Creating ZCTA counts for category 1 in RAPID_SLOW_CATEGORIES.txt ==> $OUT_DIR/RAPID.csv" >&2
Run_Command python NTM_ZCTA_category_counts.py -h -c 1 -C RAPID_SLOW_CATEGORIES.txt $OUT_DIR/$DIAGNOSED > $OUT_DIR/RAPID.csv

echo " " >&2
echo "Creating ZCTA counts for category 2 in RAPID_SLOW_CATEGORIES.txt ==> $OUT_DIR/SLOW.csv" >&2
Run_Command python NTM_ZCTA_category_counts.py -h -c 2 -C RAPID_SLOW_CATEGORIES.txt $OUT_DIR/$DIAGNOSED > $OUT_DIR/SLOW.csv


# Using INDIVIDUAL_CATEGORIES.txt

echo " " >&2
echo "Creating ZCTA counts for category ANY in INDIVIDUAL_CATEGORIES.txt ==> $OUT_DIR/ANY_INDIVIDUAL.csv" >&2
Run_Command python NTM_ZCTA_category_counts.py -h -a -C INDIVIDUAL_CATEGORIES.txt $OUT_DIR/$DIAGNOSED > $OUT_DIR/ANY_INDIVIDUAL.csv

echo " " >&2
echo "Creating ZCTA counts for category OTHER in INDIVIDUAL_CATEGORIES.txt ==> $OUT_DIR/OTHER_THAN_INDIVIDUAL.csv" >&2
Run_Command python NTM_ZCTA_category_counts.py -h -o -C INDIVIDUAL_CATEGORIES.txt $OUT_DIR/$DIAGNOSED > $OUT_DIR/OTHER_THAN_INDIVIDUAL.csv


# Loop thru the SPECIES to generate individual count files
SPECIES_ID=1
for SPECIES in ABSCESSUS AVIUM INTRACELLULARE CHIMAERA CHELONAE FORTUITUM SIMIAE GORDONAE KANSASII MASSILIENSE MUCOGENICUM PEREGRINUM
	do
	echo " " >&2
	echo "Creating ZCTA counts for category $SPECIES_ID in INDIVIDUAL_CATEGORIES.txt ==> $OUT_DIR/$SPECIES.csv" >&2
	Run_Command Run_Command python NTM_ZCTA_category_counts.py -h -c $SPECIES_ID -C INDIVIDUAL_CATEGORIES.txt $OUT_DIR/$DIAGNOSED > $OUT_DIR/$SPECIES.csv
	echo "Created individual species file of counts for:" $((SPECIES_ID++)) $SPECIES "==> $OUT_DIR/$SPECIES.csv" >&2
	done



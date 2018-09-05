#!/bin/bash
# Run this script from the command line, capture the stderr output into a file
#		./NTM_build_datasets.sh  [results_dir] 2> build.txt
#
#	The data analysis pipe line:
#		1. 	Using manually fixed (spelling) data, 
#			summarize the data (types of species and methods cited, number of patients, ...)
#
#		2. 	Using manually fixed (spelling) data, 
#			split the data into two sets: CF patients, NON-CF patients
#
#		3. 	Using the Non-CF patient data,
#			extract the species and methods from each record, 
#			produce records for each <species,method> diagnosed for a patient.
#			Only output the records with recognized methods.
#			
#		4. 	Using the Non-CF patient data, 
#			extract the species and methods from each record, 
#			produce records for each <species,method> diagnosed for a patient
#			and a record for each UNDIAGNOSED patient.
#			Only output the records with recognized methods.
#			
#		5.	Using the extracted species_per_patient data,
#			Count the occurrences of patients in each ZTCA region within the data 
#			Create counts for number of patients with each category of species diagnosis.
#			This can be used to count multiple different species in category 
#			or count individual species.
#			
#		6.	Using the extracted species_per_patient data,
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

INPUT_FILE=Lipner_NTM_CO_FINAL2.csv
CF_PATIENT_IDS=NTM_CF_patient_ids.csv
CF_PATIENTS=NTM_CF_patients.csv
NON_CF_PATIENTS=NTM_Non_CF_patients.csv
SUMMARY=summary.txt
UNDIAGNOSED=multi_per_patient_undiagnosed.csv
DIAGNOSED=multi_per_patient_diagnosed.csv
COLO_DIAGNOSED=CO_only_per_patient.csv
PATIENT_SPECIES=species_freq.csv


# Function that prints the command line to stderr and performs the command
# This is used to record the parameters being used in the output of the script
function Run_Command() { CMD=$* ; echo '###' $CMD >&2 ; echo " " >&2; $CMD ; }

if [ ! -d "$OUT_DIR" ]; then
# Create directory
Run_Command mkdir $OUT_DIR
fi

echo " " >&2
$PYTHON --version 
Run_Command $PYTHON --version

echo " " >&2
echo "Creating copy of this script in output directory [$OUT_DIR/script_used.sh]" >&2
Run_Command cp NTM_build_datasets.sh $OUT_DIR/script_for_datasets.sh

# split the source data into CF and NON-CF patients
echo "Splitting the input file [$INPUT] into CF and NON-Cf patient records ==> $OUT_DIR/$NON_CF_PATIENTS and $OUT_DIR/$CF_PATIENTS" >&2
Run_Command $PYTHON NTM_Split_CF_patients.py  -r -c NTM_CF_patient_ids.csv $INPUT_FILE > $OUT_DIR/$NON_CF_PATIENTS
Run_Command $PYTHON NTM_Split_CF_patients.py  -m -c NTM_CF_patient_ids.csv $INPUT_FILE > $OUT_DIR/$CF_PATIENTS

# Extract diagnosis and method from patient records and write summary
echo " " >&2
echo "Creating summary of the input file [$OUT_DIR/$NON_CF_PATIENTS] ==> $OUT_DIR/$SUMMARY" >&2
Run_Command $PYTHON NTM_species_summary.py -s -m $OUT_DIR/$NON_CF_PATIENTS > $OUT_DIR/NON_CF_$SUMMARY

# Extract diagnosis and method from patient records and write summary
echo " " >&2
echo "Creating summary of the input file [$OUT_DIR/$NON_CF_PATIENTS] ==> $OUT_DIR/$SUMMARY" >&2
Run_Command $PYTHON NTM_species_summary.py -s -m $OUT_DIR/$CF_PATIENTS > $OUT_DIR/CF_$SUMMARY

# Extract diagnosis and method from patient records
echo " " >&2
echo "Creating list of species found for each patient [$OUT_DIR/$NON_CF_PATIENTS] ==> $OUT_DIR/$DIAGNOSED" >&2
Run_Command $PYTHON NTM_species_per_patient.py -r $OUT_DIR/$NON_CF_PATIENTS > $OUT_DIR/$DIAGNOSED

# Extract undiagnosed patients
echo " " >&2
echo "Creating list of both diagnosed and undiagnosed patients [$OUT_DIR/$NON_CF_PATIENTS] ==> $OUT_DIR/$UNDIAGNOSED" >&2
Run_Command $PYTHON NTM_species_per_patient.py -r -u $OUT_DIR/$NON_CF_PATIENTS > $OUT_DIR/$UNDIAGNOSED

# Extract CO diagnosed patients
echo " " >&2
echo "Creating list of both Colorado only diagnosed  [$OUT_DIR/$NON_CF_PATIENTS] ==> $OUT_DIR/$COLO_DIAGNOSED" >&2
Run_Command $PYTHON NTM_state_filter.py -s CO $OUT_DIR/$DIAGNOSED > $OUT_DIR/$COLO_DIAGNOSED


#
# Count the number of patients in each ZCTA with given diagnosis 
#
echo " " >&2
echo "Creating data count files (prefix: NonCF_ALL) for $DIAGNOSED" >&2
/bin/bash ./NTM_build_data_counts.sh $OUT_DIR NonCF_ALL $OUT_DIR/$DIAGNOSED >&2

echo " " >&2
echo "Creating data count files (prefix: NonCF_ALL) for $DIAGNOSED" >&2
/bin/bash ./NTM_build_data_counts.sh $OUT_DIR NonCF_ALL_W_STATE $OUT_DIR/$DIAGNOSED "-h -s" >&2

echo " " >&2
echo "Creating data count files (prefix: NonCF_CO) for $COLO_DIAGNOSED" >&2
/bin/bash ./NTM_build_data_counts.sh $OUT_DIR NonCF_CO $OUT_DIR/$COLO_DIAGNOSED >&2

#
# Create combined species per patient data set
#
echo " " >&2
echo "Creating combined list of species diagnosed for each patient ==> $OUT_DIR/NonCF_ALL_$PATIENT_SPECIES" >&2
Run_Command $PYTHON NTM_combined_patient_species.py -h $OUT_DIR/$DIAGNOSED > $OUT_DIR/NonCF_ALL_$PATIENT_SPECIES

echo " " >&2
echo "Creating combined list of species diagnosed for each CO patient ==> $OUT_DIR/NonCF_CO_PATIENT_SPECIES" >&2
Run_Command $PYTHON NTM_combined_patient_species.py -h $OUT_DIR/$COLO_DIAGNOSED > $OUT_DIR/NonCF_CO_$PATIENT_SPECIES

#
# Generate the attribute files for DIAGNOSED and COLO_DIAGNOSED
#
echo " " >&2
echo "Creating data attribute files (prefix: NonCF_ALL) for $DIAGNOSED" >&2
/bin/bash ./NTM_build_data_attr.sh $OUT_DIR NonCF_ALL $OUT_DIR/$DIAGNOSED >&2

echo " " >&2
echo "Creating data attribute files (prefix: NonCF_CO) for $COLO_DIAGNOSED" >&2
/bin/bash ./NTM_build_data_attr.sh $OUT_DIR NonCF_CO $OUT_DIR/$COLO_DIAGNOSED >&2

# Processing NTM patient species and zip code data
#
# Copyright (2011-2015) University of Colorado
# All Rights Reserved
# Author: David Knox
#

import string
import sys, os, re, getopt
from NTM_extract_data import * 

###############################################################################
#
def Usage():
	sys.stderr.write( 'Usage: %s [options] <source data> \n'%(re.sub('^.*/','',sys.argv[0])))
	sys.stderr.write( '\t This application extracts the species and identification method from patient data\n')
	sys.stderr.write( '\t and prints a record for each species in each patient.\n')
	sys.stderr.write( '\n')
	sys.stderr.write( '\t Options:\n')
	sys.stderr.write( '\t     -r    only output recognized methods')
	sys.stderr.write( '\t     -u    output record for undiagnosed patients\n')
	sys.stderr.write( '\n\n')
# end of Usage()


###############################################################################
# 	Process the records given, combining the information into a single output
#	record.  Check the records to see if there were RAPID or SLOW growing 
#	species diagnosed.  Add a column with the correct ZCTA for given zip code.
###############################################################################

def ProcessRecords(records):
#OLD				NEW
#   9 J Current Age		-> 15
#   10 K Gender of Subject	-> 16
#   11 L Race of subject	-> 17
#   12 M Ethnicity of subject	-> 18
#   13 N City			->  3
#   14 O State			->  4
#   15 P ZIP			->  5
#   16 Q Marital Status		->  6
	DATE = 7
	global only_recognised_method
	global undiagnosed_patients

	#Create dictionary for species identification
	#   Key: species, Value: [[list of methods],[list of line no]] 
	#
	patient_species = {}

	if len(records) == 0:
		return patient_species
		
#	sys.stderr.write("\tRecords:\n", len(records), records
	patient_id = records[0][0]
#	sys.stderr.write("Processing patient id: %s (%d)\n"%(patient_id,len(records)))
	
	record_date = "no date"

	for rec in records:
		if (len(rec) <= DATE): 
			sys.stderr.write("Skipping record [%d] for patient id [%s], because no date field available.\n"%(rec[-1],rec[0]))
			continue
		record_date = rec[DATE]
		rec_species,rec_methods = ExtractData(rec, only_recognised_method)

		if (len(rec_methods) == 0):		# skip records that do not contain both a species and a method
			if (len(rec_species) > 0):
				# report the skipping of patient record
				sys.stderr.write("Skipping record [%d] for patient id [%s], because no method indicated.\n"%(rec[-1],rec[0]))
				sys.stderr.write("\t[%s][%s]\n"%(rec[8],rec[9]))
				
			continue
			
		# get a list of methods in record
		methods = rec_methods.keys()
		for s in rec_species:
			if (patient_species.has_key(s)):
				# add the methods to the current list of methods
				for m in methods:
					if (not m in patient_species[s][0]):
						patient_species[s][0].append(m)
				# add the line numbers to the current list of line numbers
				patient_species[s][1].extend(rec_species[s])
			else:
				patient_species[s] = [methods, rec_species[s]]

	# uses the data from the last record for the patient
	# print an entry for each species found
	try:
		# convert age
		age_str = "---"
		age_str = rec[15]
		age = int(age_str)
	except:
		sys.stderr.write("[%d] for patient id [%s], bad age [%s].\n"%(rec[-1],rec[0], age_str))

	try:
		patient_data =  ", " + ', '.join([rec[15], rec[16], rec[17], rec[3], rec[4], rec[5], rec[6]])
	except:
		patient_data = "incomplete"
		
	if (len(patient_species) == 0):
		# undiagnosed patient
		if (undiagnosed_patients):
			print ', '.join([patient_id, record_date, "", ""]), patient_data
	else:
		for s in patient_species:
			for m in patient_species[s][0]:
				print ', '.join([patient_id, record_date, s, m]), patient_data
						
	return patient_species
	
#end of ProcessRecords


###############################################################################
#
# Main application processing 
#
###############################################################################

def Main():

	global only_recognised_method
	global separate_patients
	global undiagnosed_patients
	
	only_recognised_method = False
	separate_patients = True
	undiagnosed_patients = False
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ru", ["help"])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)

	for opt, value in opts:
		#print opt, value
		if	 opt == '-r':		only_recognised_method = True
		elif opt == '-u':		undiagnosed_patients = True
		else: 
			sys.stderr.write("Unhandled opt [%s][%s]\n"%(opt,value))

	if (len(args) < 1):
		Usage()
		exit(-1)

	# open a filename given on the command line.
	fh=open(args[0])

	n_patients = 0
	n_missing = 0
	n_diagnosed = 0
	n_written = 0

	line_no = 0
	current_patient = ""
	records = []
	patients = {}
	undiagnosed = {}
		
	for line in fh.readlines():
		line_no += 1
		line = line.strip()		
		if (len(line) < 2):
			sys.stderr.write("skipping line: [%s]\n"%line)
			continue

		line = line.upper()
		cols = line.split(',')

		patients[cols[0]] = 1
		
	#	print cols[0], "[%s, %s]"%(cols[2],cols[3])

		# for each set of records for a patient
		#		collect counts of each category of species
		#		write new record with counts

		if cols[0] != current_patient:
			if (len(records) > 0): 
				n_patients += 1
				
#				if (separate_patients):
#					print	# separate patients
				patient_species = ProcessRecords(records)
			
				if (len(patient_species) == 0):
					n_missing += 1
					undiagnosed[current_patient] = 1
				else:
					# count number of records written
					for s in patient_species:			
						n_written += len(patient_species[s][0])	# count number of methods for species
					n_diagnosed += 1
					
			records = []
			current_patient = cols[0]

		cols.append(line_no)
		records.append(cols)	
	
	# process the last patient records
	if (len(records) > 0): 
		n_patients += 1
		
#		if (separate_patients):
#			print	# separate patients
		patient_species = ProcessRecords(records)
	
		if (len(patient_species) == 0):
			n_missing += 1
			undiagnosed[current_patient] = 1
		else:
			# count number of records written
			for s in patient_species:			
				n_written += len(patient_species[s][0])	# count number of methods for species
			n_diagnosed += 1

	# Print the summary information

	sys.stderr.write("\n")
	sys.stderr.write( "Lines Processed:        %6d\n"%line_no)
	sys.stderr.write( "Patients Processed:     %6d\n"%n_patients)
	sys.stderr.write( "Unique Patient IDs:     %6d\n"%len(patients))
	sys.stderr.write( "Patients with diagnosis:%6d\n"%n_diagnosed)
	sys.stderr.write( "Patients w/o diagnosis: %6d\n"%n_missing)
	sys.stderr.write( "Records written:        %6d\n"%n_written)
				
	return
# end if Main()

###############################################################################
#
###############################################################################
if __name__ == '__main__':

	# reopen stdout file descriptor with write mode and 0 as the buffer size (unbuffered)
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

	Main()
	
###############################################################################
###############################################################################

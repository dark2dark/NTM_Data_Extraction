# Processing NTM patient split out records for either matching or non-matching patient ids
#
# Copyright (2011-2015) University of Colorado
# All Rights Reserved
# Author: David Knox
#

import string
import sys, re, os, getopt
import math

###############################################################################

def Usage():
	print 'Usage: %s [options] -c <id file> <source data> '%(re.sub('^.*/','',sys.argv[0]))
	print '\t This application collects data for patients within either matching or non-matching patient ids.'
	print '\t      -c <id file>  each row contains a patient id in first column.  (CSV format)'
	print '\t      -r   remove records from source data that have a matching id.'
	print '\t      -m   collect records from source data that have a matching id. (DEFAULT)'
	print '\n'
# end of Usage()

###############################################################################

###############################################################################
# 	Read the records in the file and extract the id from first column.
###############################################################################
def ReadIdFile(filename):
	result = {}
	
	with open(filename, 'r') as infile:
#		header = infile.readline()
		for line in infile.readlines():
			fields = line.split(',')

			id = fields[0].strip()
			id = id.upper()

			result[id] = line

	return result

###############################################################################
# 	Process the records given, combining the information into a single output
#	record.  Check the records to see if there were RAPID or SLOW growing 
#	species diagnosed.  Add a column with the correct ZCTA for given zip code.
###############################################################################

def ProcessRecords(records):

	if len(records) == 0:
		return (None, None)
		
	global category
	global categories
	global want_any
#	global want_rapid
#	global want_slow
#	global want_other
		
#	print "\n\tRecords:", len(records), records
	
	patient_id = records[0][0]
	zcta = Lookup_ZCTA(records[0][9].strip())
	if (zcta == ""):
		sys.stderr.write("empty ZCTA for ZIP: (%s) ["%(records[0][9].strip()))
		for r in records[0]:
			sys.stderr.write("\t%s"%(r))
		sys.stderr.write("]\n")
	if (zcta == None) or (zcta == ""):
		return (None, None)
		
	counts = []
	for cat in enumerate(categories):
		counts.append(0)
	count_other = 0

	for rec in records:
		species = rec[2].strip()
		
		# check to see if the given species is in one of the categories.
		# if not found in any category, add it to other species count.
		counted = 0
		for i,cat in enumerate(categories):
			if (species in cat):
				counts[i] += 1
				counted += 1
		if (counted == 0):
		#	sys.stderr.write("Other:[%s] %s\n"%(species,rec[0]))
			count_other += 1				

	# Columns of the input:
	#	0	ASID
	#	1	Date of diagnosis
	#	2	Species diagnosed 
	#	3	Method of diagnosis 
	#	4	Current Age
	#	5	Gender of Subject
	#	6	Ethnicity of subject
	#	7	City 
	#	8	State 
	#	9	ZIP
	#	10	Marital Status 

	zcta = Lookup_ZCTA(rec[9].strip())

	# If this patient matches criteria
	# 		add patient to list for given ZCTA 
	
	matches = False
	
	if (want_any):
		# check to see if any of the counts is non-zero	
		for c in counts:
			if (c > 0): 
				matches = True
		if (count_other > 0):
			matches = True
	elif (want_other and (count_other > 0)):
			matches = True
	else:
		# looking for values in specific category 
#		if (want_rapid or want_slow or want_other):
#			matches = True		#assume it matches, unless missing a wanted value
#		if (want_rapid and (counts[0] == 0)):
#			matches = False
#		if (want_slow and (counts[1] == 0)):
#			matches = False
		if (counts[category] > 0):
			matches = True
	if (matches):
		# add the patient id to the list for given ZCTA
		return (records[0], zcta)
	else:
		return (None,None)
		
#end of ProcessRecords


###############################################################################
#
# Main application processing 
#
###############################################################################

def Main():

	global match
	
	id_filename = None 

	match = True
			
	try:
		opts, args = getopt.getopt(sys.argv[1:], "rmc:", ["help"])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)

	for opt, value in opts:
		#print opt, value
		if	 opt == '-m':			match = True
		elif opt == '-r':			match = False
		elif opt == '-c':			id_filename = value
		else: 
			print "Unhandled opt [%s][%s]"%(opt,value)

	if (len(args) < 1) or (not id_filename):
		Usage()
		exit(-1)

	ids = ReadIdFile(id_filename)
	sys.stderr.write("%d ids in file [%s]\n"%(len(ids),id_filename))
			
	# open a filename given on the command line.
	fh=open(args[0])

	line_no = 0
	current_patient = ""
	records = []
	n_patients = 0
	n_records = 0
	n_ids_written = 0
	
	for line in fh.readlines():
		line = line.strip()
		if (len(line) < 2):		continue
		if (line[0] == '#'):	continue
				
		line_no += 1
		line = line.upper()
		cols = line.split(',')

		if cols[0] != current_patient:
			if (len(records) > 0):
				n_patients += 1
				
				if (match and ids.has_key(current_patient)) or (not match and not ids.has_key(current_patient)) :
					# write out records
					n_ids_written += 1
					for rec in records: 		
						print ",".join(rec)
					n_records += len(records)
							
			current_patient = cols[0].upper()
			records = []
			
		records.append(cols)	
	
	if (len(records) > 0):
		n_patients += 1
		if (match and ids.has_key(current_patient)) or (not match and not ids.has_key(current_patient)) :
			# write out records
			n_ids_written += 1
			for rec in records: 		
				print ",".join(rec)
			n_records += len(records)
			
				
	sys.stderr.write("# Patients processed: %d\n"%n_patients)
	sys.stderr.write("# Patients written:   %d\n"%n_ids_written)
	sys.stderr.write("# Records written:    %d\n"%n_records)	

###############################################################################
#
###############################################################################
if __name__ == '__main__':

	# reopen stdout file descriptor with write mode and 0 as the buffer size (unbuffered)
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

	Main()
	
###############################################################################
###############################################################################

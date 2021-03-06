# Processing NTM patient species and zip code data
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
	print 'Usage: %s [options] -s <catagories file> <source data> '%(re.sub('^.*/','',sys.argv[0]))
	print '\t This application collects data for patients within each ZCTA.'
	print '\t      -c <category>  count patients with given category (1 based category number)'
	print '\t      -o   count patients with diagnosis not in any other category'
	print '\t      -a   count patients with diagnosis in any category'
	print '\n'
# end of Usage()

###############################################################################

def LoadCategories(filename):

	# Species Category file format is:
	# 	[cat1_name]
	# 	species1_name
	# 	species2_name
	# 	species3_name
	# 	...
	#
	# 	[cat2_name]
	# 	species1_name
	# 	...
	#
	# 	...
	#
	# Returns:
	#	categories is a list of [name, species, ...]
	#
	categories = []

	key = ""
	entries = []
	
	with open(filename, 'r') as catfile:
		for line in catfile.readlines():
			line = line.strip()
			if (len(line) == 0):  # is an empty line
				continue
			if (line[0] == '#'):  # is a comment line
				continue

			if (line[0] == '[') and (line[-1] == ']'):
				# append current entries to categories
				if (len(entries) > 0):
					categories.append(entries)
				key = line[1:-1]
				entries = [key]
			else:
				entries.append(line)

	# append final entries to categories
	if (len(entries) > 0):
		categories.append(entries)

	return categories
	
# end of ReadCategories

###############################################################################
# LoadZCTA - create mapping from zip to ZCTA value
#		Creates a global variable to hold the data for mapping
#		a zip code into ZCTA code
#		Data is parsed from the file whose name is given as a parameter
###############################################################################

def LoadZCTA(fipstozcta_file):

	global zip_to_zcta
	
	zip_to_zcta = {}
	
	with open(fipstozcta_file, 'r') as infile:
		header = infile.readline()
		for line in infile.readlines():
			fields = line.split('\t')
			zip = fields[0].strip()
			zcta = fields[4].strip()
			zip_to_zcta[zip] = zcta

	return

# end of LoadZCTA()

###############################################################################
# Lookup_ZCTA - Find the ZCTA value for the given zip code
#
#	Uses the global mapping data structure created in LoadZCTA.
#	Strips zip down to 5 digit code.
#	Looks up the 5 digit code in the mapping data structure.
#	Makes sure the result is a 5 digit string with leading 0's
###############################################################################
def Lookup_ZCTA(zip_str):

	global zip_to_zcta

	zip_whole = zip_str.strip()
	zip = zip_whole.split("-")[0]
	#print zip_whole + '\t' + zip

	# pad out the zip to 5 digits with leading 0's
	if zip.isdigit():
		while (len(zip) < 5):
			zip = "0"+zip
	
	if zip in zip_to_zcta:
		zcta = zip_to_zcta[zip]
		if (zcta == ""):
			sys.stderr.write("empty ZCTA for ZIP: (%s)\n"%(zip))
	else:
		return None
#		sys.stderr.write("Using unknown ZIP: (%s)\n"%(zip))
#		zcta = zip

	# pad out the code to 5 digits with leading 0's
	if zcta.isdigit():
		while (len(zcta) < 5):
			zcta = "0"+zcta

	return zcta

# end of Lookup_ZCTA()

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

	global category
	global categories

	global want_any
#	global want_rapid
#	global want_slow
	global want_other
		
	want_any  	= False
#	want_rapid	= False
#	want_slow	= False
	want_other	= False

	category = 1
	cat_filename = "SPECIES_CATEGORIES.TXT"
	write_header = False

	filename_ZTAC = "zipcodezctatable.txt"
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ac:hors:z:", ["help"])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)

	for opt, value in opts:
		#print opt, value
		if	 opt == '-z':			filename_ZTAC = value
		elif opt == '-a':			want_any = True
		elif opt == '-c':			category = int(value)
		elif opt == '-h':			write_header = True
		elif opt == '-o':			want_other = True
		elif opt == '-s':			cat_filename = value
#		elif opt == '-o':			outfilename = value
		else: 
			print "Unhandled opt [%s][%s]"%(opt,value)

	if (len(args) < 1):
		Usage()
		exit(-1)

	categories = LoadCategories(cat_filename)
	# print the categories
	for i, entries in enumerate(categories):
		sys.stderr.write("%5d %s:"%(i+1,entries[0]))
		for i,e in enumerate(entries[1:]):
			if (i%8 == 0):
				sys.stderr.write("\n\t")
			sys.stderr.write(" %s"%e)
		sys.stderr.write("\n")
			
	if (category < 1) or (category > len(categories)):
		sys.stderr.write("\nError: invalid category number [%s]. Category value must be in range (1 .. %d)\n"%(category, len(categories)))
		Usage()
		exit(-1)
		
	category -=1		# specified as 1 based, convert to 0 based
	cat_name = categories[category][0]
	if (want_other):
		cat_name = "OTHER"
	elif (want_any):
		cat_name = "ANY"
	sys.stderr.write("Collecting data for patients in each ZCTA with [%s] diagnosis\n"%cat_name)
	
	
	LoadZCTA(filename_ZTAC)
	
	# open a filename given on the command line.
	fh=open(args[0])

	line_no = 0
	current_patient = ""
	records = []
	n_patients = 0

	counts_per_ZCTA = {}

	for line in fh.readlines():
		line = line.strip()
		if (len(line) < 2):
			continue
		
		line_no += 1
		line = line.upper()
		cols = line.split(',')

	#	print cols[0], "[%s, %s]"%(cols[2],cols[3])

		# for each set of records for a patient
		#		collect counts of each category of species
		#		write new record with counts

		if cols[0] != current_patient:
			if (len(records) > 0):
				n_patients += 1
			p_rec,key = ProcessRecords(records)
			if (p_rec):
				if (counts_per_ZCTA.has_key(key)):
					counts_per_ZCTA[key].append(p_rec)
				else:
					counts_per_ZCTA[key] = [p_rec]
					
			records = []
			current_patient = cols[0]

		records.append(cols)	
	
	if (len(records) > 0):
		n_patients += 1
	p_rec,key = ProcessRecords(records)		#process the last patient
	if (p_rec):
		if (counts_per_ZCTA.has_key(key)):
			counts_per_ZCTA[key].append(p_rec)
		else:
			counts_per_ZCTA[key] = [p_rec]


	#	Create a record for each ZCTA value that includes:
	#		ztca
	#		count of records
	#		avg age
	#		% female
	#		% married
	#		
	if (write_header):
		header = "ZCTA, total cases, # w/ages, cases 65+, cases <65"
		print header

	n_ages = 0
	n_records = 0		
	for zcta in sorted(counts_per_ZCTA):
		# calculate the data from records for this ZCTA
		records = counts_per_ZCTA[zcta]

	#	print "--------------------"
	#	print records
		
		ages = []
		n_65_plus = 0
		n_under_65 = 0

		for rec in records:
			if rec[4].strip() != '':	
				age = int(rec[4])
				ages.append(age)				
				if (age < 65):
					n_under_65 += 1
				else:
					n_65_plus += 1
						
		print "%s, %d, %d, %d, %d"%(zcta, len(records), len(ages), n_65_plus, n_under_65)
		n_ages += len(ages)
		n_records += len(records)
		
	sys.stderr.write("# Patients:        %d\n"%n_patients)
	sys.stderr.write("# Total # records: %d\n"%n_records)
	sys.stderr.write("# Records w/age:   %d\n"%n_ages)
	sys.stderr.write("# ZCTA:            %d\n"%len(counts_per_ZCTA))	

###############################################################################
#
###############################################################################
if __name__ == '__main__':

	# reopen stdout file descriptor with write mode and 0 as the buffer size (unbuffered)
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

	Main()
	
###############################################################################
###############################################################################

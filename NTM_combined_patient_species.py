# Find the counts for each possible species for each patient
#
# Copyright (2011-2015) University of Colorado
# All Rights Reserved
# Author: David Knox
#

import string
import sys, re, os, getopt
import operator

###############################################################################

	# Columns of the input:
	#	0	ASID
	# 	1	Date of diagnosis   - remove this field
	# 	2	Species diagnosed   - remove this field
	# 	3	Method of diagnosis - remove this field
	#	4	Current Age
	#	5	Gender of Subject
	#	6	Ethnicity of subject
	#	7	City 
	#	8	State 
	#	9	ZIP
	#	10	Marital Status 

###############################################################################

def Usage():
	sys.stderr.write( 'Usage: %s [options] <source data> \n'%(re.sub('^.*/','',sys.argv[0])) )
	sys.stderr.write( '\t This application combines the individual species data for each patient into a single entry.\n' )
	sys.stderr.write( '\t   -h  write header to output\n' )
	sys.stderr.write( '\n\n' )
# end of Usage()


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
	z = zip_whole.split("-")[0]
	#print zip_whole + '\t' + zip

	# pad out the zip to 5 digits with leading 0's
	if z.isdigit():
		while (len(z) < 5):
			z = "0"+z
	
	if z in zip_to_zcta:
		zcta = zip_to_zcta[z]
		if (zcta == ""):
			sys.stderr.write("empty ZCTA for ZIP: (%s)\n"%(z))
	else:
		return None
#		sys.stderr.write("Using unknown ZIP: (%s)\n"%(z))
#		zcta = z

	# pad out the code to 5 digits with leading 0's
	if zcta.isdigit():
		while (len(zcta) < 5):
			zcta = "0"+zcta

	return zcta

# end of Lookup_ZCTA()

###############################################################################
# 	Process the records given, counting the number of species diagnosed for 
#	patient.  Returns species counts.
###############################################################################

def ProcessRecords(records, species, sorted_species_list):

	if len(records) == 0:
		return (None, None)
		
	# reset all species counts to 0
	for s in species:	
		species[s] = 0
		
#	print "\n\tRecords:", len(records), records
	
	patient_id = records[0][0]

	# lookup ZCTA number
	zipcode = records[0][9].strip()
	zcta = Lookup_ZCTA(zipcode)
	if (not zcta) or (zcta == ""):
		sys.stderr.write("empty ZCTA for ZIP: (%s) ["%(zipcode))
		sys.stderr.write("pid=%s"%(patient_id))
	#	for r in records[0]:
	#		sys.stderr.write("\t%s"%(r))
		sys.stderr.write("]\n")
		zcta = ""
#	if (zipcode != zcta):
#		sys.stderr.write("ZCTA [%s] from ZIP[%s]\n"%(zcta,zipcode))
		
	for rec in records:
		diagnosis = rec[2].strip()
		species[diagnosis] += 1		# count occurrences
		
	# write the new combined record
	# remove selected fields of the record
		#	1	Date of diagnosis
		#	2	Species diagnosed 
		#	3	Method of diagnosis 
	new_rec = [rec[0],rec[4],rec[5],rec[6],rec[7],rec[8],zipcode,zcta,rec[10]]
	
	# ??? add ZCTA value ???
	
	# add the species markers for species seen
	for s,c in sorted_species_list:
		value = '0'
		if (species[s] > 0):
			value = '1'
		new_rec.append(value)
	
	print ','.join(new_rec)	

#end of ProcessRecords

###############################################################################
# 	Process the record given, combining the species information into a dictionary
###############################################################################

def CollectSpecies(rec, species):

	if len(rec) == 0: return
	
	diagnosis = rec[2].strip()

	if not species.has_key(diagnosis):
		species[diagnosis] = 0	

	species[diagnosis] += 1		# count occurrences
		
#end of CollectSpecies


###############################################################################
#
# Main application processing 
#
###############################################################################

def Main():
	
	output_col = -1
	write_header = False

	filename_ZTAC = "zipcodezctatable.txt"
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hz:", ["help"])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)

	for opt, value in opts:
		#print opt, value
		if	 opt == '-z':			filename_ZTAC = value
		elif opt == '-h':			write_header = True
#		elif opt == '-o':			outfilename = value
		else: 
			sys.stderr.write("Unhandled opt [%s][%s]\n"%(opt,value))
			
	if (len(args) < 1):
		Usage()
		exit(-1)

	LoadZCTA(filename_ZTAC)
	
	#
	#	Read the input file and collect all the possible species
	#	Re-read input file to process each patient
	#		mark the number of species that are diagnosed for that patient
	#		write a record for the patent specifying all the species found
	#

	# open a filename given on the command line.
	fh=open(args[0])

	species = {}
	
	line_no = 0
	for line in fh.readlines():
		line = line.strip()
		if (len(line) < 2):
			continue
		
		line_no += 1
		line = line.upper()
		cols = line.split(',')

		CollectSpecies(cols, species)

	sorted_species_list = sorted(species.items(), key=operator.itemgetter(1),reverse=True)
	#  sorted_species_list

	# create header with all the data being output, list of species
	header = [	"ASID", 
				"Current Age",
				"Gender of Subject",
				"Ethnicity of subject",
				"City", 
				"State", 
				"ZIP",
				"ZCTA",
				"Marital Status"
			 ] 

	for s,c in sorted_species_list:
		header.append(s)
		
	if (write_header):
		print ",".join(header)
			
	fh.seek(0, 0)
	current_patient = ""
	records = []
	n_patients = 0
		
	line_no = 0			
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
				ProcessRecords(records, species, sorted_species_list)
					
			records = []
			current_patient = cols[0]

		records.append(cols)	
	
	if (len(records) > 0):
		n_patients += 1
		ProcessRecords(records, species, sorted_species_list)		#process the last patient
				
	sys.stderr.write("# N Species: %d\n"%len(species))
	sys.stderr.write("# Patients:  %d\n"%n_patients)

###############################################################################
#
###############################################################################
if __name__ == '__main__':

	# reopen stdout file descriptor with write mode and 0 as the buffer size (unbuffered)
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

	Main()
	
###############################################################################
###############################################################################

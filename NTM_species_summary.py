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
	print 'Usage: %s [options] <source data> '%(re.sub('^.*/','',sys.argv[0]))
	print '\t This application extracts the species and identification method from patient data'
	print '\t and prints a summary of the processing.'
	print
	print '\t Options:'
	print '\t     -m    print summary of methods extracted'
	print '\t     -s    print summary of species extracted'
	print '\t     -u    print summary of patients without MYCOBACTERIUM diagnosis'
	print '\n'
# end of Usage()

###############################################################################
# SplitCols - splits columns but takes quotes into account
###############################################################################
PATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')
def SplitCols(line):
	return PATTERN.split(line)[1::2]
#end SplitCols

###############################################################################
# 	Process the records given, combining the information into a single output
#	record.  Check the records to see if there were RAPID or SLOW growing 
#	species diagnosed.  Add a column with the correct ZCTA for given zip code.
###############################################################################

def ProcessRecords(records):
	global display_species
	global display_methods
	global only_recognised_method

	#Create dictionary for species identification
	species = {}

	#Create dictionary for identification method
	methods = {}
	
	if len(records) == 0:
		return (species, methods)
		
#	print "\n\tRecords:", len(records), records
	patient_id = records[0][0]
	
#	if patient_id == "2756708":
#		sys.stderr.write("===> processing [%s]\n"%(patient_id, ))
#		for rec in records:
#			sys.stderr.write("%6d [%s]\n"%(rec[-1],",".join(rec[:-1])))

	for rec in records:
		rec_species,rec_methods = ExtractData(rec, only_recognised_method)

		for s in rec_species:
			if (species.has_key(s)):
				species[s].extend(rec_species[s])
			else:
				species[s] = rec_species[s]

		for m in rec_methods:
			if (methods.has_key(m)):
				methods[m].extend(rec_methods[m])
			else:
				methods[m] = rec_methods[m]

#	if patient_id == "2756708":
#		sys.stderr.write("\n===> [")
#		for s in species:	sys.stderr.write("%s"%s)
#		sys.stderr.write("] [")
#		for m in methods:	sys.stderr.write("%s"%m)
#		sys.stderr.write("]\n")

	return (species, methods)
#end of ProcessRecords


###############################################################################
#
# Main application processing 
#
###############################################################################

def Main():

	global display_species
	global display_methods
	global only_recognised_method
	
	display_species = False
	display_methods = False
	display_undiagnosed = False

	only_recognised_method = False
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "msu", ["help"])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)

	for opt, value in opts:
		#print opt, value
		if	 opt == '-m':			display_methods = True
		elif opt == '-s':			display_species = True
		elif opt == '-u':			display_undiagnosed = True
		else: 
			print "Unhandled opt [%s][%s]"%(opt,value)

	if (len(args) < 1):
		Usage()
		exit(-1)

	# print "display_undiagnosed = ", display_undiagnosed
	
	#Create dictionary for all species identified
	total_species = {}

	#Create dictionary for all methods identified
	total_methods = {}

	# open a filename given on the command line.
	fh=open(args[0])

	n_patients = 0
	n_missing = 0
	n_diagnosed = 0

	line_no = 0
	current_patient = ""
	records = []
	patients = {}
	undiagnosed = {}
		
	for line in fh.readlines():
		line_no += 1
		line = line.strip()		
		if (len(line) < 2):
			continue

		line = line.upper()
		cols = SplitCols(line)  #line.split(',')

		patients[cols[0]] = 1
		
	#	print cols[0], "[%s, %s]"%(cols[2],cols[3])

		# for each set of records for a patient
		#		collect counts of each category of species
		#		write new record with counts

		if cols[0] != current_patient:
			if (len(records) > 0): 
				n_patients += 1
				
				patient_species,patient_methods = ProcessRecords(records)
			
				if (len(patient_species) == 0):
					n_missing += 1
					undiagnosed[current_patient] = 1
				else:
					n_diagnosed += 1
					
				for s in patient_species:
					if (s in total_species):
						total_species[s].extend(patient_species[s])
					else:
						total_species[s] = patient_species[s]
			
				# add in the results to the global list of methods
				for m in patient_methods:
					if (m in total_methods):
						total_methods[m].extend(patient_methods[m])
					else:
						total_methods[m] = patient_methods[m]
			
			records = []
			current_patient = cols[0]

		cols.append(line_no)
		records.append(cols)	
	
	# process the last patient records
	if (len(records) > 0): 
		n_patients += 1
		
		patient_species,patient_methods = ProcessRecords(records)		

		# add in the results to the global list of species
		if (len(patient_species) == 0):
			n_missing += 1
			undiagnosed[current_patient] = 1
		else:
			n_diagnosed += 1
		
		for s in patient_species:
			if (s in total_species):
				total_species[s].extend(patient_species[s])
			else:
				total_species[s] = patient_species[s]
			
		# add in the results to the global list of methods
		for m in patient_methods:
			if (m in total_methods):
				total_methods[m].extend(patient_methods[m])
			else:
				total_methods[m] = patient_methods[m]

	# Print the summary information

	if (display_species):
		print
		print "Species:"
		sort = []		 
		for s in total_species:
			sort.append([len(total_species[s]),s,total_species[s]])
		total = 0
		for s in sorted(sort):
			total += s[0]
			if (len(s[2]) < 20):
				print "%6d"%s[0],s[1],s[2]
			else:
				print "%6d"%s[0],s[1], s[2][:20], "..."
		print "------\n%6d"%total
		
	if (display_methods):
		print
		print "Methods:"
		sort = []		 
		for m in total_methods:
			sort.append([len(total_methods[m]),m,total_methods[m]])
		for m in sorted(sort):
			if (len(m[2]) < 20):
				print "%6d"%m[0],m[1],m[2]
			else:
				print "%6d"%m[0],m[1], m[2][:20], "..."

	if (display_undiagnosed):	
		print "No species diagnosed for patients:"
		pid_per_line = 10
		sort = sorted(undiagnosed)
		for x in range(0,len(sort),pid_per_line):
			print "\t", sort[x:x+pid_per_line]

	print
	print "Lines Processed:        ", "%6d"%line_no
	print "Patients Processed:     ", "%6d"%n_patients
	print "Unique Patient IDs:     ", "%6d"%len(patients)
	print "Patients with diagnosis:", "%6d"%n_diagnosed
	print "Patients w/o diagnosis: ", "%6d"%n_missing
	print "Species:                ", "%6d"%len(total_species)	
	print "Methods:                ", "%6d"%len(total_methods)
				
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

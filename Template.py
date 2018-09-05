# Template program for processing records per <patient,species,method>
# Each record has the format:
#	 Columns of the input:
#		0	ASID
#		1	Date of diagnosis
#		2	Species diagnosed 
#		3	Method of diagnosis 
#		4	Current Age
#		5	Gender of Subject
#		6	Ethnicity of subject
#		7	City 
#		8	State 
#		9	ZIP
#		10	Marital Status 
#
# Copyright (2011-2015) University of Colorado
# All Rights Reserved
# Author: David Knox
#


import string
import sys, re, os, getopt


###############################################################################

def Usage():
	print 'Usage: %s [options] -s <catagories file> <source data> '%(re.sub('^.*/','',sys.argv[0]))
	print '\t Template program for processing records per <patient,species,method>.'
	print '\t      -c <category>  count patients with given category (1 based category number)'
	print '\n'
# end of Usage()

###############################################################################


###############################################################################
#
# Main application processing 
#
###############################################################################

def Main():
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "c:", ["help"])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)

	for opt, value in opts:
		#print opt, value
		if opt == '-c':				category = int(value)
#		elif opt == '-o':			outfilename = value
		else: 
			print "Unhandled opt [%s][%s]"%(opt,value)

	if (len(args) < 1):
		Usage()
		exit(-1)

	
	# open a filename given on the command line.
	fh=open(args[0])

	line_no = 0

	for line in fh.readlines():
		line_no += 1

		sline = line.strip()
		if (len(sline) < 2):
			continue
		
		sline = sline.upper()
		cols = sline.split(',')

		print cols[0], "[%s, %s]"%(cols[2],cols[3])

		# process the record
		
		
		
	sys.stderr.write("processe %d lines\n"%line_no)	

###############################################################################
#
###############################################################################
if __name__ == '__main__':

	# reopen stdout file descriptor with write mode and 0 as the buffer size (unbuffered)
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

	Main()
	
###############################################################################
###############################################################################

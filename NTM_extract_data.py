# Find the counts for each possible species for each patient
#
# Copyright (2011-2018) David Knox, University of Colorado
# All Rights Reserved
# Author: David Knox
#
import string
import sys, os, re, getopt

RECOGNIZED_METHODS = ["GEN", "GENPROBE", "BIOCHEMICAL", "BIOCHEMICALS", "RPOB", "16S", "MALDI-TOF"]

###############################################################################
# StripWord - removes all the known punctuation and artifacts from the word
###############################################################################
def StripWord(w):
	if w.endswith("<COMMA>"):
		w = w[:7]

	# remove punctuation at start and end of word
	w = w.strip(",.; )(][")

	return w
# end of StripWord()


###############################################################################
# Extract the species and methods from this individual record.
#	Select the column from which to extract the data
#	Search for keywords in the text specifying the species and method diagnosed.
# Returns: dict of species and dict of methods extracted
###############################################################################

def ExtractData(rec, only_recognised_method=False):

# for debugging, we generate a file of records from which species was extracted
# and a second file with records that did not have a species extracted.
# These file scan be used to validate the extraction of the correct data from the records.
	
	rec_species = {}
	rec_methods = {}
	if (len(rec) < 11):
		return rec_species, rec_methods
	
	#  Original columns 2015
	#*  2 C GENPROBE IDENTIFICATION Text Result
	#*  3 D IDENTIFICATION Text Result
	#*  6 G HPLC IDENTIFICATION NO 1 Text Result
	#*  7 H HPLC IDENTIFICATION NO 2 Text Result
#	GENPROBE = 2
#	IDENT_TEXT = 3
#	HPLC_1 = 6
#	HPLC_2 = 7

	#  New columns 2018
	#*  8 I GENPROBE IDENTIFICATION Text Result
	#*  9 J IDENTIFICATION Text Result
	#*  10 K HPLC IDENTIFICATION NO 1 Text Result
	#*  11 L HPLC IDENTIFICATION NO 2 Text Result
	GENPROBE = 8
	IDENT_TEXT = 9
	HPLC_1 = 10
	HPLC_2 = 11
		
	# get the line number for this record (appended as last col in record)
	line_no = rec[-1]		

	debugging = True
	if (debugging and line_no <= 1):
		debug_file = open("debug_extracted.csv", 'w')
		debug_file.close()
		debug_file = open("debug_ignored.csv", 'w')
		debug_file.close()

	# find the text describing the diagnosis
	f = rec[GENPROBE]
	diagnosis_col = GENPROBE
	
	if len(f) == 0:	# if the field is empty, try the next column
		f = rec[IDENT_TEXT]
		diagnosis_col = IDENT_TEXT
	
	# alternate columns for text
	# ######are now being ignored because it is only observational information
	# trying to use the HPLC columns for diagnosis
		if len(f)==0:
			f = rec[HPLC_1]
			diagnosis_col = HPLC_1
		if len(f)==0:
			f = rec[HPLC_2]
			diagnosis_col = HPLC_2

	# need to replace "M." with "M" to keep it in same sentence
	fp = re.sub(r"^M. ", "M ", f)
##	if (fp != f): sys.stderr.write("===> [%d][%10s] M. processing [%s][%s]\n"%(rec[-1], rec[0], f,fp))
	f = fp
	
	sentences = re.split(r'[.;]+', f)
	
	# for each sentence, collect the species
	
	for s in sentences:
		words=s.split(' ') # f.split(' ')

	#	if rec[0] == "2756708":
	# 	if rec[0] == "74761":
	# 		sys.stderr.write("===> processing [%s][%d] from field %d\n"%(rec[0], rec[-1], diagnosis_col))
	# 		for w in words:
	# 			sys.stderr.write("[%s]"%w)
	# 		sys.stderr.write("\n")
			
		if ("NEGATIVE" in f) or ("UNABLE" in f):
	#		print "found neg"
			##return rec_species, rec_methods
			continue # skip the rest of the sentence

		still_checking_for_species = True  # set false if we find a complex species
		
		# search each word of the text for the species and method
		for i,w in enumerate(words):
			w = StripWord(w)
			next_word = ""
			if (i < len(words)-1): 
				next_word = StripWord(words[i+1])
			third_word = ""
			if (i < len(words)-2): 
				third_word = StripWord(words[i+2])
				
	#		if rec[0] == "2756708": 			sys.stderr.write("===> Word,next word: [%s][%s]\n"%(w,next_word))

			#  if we should look for avium complex after 'mycolic acid profile ... resembles'
			if (True and still_checking_for_species):
				if ("MYCOLIC"==w) and ("ACID"==next_word):
					# 
#					sys.stderr.write("\tchecking for avium complex, after finding 'mycolic acid' [%s][%s] [%s]\n"%(rec[0],rec[-1]," ".join(words[i+2:])))
					special = ["PROFILE", "MOST", "CLOSELY", "RESEMBLES"]
					
					count = 0
					for j in range (i+2,i+6):
						w = StripWord(words[j])
						if w in special:
							count += 1
					# check to see that at least three words match the phrase.  
					# Allows for misspelling of one word
				#	if (count < 4):
				#		sys.stderr.write("[%s][%s] Partial phrase match [%d of 4], after finding 'mycolic acid' : [%s]\n"%(rec[0],rec[-1],count," ".join(words[i+2:])))
					if (count < 3): 
						sys.stderr.write("[%s][%s] skipping phrase match [%d of 4], after finding 'mycolic acid' : [%s]\n"%(rec[0],rec[-1],count," ".join(words[i+2:])))
						continue  # to next word
					
					#check for M. avium complex consecutive in text
					special_avium = [["M", "M.", "MYCOBACTERIUM"], ["AVIUM"], ["COMPLEX"]]
					matched = False
				
					for j in range (i+3,len(words)):		# for each remaining word in sentence
						matched = True				# 	assume match
						for k in range(3):			# 	look for consecutive match to phrase
							w = StripWord(words[j+k])	
							if w not in special_avium[k]:	
								matched = False
								break
					#		sys.stderr.write("\tpartial M,A,C [%s][%s] [%s]\n"%(rec[0],rec[-1]," ".join(words[j:j+k+1])))
	
						if matched: 
					#		sys.stderr.write("\tfound M,A,C [%s][%s] [%s]\n"%(rec[0],rec[-1]," ".join(words[j:j+3])))
							break # out of phrase match on remaining words
							
					if matched:
						key="%s %s" %("M.", "AVIUM_COMPLEX")  
					#	sys.stderr.write("\tfound MAC [%s][%s] [%s]\n"%(rec[0],rec[-1]," ".join(words[i+2:])))
					#	sys.stderr.write("\t[%d][%s]\n"%(line_no, key))
					#	print "\t\tSpecies:",line_no, key
						if not rec_species.has_key(key):
							rec_species[key] = [line_no]
						else:
							if (rec_species[key][-1] != line_no):
								rec_species[key].append(line_no)
						still_checking_for_species = False  # found a complex species
					####break  # out of word processing, ignore all other species???  
				#	elif (count > 0):
				#		sys.stderr.write("\tdid not find MAC [%s][%s] [%s]\n"%(rec[0],rec[-1]," ".join(words[i+2:])))
				#	else:
				#		sys.stderr.write("\tdid not find MAC [%s][%s] [%s]\n"%(rec[0],rec[-1]," ".join(words[i+2:])))
			# end MYCOLIC ACID check
					
			# check to see if this is an intro word for the species
	#		if ("M." == w) or ('M' == w):
	#			sys.stderr.write("===> Species: [%10s][%s][%s]\n"%(rec[0], w,next_word))

			if (still_checking_for_species):
				if (("MYCOBACTERIUM" == w) or ("M." == w) or ('M' == w)) and (len(next_word) > 0):
					if rec[0] == "60597130": sys.stderr.write("===> Species[%s]: [%s][%s]\n"%(s,w,next_word))
					#print neg_string, "M.", words[i+1]
					species_name = next_word
					if (species_name == "AVIUM") and (third_word == "COMPLEX"):
						species_name = "AVIUM_COMPLEX"
					if (species_name == "ABSCESSUS") and (third_word == "GROUP"):
						species_name = "ABSCESSUS_GROUP"

					key="%s %s" %("M.", species_name)  
				#	print "Species:",line_no, key
					if not rec_species.has_key(key):
						rec_species[key] = [line_no]
					else:
						if (rec_species[key][-1] != line_no):
							rec_species[key].append(line_no)
	
			# check for the method with in the text
			if ("BY"==w) or ("USING"==w):
	#			if rec[0] == "74761": 			sys.stderr.write("===> Method: [%s][%s]\n"%(w,next_word))
				method_name = next_word
				key = method_name	 
				if not only_recognised_method or (key in RECOGNIZED_METHODS):
			#		print "Method:", line_no, key
					if not rec_methods.has_key(key):
						rec_methods[key] = [line_no]
					else:
						if (rec_methods[key][-1] != line_no):
							rec_methods[key].append(line_no)
		# end for each word
	# end for each sentence
	
	if (len(rec_species) > 0) and (len(rec_methods) == 0):
		if (diagnosis_col == GENPROBE):	# can we assume GENPROBE?
			rec_methods["GENPROBE"] = [line_no] 
	
	debugging = True
	if (debugging):
		species = ':'.join(rec_species)
		methods = ':'.join(rec_methods)
		record  = ','.join(rec[:-1])  # leave off last col which is a integer line #
		if (line_no == 1): # header line
			species = "species"
			methods = "methods"
		if (len(rec_species) > 0) and (len(rec_methods) > 0):
			debug_file = open("debug_extracted.csv", 'a')
			if (len(rec_species) > 1):
				sys.stderr.write("===> [%d][%10s] Multiple Species:[%s][%s]\n"%(rec[-1],rec[0], species, methods))
				key="%s %s" %("M.", "AVIUM_COMPLEX")  
				if rec_species.has_key(key):
					sys.stderr.write("===> [%d][%10s] AVIUM COMPLEX detected\n"%(rec[-1],rec[0]))
				
		else:
			debug_file = open("debug_ignored.csv", 'a')

		str = "%d,[%s],[%s],%s\n"%(rec[-1], species, methods, record)
		debug_file.write(str)
		debug_file.close()

	return rec_species, rec_methods

# end of ExtractData()

def OLD_ExtractData(rec):

	rec_species = {}
	rec_methods = {}
	
	# get the line number for this record (appended as last col in record)
	line_no = rec[-1]		

	# find the text describing the diagnosis
	f = rec[2]
	diagnosis_col = 2
	
	if len(f) == 0:	# if the field is empty, try the next column
		f = rec[3]
		diagnosis_col = 3
	
	# alternate columns for text
	# are now being ignored because it is only observational information
#		if len(f)==0:
#			f = rec[4]
#			diagnosis_col = 4
#		if len(f)==0:
#			f = rec[5]
#			diagnosis_col = 5

	words=f.split(' ')

	if ("NEGATIVE" in f) or ("UNABLE" in f):
#		print "found neg"
		return rec_species, rec_methods

	# search each word of the text for the species and method
	for i,w in enumerate(words):
		w = StripWord(w)
		next_word = ""
		if (i < len(words)-1): 
			next_word = StripWord(words[i+1])

		if (True):		#  if we exclude species that come after 'mycolic acid'
			if ("MYCOLIC"==w) and ("ACID"==next_word):
				# skip rest of the words in this text
				sys.stderr.write("Skipping rest of text after finding 'mycolic acid' [%s][%s] [%s]\n"%(rec[0],rec[-1]," ".join(words[i+2:])))
				break	# exits for loop
			
		# check to see if this is an intro word for the species
		if (("MYCOBACTERIUM" == w) or ("M." == w) or ('M' == w)):
			#print neg_string, "M.", words[i+1]
			species_name = next_word
			key="%s %s" %("M.", species_name)  
		#	print "Species:",line_no, key
			if not rec_species.has_key(key):
				rec_species[key] = [line_no]
			else:
				if (rec_species[key][-1] != line_no):
					rec_species[key].append(line_no)
	
		# check for the method with in the text
	#	if ("BY"==w):
		if ("BY"==w) or ("USING"==w):
			method_name = next_word
			key = method_name	 
			if not only_recognised_method or (key in RECOGNIZED_METHODS):
		#		print "Method:", line_no, key
				if not rec_methods.has_key(key):
					rec_methods[key] = [line_no]
				else:
					if (rec_methods[key][-1] != line_no):
						rec_methods[key].append(line_no)

	if (len(rec_species) > 0) and (len(rec_methods) == 0):
		if (diagnosis_col == 2):	# can we assume GENPROBE?
			rec_methods["GENPROBE"] = [line_no] 
			
	return rec_species, rec_methods

# end of OLD ExtractData()

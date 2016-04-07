'''
This little program should take the XML clean text out of the XML files earlier created in Python and move
it into a corpus directory for use by NLTK.

As of January 26, 2014, it does not route output files to two subdirectories categorized by gender; instead, it puts everything out to a single directory.

'''
#This segment imports important tools.

from __future__ import division
import sys
sys.path.append('/users/BrianLarson/terminal/PythonCode')

import numpy, re, pprint, matplotlib, pylab #re is for regular expressions
import nltk
from lxml import etree
import os
import csv
import shutil
import codecs
from unidecode import unidecode

# This parser change for lxml results from this recommendation:
# http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
parser = etree.XMLParser(remove_blank_text=True) #it affects subsequent etree.parse calls that use it as a second argument

######
#RUN TIME VARIABLES
######
#These set some of the working directories.
home_dir = "/Users/brianlarson/Dropbox/Terminal/140209Data/"
xmlinput_dir = home_dir + "XMLOutfromPython/"
nltkcorpus_dir = home_dir + "NLTKCorporaUncatUntag/"
nltkfulltext_dir = nltkcorpus_dir + "Fulltext/"
nltkfacttext_dir = nltkcorpus_dir + "Facttext/"
nltknonfacttext_dir = nltkcorpus_dir + "Nonfacttext/"

end_wd = "/users/BrianLarson/Dropbox/github/Gender-Genre/"

#For now, I'm just pulling a few papers. These are their numbers and the beginnings of their file names.
sought_papers = ["1007", "1055", "2021"] 


def textcorpusout(paper_num, text, outdir, seg_ID):
    out_doc_full_path = outdir + paper_num + seg_ID + ".txt"
    text = unidecode(text) #Replaces unicode chars with ASCII ones that don't freak out NLTK tokenizers.

    #This next line keeps the files written out encoded in utf-8, though that's not as important since I've replaced
    #the unicode chars with ASCII ones int he previous line. Later, I'd like NLTK to deal with Unicode.
    f = codecs.open(out_doc_full_path, encoding='utf-8', mode='w+')
    f.write(text)
    f.close()    

#Iterate through the files in the xmlinput_dir.
for orig_doc_name in os.listdir(xmlinput_dir):
    paper_num = orig_doc_name[0:4] #Note: this makes paper_num a str
    if (not orig_doc_name.startswith('.') ) : #Screens out Mac OS hidden files,
                                                                            #names of which start '.'
        #If you want only limited files, add this condition to the preceding if-statement: and paper_num in sought_papers
        #and then uses only files BNL
        #selected in sought_papers list above
        orig_doc_full_path = xmlinput_dir + orig_doc_name
        
        gate_doc = etree.parse(orig_doc_full_path, parser) #Parse file with defined parser creating ElementTree
        doc_root = gate_doc.getroot() #Get root Element of parsed file
        print "\n\n" # For debugging.
        print "Paper " + paper_num + " loaded." # This is just for debugging.

        #These lines grab the Analysis_Gender value from the text and assign it to var gender. We'll use it to categorize the NLTK corpus
        #and to withhold non-gender-categorized texts from the corpus. This prolly should be a function, but that will happen later.
        gender = ""
        gg = doc_root.find("GG")
        quest = gg.find("Questionnaire")
        for i in quest.iter("Feature"):
            if i.get("Name") == "Analysis_Gender":
                gender = i.get("Value")
        
        #These lines save the files out to the appropriate location, if the file is categorized for gender (some files are not)
        if gender in ["0", "1"]:
            #The next few lines extract the text segments.
            cleantext = doc_root.find("Cleantext") 
            fulltext = cleantext.find("CleanFull").text
            facttext = cleantext.find("CleanFact").text
            nonfacttext = cleantext.find("CleanNonFact").text
            # These lines for debugging.
            print "Fulltext length: " + str(len(fulltext))
            print "Facttext length: " + str(len(facttext))
            print "Nonfacttext length: " + str(len(nonfacttext))
            checklength = len(fulltext) - len(facttext) - len(nonfacttext)
            if abs(checklength) > 30:
                print "CHECKLENGTHS! Difference = " + str(checklength)

            #The next three lines save out the corpora.
            print 'Executing textcorpusout(paper_num, fulltext, nltkfulltext_dir, "Full")'
            textcorpusout(paper_num, fulltext, nltkfulltext_dir, "Full")
            print 'Executing             textcorpusout(paper_num, facttext, nltkfacttext_dir, "Fact")'
            textcorpusout(paper_num, facttext, nltkfacttext_dir, "Fact")
            print 'Executing             textcorpusout(paper_num, nonfacttext, nltknonfacttext_dir, "Nonfact")'
            textcorpusout(paper_num, nonfacttext, nltknonfacttext_dir, "Nonfact")
        
        else:
            print "No Gender for Analysis! Not processed into corpus."
    
##POST-LOOP 
os.chdir(end_wd)

'''
This app needs to be run once for reach subcorpus, Fact, Nonfact, Full, with file directories and names changed.

'''
#!/usr/bin/env python
from __future__ import division

#Set up run-time variables for files and directories.
run_root = "/Users/brianlarson/Dropbox/Terminal/140209Data/"
functword_file = run_root + "Functwords.txt"
tags_file = run_root + "PennTagset.txt"
nltkcorpus_dir = run_root + "NLTKCorporaUncatUntag/Nonfacttext/"
xml_dir = run_root + "XMLOutfromPython/"
pickle_dir = run_root + "NLTKCorporaUncatUntag/Pickles/"
trigramspickle = pickle_dir + "Nonfacttexttrigram.pickle"
bigramspickle = pickle_dir + "Nonfacttextbigram.pickle"
logging_file = nltkcorpus_dir + "4Log.log"
results_file = pickle_dir + "NonfacttextFeaturesPrefixes.pickle"
sought_papers = ["1007", "2021", "2013", "1116"] #For more, add , "2013", "1116"

import os
import shutil
import sys
import pickle
import nltk
import numpy, re, pprint, matplotlib, pylab #re is for regular expressions

from lxml import etree
# This parser change for lxml results from this recommendation:
# http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
parser = etree.XMLParser(remove_blank_text=True) #it affects subsequent etree.parse calls that use it as a second argument

#Direct prints to logging_file. Don't use this on the full run!
#stdout = sys.stdout
#sys.stdout = open(logging_file, 'w') #If you unremark this line, be sure to do the last one in the file, too.

#Sentence tokenizer (sentence splitter using sent_tokenize default, which is?)
from nltk.tokenize import sent_tokenize
#Word tokenizer Version using TreebankWorkTokenizer
from nltk.tokenize import TreebankWordTokenizer
tokenizer = TreebankWordTokenizer()


#The following lines load (from pickled files) the aggregate bigrams and trigrams, then trimmed to the top 100 and 500, as well as
#the lists of function words and POS tags.
corpustrigrams = pickle.load( open (trigramspickle, "rb"))
corpusbigrams = pickle.load( open (bigramspickle, "rb"))
freqtrigrams = corpustrigrams[:500] 
freqbigrams = corpusbigrams[:100] 
print "Frequent bigrams used as features... Length = " + str(len(freqbigrams))
print freqbigrams
print "Frequent trigrams used as featuresLength = " + str(len(freqtrigrams))
print freqtrigrams

with open(functword_file) as f:
    functwords = f.read().splitlines()
print "Number of function words = " + str(len(functwords))
with open(tags_file) as f:
    postags = f.read().splitlines()
print "Number of tags = " +str(len(postags))

#Tagset List appears here: Santorini, B. (1990). Part-of-speech tagging guidelines for the Penn Treebank Project (No. MN-CIS-90-47) (p. 34). Philadelphia: University of Pennsylvania, Department of Computer and Information Science. Retrieved from http://repository.upenn.edu/cis_reports/570/
#Supplemented with the punctuation items identified here: Atwell, E. (n.d.). Automatic mapping among lexico-grammatical annotation models (AMALGAM): The University of Pennsylvania (Penn) Treebank tag-set. University of Leeds, School of Computing. Retrieved from http://www.comp.leeds.ac.uk/amalgam/tagsets/upenn.html
'''Next four lines for debug only
print "Function words:"
print functwords
print "POS tags:"
print postags
'''
#papers will be a list of dictionaries. Each dictionary will have the features for one paper.
papers = [ ]

def getgender(paper_num):
        print paper_num + " GET GENDER"
        print "\n_____"
        #Go into the XML document to get the gender.
        for f in os.listdir(xml_dir):
            if f.startswith(paper_num):
                xml_doc_full_path = xml_dir + f                
        gate_doc = etree.parse(xml_doc_full_path, parser) #Parse file with defined parser creating ElementTree
        doc_root = gate_doc.getroot() #Get root Element of parsed file
        print "\n\n" # For debugging.
        print "XML Paper " + paper_num + " loaded." # This is just for debugging.
        #These lines grab the Analysis_Gender value from the text and assign it to var gender. We'll use it to categorize the NLTK corpus
        #and to withhold non-gender-categorized texts from the corpus. This prolly should be a function, but that will happen later.
        gender = ""
        gg = doc_root.find("GG")
        quest = gg.find("Questionnaire")
        for i in quest.iter("Feature"):
            if i.get("Name") == "Analysis_Gender":
                gender = i.get("Value")
        print "Gender: " + str(gender) #for debugging
        return gender

#Begin loop over papers
#For each paper, we want to do these things:
#Create a dictionary containing the following keys/values.
#   1. Gender
#   2. Count of tokens
#   3. Count of sentences
#   4. Entries and counts for all POS tags on words.
#   4. Entries and counts for all the function words
#   5. Entries and counts for all the freqtrigrams
#   6. Entries and counts for all the freqbigrams

for file_name in os.listdir(nltkcorpus_dir):
    paper_num = file_name[0:4] #Note: this makes paper_num a str
    if (not file_name.startswith('.') ) : #Screens out Mac OS hidden files,
                                        #names of which start '.'
        #If you want only limited files, add this condition to the preceding if-statement: and paper_num in sought_papers
        #and then uses only files BNL
        #selected in sought_papers list above

        filepath = nltkcorpus_dir + file_name

        print "\n*************************************************************************"
        print "LOADING " + filepath
        print "\n*************************************************************************"
        #opens the subject file , reads its contents, and closes it.
        f = open(filepath)
        infile = f.read()
        f.close()        

        #Declare the feature dictionary for this paper
        paper_dict = { }
        paper_dict["A_papernum"] = paper_num
        paper_dict["A_gender"] = getgender(paper_num)

        #Populate the dictionary with key/0 for each feature in the list of features.
        paper_dict["A_tokens"] = 0 # Total tokens in paper
        paper_dict["A_sents"] = 0 #Total sentences in paper
        paper_dict["A_trigrams"] = 0 #Total trigrams in paper
        paper_dict["A_bigrams"] = 0 #Total bigrams in paper
        for i in functwords:
            j = "F_" + i.lower()
            paper_dict[j] = 0
        for i in postags:
            j = "POS_" + i
            paper_dict[j] = 0
        for i in freqtrigrams: #Add a key for each common trigram from the corpus
            j = i[0]
            paper_dict[j] = 0
        for i in freqbigrams: #Add a key for each common bigram from the corpus
            j = i[0]
            paper_dict[j] = 0
        print "\n_____"
        print "Paper " + paper_num + "'s number of features: " + str(len(paper_dict))
        print "\n_____"
        
        #Tokenize infile into sentences. The result is a list of sentences.
        sentences = sent_tokenize(infile)
        paper_dict["A_sents"] = len(sentences)
        
        #Begin loop over sentences in paper.
        #This loop does the following:
        #1. Tokenizes the sentence and adds the number of tokens to paper_dict["tokens"].
        #2. POS-tags the sentence.
        #3. Iterates over i (tagged words) in the sentence, and increments paper_dict[i[0]] and paper_dict[i[1]], if they exist.
        #4. Finds trigrams in the sentence.
        #5. Iterates over i (trigrams), forming a text tag ("name") for each and increments paper_dict["name"] if it exists.
        #6. Finds bigrams in this sentence.
        #7. Iterates over i (bigrams), forming a text tag ("name") for each and increments paper_dict["name"] if it exists.
        print "\n_____"
        print paper_num + " LOOP OVER SENTENCES"
        print "\n_____"
        sentence_counter = 0
        for i in sentences: #For each sentence in the paper...
            print "\nSentence number: " + str(sentence_counter)
            print i # This is just for debug.
            #Word-tokenize it.
            tokenized = tokenizer.tokenize(i) #Result is a list of word-tokens.
            print "\nTokenized sentence: " + str(sentence_counter)
            print tokenized #for debug only
            paper_dict["A_tokens"] += len(tokenized) # adds number of tokens in this sentence to number tokens in the paper.

            #POS Tag it
            postagged = nltk.pos_tag(tokenized) #Result is a list of tuples, with word-token and pos-token.
            print "\nPOS tagged sentence: " + str(sentence_counter)
            print postagged #for debug only
            for i in postagged:
                j = "F_" + i[0].lower()
                if j in paper_dict.keys(): #if the word is a function word, add one to that function word's count in paper_dict
                    paper_dict[j] += 1
                j = "POS_" + i[1]
                if j in paper_dict.keys():
                    paper_dict[j] += 1 #increment the tag's count in paper_dict
                else: 
                    print "Unexpected tag or no tag appearing in sentence " + str(sentence_counter) + ". Token: " + i[0] + "  Tag: " + i[1]
                    #paper_dict[i[1]] = 1 #Delete this line if you want only tags listed in postags (probably from external file)

            trigrams = nltk.trigrams(postagged) #Result is a list of lists of lists.
            print "\nTrigrams in sentence: " + str(sentence_counter)
            print trigrams #for debug only
            for i in trigrams: #For each trigram in the sentence...
                paper_dict["A_trigrams"] += 1
                v = "Tri_"
                for j in i:
                    v += j[1]
                    v += "_"
                v = v[:-1]
                if v in paper_dict.keys():
                    paper_dict[v] += 1

            #Next three lines repeat the previous three, except with bigrams in stead of trigrams.
            bigrams = nltk.bigrams(postagged) #This is POS/word pair bigrams, not just POS.
            print "\nBigrams in sentence: " + str(sentence_counter)
            print bigrams #for debug only
            for i in bigrams:
                paper_dict["A_bigrams"] += 1
                v = "Bi_"
                for j in i:
                    v += j[1]
                    v += "_"
                v = v[:-1]
                if v in paper_dict.keys():
                    paper_dict[v] += 1
            sentence_counter += 1
        
        #Now we need to normalize the data.
        #1. Multiply value of each of the following types of feature by 1/#tokens: functionwords, postags.
        #2. Multiply value of each of trigrams 4/#tokens
        #3. Multiply value of each of bigrams 2/#tokens
        tokensfactor = 1 / paper_dict["A_tokens"]
        bigramsfactor = tokensfactor * 2
        trigramsfactor = tokensfactor * 4
        print "Factors: Tokens = " + str(tokensfactor) + "  Bigrams = " + str(bigramsfactor) + "  Trigrams = " + str(trigramsfactor)
        for i in paper_dict.iterkeys():
            if i.startswith("F_") or i.startswith("POS_"):
                paper_dict[i] = paper_dict[i] * tokensfactor
            if i.startswith("Bi_"):
                paper_dict[i] = paper_dict[i] * bigramsfactor
            if i.startswith("Tri_"):
                paper_dict[i] = paper_dict[i] * trigramsfactor
            
        #Use following three lines for debug only
        #print "Feature set:"
        #for key in sorted(paper_dict.iterkeys()):
        #    print "%s: %s" % (key, paper_dict[key])
        
        papers.append(paper_dict)

pickle.dump(papers, open (results_file, "wb"))

#sys.stdout = stdout



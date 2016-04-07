'''
This application needs to be run once for each subcorpus, Factext, Fulltext, and Nonfacttext.
Operator needs to change the directories and pickle filenames.


'''
#!/usr/bin/env python
from __future__ import division
import os
import shutil
import sys
import pickle

import nltk
import numpy, re, pprint, matplotlib, pylab #re is for regular expressions

#Sentence tokenizer (sentence splitter using sent_tokenize default, which is?)
from nltk.tokenize import sent_tokenize
#Word tokenizer Version using TreebankWorkTokenizer
from nltk.tokenize import TreebankWordTokenizer
tokenizer = TreebankWordTokenizer()

working_root = "/Users/brianlarson/Dropbox/Terminal/140209Data/NLTKCorporaUncatUntag/"
nltkcorpus_dir = working_root + "Nonfacttext/"
pickle_dir = working_root + "Pickles/"
trigrampickle = pickle_dir + "Nonfacttexttrigram.pickle"
bigrampickle = pickle_dir + "Nonfacttextbigram.pickle"
sought_papers = ["1007", "1055", "2021"] 

#Global variables over all the papers.
aggregate_bigrams = [ ]
aggregate_trigrams = [ ]

#Begin loop over papers
for file_name in os.listdir(nltkcorpus_dir):
    paper_num = file_name[0:4] #Note: this makes paper_num a str
    if (not file_name.startswith('.') ) : #Screens out Mac OS hidden files,
                                        #names of which start '.'
        #If you want only limited files, add this condition to the preceding if-statement: and paper_num in sought_papers
        #and then uses only files BNL
        #selected in sought_papers list above

        filepath = nltkcorpus_dir + file_name
        print "\n***********"
        print "Paper #: " + paper_num
        print "At: " + filepath
        #opens the subject file , reads its contents, and closes it.
        f = open(filepath)
        infile = f.read()
        f.close()
        
        #Tokenize infile into sentences. The result is a list of sentences.
        sentences = sent_tokenize(infile)
        
        #Begin loop over sentences in paper.
        for i in sentences: #For each sentence in the paper...
            #Word-tokenize it.
            tokenized = tokenizer.tokenize(i) #Result is a list of word-tokens.
            #POS Tag it
            postagged = nltk.pos_tag(tokenized) #Result is a list of tuples, with word-token and pos-token.
            #Find trigrams in this sentence.
            trigrams = nltk.trigrams(postagged) #Result is a list of lists of lists. 
            for i in trigrams: #For each trigram in the sentence...
                aggregate_trigrams.append(i) #Append that trigram to the global aggregate_trigram.
            #Next three lines repeat the previous three, except with bigrams in stead of trigrams.
            bigrams = nltk.bigrams(postagged)
            for i in bigrams:
                aggregate_bigrams.append(i)    
        #end loop over files

#Here begins the number crunching, looking for the most common bigrams and trigrams.
    
#We do the same things for bigrams and trigrams:
    #ID each instance of a bigram, create a text label for it, and add it to the list agg_posbigrams.append(v)
    #Do a frequency distribution of the bigram and create a list of its items.
    #Pickle that list (for use later)
print "\n**************************"
print "TOP BIGRAMS"
print "\n**************************"
agg_posbigrams = [ ]
for l in aggregate_bigrams:
    v = "Bi_"
    for m in l:
        v += m[1]
        v += "_"
    v = v[:-1]
    agg_posbigrams.append(v) 

fdistbigram = nltk.FreqDist(agg_posbigrams)
bigramlist = fdistbigram.items()
print bigramlist[:50]
pickle.dump(bigramlist, open (bigrampickle, "wb"))

print "\n**************************"
print "TOP TRIGRAMS"
print "\n**************************"
agg_postrigrams = [ ]
for l in aggregate_trigrams:
    v = "Tri_"
    for m in l:
        v += m[1]
        v += "_"
    v = v[:-1]
    agg_postrigrams.append(v) 

fdisttrigram = nltk.FreqDist(agg_postrigrams)
trigramlist = fdisttrigram.items()
print trigramlist[:50]
pickle.dump(trigramlist, open (trigrampickle, "wb"))



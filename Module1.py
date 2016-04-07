'''
This code takes XML output from GATE, enriches it with data from the questionnaire that BNL administered to students,
produces clean texts of sections of the student documents after removing citations, etc.
Last modified: January 26, 2014.

NOTE: As ofr January 2, 2014, this code fails to perform on a small number (7) of the 200 or so texts BNL put through it.
Performance/responses are explained in applicable Evernote note for the project. The console output for this program makes
it possible to see where problems, and they can be corrected manually before the next phase.

'''
#THIS SEGMENT imports tools, operating system stuff and sets the working directory.
from __future__ import division
import sys
sys.path.append('/users/BrianLarson/terminal/PythonCode')

import numpy, re, pprint, matplotlib, pylab #re is for regular expressions
import nltk
from lxml import etree
import os
import csv
import shutil
import re
import codecs

# This parser change for lxml results from this recommendation:
# http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
parser = etree.XMLParser(remove_blank_text=True) #it affects subsequent etree.parse calls that use it as a second argument

######
#RUN TIME VARIABLES
######
#These set some of the working directories.
home_dir = "/Users/brianlarson/Dropbox/Terminal/PythonCode/140129Data/"
start_wd = home_dir + "XMLoutfromGATE/"
defective_xml_out = home_dir + "DefectiveXMLfromGATE/"
xml_output_dir = home_dir + "XMLOutfromPython/"
end_wd = "/users/BrianLarson/Dropbox/github/Gender-Genre/"

#This sets the file where the CSV data from the Excel export is.
csv_file = home_dir + 'CSVSurveyData/MasterDataForXML.csv'

#For testing, I may just want to pull a few papers. These are their numbers and the beginnings of their file names.
sought_papers = ["1007", "1055", "2021"] 

#These are large segments deleted before processing. They are NEVER processed.
lg_segments_out = ["Caption", "TOCTOA", "OtherFormal"] 

#This IDs the annotation sets that are possible based on who the annotators were.
as1 = "SLL"
as2 = "BNL"

##FUNCTIONS SEGMENT
## sets up functions that will be used below.
def add_unq_subelement(parent, name): #Adds a unique subelement to parent.
    # parent is a tree element or subelement. name will be the name of a subelement under parent
    #First check to see if there is already an element with this name.
    name_present = False #This value is switched to True only if an element by this name is already present.
    for element in parent: #Test whether element by this name is already present.
        if element.tag == name:
            print "Func add_unq_subelement: This parent already has a " + name + " subelement!"
            name_present = True
    #If this subelement does not already exist, create it.
    if name_present == False:
        return etree.SubElement(parent, name)    

def add_unq_feature(parent, name, value): #Adds a unique feature under an element
    # parent is a tree element or subelement. name and value will apply to the newly created feature
    #First check to see if there is already a feature with this name.
    f_present = False #This value is switched to True only if a Feature by this name is already present.
    for i in range(len(parent)): #This iterates through the parent looking for a Feature subelement with this name.
        if parent[i].tag == "Feature" and parent[i].get("Name") == name:
            print "Func add_unq_feature: This element's " + name + " feature is already set!"
            f_present = True
    #If a Feature by this name does not already exist, create it.
    if f_present == False:
        return etree.SubElement(parent, "Feature", Name = name, Value = value)

def get_csv_data(file_name, paper_num): #This function returns the record from the Micrsoft Excel worksheet (file_name) with
    #information about the paper (paper_num). 
    with open(file_name, 'rU') as csvfile:
        csv_in = csv.DictReader(csvfile, dialect = 'excel')
        for record in csv_in:
            if record['UniqueID'] == paper_num:
                return record #This is a dictionary.
            #If there is no match, this function returns "FAIL" for which the line of code that uses it below tests.

def add_xl_features(docroot, paper_num, record): #Takes a Gate doc and adds GG elements and features.
    #Add GG element under root and Questionnaire under GG
    gg = add_unq_subelement(doc_root, "GG")
    add_unq_feature(gg, "PaperNum", paper_num)
    quest = add_unq_subelement(gg, "Questionnaire")
    for key in record.keys(): #This uses the excel data pulled with the get_csv_data function.
        add_unq_feature(quest, key, record[key])
    # print etree.tostring(gg, pretty_print = True) #First part of this line is for debuggin.
    print "XL features added to " + paper_num

def verify_annotation(docroot, paper_name): #Examines an XML file to make sure an as1 or as2 annotation set appears on it
    names = [as1, as2]
    as_present = False #This tracking variable is reset as true only if one of the approved annotator sets is present.
    for i in range(len(docroot)): #Checks for presence of one of the approved annotator sets.
        if docroot[i].tag == "AnnotationSet" and docroot[i].get("Name") in names:
            as_present = True
    if as_present == False: 
        #move file to defective folder
        paper_path = os.path.join(start_wd, paper_name)
        print "\n\n"
        print "NO ANNOTATIONS IN " + paper_name + ": Copying " + paper_path + " to " + defective_xml_out
        shutil.copy(paper_path, defective_xml_out)
        return False
    else:
        return True

def extract_original_text(gatefile): #extracts the original text TextWithNodes from the GATE output in string form.
    #Opening the original file in regular file mode lets us get at the text in it and do REgex operations without
        #freaking out the XML parser.
    #original alternative
#    with open(gatefile) as f: #This reopens the original file, NOT as xml, and read-only.
#        original = f.read() #Creates a string from the original file.
#        original = unicode(original, errors='ignore')
#        re_s = re.compile(ur'<TextWithNodes>.*</TextWithNodes>', re.DOTALL) #Compiles regexpression. DOTALL allows .* to
                                                                                       #match line-ends.
#        return re_s.findall(original)[0] #Findal returns a LIST of segments from whole_doc that match re_s. Picking the first index
                                         #gives us the string at that point in the list. That should always be the one we want
                                         #because there should be only one!
    #end original alternative

    #Second alternative
    f = codecs.open(gatefile, encoding="utf-8")
    original = f.read()
    re_s = re.compile(ur'<TextWithNodes>.*</TextWithNodes>', re.DOTALL)
    
    result = re_s.findall(original)[0]
    f.close()
    return result
    #end second alternative

def get_annotation_set(root): #Given an xml root, this returns the identifier for the annotation set that should be used.
                              #It prefers the as1 set where both are present.
    as1_present = False
    as2_present = False
    for i in range(len(root)):
        if root[i].tag == "AnnotationSet" and root[i].get("Name") == as1:
            as1_present = True
        else:
            if root[i].tag == "AnnotationSet" and root[i].get("Name") == as2:
                as2_present = True
    if as1_present:
        print "Annotator as1 (" + as1 + ") is present."
        return as1
    else:
        if as2_present:
            print "Annotator as2 (" + as2 + ") is present."
            return as2
        else:
            return "ERROR: Neither annotator as1 nor as2 is present."

def extract_node_range(text,start,end): #This function works on string, not XML. It returns the node markers and all text between
                                        #them indicated by the start and end nodes.
    re_string = r'<Node id=\"' + start + r'\"/>.*<Node id=\"' + end + r'\"/>'  
    u = re.compile(re_string, re.DOTALL)
    v = u.findall(text)
    if not v:
        return "ERROR: Node range not matched in this document!"
    else:
        return v[0]

def delete_span_text(text,start,end): #This function takes a string, not XML, that has node markers and text in it and removes all
                                      #the text from between the specified start and end node markers, leaving the node markers.
    re_pattern = r'<Node id=\"' + start + r'\"/>.*<Node id=\"' + end + r'\"/>'
    re_repl = '<Node id=\"' + start + '\"/><Node id=\"' + end + '\"/>'
    text = re.sub(re_pattern, re_repl, text, flags=re.DOTALL)
    return text

def delete_segments(text, root, aset, lg_segs, sm_segs): #This function iterates through XML annotations.
                                                         #Edits happen to a text string.
                                                         #Function IDs segements where there is text that should be deleted, sending
                                                         #their start and end nodes to delete_span_text.
    for e in root.iter("AnnotationSet"):
        if e.get("Name") == aset:
            for f in e.iter("Annotation"):
                if f.get("Type") == "LargeSegment":
                    start_node = f.get("StartNode")
                    end_node = f.get("EndNode")
                    for g in f.iter("Value"):
                        if g.text in lg_segs:
                            text = delete_span_text(text,start_node,end_node)
                else:
                    if f.get("Type") in sm_segs:
                        start_node = f.get("StartNode")
                        end_node = f.get("EndNode")
                        text = delete_span_text(text,start_node,end_node)
    return text

def fact_delete(text, root, aset): #Iterates through XML features.
                                   #Identifies the start end end of the Fact section using XML features,
                                   #and removes that text from the text string by sending to delete_span_text.
    for e in root.iter("AnnotationSet"):
        if e.get("Name") == aset:
            for f in e.iter("Annotation"):
                if f.get("Type") == "LargeSegment":
                    start_node = f.get("StartNode")
                    end_node = f.get("EndNode")
                    for g in f.iter("Value"):
                        if g.text == "Facts":
                            text = delete_span_text(text,start_node,end_node)
    return text
    
def lg_seg_xtract(text, root, aset, lg_seg): #Originally, this is just to permit pulling the Facts section out,
                                             #but it would work with other sections, too.
    for e in root.iter("AnnotationSet"):
        if e.get("Name") == aset:
            for f in e.iter("Annotation"):
                if f.get("Type") == "LargeSegment":
                    start_node = f.get("StartNode")
                    end_node = f.get("EndNode")
                    for g in f.iter("Value"):
                        if g.text == lg_seg:
                            re_string = r'<Node id=\"' + start_node + r'\"/>.*<Node id=\"' + end_node + r'\"/>'  
                            #print re_string # this is for debugging; in that case, # out the next two lines. 
                            u = re.compile(re_string, re.DOTALL)
                            try:
                                text = u.findall(text)[0]
                            except IndexError:
                                text = "Function error (lg_seg_xtract): Regex search function did not match any text."
                                print text
    return text

def nodes_out(text): #This function texts a string (not XML) and removes all the node markers in it!
    re_pattern = r'<.*?>'
    re_repl = ''
    text = re.sub(re_pattern, re_repl, text, flags=re.DOTALL)
    return text


##MAIN LOOP This loop iterates over files in start_wd directory and does stuff to files.
os.chdir(start_wd)

for orig_gate_doc_name in os.listdir(os.getcwd()):
    if (not orig_gate_doc_name.startswith('.') and not orig_gate_doc_name.startswith('xxxx') ):
        #Screens out Mac OS hidden files, names of which start '.' and BNL-excluded files, which start xxxx;
        #and if sought_papers is specified above, add this condition: and orig_gate_doc_name[0:4] in sought_papers.
        gate_doc = etree.parse(orig_gate_doc_name, parser) #Parse file with defined parser creating ElementTree
        doc_root = gate_doc.getroot() #Get root Element of parsed file
        paper_num = orig_gate_doc_name[0:4] #NOTE: this makes paper_num a str
        # Run verify_annotation as a condition of processing the file further.
        if verify_annotation(doc_root, orig_gate_doc_name): #If verify_annotation is false, we move to next file.
            xl_rec_contents = get_csv_data(csv_file, paper_num) #Gets corresponding data from CSV file.
            if xl_rec_contents == "FAIL":
                print "Paper num: " + paper_num + " not appearing in CSV file!" #If there's no Excel/CSV data matching, we move to the
                                                                                #next file.
            ##Assuming we pass those two checks, we get to process the file.
            
            ###########
            ##THIS IS THE PAYLOAD, WHERE EVERYTHING HAPPENS
            ###########
            else: 
                print '\n\n'
                print "************************"
                print "PAPER NUMBER: " + paper_num
                print "************************"
                
                #Add features from the Excel file (survey, etc.) to the xml file.
                add_xl_features(doc_root, paper_num, xl_rec_contents)
                
                #Save the results to a new XML file (we don't edit the original from GATE at all.)
                rev_gate_doc_name = xml_output_dir + orig_gate_doc_name #Creates new name for the xml output of this program
                                                                    #(this version replaced by next line)
                gate_doc.write(rev_gate_doc_name, pretty_print = True, xml_declaration=True, encoding='UTF-8')
                    #xml_declaration and encoding necessary to open UTF later
                print "Saved as " + rev_gate_doc_name

                xml_doc = etree.parse(rev_gate_doc_name, parser) #Reads the new file in. Parse the new file into etree.
                xml_root = xml_doc.getroot() #Creates a variable for referring to the root of this xml doc.

                orig_w_nodes = extract_original_text(orig_gate_doc_name) #Get the TextWithNodes from the original file
                #NOTE: In the next few lines, we are operating on the string pulled in from orig_gate_doc_name, not on
                #XML file. This allows us to treat regard the XML nodes as strings rather than having to use complicated
                #XML parsing to clean them out of the string before it can be passed to NLP functions like splitter, tokenizer, etc.
                #print orig_w_nodes #This is for debugging only
                
                #Delete the text components from all segments that will not be analyzed from orig_w_nodes.
                #Prefer the annotation set ascribed to as1, otherwise use as2.
                gate_ann_set = get_annotation_set(xml_root)
                sm_segments_out = ["Heading", "Footnote", "Cite", "Blockquote"] #List of small segments to be cleansed.
                
                #Cleanse text out of segments that won't be analyzed.
                orig_w_nodes = delete_segments(orig_w_nodes, xml_root, gate_ann_set, lg_segments_out, sm_segments_out)

                #THEN: Create two new strings for the text that is just the facts and text that is everything but facts.
                nonfact_w_nodes = fact_delete(orig_w_nodes, xml_root, gate_ann_set)
                facts_w_nodes = lg_seg_xtract(orig_w_nodes, xml_root, gate_ann_set, "Facts")
                #print facts_w_nodes #This is for debugging only.
                
                #We now have three strings, each cleansed of segments we don't want but each having the node markers,
                    #which we now no longer need. We first create a place in our XML document to hold the results.
                                    
                cleantext = add_unq_subelement(xml_root,"Cleantext")
                cleanfull = add_unq_subelement(cleantext, "CleanFull")
                cleannonfact = add_unq_subelement(cleantext, "CleanNonFact")
                cleanfact = add_unq_subelement(cleantext, "CleanFact")
                
                #then we put the results in after running through the nodes_out function.
                try:
                    cleanfull.text = nodes_out(orig_w_nodes)
                except ValueError:
                    print "XML error thrown while writing cleanfull.text: "
                try:
                    cleannonfact.text = nodes_out(nonfact_w_nodes)
                except ValueError:
                    print "XML error thrown while writing cleannonfact.text: "
                try:
                    cleanfact.text = nodes_out(facts_w_nodes)
                except ValueError:
                    print "XML error thrown while writing cleanfact.text: "
                
                #Finally, we write the revised XML file out.
                xml_doc.write(rev_gate_doc_name, pretty_print = True, xml_declaration=True, encoding='UTF-8')

##POST-LOOP 
os.chdir(end_wd)

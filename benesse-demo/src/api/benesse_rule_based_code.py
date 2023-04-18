#!/usr/bin/env python
# coding: utf-8

# In[26]:


import stanfordnlp
from pattern.en import suggest
from pattern.en import referenced
import codecs
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from pattern.en import conjugate
from pattern.en import pluralize, singularize
from nltk import download
from os import path
from pprint import pprint


if path.exists(f"{path.expanduser('~')}/stanfordnlp_resources/en_ewt_models"):
    print("requirment already installed")
else:
    stanfordnlp.download("en")

    

if path.exists(f"{path.expanduser('~')}/nltk_data/tokenizers/punkt/"):
    print("requirment already installed")
else:
    download('punkt')


nlp = stanfordnlp.Pipeline(processors = "tokenize,mwt,lemma,pos",use_gpu=True)

# In[ ]:


def CapitalizeError(text,nlp,correctFlag=False):
    '''
    Purpose: To check if text has errors due to capitalization. 
             Additionally, it returns corrected sentence.
    
    Parameters: text: string
                    A string of text-single or a paragraph.
                    
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''
    doc = nlp(text)
    count=0
    text=""
    for sen in doc.sentences:
        if sen.words[0].text.islower():
            count+=1
            text+=sen.words[0].text.capitalize()
            text+=" "
        else:
            text+=sen.words[0].text
            text+=" "
        for i in range(1,len(sen.words)):
            if sen.words[i].upos=="PROPN" or sen.words[i].upos=="NNS":
                if sen.words[i].text.islower():
                    count+=1
                    text+=sen.words[i].text.capitalize()
                    text+=" "
                else:
                    text+=sen.words[i].text
                    text+=" "
            elif sen.words[i].text=="i":
                count+=1
                text+=sen.words[i].text.capitalize()
                text+=" "
            else:
                text+=sen.words[i].text.lower()
                text+=" "
    if correctFlag==True:
        return count,text
    else:
        return count


# In[ ]:


def checkSpellingError(text,nlp,correctFlag=False):
    '''
    Purpose: To check if text has errors due to wrong spellings.
             Additionally, it returns corrected sentence.
    
    Parameters: text: string
                    A string of text-single or a paragraph.
                
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''
    doc = nlp(text)
    count=0
    text=""
    for sen in doc.sentences:
        for word in sen.words:
            #print(word.text.lower())
            l=["'s","n't","'ll"]
            try:
                sugList=suggest(word.text.lower())
            except:
                sugList = []
                l.append(word.text.lower())
            for k in sugList:
                l.append(k[0])
            if (word.text.lower() in l) or (word.lemma in l):
                text+=word.text
                text+=" "
                continue
            else:
                count+=1
                text+=sugList[0][0]
                text+=" "
    if correctFlag==True:
        return count,text
    else:
        return count


# In[ ]:


def read_file(file):
    '''
    Purpose: Helper function: Read text files.
    
    Parameters: file: text file.
                    
    Returns: text: string format.
    '''    
    fp=codecs.open(file,"r",encoding='utf8',errors='ignore')
    text=fp.readlines()
    return text

def articleError(text,nlp,correctFlag=False):
    '''
    Purpose: To check if text has errors due to wrong article usage.
             Additionally, it returns corrected sentence.
             
    Parameters: text: string
                    A string of text-single or a paragraph.
                    
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''
    path="/home/manraj/benesse/data/uncNouns.txt"
    unc_text=read_file(path)
    unc_words=[]
    for i in unc_text:
        tokens=word_tokenize(i)
        unc_words.append(tokens[0].lower())
    doc = nlp(text)
    count=0
    ntext=""
    
    for s in doc.sentences:
        for t in range(len(s.words)):
            if s.words[t].text=='a' or s.words[t].text=='an':
                if ((s.words[t+1].text in unc_words) or s.words[t+1].xpos=="NNS" or s.words[t+1].xpos=="NNPS"):
                    count+=1
                elif (t<len(s.words)-2) and (s.words[t+1].xpos in ["JJ","JJR"]) and (s.words[t+2].xpos in ['NNP','NN']):
                    if (s.words[t].text=='a' and referenced(s.words[t+1].text)==('an '+s.words[t+1].text)):
                        ntext+='an'
                        count+=1
                    elif(s.words[t].text=='an' and referenced(s.words[t+1].text)==('a '+s.words[t+1].text)):
                        ntext+='a'
                        count+=1
                    else:
                        ntext+=s.words[t].text
                elif (s.words[t+1].xpos not in ["NNP","NN"] ):
                    count+=1
                elif(s.words[t].text=='a' and referenced(s.words[t+1].text)==('an '+s.words[t+1].text)):
                    ntext+='an'
                    count+=1
                elif(s.words[t].text=='an' and referenced(s.words[t+1].text)==('a '+s.words[t+1].text)):
                    ntext+='a'
                    count+=1
                else:
                    ntext+=s.words[t].text
                ntext+=" "
#             elif (t<len(s.words)-1) and (s.words[t].xpos in ["JJ","JJR"]) and (s.words[t+1].xpos in ['NNP','NN']):
#                 ntext+=referenced(s.words[t].text)+" "
            else:
                ntext+=s.words[t].text
                ntext+=" "
    if correctFlag==True:
        return count,ntext
    else:
        return count


# In[ ]:


def becauseError(text,nlp,correctFlag=False):
    '''
    Purpose: To check if text after using word 'because' incomplete sentence. 
             Additionally, it returns corrected sentence.
             
    Parameters: text: string
                    A string of text-single or a paragraph.
                    
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''    
    doc = nlp(text)
    count=0
    text=""
    for s in doc.sentences:
        for i in range(len(s.words)):
            if s.words[i].text=='because':
                if s.words[i+1].upos=='PUNCT' or i==len(s.words)-1:
                    count+=1
                    text+='.'
                    break
                if s.words[i+1].xpos=='IN':
                    if i==len(s.words)-2:
                        count+=1
                    elif(s.words[i+2].xpos not in ['NN','NNS','NNP','NNPS','PRP','PRP$','DT']):
                        count+=1
                        text+="."
                        break
                    else:
                        text+=s.words[i].text
                        text+=" " 
                elif s.words[i+1].xpos in ['NN','NNS','NNP','NNPS','PRP','PRP$']:
                    if i==len(s.words)-2:
                        count+=1
                    flag=0
                    for j in range(i+2,len(s.words)):
                        if s.words[j].xpos in ['VB','VBP','VBZ','VBG','VBN','VBD','MD']:
                            flag+=1
                            break
                    if flag==0:
                        count+=1
                        text+="."
                        break    
                    else:
                        text+=s.words[i].text
                        text+=" "
                else:
                    text+=s.words[i].text
                    text+=" "
            else:
                text+=s.words[i].text
                text+=" "
    if correctFlag==True:
        return count,text
    else:
        return count


# In[ ]:


def apostropheError(text,nlp,correctFlag=False):
    '''
    Purpose: To check for apostophe errors. 
             Additionally, it returns corrected sentence.
             
    Parameters: text: string
                    A string of text-single or a paragraph.
                    
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''    
    doc = nlp(text)
    count=0
    text=""
    suffixList=["m","re","s","nt","ll","ve","d"]
    for s in doc.sentences:
        for i in range(len(s.words)):
            if i<(len(s.words)-1) and s.words[i].xpos in ['NN','NNS','NNP','NNPS']:
                if s.words[i].text[-1]=='s':
                    if s.words[i+1].xpos in ['NN','NNS','NNP','NNPS']:
                        status=handleCompoundErrors(s.words[i].text,s.words[i+1].text)
                        if status==True:
                            text+=s.words[i].text+" "
                        else:
                            count+=1
                            text+=s.words[i].text
                            text+="' "
                    else:
                        text+=s.words[i].text
                        text+=" "
                else:
                    if s.words[i+1].xpos in ['NN','NNS','NNP','NNPS']:
                        status=handleCompoundErrors(s.words[i].text,s.words[i+1].text)
                        if status==True:
                            text+=s.words[i].text+" "
                        else:
                            count+=1
                            text+=s.words[i].text
                            text+="'s "
                    else:
                        text+=s.words[i].text
                        text+=" "
            elif s.words[i].text in suffixList:
                if s.words[i].text[0]!="'":
                    count+=1
                    text+="'"+s.words[i].text+" "
                else:
                    text+=s.words[i].text+" "
            else:
                text+=s.words[i].text+" "
                text+=" "
    if correctFlag==True:
        return count,text
    else:
        return count


# In[ ]:


def SubVerbAgreementError(text,nlp,correctFlag=False):
    '''
    Purpose: To check for errors due to subject-verb agreement error. 
             Additionally, it returns corrected sentence.
             
    Parameters: text: string
                    A string of text-single or a paragraph.
                    
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''
    doc = nlp(text)
    count=0
    text=""
    for s in doc.sentences:
        for i in range(len(s.words)):
            try:
                if s.words[i].xpos=='NN' or s.words[i].xpos=='NNP':
                    if (i!=len(s.words)-1) and (s.words[i+1].xpos in ['VB','VBP','VBG']):
                        verbLemma=s.words[i+1].lemma
                        v=conjugate(verbLemma, tense = "present",person = 3, number = "singular", mood = "indicative",aspect = "imperfective",negated = False)
                        text+=s.words[i].text+" "
                        if s.words[i+1].text!=v:
                            count+=1
                            s.words[i+1].text=v
                        text+=" "
                    else:
                        text+=s.words[i].text
                        text+=" "
                elif (i!=len(s.words)-1) and (s.words[i].xpos=='NNS' or s.words[i].xpos=='NNPS'):
                    if s.words[i+1].xpos in ['VBG','VBZ']:
                        verbLemma=s.words[i+1].lemma
                        v=conjugate(verbLemma, tense = "present",person = 3, number = "plural", mood = "indicative",aspect = "imperfective",negated = False)
                        text+=s.words[i].text+" "
                        if s.words[i+1].text!=v:
                            count+=1
                            s.words[i+1].text=v
                        text+=" "
                    else:
                        text+=s.words[i].text
                        text+=" "
                elif (i!=len(s.words)-1) and s.words[i].xpos=='PRP':
                    if s.words[i].text=='I':
                        if s.words[i+1].xpos in ['VBZ','VBN','VBG']:
                            
                            verbLemma=s.words[i+1].lemma
                            v=conjugate(verbLemma, tense = "present",person = 1, number = "singular", mood = "indicative",aspect = "imperfective",negated = False)
                            text+=s.words[i].text+" "
                            if s.words[i+1].text!=v:
                                count+=1
                                s.words[i+1].text=v
                            text+=" "
                        else:
                            text+=s.words[i].text
                            text+=" "
                    elif s.words[i].text.lower() in ['he','she','it']:
                        if s.words[i+1].xpos in ['VBP','VB','VBN','VBG']:
                            
                            verbLemma=s.words[i+1].lemma
                            v=conjugate(verbLemma, tense = "present",person = 3, number = "singular", mood = "indicative",aspect = "imperfective",negated = False)
                            text+=s.words[i].text+" "
                            if s.words[i+1].text!=v:
                                count+=1
                                s.words[i+1].text=v
                            text+=" "
                        else:
                            text+=s.words[i].text
                            text+=" "
                    elif s.words[i].text.lower() in ['we','they','you']:
                        if s.words[i+1].xpos not in ['VB','VBP']:
                            
                            verbLemma=s.words[i+1].lemma
                            v=conjugate(verbLemma, tense = "present",person = 3, number = "plural", mood = "indicative",aspect = "imperfective",negated = False)
                            text+=s.words[i].text+" "
                            if s.words[i+1].text!=v:
                                count+=1
                                s.words[i+1].text=v
                            text+=" "
                        else:
                            text+=s.words[i].text
                            text+=" "
                    else:
                        text+=s.words[i].text
                        text+=" "
                else:
                    text+=s.words[i].text
                    text+=" "
            except:
                text+=s.words[i].text
                text+=" "
    if correctFlag==True:
        return count,text
    else:
        return count


# In[ ]:


def pluralizationError(text,nlp,correctFlag=False):
    '''
    Purpose: To check for pluralization error. 
             Additionally, it returns corrected sentence.
             
    Parameters: text: string
                    A string of text-single or a paragraph.
                    
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''    
    
    doc = nlp(text)
    count=0
    text=""
    for s in doc.sentences:
        for i in range(len(s.words)):
            if (i!=len(s.words)-1) and (s.words[i].xpos=="NN" or s.words[i].xpos=="NNP"):
                if s.words[i+1].xpos in ["VB","VBP"]:
                    count+=1
                    text+=pluralize(s.words[i].text)+" "
                else:
                    text+=s.words[i].text+" "
            elif (i!=len(s.words)-1) and (s.words[i].xpos=="NNS" or s.words[i].xpos=="NNPS"):
                if s.words[i+1].xpos=="VBZ":
                    text+=singularize(s.words[i].text)+" "
                else:
                    text+=s.words[i].text+" "
            elif  (i!=len(s.words)-1) and s.words[i].xpos=="CD":
                if s.words[i].text=="1" or s.words[i].text=="one":
                    if s.words[i+1].xpos=="NNS" or s.words[i+1].xpos=="NNPS":
                        count+=1
                        s.words[i+1].text=singularize(s.words[i+1].text)
                        text+=s.words[i].text+" "
                else:
                    if s.words[i+1].xpos=="NN" or s.words[i+1].xpos=="NNP":
                        count+=1
                        s.words[i+1].text=pluralize(s.words[i+1].text)
                        text+=s.words[i].text+" "
            else:
                    text+=s.words[i].text+" "
    if correctFlag==True:
        return count,text
    else:
        return count


# In[ ]:


def handleCompoundErrors(w1,w2):
    '''
    Purpose: Helper function: Check if the words make a compound word together.
             
    Parameters: w1: string
                w2: string
                    
    Returns: booolean
                if True, it is a compound words, else not a compound words.
    '''    
    path="/home/manraj/benesse/data/compunds.txt"
    text=read_file(path)
    compounds=[]
    for t in text:
        tokens=word_tokenize(t)
        word=tokens[0]+" "
        if tokens[1][-3:]=="was":
            word+=tokens[1][:-3]
        else:
            word+=tokens[1]
        compounds.append(word)
    w=w1+" "+w2
    if w in compounds:
        return True
    else:
        return False


# In[ ]:


def TenseError(text,nlp,correctFlag=False):
    '''
    Purpose: To check if text has tense errors. 
             Additionally, it returns corrected sentence.
             
    Parameters: text: string
                    A string of text-single or a paragraph.
                    
                correctFlag:boolean 
                   True or False
                    
    Returns: count: integer  
             text: Corrected sentence. (If correctFlag is True)
    '''    
    doc = nlp(text)
    count=0
    text=""
    for s in doc.sentences:
        dic={"VB":0,"VBP":0,"VBD":0,"VBZ":0,"VBN":0,"VBG":0,"MD":0}
        for i in range(len(s.words)):
            try:
                if s.words[i].xpos in ["MD"]:
                    if (i<len(s.words)-1) and (s.words[i+1].xpos in ["VBZ",'VBP','VBN','VBG','VBD']):
                        if s.words[i+1].text!=s.words[i+1].lemma:
                            s.words[i+1].text=s.words[i+1].lemma
                            count+=1
                        dic["VB"]+=1
                        dic["MD"]+=1
                    if i<len(s.words)-2 and s.words[i+1].text=="be" and (s.words[i+2].xpos in ["VB","VBP","VBZ","VBD"]):
                        v=s.words[i+2].lemma
                        vp=conjugate(v,"part")
                        if vp!=s.words[i+2].text:
                            s.words[i+2].text=vp
                            count+=1
                        dic["VBG"]+=1
                        dic["MD"]+=1
                    elif i<len(s.words)-2 and (s.words[i+1].xpos in ["VB","VBP"]) and (s.words[i+2].xpos in ["VB","VBP","VBZ","VBD","VBG"]):
                        
                        v=s.words[i+2].lemma
                        vp=conjugate(v,"ppart")
                        if vp!=s.words[i+2].text:
                            s.words[i+2].text=vp
                            count+=1
                        dic["VBN"]+=1
                        dic["MD"]+=1
                    text+=s.words[i].text+" "
                elif i<len(s.words)-1 and s.words[i].xpos=="VBD":
                    if s.words[i].text=="had" and s.words[i+1].xpos!="VBN":
                        v=s.words[i+1].lemma
                        vp=conjugate(v,"ppart")
                        if vp!=s.words[i+1].text:
                            s.words[i+1].text=vp
                            count+=1
                        dic["VBD"]+=1
                        dic["VBN"]+=1
                        text+=s.words[i].text+" "
                    elif s.words[i+1].xpos in ["VB","VBP","VBZ","VBD","VBN"]:
                        v=s.words[i+1].lemma
                        vp=conjugate(v,"part")
                        if vp!=s.words[i+1].text:
                            s.words[i+1].text=vp
                            count+=1
                        dic["VBD"]+=1
                        dic["VBG"]+=1
                        text+=s.words[i].text+" "
                    else:
                        text+=s.words[i].text+" "
                elif s.words[i].xpos in ["VB","VBP","VBZ"]:
                    if i<(len(s.words)-1) and (s.words[i].text in ["has","have"]) and (s.words[i+1].xpos in ["VBZ","VBD","VB","VBP","VBG"]):
                        
                        v=s.words[i+1].lemma
                        vp=conjugate(v,"ppart")
                        if vp!=s.words[i+1].text:
                            s.words[i+1].text=vp
                            count+=1
                        dic["VBN"]+=1
                        text+=s.words[i].text+" "
                    elif i<(len(s.words)-1) and (s.words[i].text in ["is","am","are"]) and (s.words[i+1].xpos in ["VBZ","VBD","VB","VBP"]):
                        
                        v=s.words[i+1].lemma
                        vp=conjugate(v,"part")
                        if vp!=s.words[i+1].text:
                            s.words[i+1].text=vp
                            count+=1
                        dic["VBG"]+=1
                        text+=s.words[i].text+" "
                    else:
                        text+=s.words[i].text+" "
                else:
                    text+=s.words[i].text+" "
            except:
                text+=s.words[i].text+" "
    if correctFlag==True:
        return count,text
    else:
        return count                  


# In[ ]:


def grammar_correction(text):

    count=0
    c,t=CapitalizeError(text,nlp,True)
    count+=c

    c,t=checkSpellingError(t,nlp,True)
    count+=c

    c,t=articleError(t,nlp,True)
    count+=c

    c,t=becauseError(t,nlp,True)
    count+=c

    c,t=SubVerbAgreementError(t,nlp,True)
    count+=c

    c,t=pluralizationError(t,nlp,True)
    count+=c

    c,t=TenseError(t,nlp,True)
    count+=c
    
    seq1 = word_tokenize(text)
    seq2 = word_tokenize(t)
    dist, errors = edit_distance(seq1,seq2,text,t)

    return_json={
    "text":None,
    "errors":[{
        "offset":None,
        "length":None,
        "error_code":None,
        "error_category":None,
        "description":None,
        "correction":None
    },{
        "offset":None,
        "length":None,
        "error_code":None,
        "error_category":None,
        "description":None,
        "correction":None
    }],
    "exceptions":[],
    "correction":None
    }
    return_json["errors"]=errors
    return_json["text"]=text
    return_json["correction"]=t

    return return_json


# In[74]:


import numpy as np

def edit_distance(seq1, seq2, s1, s2):
    '''
    Edit Distance Assumptions:
    Cost of addition - 1
    Cost of deletion - 1
    Cost of substitution - 1
    
    Parameters:
    seq1 - word sequence of input sentence
    seq2 - word sequence of corrected sentence
    s1 - input sentence string
    s2 - correct sentence string
    
    Returns:
    1. Edit Distance
    2. List of errors ( each error in the form of a dictionary)
    
    '''
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    bp = np.zeros((size_x,size_y,2))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y
    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
                if matrix[x,y] == matrix[x-1,y] + 1:
                    bp[x,y,0] = x-1
                    bp[x,y,1] = y
                elif matrix[x,y] == matrix[x,y-1] + 1:
                    bp[x,y,0] = x
                    bp[x,y,1] = y-1
                else:
                    bp[x,y,0] = x-1
                    bp[x,y,1] = y-1
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
                if matrix[x,y] == matrix[x-1,y] + 1:
                    bp[x,y,0] = x-1
                    bp[x,y,1] = y
                elif matrix[x,y] == matrix[x,y-1] + 1:
                    bp[x,y,0] = x
                    bp[x,y,1] = y-1
                else:
                    bp[x,y,0] = x-1
                    bp[x,y,1] = y-1
                    
    #print (matrix)
    fx = int(size_x - 1)
    fy = int(size_y - 1)
    errors = []
    while(fx != 0 or fy != 0):
        nx = int(bp[fx,fy,0])
        ny = int(bp[fx,fy,1])
        
        if (nx == fx - 1) and (ny == fy - 1):
            
            if seq1[nx] != seq2[ny]:
                d = {}
                d['error code'] = "Grammar Error"
                d['description'] = "Word statrting at index {offset} needs to be substituted"
                d['operation_required'] = "Substitution"
                d['correction'] = [seq1[nx],seq2[ny]]
                d['length'] = len(seq1[nx])
                d['offset'] = s1.index(seq1[nx])
                #print(d)
                errors.append(d)
                #print('\n')
                
        elif (nx == fx) and (ny == fy - 1):
            d = {}
            d['error code'] = "Grammar Error"
            d['description'] = "Word need to be inserted in the first white space after {offset}"
            d['operation_required'] = "Add"
            d['correction'] = seq2[ny]
            d['length'] = len(s1[s1.index(seq1[nx-1]):s1.index(seq1[nx])])+len(seq1[nx]) #TODO
            d['offset'] = s1.index(seq1[nx-1])
            #print(d)
            errors.append(d)
            #print('\n')
            
        elif (nx == fx - 1) and (ny == fy):
            d = {}
            d['error code'] = "Grammar Error"
            d['description'] = "Word starting at index {offset} needs to be deleted"
            d['operation_required'] = "Delete"
            d['correction'] = seq1[nx]
            d['length'] = len(seq1[nx])
            d['offset'] = s1.index(seq1[nx])
            #print(d)
            errors.append(d)
            #print('\n')
            
        fx = nx
        fy = ny
    return (matrix[size_x - 1, size_y - 1],errors)

'''
For testing- 

s1 = "Teacher teach student."
s2 = "Teachers teach students."
seq1 = word_tokenize(s1)
seq2 = word_tokenize(s2)
dist, errors = edit_distance(seq1,seq2,s1,s2)
print("Edit Distance", dist)
print("No of errors", len(errors))
'''


# In[ ]:


if __name__=="__main__":
    test_file_path="/home/manraj/benesse/data/test_data.txt"
    text=read_file(test_file_path)
    for t in text:
        pprint(grammar_correction(t))

#!/usr/bin/env python
# coding: utf-8

from spellchecker import SpellChecker
import codecs

import re
# >>> strs = """text:u'MUC-EC-099_SC-Memory-01_TC-25'
# text:u'MUC-EC-099_SC-Memory-01_TC-26'
# text:u'MUC-EC-099_SC-Memory-01_TC-27'"""
# >>> re.findall(r"'(.*?)'", strs, re.DOTALL)
# ['MUC-EC-099_SC-Memory-01_TC-25',
#  'MUC-EC-099_SC-Memory-01_TC-26',
#  'MUC-EC-099_SC-Memory-01_TC-27'
# ]



def get_raw_io(raw_files_in):
    #returns list of raw input files and corresponding raw output files
    raw_files_out = []
    cnt_files = []
    for i in range(len(raw_files_in)):
        fname = raw_files_in[i]
        fname_cnt = raw_base+"cnt_"+fname        
        fname_out = raw_base+"spell_"+fname

        raw_files_in[i] = raw_base+raw_files_in[i]
        raw_files_out.append(fname_out)
        cnt_files.append(fname_cnt)
        
    return raw_files_in,raw_files_out,cnt_files
    
    
def correction(word):
    #returns corrected word
    global cnt
    if word.isupper() or not word.isalpha() or (len(spell.known([word]))>0):
        new_word = word
    else:
        if(word[0]in ["'","`"]):
            i =0 #first alpha char
            j  =0 #last alpha char            
            while(not word[i].isalpha()):
                i+=1
            j = i
            while(word[j].isalpha()):
                j+=1
            new_word = word[:i]+spell.correction(word[i:j])+word[j+1:]
        else:
            new_word = spell.correction(word)
    if(new_word!=word):
        cnt+=1
        cur_line =  str(cnt)+" "+word+" -> "+new_word+"\n"
        write_file(cnt_file,[cur_line],mode='a')
        print(cur_line)
    return new_word

def split_string(string): 
  
    # Split the string based on space delimiter 
    list_string = string.split(' ') 
    return list_string

  
def join_string(list_string): 
    # Join the string based on '-' delimiter 
    string = ' '.join(list_string)
    return string 

def correct_line(line,raw = False):
    list_string = split_string(line)
    list_string[-1] = list_string[-1].strip()
    corrected_list = [correction(x) for x in list_string]
#     if(not raw):
    corrected_list.append("\n")
    line = join_string(corrected_list)
    return line


    
    
def read_file(file):
    fp=codecs.open(file,"r",encoding='utf8',errors='ignore')
    text=fp.readlines()
    return text

def write_file(file,lines,mode = 'w'):
    f = open(file, mode)
    f.writelines(lines)
    f.close()    
    
def is_annot(line):
    line_string = split_string(line)
    if(len(line_string)>=3):
        if(line_string[0]=='A' and line_string[1].isnumeric()):
             return True
    return False
        


# In[149]:
def correct_annot(annot_file_in,annot_file_out):
    #corrects files with annotations
    lines = read_file(annot_file_in)
    new_lines = []
    i =0
    for line in lines[:10]:
        i+=1
        if(i%50==0):
            print("Index: ",i)
#             print(line)
        if is_annot(line) or (not line.strip()):
            #don't correct
            pass
        else:
            line = correct_line(line)
        new_lines.append(line)

    write_file(annot_file_out,new_lines)
    
    
def correct_annot_to_raw(annot_file_in,annot_file_out):
    #corrects files with annotations
    lines = read_file(annot_file_in)
    new_lines = []
    i =0
    for line in lines:
        i+=1
#         print(type(line),"Line:",line)
        if(i%25==0):
            print("Index: ",i)
#             print(line)
        if is_annot(line) or (not line.strip()):
            #don't correct
#             pass
            continue
        else:
            if(line[0]=='S'):
                line = line[2:]
#             print("line_now",line)
            line = correct_line(line)
        new_lines.append(line)

    write_file(annot_file_out,new_lines)    

    
def annot_to_raw(annot_file_in,annot_file_out):
    #corrects files with annotations
    lines = read_file(annot_file_in)
    new_lines = []
    i =0
    for line in lines:
        i+=1
#         print(type(line),"Line:",line)
        if(i%25==0):
            print("Index: ",i)
#             print(line)
        if is_annot(line) or (not line.strip()):
            #don't correct
#             pass
            continue
        else:
            if(line[0]=='S'):
                line = line[2:]
#             print("line_now",line)
#             line = correct_line(line)
        new_lines.append(line)
    write_file(annot_file_out,new_lines)    
    

# In[112]:


# In[ ]:

def correct_raw(raw_file_in,raw_file_out):
    #for raw file
    lines = read_file(raw_file_in)
    new_lines = []
    i =0
    for line in lines:
        i+=1
        if(i%50==0):
            print("Index: ",i)
            print(line)
        line = correct_line(line,raw = True)
        new_lines.append(line)

    write_file(raw_file_out,new_lines)


if __name__ == '__main__':
    dict_path = "/media/nas_mount/Rohan/out_latest/out/data_raw/dict.src.txt"
    #files having sentences with annotations
    annot_file_in = "/home/rohan/tejas/fairseq-gec_copy/data/test.m2"
#     annot_file_in = "/home/rohan/tejas/fairseq-gec_copy/data/sample.m2"    
    annot_file_out = "/home/rohan/tejas/fairseq-gec_copy/data/pyspell_test.m2"
    raw_file_out = "/media/nas_mount/Rohan/out_latest/out/data_raw/pyspell_raw_connl.txt" 
    cnt_file = "/home/rohan/tejas/fairseq-gec_copy/cnt_pyspell.txt"    
    raw_file_connl = "/media/nas_mount/Rohan/out_latest/out/data_raw/connl_raw.txt"
    
    #files having sentences without annotations
    #Conll
#     raw_file_in = "/media/nas_mount/Rohan/out_latest/out/data_raw/test.src-tgt.src.old" 
#     raw_file_out = "/media/nas_mount/Rohan/out_latest/out/data_raw/spell_raw_connl.txt" 
    
    #Benesse
    #the input file for raw sentences
    
    '''
    
    raw_file_in = "/media/nas_mount/Rohan/out_latest/out/data_raw/combined_raw.txt" 
    #the output file for raw sentences post spell correction    
    raw_file_out = "/media/nas_mount/Rohan/out_latest/out/data_raw/spell_raw_ben_30.txt" 
    
#     cnt_file = "/home/rohan/tejas/fairseq-gec_copy/cnt__ben_file.txt"

#   The file for logging the corrections made
    cnt_file = "/home/rohan/tejas/fairseq-gec_copy/cnt_ben_para.txt"
    
    

    
    '''
    
#     raw_base = "/media/nas_mount/Rohan/out_latest/out/data_raw/"
#     raw_files_in = ["train_merge.src","valid.src"]
#     raw_files_in, raw_files_out,cnt_files = get_raw_io(raw_files_in)    
    
#     print("Input files",raw_files_in,"\n","Output files",raw_files_out,"\n","Cnt_files",cnt_files,"\n")

    #Initializing Spell Checker Object
#     f = open(cnt_file,'w')#erasing data in cnt_file
#     f.close()                               
    
    cnt = 0            
    spell = SpellChecker()
    spell.word_frequency.load_text_file(dict_path)
    spell.word_frequency.load_words(["'s","n't","'ll","'m","'re","'ve","'d","'t","'all","``","''","'"])
    word = "''potential"
#     print("Word is",word)
#     new_word = word
#     new_word = spell.candidates(word)    
#     print(spell.known([word[:2]]))
#     print(new_word)
#     correct_annot_to_raw(annot_file_in,raw_file_out)
    annot_to_raw(annot_file_in,raw_file_connl)
    '''
    for i in range(len(raw_files_in)):

        cnt = 0        
        raw_file_in = raw_files_in[i]
        raw_file_out = raw_files_out[i]
        cnt_file = cnt_files[i]

        f = open(cnt_file,'w')#erasing data in cnt_file
        f.close()                           
        
        
        cur_line = "Raw correction begins for "+raw_file_in+"\n"
        print(cur_line)
                   
        write_file(cnt_file,[cur_line],mode='a')    

        correct_raw(raw_file_in,raw_file_out)

        cur_line = "Raw correction ends for "+raw_file_in+"\n"
        print(cur_line)
        
        write_file(cnt_file,[cur_line],mode='a')

    #     cur_line = "Annot correction begins\n"
    #     print(cur_line)
    #     write_file(cnt_file,[cur_line],mode='a')        

    #     cnt = 0
    #     correct_annot(annot_file_in,annot_file_out)
        print("Count of corrections: ",cnt,"\n")
    '''
    

#!/usr/bin/env python
# coding: utf-8

from spellchecker import SpellChecker
import codecs
from hunspell import Hunspell

def get_correct(word,spellchecker):
    if(spellchecker.spell(word)):
        return word
    suggestions = spellchecker.suggest(word)
    if len(suggestions)>0:
        return suggestions[0]
    else:
        return word
    
def correction(word,spellchecker):
    #returns corrected word
#     global cnt
    if word.isupper() or not word.isalpha() or spellchecker.spell(word):
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
            new_word = word[:i]+get_correct(word[i:j],spellchecker)+word[j+1:]
        else:
            new_word = get_correct(word,spellchecker)
    return new_word

def split_string(string): 
  
    # Split the string based on space delimiter 
    list_string = string.split(' ') 
    return list_string

  
def join_string(list_string): 
    # Join the string based on '-' delimiter 
    string = ' '.join(list_string)
    return string 

def correct_line(line,spellchecker,raw = False):
    list_string = split_string(line)
    list_string[-1] = list_string[-1].strip()
    corrected_list = [correction(x,spellchecker) for x in list_string]
#     if(not raw):
    corrected_list.append("\n")
    line = join_string(corrected_list)
    return line


def read_dict(dict_file,spellchecker):    
    lines = read_file(dict_file)
    i =0
    for line in lines:
        list_string = split_string(line)    
        word = list_string[0]
#         print(word)
        try:
            spellchecker.add(word)
        except:
            pass
    
    
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

def getSpellChecker():
    dict_path = "/media/nas_mount/Rohan/out_latest/out/data_raw/dict.src.txt"
    spellchecker = Hunspell('en_GB')
    known_words = ["'s","n't","'ll","'m","'re","'ve","'d","'t","'all","``","''","'"]
    for word in known_words:
        spellchecker.add(word)
    read_dict(dict_path,spellchecker)
    return spellchecker

def correct_sentence(line,spellchecker):
    return correct_line(line,spellchecker)

if __name__ == '__main__':
#     sent = " Secondly , annouance the potential risk would cause the family member to be scared of this certain issue , although the factor would not be that serious , people would still fear that they would have some potential disease in the future thus go to hospital and do additional check or take more medicine in order to prevent the disease , and this creats unnecessary costs to the family ."
    sent = "Brad Obbama is a great actor" 
    print(sent)
    print("Spell Corrected")
    spellchecker = getSpellChecker()
    print(correct_sentence(sent,spellchecker))
    


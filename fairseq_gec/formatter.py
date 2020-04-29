import numpy as np
import codecs
from nltk.tokenize import word_tokenize

import nltk
nltk.download('punkt')


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
            if nx < len(seq1):
                d['length'] = len(s1[s1.index(seq1[nx-1]):s1.index(seq1[nx])])+len(seq1[nx])
            else:
                d['length'] = len(s1[s1.index(seq1[nx-1]):])
            #d['length'] = len(s1[s1.index(seq1[nx-1]):s1.index(seq1[nx])])+len(seq1[nx]) #TODO
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

def grammar_correction(text,t):
    '''
    Purpose: 
    The function returns the output json format for the input sentence after obtaining 
    the correction for it from the model
    
    text - input sentence
    t - corrected sentence obtained from model
    '''
    #t = model_output(text) 
    
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




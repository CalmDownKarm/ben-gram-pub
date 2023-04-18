from interactive_copy import getModel, runInference
from hunspell_custom import getSpellChecker,correct_sentence
from fmtout import grammar_correction_json
import json
import re

def grammar_correction(input_sentences):
    sentence = re.sub('\\n|<\s?\w+>?\s?|<unw>|<unc>|<|>|\\r|\r', '', input_sentences)
    try:
        corrections = runInference(reqs,spellchecker,sentences = [[sentence]])
        json_obj = grammar_correction_json(input_sentences, corrections)
    except Exception:
        return json.dumps({})
    return json_obj

if __name__ == "__main__":
    reqs = getModel() #wraps models, generator, task, and relevant args
    spellchecker = getSpellChecker() #returns Hunspell spellchecker
    input_sentence = 'He did played all night'
    print(grammar_correction(input_sentence))
    # corrections = runInference(reqs,spellchecker,sentences = [[input_sentence]])
    # print grammar_correction(input_sentence, corrections)

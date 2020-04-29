from interactive_copy import getModel, runInference
from hunspell_custom import getSpellChecker,correct_sentence
from formatter import grammar_correction


def run_corrections(input_sentences):
    corrections = runInference(reqs,spellchecker,sentences = [[input_sentence]])
    json_obj = grammar_correction(input_sentence, corrections)
    print(json_obj)
    return json_obj

if __name__ == "__main__":
    reqs = getModel() #wraps models, generator, task, and relevant args
    spellchecker = getSpellChecker() #returns Hunspell spellchecker
    input_sentence = 'He did played all night'
    run_corrections(input_sentence)
    # corrections = runInference(reqs,spellchecker,sentences = [[input_sentence]])
    # print grammar_correction(input_sentence, corrections)

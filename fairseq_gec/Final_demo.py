from interactive_copy import getModel, runInference
from hunspell_custom import getSpellChecker,correct_sentence


if __name__ == "__main__":
    reqs = getModel() #wraps models, generator, task, and relevant args
    spellchecker = getSpellChecker() #returns Hunspell spellchecker
    
    corrections = runInference(reqs,spellchecker,sentences = [['He did played all night.']])
    print(corrections)

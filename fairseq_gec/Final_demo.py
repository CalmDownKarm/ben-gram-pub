from interactive_copy import getModel, runInference
from hunspell_custom import getSpellChecker,correct_sentence


if __name__ == "__main__":
    reqs = getModel() #wraps models, generator, task, and relevant args
    spellchecker = getSpellChecker() #returns Hunspell spellchecker
    
    custom_sent = "In conclusion,the state should have passed a legal bill to measure and provide information to doctors that till which extend should a doctor opt to reveal to relatives members about the genetic disease and in which situations it is open to patient 's decision.In addition,the state could also encourage to create assistance schemes to aid necessary help to needy patients to encourage them to open up for the benefit of own and family members."
    
    corrections = runInference(reqs,spellchecker,sentences = [[custom_sent]])
    print(corrections)

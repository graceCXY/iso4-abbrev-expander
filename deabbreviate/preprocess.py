import numpy as np
import re 


def clean_word(word):
    word = re.sub("\(", "", word)
    word = re.sub("\)", "", word)
    word = re.sub(",", "", word)
    return word

def get_journal_lst(journal):
    if journal == "" or journal == np.nan:
        return ""
    
    journal_new = re.sub(r"[!?&*+=|,]", "", journal)
    if ":" in journal_new and journal_new.find(":") < journal_new.find("("):
        before_colon = journal_new.split(":")[0]
        brackets = ""
        if "(" in journal_new and ")" in journal_new:
            brackets = journal_new[journal_new.find("("):journal_new.find(")")+1]
        journal_new = before_colon + " " + brackets
    
    journal_lst = journal_new.split(" ")
    result = []
    for item in journal_lst:
        if item != "":
            result.append(clean_word(item.strip()))

    return result

### Test Functions
# get_journal_lst("J. Earthq. Eng.")
# import numpy as np
# import pandas as pd
import re
# import ast 
import requests
from textblob import TextBlob
import nltk
nltk.download('wordnet')
from nltk import word_tokenize, pos_tag

from fuzzywuzzy import fuzz

from load_iso4_mappings import ltwa_df_with_abbrev, stopwords
from load_freq_models import dataset_abbrev_freq
from load_ngram_models import model_bi_forward, model_bi_backward
from preprocess import get_journal_lst


### TODO: learn more about language code conversions
language_code_2d_3d = {"en":"eng", "tr":"tur", "fr": "fre" , "sv":"swe", "ru":"rus", "et":"est", "no":"nor", 
                       "lv":"lat", "cs":"cze", "pt":"por", "mt":"mlt", "sq":"alb", "es":"spa", "de":"ger", 
                       "uk":"ukr", "is":"ice", "ka":"geo", "cy":"wel", "pl": "pol", "id":"ind", "da":"dan", 
                       "az":"aze", "bg":"bul", "ca":"cat", "nl":"dut", "af":"afr", "eu":"baq", "yi":"yid", 
                       "it":"ita", "hu":"hun", "fi":"fin", "sl":"slv", "sk":"slo", "ms":"may", "mk":"mac", "lt":"lit"}

def get_language(s):
    b = TextBlob(s)
    lang = b.detect_language()
    if lang in list(language_code_2d_3d.keys()):
        return language_code_2d_3d[lang]
    return ""


def languages_contain_lang(languages, lang):
    if type(languages) == str:
        if languages == "mul": # multiple
            return True
        if lang == languages:
            return True
    elif type(languages) == list:
        return lang in languages
    return False


def get_iso4_df_for_lang(lang):
    bools = ltwa_df_with_abbrev.apply(lambda x: languages_contain_lang(x["lang"], lang), axis = 1)
    return ltwa_df_with_abbrev[bools]


def get_iso4_expansions_for_word(word, lang):
    if "." in word: # it is an abbreviation
        lang_df = get_iso4_df_for_lang(lang)
        df = lang_df[(lang_df["abbrev"] == word)]
        if df.empty:
            return word
        elif df.shape[0] == 1:
            return df.iloc[0]["full"]
        else:
            return df["full"].tolist()
    else: # it is not an abbreviation
        return word


def get_raw_iso4_expansions(journal_lst, lang):
    raw_expansions = []
    for word in journal_lst:
        
        # special case with hyphenated word
        if "-" in word:
            w_lst = word.split("-")
            w_new = ""
            for w in w_lst:
                w_new += "|" + str(get_iso4_expansions_for_word(w.lower(), lang))
            raw_expansions.append(w_new[1:])
            continue
        
        # regular case 
        iso4_expansions = get_iso4_expansions_for_word(word.lower(), lang)
        raw_expansions.append(iso4_expansions)
    return raw_expansions


def get_most_freq_for_word(word):
    df = dataset_abbrev_freq[dataset_abbrev_freq["abbrev"] == word]
    if df.empty:
        return word
    elif df.shape[0] == 1:
        return df.iloc[0]["most_freq"]
    else:
        return df["most_freq"].tolist()

def get_most_frequent_expansions(journal_lst):
    mf_expansions = []
    for word in journal_lst:
        
        # special case with hyphenated word
        if "-" in word:
            w_lst = word.split("-")
            w_new = ""
            for w in w_lst:
                w_new += "|" + str(get_most_freq_for_word(w.lower()))
            mf_expansions.append(w_new[1:])
            continue
        
        # regular case
        curr_mf = get_most_freq_for_word(word.lower())
        mf_expansions.append(curr_mf)
    return mf_expansions


def get_frequency_for_word(abbrev, full):
    frequencies = get_frequencies_for_word(abbrev)
    if frequencies == abbrev:
        return 0
    elif type(frequencies) == dict:
        if full in frequencies.keys():
            return frequencies[full]
    elif type(frequencies) == list:
        for freq in frequencies:
            if full in freq.keys():
                return freq[full]
    return 0


def match_raw_iso4_most_freq_word(curr_raw, curr_mf, curr_abbrev):
    # correct if iso4 is the most frequent
    if curr_raw == curr_mf:
        return curr_raw

    # correct if iso4 is substring of most frequent (ex. iso4's europ- for mf's european)
    if "-" in curr_raw:
        if curr_raw.split("-")[0] in curr_mf:
            return curr_mf
        if re.sub(r"\.", "", curr_mf) in curr_raw.split("-")[0]:
            return curr_raw.split("-")[0]

    # correct if most frequent word has frequency > 80%
    if get_frequency_for_word(curr_abbrev.lower(), curr_mf) > 0.8:
        return curr_mf

    # correct if most frequent word is abbreviation format and substring raw expansion
    if "." in curr_mf:
        if curr_mf.split(".")[0] == curr_raw[:len(curr_mf)-1]:
            return curr_raw
        
    if "." in curr_raw:
        if curr_raw.split(".")[0] == curr_mf[:len(curr_raw)-1]:
            return curr_mf
        
    return ""


def verify_raw_iso4_most_freq_lst(journal_lst, raw_expansion, mf_expansion):
    verification_lst = []
    for i in range(len(journal_lst)):
        curr_abbrev = journal_lst[i].lower()
        curr_raw = raw_expansion[i]
        curr_mf = mf_expansion[i]
        
        # keep non abbreviations the way they are
        if "." not in curr_abbrev:
            verification_lst.append(curr_abbrev)
            continue
        
        # special case with hyphenated word
        if "|" in curr_raw and "|" in curr_mf:
            raw_lst = curr_raw.split("|")
            mf_lst = curr_mf.split("|")
            w_new = ""
            for i in range(len(raw_lst)):
                if "[" in raw_lst[i] or "]" in raw_lst[i]:
                    options_for_i = ast.literal_eval(raw_lst[i])
                    opt = ""
                    for o in options_for_i:
                        tmp = match_raw_iso4_most_freq_word(o, mf_lst[i], curr_abbrev)
                        if tmp:
                            opt = tmp
                    w_new += "|" + opt
                else:
                    w_new += "|" + match_raw_iso4_most_freq_word(raw_lst[i], mf_lst[i], curr_abbrev)
            verification_lst.append(re.sub(r"\|", "-", w_new[1:]))
            continue
        
        if type(curr_raw) == str:
#             print(curr_abbrev, curr_mf, get_frequency_for_word(curr_abbrev.lower(), curr_mf))
            word_to_add = match_raw_iso4_most_freq_word(curr_raw, curr_mf, curr_abbrev)
            if word_to_add != "":
                verification_lst.append(word_to_add)
            else:
                if "-" in curr_raw:
                    verification_lst.append(curr_raw.split("-")[0])
                
                elif fuzz.ratio(curr_raw, curr_mf) > 90:
                    verification_lst.append(curr_raw)
                
            continue
            
                    
        elif type(curr_raw) == list:
            verified_word = ""
            for elem in curr_raw:
                
                word_to_add = match_raw_iso4_most_freq_word(elem, curr_mf, curr_abbrev)
                if word_to_add != "":
                    verified_word = word_to_add
                else:
                    if "-" in curr_raw:
                        verified_word = curr_raw.split("-")[0]
                    elif fuzz.ratio(curr_raw, curr_mf) > 95:
                        verified_word = curr_raw
                    
            verification_lst.append(verified_word)
            continue
                
        verification_lst.append("")
    return verification_lst


def abbreviate_journal_name(journal):
    url = "https://abbreviso.toolforge.org/a/" + journal
    request = requests.get(url)
    if request.status_code != 200:
        return journal
    return request.text


def get_frequencies_for_word(word):
    df = dataset_abbrev_freq[dataset_abbrev_freq["abbrev"] == word]
    if df.empty:
        return word
    elif df.shape[0] == 1:
        return df.iloc[0]["freq"]
    else:
        return df["freq"].tolist()


def get_frequencies_expansions(journal_lst):
    freq_expansions = []
    for word in journal_lst:
        
        # special case with hyphenated word
        if "-" in word:
            w_lst = word.split("-")
            w_new = ""
            for w in w_lst:
                w_new += "|" + str(get_frequencies_for_word(w.lower()))
            freq_expansions.append(w_new[1:])
            continue
        
        # regular case
        curr_mf = get_frequencies_for_word(word.lower())
        freq_expansions.append(curr_mf)
    return freq_expansions


def get_pos_tag_for_word(word):
    text = word_tokenize(word)
    pos_lst = nltk.pos_tag(text)
    if len(pos_lst) >= 1:
        pos_item = pos_lst[0]
        if len(pos_item) == 2:
            pos = pos_item[1]
            if "NN" in pos:
                return "noun"
            if "JJ" in pos:
                return "adj"
            if "V" in pos:
                return "verb"
            return "other"
        return ""
    return ""


def get_max_prob_word_in_dict(d):
    if not d:
        return ""
    keys = list(d.keys())
    vals = list(d.values())
    return keys[vals.index(max(vals))]


def most_freq_noun_for_word(word):
    word = word.lower()
    frequencies = get_frequencies_for_word(word)
    nouns = dict()
    if frequencies and type(frequencies) == str:
        return frequencies
    elif frequencies and type(frequencies) == dict:
        for elem in frequencies.keys():
            if word.split(".")[0] == elem[:len(word)-1]:
                if get_pos_tag_for_word(elem) == "noun":
                    nouns[elem] = frequencies[elem]
    if nouns:
        return get_max_prob_word_in_dict(nouns)
    return ""


def filter_non_stopwords_in_dict(d):
    result = {}
    for e in d.keys():
        if e in stopwords:
            result[e] = d[e]
    return result


def filter_stopwords_in_dict(d):
    result = {}
    for e in d.keys():
        if e not in stopwords:
            result[e] = d[e]
    return result


def ngram_predict(model, word, stopwords = False, abbrev = ""):
    if word in model.keys():
        word_pred_d = dict(model[word])
        if stopwords:
            word_pred_d = filter_non_stopwords_in_dict(word_pred_d)
        else:
            word_pred_d = filter_stopwords_in_dict(word_pred_d)
        
        result = {}
        if abbrev == "":
            max_prob_word = get_max_prob_word_in_dict(word_pred_d)
            if max_prob_word and word_pred_d[max_prob_word]:
                result[max_prob_word] = word_pred_d[max_prob_word]
        else:    
            ## make sure we are only choosing from words with appropriate stem 
            if word_pred_d:
                temp = {}
                for w in word_pred_d.keys():
                    if w and abbrev.split(".")[0] in w:
                        temp[w] = word_pred_d[w]
                    
                max_prob_word = get_max_prob_word_in_dict(temp)
                if max_prob_word and word_pred_d[max_prob_word]:
                    result[max_prob_word] = word_pred_d[max_prob_word]
                    
        return result
    return {}


def bigram_stopword_recovery(word_lst, m_forward, m_backward):
    result = []
    for i in range(len(word_lst) - 1):
        
        curr_word = word_lst[i]
        result.append(curr_word)
        next_stopword_pred = ngram_predict(m_forward, curr_word, True)
        
        next_word = word_lst[i + 1]
        prev_stopword_pred = ngram_predict(m_backward, next_word, True)
        
        if not next_stopword_pred:
            continue

        if list(next_stopword_pred.values())[0] > 0.8:
            result.append(list(next_stopword_pred.keys())[0])
        elif (prev_stopword_pred and 
              (list(next_stopword_pred.values())[0] > 0.3 or list(prev_stopword_pred.values())[0] > 0.3)):
            
            if list(next_stopword_pred.keys())[0] == list(prev_stopword_pred.keys())[0]:
                result.append(list(next_stopword_pred.keys())[0])
        
    result.append(word_lst[len(word_lst) - 1])
    return result


def bigram_find_blank_words(word_lst, m_forward, m_backward, abbrev_lst):
    
    # have a vector that keeps track of what should be changed 
    check = [0] * len(word_lst)
    for i in range(len(word_lst)):
        if word_lst[i] == "":
            check[i] = 1
    
    # all words filled already 
    if sum(check) < 1:
        return word_lst
    
    for i in range(len(check)):
        
        if check[i] == 1:
            abbrev = abbrev_lst[i].lower()
            next_word_pred = {}
            prev_word_pred = {}
            if i == 0:
                next_word = word_lst[i + 1]
                prev_word_pred = ngram_predict(m_backward, next_word, False, abbrev)
            elif i == len(check) - 1:
                prev_word = word_lst[i - 1]
                next_word_pred = ngram_predict(m_forward, prev_word, False, abbrev)
            else:
                prev_word = word_lst[i - 1]
                next_word_pred = ngram_predict(m_forward, prev_word, False, abbrev)
                next_word = word_lst[i + 1]
                prev_word_pred = ngram_predict(m_backward, next_word, False, abbrev)
            
            curr_from_prev = ""
            curr_from_next = ""
            if next_word_pred:
                curr_from_prev = list(next_word_pred.keys())[0]
            if prev_word_pred:
                curr_from_next = list(prev_word_pred.keys())[0]
                
            if curr_from_prev != "" and curr_from_next != "":
                if curr_from_next == curr_from_prev:
                    word_lst[i] = curr_from_prev
                elif prev_word_pred[curr_from_next] > next_word_pred[curr_from_prev]:
                    word_lst[i] = curr_from_next
                else:
                    word_lst[i] = curr_from_prev
            elif curr_from_prev != "":
                word_lst[i] = curr_from_prev
            elif curr_from_next != "":
                word_lst[i] = curr_from_next
        
    return word_lst


def fix_capital_for_word(init_word, curr_word):
    
    if not init_word or not curr_word:
        return curr_word
    
    # if previous word is not abbreviation and all caps, keep it that way
    if "." not in init_word and init_word.isupper():
        return init_word
    
    # if previous word has its first character capitalized, do the same
    if init_word[0].isupper():
        return curr_word[0].upper() + curr_word[1:]
        
    # else, keep curr word
    return curr_word


def fix_capitalization(initial_lst, lst_to_change):
    result = []
    if len(initial_lst) > len(lst_to_change):
        print("something went wrong")
        return lst_to_change
    
    i_i = 0
    for i_j in range(len(lst_to_change)):
        init_word = initial_lst[i_i]
        curr_word = lst_to_change[i_j]
        if type(init_word) != str and type(curr_word) != str:
            result.append(curr_word)
            i_i += 1
            continue
        if curr_word == "" or init_word == "":
            result.append(curr_word)
            continue
        if curr_word in stopwords:
            result.append(curr_word)
            continue
        if "-" in curr_word and "-" in init_word:
            c_w_lst = curr_word.split("-")
            i_w_lst = init_word.split("-")
            new_w = ""
            for i in range(len(i_w_lst)):
                new_w += "-" + fix_capital_for_word(i_w_lst[i], c_w_lst[i])
            
            result.append(new_w[1:])
            i_i += 1
            continue
            
        result.append(fix_capital_for_word(init_word, curr_word))
        i_i += 1
#         print(init_word, curr_word)
        
    return result



def expand_abbreviation(journal_abbrev, verbose = False, lang = ""):
    if not lang:
        lang = get_language(journal_abbrev)
        if not lang:
            lang = "eng"
        
    journal_lst = get_journal_lst(journal_abbrev)
    
    raw_expansion = get_raw_iso4_expansions(journal_lst, lang)
    
    mf_expansion = get_most_frequent_expansions(journal_lst)
    
    if verbose:
        print("journal list: ", journal_lst)
        print("raw iso4 expansion: ", raw_expansion)
        print("most frequent expansion: ", mf_expansion)
    
    if len(raw_expansion) != len(mf_expansion):
        print("something went wrong")
        
    verify_raw_mf = verify_raw_iso4_most_freq_lst(journal_lst, raw_expansion, mf_expansion)
    if verbose: print("verfication list: ", verify_raw_mf)
        
    bigram_pred = bigram_find_blank_words(verify_raw_mf, model_bi_forward, model_bi_backward, journal_lst)
    if verbose: print("bigram prediction: ", bigram_pred)
    
    if get_pos_tag_for_word(bigram_pred[-1]) != "noun":
        mf_noun = most_freq_noun_for_word(journal_lst[-1])
        if mf_noun:
            bigram_pred = bigram_pred[:-1] + [mf_noun]
            
    if verbose: print("word list after fixing pos tagging: ", bigram_pred)
        
    bigram_pred_w_stop = bigram_stopword_recovery(bigram_pred, model_bi_forward, model_bi_backward)
    if verbose: print("bigram prediction with stop words: ", bigram_pred_w_stop)
    
    word_lst_fixed_capital = fix_capitalization(journal_lst, bigram_pred_w_stop)
    if verbose: print("fixed capitalization: ", word_lst_fixed_capital)
    
    journal_final_expansion = " ".join(word_lst_fixed_capital)
    
    if verbose: print("RESULT: ", journal_final_expansion)
    return journal_final_expansion




# expand_abbreviation("proc. natl. acad. sci. u. s. a.", verbose = True) 
# expand_abbreviation("bot. j. linn. soc.", True)
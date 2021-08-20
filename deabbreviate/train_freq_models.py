import re 
import pandas as pd
import numpy as np

from load_iso4_mappings import stopwords
from preprocess import get_journal_lst
    

data_path = "deabbreviate/data/"


def load_train_csv():
    data = []
    with open(data_path + "train.csv") as file:
        lines = file.readlines()
        for curr_line in lines:
            curr_info = {}
            curr_line = curr_line.strip()
            curr_line_lst = curr_line.split(";")
            if len(curr_line_lst) == 2:
                curr_info["full"] = curr_line_lst[0]
                curr_info["abbrev"] = curr_line_lst[1]
            elif len(curr_line_lst) == 1:
                curr_info["full"] = curr_line_lst[0]
                curr_info["abbrev"] = ""
            else:
                curr_info["full"] = ""
                curr_info["full"] = ""
            data.append(curr_info)
            
    abbrev_df = pd.DataFrame(data)
    abbrev_df = abbrev_df.fillna("")
    abbrev_df = abbrev_df.drop_duplicates()
    return abbrev_df

def matching(full_lst, abbrev_lst):
    
    if len(full_lst) > len(abbrev_lst):
        for elem in full_lst:
            if elem.lower() in stopwords:
                full_lst.remove(elem)
    
    if len(full_lst) == len(abbrev_lst):
        result = []
        for i in range(len(full_lst)):
            result.append((full_lst[i], abbrev_lst[i]))
        return result
    else:
        return ""

def clean_word(word):
    word = re.sub("\(", "", word)
    word = re.sub("\)", "", word)
    word = re.sub(",", "", word)
    return word.lower()

def calc_count(lst_words):
    result = {}
    for elem in lst_words:
        if elem in result.keys():
            result[elem] += 1
        else:
            result[elem] = 1

    return result

def calc_freq(counts):
    total = sum(counts.values())
    result = {}
    for elem in counts.keys():
        result[elem] = counts[elem] / total
    return result

def most_freq(frequencies):
    v = list(frequencies.values())
    k = list(frequencies.keys())
    return k[v.index(max(v))]

def get_mapping_df(abbrev_df):
    abbrev_df["full_lst"] = abbrev_df["full"].apply(get_journal_lst)
    abbrev_df["abbrev_lst"] = abbrev_df["abbrev"].apply(get_journal_lst)
    abbrev_df["mappings"] = abbrev_df.apply(lambda x: matching(x["full_lst"], x["abbrev_lst"]), axis = 1)
    mappings_df = abbrev_df[abbrev_df["mappings"] != ""]
    mapping_lst = mappings_df["mappings"].tolist()
    mappings = []
    for m in mapping_lst:
        mappings.extend(m)

    dataset = pd.DataFrame(mappings, columns = ["full", "abbrev"])
    return dataset

def get_abbrev_freq_df(mapping_df):

    dataset_abbrev = mapping_df[mapping_df["full"] != mapping_df["abbrev"]]
    dataset_abbrev = dataset_abbrev.reset_index(drop = True)

    dataset_abbrev_freq = dataset_abbrev.groupby(["abbrev"]).agg(list)
    dataset_abbrev_freq = dataset_abbrev_freq.reset_index(drop = False)

    dataset_abbrev_freq["count"] = dataset_abbrev_freq["full"].apply(calc_count)
    dataset_abbrev_freq["freq"] = dataset_abbrev_freq["count"].apply(calc_freq)
    dataset_abbrev_freq["most_freq"] = dataset_abbrev_freq["freq"].apply(most_freq)

    return dataset_abbrev_freq


def retrain_freq_models():
    abbrev_df = load_train_csv()
    mapping_df = get_mapping_df(abbrev_df)
    dataset_abbrev_freq = get_abbrev_freq_df(mapping_df)
    df_freq_to_write = dataset_abbrev_freq[["abbrev", "full", "freq", "most_freq"]]
    df_freq_to_write.to_csv("frequencies_train.csv")
    print("Frequency Models saved.")
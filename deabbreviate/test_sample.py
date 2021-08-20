import pandas as pd

from fuzzywuzzy import fuzz

from train_freq_models import load_train_csv
from pipeline import expand_abbreviation, abbreviate_journal_name

data_path = "deabbreviate/data/"

sample_size = 20

def generate_test_result():
    abbrev_df = load_train_csv()
    sample = abbrev_df.sample(n=sample_size)
    sample["abbrev_exact"] = sample["full"].apply(abbreviate_journal_name)
    sample["abbrev_exact_expand"] = sample["abbrev_exact"].apply(expand_abbreviation)

    sample["fuzzy_score"]= sample.apply(lambda x: fuzz.ratio(x["abbrev_exact_expand"], x["full"]), axis = 1)
    return sample

def print_format(full, abbrev, abbrev_exact, expanded, score):
    print("---")
    print("Full: ", full)
    print("Abbrev: ", abbrev)
    print("Abbrev Exact: ", abbrev_exact)
    print("Expanded: ", expanded)
    print("Fuzzy Matching Score: ", score)
    print("---")

def print_sample_test():
    test_result = generate_test_result()
    print("Generated test result")
    test_result.apply(lambda x: print_format(x["full"], x["abbrev"], x["abbrev_exact"], 
    x["abbrev_exact_expand"], x["fuzzy_score"]), axis = 1)

def output_sample_test_csv():
    test_result = generate_test_result()
    test_result.to_csv("sample_test.csv")

# output_sample_test_csv() 
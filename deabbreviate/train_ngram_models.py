import pandas as pd
# import json

print('hi')
# import nltk
# nltk.download('wordnet')

# from nltk import bigrams
# from collections import defaultdict

# from tokenize import get_journal_lst

# data_path = "deabbreviate/data/"

# def build_model_bi_forward_predict(train_data):
#     # Create a placeholder for model
#     m = defaultdict(lambda: defaultdict(lambda: 0))

#     # Count frequency of co-occurance  
#     for sentence in train_data:
#         for w1, w2 in bigrams(sentence, pad_right=True, pad_left=True):
#             if w1:
#                 w1 = w1.lower()
#             if w2: 
#                 w2 = w2.lower()
#             m[w1][w2] += 1

#     for w1 in m:
#         total_count = float(sum(m[w1].values()))
#         for w2 in m[w1]:
#             m[w1][w2] /= total_count
            
#     return m


# def build_model_bi_backward_predict(train_data):
#     # Create a placeholder for model
#     m = defaultdict(lambda: defaultdict(lambda: 0))

#     # Count frequency of co-occurance  
#     for sentence in train_data:
#         for w1, w2 in bigrams(sentence, pad_right=True, pad_left=True):
#             if w1:
#                 w1 = w1.lower()
#             if w2: 
#                 w2 = w2.lower()
#             m[w2][w1] += 1

#     for w2 in m:
#         total_count = float(sum(m[w2].values()))
#         for w1 in m[w2]:
#             m[w2][w1] /= total_count
            
#     return m



# def save_models(train_data):

#     model_bi_forward = build_model_bi_forward_predict(train_data)
#     model_bi_backward = build_model_bi_backward_predict(train_data)
#     json.dump(model_bi_forward, open("model_bi_forward.json", 'w'))
#     json.dump(model_bi_backward, open("model_bi_backward.json", 'w'))


# def load_data():
#     data = []
#     with open(data_path + "train.csv") as file:
#         lines = file.readlines()
#         for curr_line in lines:
#             curr_info = {}
#             curr_line = curr_line.strip()
#             curr_line_lst = curr_line.split(";")
#             if len(curr_line_lst) == 2:
#                 curr_info["full"] = curr_line_lst[0]
#                 curr_info["abbrev"] = curr_line_lst[1]
#             elif len(curr_line_lst) == 1:
#                 curr_info["full"] = curr_line_lst[0]
#                 curr_info["abbrev"] = ""
#             else:
#                 curr_info["full"] = ""
#                 curr_info["full"] = ""
#             data.append(curr_info)
            
#     abbrev_df = pd.DataFrame(data)
#     abbrev_df = abbrev_df.fillna("")
#     abbrev_df = abbrev_df.drop_duplicates()
#     return abbrev_df


# abbrev_df = load_data()
# ngram_train = abbrev_df["full"].apply(get_journal_lst).tolist()
# save_models(ngram_train)
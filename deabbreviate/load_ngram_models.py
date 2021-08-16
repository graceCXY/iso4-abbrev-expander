import json 

data_path = "deabbreviate/data/"

model_bi_forward = json.load(open(data_path + "model_bi_forward.json"))
model_bi_backward = json.load(open(data_path + "model_bi_backward.json"))
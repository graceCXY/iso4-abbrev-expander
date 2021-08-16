import pandas as pd
import re

data_path = "deabbreviate/data/"

ltwa_data = []
with open(data_path + "ltwa_20210702.csv") as file:
    lines = file.readlines()
    for curr_line in lines:
        curr_info = {}
        curr_line = curr_line.strip()
        curr_line = re.sub("\"", "", curr_line)
        curr_line_lst = curr_line.split(";")
        if len(curr_line_lst) == 3:
            curr_info["full"] = curr_line_lst[0]
            if curr_line_lst[1] == "n.a.":
                curr_info["abbrev"] =  ""
            else:
                curr_info["abbrev"] = curr_line_lst[1]
            if "," in curr_line_lst[2]:
                lang_lst = [x.strip() for x in curr_line_lst[2].split(",")]
                curr_info["lang"] = lang_lst
            else:
                curr_info["lang"] = curr_line_lst[2]
        
        ltwa_data.append(curr_info)


ltwa_df = pd.DataFrame(ltwa_data)
ltwa_df_with_abbrev = ltwa_df[ltwa_df["abbrev"] != ""]
ltwa_df_with_abbrev = ltwa_df_with_abbrev.reset_index(drop = True)


stopwords = []
with open(data_path + "stopwords.txt") as file:
    lines = file.readlines()
    for curr_line in lines:
        stopwords.append(re.sub("\n", "", curr_line))

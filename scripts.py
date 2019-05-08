import re
from Utils import Utils
import pandas as pd
import numpy as np
import random
import csv


# Test case generation script
skills_file_path = "skills.csv"
all_skills_df = pd.read_csv(skills_file_path, delimiter=",", header=0)
skills_names = all_skills_df["Skill"].values
skills_description= all_skills_df["Description"].values


skills_count = skills_names.size
# skills_count = 10
all_pairs = []
all_pairs_check = []
for i in range(100):
    index1, index2 = random.randint(0,skills_count-1) , random.randint(0,skills_count-1)
    while (index1,index2) in all_pairs_check or index1==index2:
        index1, index2 = random.randint(0, skills_count - 1), random.randint(0, skills_count - 1)

    all_pairs.append((index1,index2))
    all_pairs_check.append((index2,index1))
    all_pairs_check.append((index1,index2))

print(all_pairs)
skills_pairs = [ (skills_names[index1],skills_description[index1] , skills_names[index2] ,skills_description[index2] )
                 for index1,index2 in all_pairs]
with open("test_skills.csv", 'w' , newline="") as file:
    writter = csv.writer(file)
    for skills_pair in skills_pairs:
        writter.writerow(skills_pair)
print(skills_pairs)
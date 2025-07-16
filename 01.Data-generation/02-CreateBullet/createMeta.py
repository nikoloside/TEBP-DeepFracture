import yaml
import glob
import os
import pandas as pd
import shutil

# Load the config.yaml
with open('../../config.yaml', 'r') as file:
    config = yaml.safe_load(file)

shape_category = config.get('shape_category')
data_path = config.get('data_bullet_path')

# Load the OBJ files
uid_list = glob.glob(os.path.join(data_path, shape_category, '*.bullet'))

print(len(uid_list))
# Remove non-existent materials folders
valid_uids = []
for uid_path in uid_list:
    uid = os.path.basename(uid_path).replace('.bullet', '')
    valid_uids.append(uid)

# Override the CSV file with the correct UID list
csv_file_path = os.path.join(data_path, shape_category + '.txt')
pd.DataFrame(valid_uids).to_csv(csv_file_path, index=False, header=False)

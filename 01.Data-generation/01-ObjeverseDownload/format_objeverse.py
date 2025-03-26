import yaml
import glob
import os
import pandas as pd
import shutil

# Load the config.yaml
with open('../../config.yaml', 'r') as file:
    config = yaml.safe_load(file)

shape_category = config.get('shape_category')
data_path = config.get('data_path')

# Load the OBJ files
uid_list = glob.glob(os.path.join(data_path, shape_category, 'objs', '*.obj'))

print(len(uid_list))
# Remove non-existent materials folders
valid_uids = []
for uid_path in uid_list:
    uid = os.path.basename(uid_path).replace('.obj', '')
    valid_uids.append(uid)
    materials_path = os.path.join(data_path, shape_category, 'materials', uid)
    if os.path.exists(materials_path):
        shutil.rmtree(materials_path)  # Remove the materials folder if it exists
        print("rm ", materials_path)

# Override the CSV file with the correct UID list
csv_file_path = os.path.join(data_path, shape_category, 'output.txt')
pd.DataFrame(valid_uids).to_csv(csv_file_path, index=False, header=False)

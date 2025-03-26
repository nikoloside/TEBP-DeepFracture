import shutil
import os
import subprocess

animalObjPath = "/Users/yuhanghuang/Workspaces/ShapeNetv2/Result/bowlObj_norm/"

folders = os.listdir(animalObjPath)

# print(folders)
with open('/Users/yuhanghuang/Workspaces/ShapeNetv2/Result/Meta/bowl_output.txt', 'w') as outfile:
    for filename in folders:
        if filename == ".DS_Store" or filename == "taxonomy.json":
            continue
        outfile.write(filename.split(".")[0] + '\n')
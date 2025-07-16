import pymesh
import os, glob

path = "data/Experiments/sca2024/"
# path = "data/Experiments/"

targetList = ["base", "squirrel", "bunny", "pot", "lion"]
targetList = ["s", "c", "a", "2", "0","4","chair","mug"]

for target in targetList:

    # folder = path + target + "/v2/" + target + "-*/"+ target + "/objs/*.obj"
    folder = path + target + "/sca/" + target + "-falling-small/"+ target + "/objs/*.obj"


    objs = glob.glob(folder)

    for obj in objs:
        # print(obj)
        dirName = os.path.dirname(obj)
        objName = os.path.basename(obj)

        os.makedirs(dirName+"/fix/", exist_ok=True)

        print(dirName, objName)

        baseMesh = pymesh.load_mesh(obj)
        pymesh.save_mesh(dirName+"/fix/"+objName, baseMesh);


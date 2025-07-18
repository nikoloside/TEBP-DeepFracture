import pymesh
import os, glob

path = "path/to/run-time/"

targetList = ["base", "squirrel", "bunny", "pot", "lion"]
targetList = ["s", "c", "a", "2", "0","4","chair","mug"]

for target in targetList:

    folder = os.path.join(path, target, "objs", "*.obj")


    objs = glob.glob(folder)

    for obj in objs:
        dirName = os.path.dirname(obj)
        objName = os.path.basename(obj)

        os.makedirs(dirName+"/fix/", exist_ok=True)

        print(dirName, objName)

        baseMesh = pymesh.load_mesh(obj)
        pymesh.save_mesh(dirName+"/fix/"+objName, baseMesh);


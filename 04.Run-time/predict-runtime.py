import glob, os
import numpy as np
from BreakableWorld import BreakableWorld
from predict.Model.load_VQfinal2resolutionv2 import MultiLatentEncoder, AutoDecoder
import pybullet as p
import yaml
import time
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils_config import load_config

size256 = 2
size128 = 1
size64 = 0

collisionNum = 1
impulseMax = 10000

config = load_config()
ws_data = config["data_runtime_data_path"]
ws_workspace = config["data_runtime_workspace_path"]

maxValues = {"bar": 1.1, "squirrel": 1.0, "bunny": 1.0, "base": 1.0, "lion": 1.0, "plane": 1.0, "sphere": 1.0, "static": 1.0}

shape = "bunny"
csvNum=260

modelShape = "bunny"
modelName = "cgf/"

projectName = shape + "/"
target = shape
# modelName = "cgf/squirrel-VQPG-impulseDiff-v1/"
projectPath = os.path.join(ws_data, projectName)

csvPath = os.path.join(projectPath, "csv", f"{shape}-{csvNum}.csv")

isFracturingOrSaving = True

world = BreakableWorld(isDirect = False, bulletFile = "", needOutput = not isFracturingOrSaving, allowAutoFracture = isFracturingOrSaving, timeRange = 20, hasGravity = False, collisionNum = collisionNum, impulseMax = impulseMax)
run_name = os.path.basename(csvPath).split(".")[0] + f"-{csvNum}"

run_path = os.path.join(modelName, run_name)
print(run_name, csvPath, run_path)

targetNameA = target
targetNameB = "sphere"

garagePathA = os.path.join(ws_workspace, run_path, targetNameA)
# garagePathB = os.path.join(run_path, targetNameB)

world.resultPath = os.path.join(ws_workspace, run_path, "obj_animation")

fracturePathA = os.path.join(garagePathA, "objs", "*.obj")
if isFracturingOrSaving:
    fracturePathA = ""
# fracturePathB = os.path.join(garagePathB, "objs", "*.obj")

objAPath = os.path.join(projectPath, "models", f"{targetNameA}.obj")
objBPath = os.path.join(projectPath, "models", f"{targetNameB}.obj")

modelNameA = os.path.join(ws_data, "network-models", modelName, modelShape, modelShape + "-")
# modelNameB = os.path.join(ws_data, "network-models", modelName, targetNameB, targetNameB + "-")

shapeName = [targetNameA, targetNameB]
targetName = [targetNameA, targetNameB]
paths = [objAPath, objBPath]
colors = [[0,1,0,1], [1,0,0,1]]
garagePaths = [garagePathA, ""]
fracturePaths = [fracturePathA, ""]
models = [modelNameA, ""]
staticsMass = [1, 1]
isBig = [size128, size128]
frictions = [-1, -1]
restitutions = [-1, -1]

os.makedirs(os.path.join(garagePathA), exist_ok=True) 
# os.makedirs(os.path.join(ws_data, garagePathB), exist_ok=True) 
os.makedirs(world.resultPath, exist_ok=True) 

csv = open(csvPath, 'r')
Lines = csv.readlines()

print("total object %d." % (len(Lines)))

# Create all objects first
for i in range(len(Lines)):
    strs = Lines[i].split(';')
    objName = targetName[i] # strs[1]

    print("Start loading: %s, %f, %f, %f" % (objName,float(strs[2]), float(strs[3]), float(strs[4])))
    pos = [float(strs[2]), float(strs[3]), float(strs[4])]
    rot = p.getQuaternionFromEuler([float(strs[5]), float(strs[6]), float(strs[7])])
    lVel = [float(strs[8]), float(strs[9]), float(strs[10])]
    aVel = [float(strs[11]), float(strs[12]), float(strs[13])]
    
    world.CreateBreakableObj(objName, pos, rot, lVel, aVel, paths[i], colors[i], staticsMass[i], frictions[i], restitutions[i], fracturePaths[i], garagePaths[i], models[i], isBig[i], maxValues[shapeName[i]], False, ws_workspace)

# Now that objects are created, set up debug page
if world.SetupDebugPage():
    print("Debug page setup successful, entering idle mode...")
    world.Idle()
else:
    print("Failed to setup debug page, proceeding without debug interface...")

start = time.time()

world.StartRun()

end = time.time()

time_diff = end - start
print("total time: ", time_diff)

world.StopRun()

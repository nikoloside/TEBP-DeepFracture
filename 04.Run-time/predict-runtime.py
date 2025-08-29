import glob, os
import numpy as np
from BreakableWorld import BreakableWorld
from predict.Model.load_VQfinal2resolutionv2 import MultiLatentEncoder, AutoDecoder
import pybullet as p
import yaml
import time
import sys
import argparse
from huggingface_hub import hf_hub_download
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils_config import load_config

def get_local_file_path(filename, file_type="file"):
    """Get local file path from data/run-time directory"""
    local_path = os.path.join("data", "run-time", filename)
    
    if os.path.exists(local_path):
        print(f"✓ Found local {file_type}: {local_path}")
        return local_path
    else:
        print(f"✗ Local {file_type} not found: {local_path}")
        print(f"  Please ensure the file exists in data/run-time/")
        return None

def download_from_huggingface(filename, file_type="file"):
    """Generic function to download files from Hugging Face (fallback)"""
    try:
        # First try to get from local directory
        local_path = get_local_file_path(filename, file_type)
        if local_path:
            return local_path
            
        # Fallback: Download from Hugging Face
        print(f"Downloading {file_type} from Hugging Face: {filename}")
        local_path = hf_hub_download(
            repo_id="nikoloside/deepfracture",
            filename=filename,
            cache_dir="data/run-time"
        )
        
        return local_path
    except Exception as e:
        print(f"Error downloading {file_type} {filename}: {e}")
        return None

def get_model_path_from_huggingface(model_shape):
    """Get model file path from Hugging Face"""
    # Define the model file patterns with folder structure
    # For encoder, return base path without .pt extension
    # This allows predictshapes.py to append "encoder.pt" and "decoder.pt"
    filename = f"{model_shape}/{model_shape}-"
    local_path = os.path.join("data", "run-time", filename)
    encoder_file = local_path + "encoder.pt"
    decoder_file = local_path + "decoder.pt"
    
    # Check if both encoder and decoder files exist
    if os.path.exists(encoder_file) and os.path.exists(decoder_file):
        print(f"✓ Found local encoder model: {encoder_file}")
        print(f"✓ Found local decoder model: {decoder_file}")
        return local_path
    else:
        if not os.path.exists(encoder_file):
            print(f"✗ Local encoder model not found: {encoder_file}")
        if not os.path.exists(decoder_file):
            print(f"✗ Local decoder model not found: {decoder_file}")
        return None
        
def get_csv_path_from_huggingface(shape, csv_num):
    """Get CSV file path from Hugging Face"""
    filename = f"csv/{shape}-{csv_num}.csv"
    
    return download_from_huggingface(filename, f"CSV for {shape}-{csv_num}")

def get_obj_path_from_huggingface(obj_name):
    """Get OBJ file path from Hugging Face"""
    filename = f"objs/{obj_name}.obj"
    
    return download_from_huggingface(filename, f"OBJ {obj_name}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="DeepFracture Runtime Prediction")
    parser.add_argument("--use_fractured_pattern", action="store_true", 
                       help="Use existing pre-computed fracture patterns (don't predict)")
    parser.add_argument("--save-animation", action="store_true",
                       help="Enable animation saving mode")
    parser.add_argument("--shape", type=str, default="bunny",
                       help="Shape to use (default: bunny)")
    parser.add_argument("--csv-num", type=int, default=260,
                       help="CSV number (default: 260)")
    parser.add_argument("--auto-run", action="store_true",
                       help="Enable auto run mode")
    
    return parser.parse_args()

# Parse command line arguments
args = parse_arguments()

size256 = 2
size128 = 1
size64 = 0

collisionNum = 1
impulseMax = 10000

config = load_config()
ws_data = config["data_runtime_data_path"]
ws_workspace = config["data_runtime_workspace_path"]

maxValues = {"squirrel": 1.0, "bunny": 1.0, "base": 1.0, "lion": 1.0, "pot": 1.0, "sphere": 1.0}

shape = args.shape
csvNum = args.csv_num

modelShape = shape
modelName = "cgf/"
auto_run = args.auto_run

projectName = shape + "/"
target = shape
# modelName = "cgf/squirrel-VQPG-impulseDiff-v1/"
projectPath = os.path.join(ws_data, projectName)

# Get CSV path from Hugging Face
print(f"Loading CSV for shape: {shape}, csv_num: {csvNum}")
csvPath = get_csv_path_from_huggingface(shape, csvNum)
if csvPath is None:
    print(f"Failed to load CSV for {shape}-{csvNum}")
    sys.exit(1)

# Set fracture and saving modes based on arguments (can be parallel)
isFracturing = True   # Default to using neural network to predict fracture patterns
isSaving = False      # Default to not saving animation

if args.use_fractured_pattern:
    isFracturing = False   # Use existing pre-computed fracture patterns (don't predict)

if args.save_animation:
    isSaving = True        # Enable animation saving

world = BreakableWorld(isDirect = False, bulletFile = "", needOutput = isSaving, allowAutoFracture = isFracturing, timeRange = 20, hasGravity = False, collisionNum = collisionNum, impulseMax = impulseMax)
run_name = os.path.basename(csvPath).split(".")[0] + f"-{csvNum}"

run_path = os.path.join(modelName, run_name)
print(run_name, csvPath, run_path)

targetNameA = target
targetNameB = "sphere"

garagePathA = os.path.join(ws_workspace, run_path, targetNameA)
# garagePathB = os.path.join(run_path, targetNameB)

world.resultPath = os.path.join(ws_workspace, run_path, "obj_animation")

fracturePathA = os.path.join(garagePathA, "objs", "*.obj")
if isFracturing:
    fracturePathA = ""  # Clear fracture path when using neural network prediction
else:
    # Use existing pre-computed fracture patterns from files
    pass
# fracturePathB = os.path.join(garagePathB, "objs", "*.obj")

# Get OBJ paths from Hugging Face
print(f"Loading OBJ files for: {targetNameA}, {targetNameB}")
objAPath = get_obj_path_from_huggingface(targetNameA)
objBPath = get_obj_path_from_huggingface(targetNameB)

if objAPath is None:
    print(f"Failed to load OBJ for {targetNameA}")
    sys.exit(1)
if objBPath is None:
    print(f"Failed to load OBJ for {targetNameB}")
    sys.exit(1)

# Get model paths from Hugging Face
print(f"Loading models for shape: {modelShape}")
modelNameA = get_model_path_from_huggingface(modelShape)
if modelNameA is None:
    print(f"Failed to load encoder model for {modelShape}")
    sys.exit(1)

# For now, we'll use the same model for both objects
# modelNameB = get_model_path_from_huggingface(targetNameB, "encoder")

shapeName = [targetNameA, targetNameB]
targetName = [targetNameA, targetNameB]
paths = [objAPath, objBPath]
colors = [[0,1,0,1], [1,0,0,1]]
garagePaths = [garagePathA, ""]
fracturePaths = [fracturePathA, ""]
models = [modelNameA, ""]  # modelNameA now contains the full path from Hugging Face
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
    world.Idle(auto_run)
else:
    print("Failed to setup debug page, proceeding without debug interface...")

start = time.time()

world.StartRun()

end = time.time()

time_diff = end - start
print("total time: ", time_diff)

world.StopRun()

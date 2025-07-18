from Model.load_VQfinal2resolutionv2 import MultiLatentEncoder, AutoDecoder
import torch
import json
import numpy as np
import torch.nn.init as init
import os, time
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils_config import get_training_config


from animator3d import MedicalImageAnimator

import nibabel as nib

def save_as_nib(file_name, variable):
    ni_img = nib.Nifti1Image(variable, affine=np.eye(4))
    nib.save(ni_img, file_name)

def getPos(jsonName):
    maxInx = 0
    max = 0
    impList = []
    dirList = []
    posList = []
    # Read maxImpulse from config file
    training_config = get_training_config()
    maxImpulse = training_config.get('max_impulse', 304527)
    with open(jsonName) as f:
        jsonInput = json.load(f)
        ind = 0
        for imp in jsonInput:
            Imp = imp["collImpulse"]
            impList.append(np.array([Imp / maxImpulse], dtype=np.float32))
            dirList.append(np.array([imp["collDirections"][0], imp["collDirections"][1],imp["collDirections"][2]],dtype = np.float32))
            posList.append(np.array([imp["collPoints"][0],imp["collPoints"][1],imp["collPoints"][2]],dtype = np.float32))

            if Imp > max:
                max = Imp
                maxInx = ind

            ind += 1
    return posList[maxInx], dirList[maxInx], impList[maxInx]


from MorphoImageJ import processCagedSDFSeg
import glob
import shutil

def predict(work_path, objName, imp, pos, direct, is_Big):

    mps_device = torch.device("cpu")
    encoder = torch.load("Model/squirrel-encoder.pt", map_location=mps_device)
    decoder = torch.load("Model/squirrel-decoder.pt", map_location=mps_device)

    encoder.to(mps_device)
    decoder.to(mps_device)

    encoder.eval()
    decoder.eval()


    start = time.time()

    imp = torch.Tensor(imp, device="cpu").to(mps_device)
    pos = torch.Tensor(pos, device="cpu").to(mps_device)
    direct = torch.Tensor(direct, device="cpu").to(mps_device)

    print(imp, pos, dir)

    feature = encoder.predict(pos, direct, imp).unsqueeze(0)

    latent_z = torch.FloatTensor(1, 8, device="cpu").to(mps_device)
    init.xavier_normal_(latent_z)

    # Cook
    input_x, min_index, dist = decoder.Cook(feature, latent_z)

    print(input_x, min_index, dist)

    # Small
    output = decoder.forwardBig(input_x).squeeze().squeeze()
    end = time.time()

    time_diff = end - start
    print("predict time: ", time_diff)

    os.makedirs(work_path, exist_ok=True) 

    clean_folder = work_path + "*"
    files = glob.glob(clean_folder)
    if len(files) > 0:
        shutil.rmtree(work_path) 
        os.makedirs(work_path, exist_ok=True) 

    processCagedSDFSeg(output.to('cpu').detach().numpy(), work_path, objName, is_Big)


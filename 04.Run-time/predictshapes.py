import torch
import json
import numpy as np
import torch.nn.init as init
import os, time, yaml
from utils_config import get_training_config


# Monkey-patch because I trained with a newer version.
# This can be removed once PyTorch 0.4.x is out.
# See https://discuss.pytorch.org/t/question-about-rebuild-tensor-v2/14560
import torch._utils
try:
    torch._utils._rebuild_tensor_v2
except AttributeError:
    def _rebuild_tensor_v2(storage, storage_offset, size, stride, requires_grad, backward_hooks):
        tensor = torch._utils._rebuild_tensor(storage, storage_offset, size, stride)
        tensor.requires_grad = requires_grad
        tensor._backward_hooks = backward_hooks
        return tensor
    torch._utils._rebuild_tensor_v2 = _rebuild_tensor_v2

# from animator3d import MedicalImageAnimator

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
    # 从配置文件读取 maxImpulse
    training_config = get_training_config()
    maxImpulse = training_config.get('max_impulse', 304527) * 0.1
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


Shape3Lists = {"squirrel":0, "bunny":1, "lion": 2}

def judge(impList, posList, dirList, collisionNum):
    # sourcePath = "/Users/yuhanghuang/Workspaces/DeepFracture-3D/pybullet/"
    # model = "data/Experiments/network-models/cgf/squirrel-impulse/squirrel-impact-"
    mps_device = torch.device("cpu")
    encoderPath = sourcePath + model + "encoder.pt"
    decoderPath = sourcePath + model + "decoder.pt"
    print(decoderPath)
    encoder = torch.load(encoderPath, map_location=mps_device, weights_only=False)
    decoder = torch.load(decoderPath, map_location=mps_device, weights_only=False)

    encoder.to(mps_device)
    decoder.to(mps_device)

    encoder.eval()
    decoder.eval()

    impVec = []
    posVec = []
    dirVec = []
    featureVec = []

    # imp, pos, direct = getPos("impact/1-c.txt")
    for ind in range(collisionNum):
        imp = torch.Tensor(impList[ind], device="cpu").to(mps_device)
        pos = torch.Tensor(posList[ind], device="cpu").to(mps_device)
        direct = torch.Tensor(dirList[ind], device="cpu").to(mps_device)

        impVec.append(imp)
        posVec.append(pos)
        dirVec.append(direct)

        fea = torch.concat((pos, direct, imp), -1)

        featureVec.append(fea)

        print(imp, pos, direct)

    feature = []

    if collisionNum == 1:
        feature = encoder.predict(posVec[0], dirVec[0], impVec[0]).unsqueeze(0)
    
    if collisionNum == 2:
        feature = encoder.predict(posVec[0], dirVec[0], impVec[0], posVec[1], dirVec[1], impVec[1]).unsqueeze(0)

    if collisionNum > 2:
        torch.concat((pos, direct, imp), -1)
        feature = encoder.predict(fea).unsqueeze(0)

    print(collisionNum, feature)
    output = decoder.forward(feature)
    return output[0][1] > output[0][0]


def predict(work_path, objName, model, impList, posList, dirList, is_Big, maxValue, isMulShapes, name, collisionNum):
    mps_device = torch.device("cpu")
    encoderPath = model + "encoder.pt"
    decoderPath = model + "decoder.pt"
    print(decoderPath)
    encoder = torch.load(encoderPath, map_location=mps_device, weights_only=False)
    decoder = torch.load(decoderPath, map_location=mps_device, weights_only=False)

    encoder.to(mps_device)
    decoder.to(mps_device)

    encoder.eval()
    decoder.eval()

    impVec = []
    posVec = []
    dirVec = []
    featureVec = []

    # imp, pos, direct = getPos("impact/1-c.txt")
    for ind in range(collisionNum):
        imp = torch.Tensor(impList[ind], device="cpu").to(mps_device)
        pos = torch.Tensor(posList[ind], device="cpu").to(mps_device)
        direct = torch.Tensor(dirList[ind], device="cpu").to(mps_device)

        impVec.append(imp)
        posVec.append(pos)
        dirVec.append(direct)

        fea = torch.concat((pos, direct, imp), -1)

        featureVec.append(fea)

        print(imp, pos, direct)

    feature = []

    if collisionNum == 1:
        feature = encoder.predict(posVec[0], dirVec[0], impVec[0]).unsqueeze(0)
    
    if collisionNum == 2:
        feature = encoder.predict(posVec[0], dirVec[0], impVec[0], posVec[1], dirVec[1], impVec[1]).unsqueeze(0)

    if collisionNum > 2:
        torch.concat((pos, direct, imp), -1)
        feature = encoder.predict(fea).unsqueeze(0)

    

    # print(feature)

    latent_z = torch.FloatTensor(1, 8, device="cpu").to(mps_device)
    init.xavier_normal_(latent_z)

    # print(feature.unsqueeze(0).shape, latent_z.shape)

    start = time.time()

    # Cook
    if not isMulShapes:
        input_x, min_index, dist = decoder.Cook(feature, latent_z)
    else:
        # print(decoder.shapes()[Shape3Lists[name]], feature, latent_z)
        input_x, min_index, dist = decoder.Cook(decoder.shapes()[Shape3Lists[name]].unsqueeze(0), feature, latent_z)


    print(input_x, min_index, dist)

    # Small
    if is_Big == 2:
        output = decoder.forwardBig(input_x).squeeze().squeeze()
    elif is_Big == 1:
        output = decoder.forwardMiddle(input_x).squeeze().squeeze()
    else: # is_Big == 0:
        output = decoder.forwardMiddle(input_x)
        downsample = torch.nn.Upsample(size=(64, 64, 64))
        output = downsample(output).squeeze().squeeze()

    print(output.shape)

    end = time.time()
    print("Pred. Time: ", (end - start))
    # ind = 999
    # save_path=""

    # gif_path = os.path.join(save_path, 'truth_%d.gif' % (ind))
    # animator = MedicalImageAnimator(output.to('cpu').detach().numpy().copy().squeeze(), [], 0, save=True)
    # animate = animator.run(gif_path)

    # vox_path = os.path.join(save_path, 'truth_%d.nii' % (ind))
    # save_as_nib(vox_path, output.to('cpu').detach().numpy().copy())



    # work_path = "/Users/yuhanghuang/Workspaces/DeepFracture-3D/pybullet/data/run-time/squirrel-2/"

    os.makedirs(work_path, exist_ok=True) 

    clean_folder = os.path.join(work_path, "objs")
    files = glob.glob(clean_folder)
    if len(files) > 0:
        shutil.rmtree(os.path.join(work_path, "objs")) 
    os.makedirs(os.path.join(work_path, "objs"), exist_ok=True) 

    # obj_path = "/Users/yuhanghuang/Workspaces/DeepFracture-3D/pybullet/data/squirrel.obj"
    processCagedSDFSeg(output.to('cpu').detach().numpy(), work_path, objName, is_Big, maxValue)

    # processCagedSDFSeg

    # print(base.latent_vectors)
    # base.

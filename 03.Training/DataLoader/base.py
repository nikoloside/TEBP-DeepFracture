import json
import os

import glob
import numpy as np
import nibabel as nib

import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from Utils.utils_config import get_training_config
from Utils.utils_device import get_device

class InputMapDataset(Dataset):
    def __init__(self):
        super(InputMapDataset, self).__init__()

    def name(self):
        return 'InputMapDataset'

    def __len__(self):
        return min(len(self.AB_paths), self.opt.train_dataset_size + self.opt.test_dataset_size)
    
    def getPos(self, jsonName):
        maxInx = 0
        max = 0
        impList = []
        dirList = []
        posList = []
        maxImpulse = self.opt.max_impulse
        
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
    

    def get_from_nib(self, file_name):
        img = nib.load(file_name)
        data = img.get_fdata() # Get the data object
        return data


    def getVox(self, expTime):
        niiName = os.path.join(self.workspacePath, "nii", f"{expTime}.nii")
        image = self.get_from_nib(niiName)
            
        return image


    def __getitem__(self, idx):
        expTime = os.path.basename(self.AB_paths[idx]).split(".")[0]
        jsonName = os.path.join(self.workspacePath, "impact", expTime + ".txt")

        pos, direct, imp = self.getPos(jsonName)

        pos = torch.from_numpy(pos).to(torch.float32)
        direct = torch.from_numpy(direct).to(torch.float32)
        imp = torch.from_numpy(imp).to(torch.float32)

        image_middle = self.getVox(expTime)

        normalized = 1
        image_middle = image_middle / normalized

        if self.transforms:
            image_middle = self.transforms(image_middle)

        # add channel
        image_middle = image_middle[None, :]

        return pos, direct, imp, image_middle.float(), idx

    def initialize(self,opt):
        self.opt = opt
        self.root = opt.dataroot
        self.dir_AB = os.path.join(opt.dataroot, opt.phase)
        self.pos_encode_dim = opt.pos_encode_dim

        self.projectPath = opt.projName
        self.workspacePath = opt.dataroot
        self.AB_paths = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join(self.workspacePath, 'info', '*.txt'))]
        self.AB_paths = sorted(self.AB_paths)

        transform_list = transforms.Compose([
            transforms.ToTensor(),
        ])

        self.transforms = transform_list



class DataLoader():
    def __init__(self):
        pass
    
    def initialize(self, opt):
        self.opt = opt
        self.dataset = InputMapDataset()
        print("dataset [%s] was created" % (self.dataset.name()))
        self.dataset.initialize(opt)
        
        # set pin_memory
        device = get_device(getattr(opt, 'use_cuda', True))
        pin_memory = device.type == "cuda"  # set pin_memory only cuda
        
        self.dataloader = torch.utils.data.DataLoader(
            self.dataset,
            batch_size=opt.batch_size,
            shuffle=opt.serial_batches,
            pin_memory=pin_memory,
            num_workers=0
            )
    
    def load_data(self):
        return self.dataloader


    def __len__(self):
        return min(len(self.dataset), self.opt.train_dataset_size + self.opt.test_dataset_size)
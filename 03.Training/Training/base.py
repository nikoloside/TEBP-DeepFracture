from Utils.utils_visualize import Utils_visualize
from Utils.utils_network import Utils_network
from Utils.utils_device import get_device, to_device
from DataLoader.base import DataLoader
from Models.network import MultiLatentEncoder
from Models.network import AutoDecoder

import os
import glob
import numpy as np
import torch
import torch.nn as nn
import igl

class TrainingProcess:
    def __init__(self, opt):
        self.opt = opt

    def Prepare(self):        
        self.data_loader = DataLoader()
        self.data_loader.initialize(self.opt)
        self.dataset = self.data_loader.load_data()
        dataset_size = len(self.data_loader.dataset)

        print('#Load images = %d' % dataset_size)
        if dataset_size == 0:
            print('Alert: No images loaded!')
        print('#Train images = %d' % self.opt.train_dataset_size)

        self.save_path = os.path.join(self.opt.save_path, self.opt.runName)
        fileExist = glob.glob(self.save_path)
        if len(fileExist) <= 0:
            os.makedirs(self.save_path, exist_ok=True)

        # set device
        self.device = get_device(getattr(self.opt, 'use_cuda', True))

        self.encoder = MultiLatentEncoder(self.opt)
        self.decoder = AutoDecoder(self.opt)
        self.encoder.apply(Utils_network.weights_init)

        self.log_file = open(self.save_path + "log.txt", "w")

        # 将模型移动到选择的设备
        self.decoder = to_device(self.decoder, self.device)
        self.encoder = to_device(self.encoder, self.device)
        
        self.g_criterion = nn.MSELoss()
        self.d_criterion = nn.BCEWithLogitsLoss()

        if self.opt.continue_train:
            self.decoder = torch.load('{}{}-{}'.format(self.save_path, self.opt.projName, "decoder.pt"), map_location=self.device)
            self.encoder = torch.load('{}{}-{}'.format(self.save_path, self.opt.projName, "encoder.pt"), map_location=self.device)
            self.decoder = to_device(self.decoder, self.device)
            self.encoder = to_device(self.encoder, self.device)

        learning_rate = 5e-3
        self.optimizer_d = torch.optim.Adam(self.decoder.parameters(), lr=learning_rate)
        self.optimizer_e = torch.optim.Adam(self.encoder.parameters(), lr=learning_rate)

        print(self.decoder.codes())    
        self.log_file.write('Decoder codes {}\n'.format(self.decoder.codes()))

        self.decoder.train()
            
    def Train(self, tq, wandb, epoch):
        total_l1_md_loss=0

        for i, (pos, direct, imp, x_md, ind) in enumerate(self.dataset):
            
            if i >= self.opt.train_dataset_size:
                break
            
            # Forward pass
            x_md = to_device(x_md, self.device)
            pos = to_device(pos, self.device)
            direct = to_device(direct, self.device)
            imp = to_device(imp, self.device)

            self.optimizer_d.zero_grad()

            feature = self.encoder(pos, direct, imp)
            feature_z = self.decoder.codes()[ind]

            input_x, min_index, dist = self.decoder.Cook(feature, feature_z)

            # Forward Middle
            Utils_network.set_decoder_requires_grad(self.decoder, "all", True)

            x_reconst = self.decoder.forwardMiddle(input_x)

            loss_md = self.g_criterion(x_md, x_reconst)
            loss_md.backward()

            self.optimizer_d.step()
            total_l1_md_loss += loss_md.item()

            tq.update(1)
            tq.set_postfix(loss_md='{:.5f}'.format(loss_md.item()))

            wandb.log({"epoch": epoch, "loss_md": loss_md.item()})

        self.log_file.write('Epoch {}, l1_loss_md={}\n'.format(epoch, total_l1_md_loss / self.opt.train_dataset_size))

    def Visualize(self, epoch):
        self.decoder.eval()
        Utils_visualize.VisualizeMain(self.encoder, self.decoder, self.dataset, self.save_path, epoch, True, self.opt)
        self.decoder.train()

    def SaveModel(self, epoch):
        torch.save(self.decoder, '{}{}-{}-{}'.format(self.save_path, self.opt.projName, str(epoch), "decoder.pt"))
        torch.save(self.encoder, '{}{}-{}-{}'.format(self.save_path, self.opt.projName, str(epoch), "encoder.pt"))

    def UpdateLr(self):
        learning_rate = self.opt.lr
        self.optimizer_d = torch.optim.Adam(self.decoder.parameters(), lr=learning_rate)
        self.optimizer_e = torch.optim.Adam(self.encoder.parameters(), lr=learning_rate)


    def Test(self):
        decoder = torch.load('{}{}-{}'.format(self.save_path, self.opt.projName, "decoder.pt"))
        encoder = torch.load('{}{}-{}'.format(self.save_path, self.opt.projName, "encoder.pt"))
        data = np.load('{}{}-{}'.format(self.save_path, self.opt.projName, "codebook.npz"))

        Utils_visualize.drawGraph(encoder, decoder, self.dataset, self.save_path, 999, True, self.opt)
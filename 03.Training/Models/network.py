import torch

import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init

from siren_pytorch import Siren


class MultiLatentEncoder(nn.Module):
    def __init__(self, opt):
        super(MultiLatentEncoder, self).__init__()

        self.neuron_input = Siren(
            dim_in = 7,
            dim_out = opt.pos_encode_dim
        )

    def forward(self, pos, direct, imp):
        input_encoded = torch.concat((pos, direct, imp), -1)
        output = self.neuron_input(input_encoded)
        return output

    def predict(self, pos, direct, imp):
        input_encoded = torch.concat((pos, direct, imp), -1)
        output = self.neuron_input(input_encoded)
        return output

class AutoDecoder(nn.Module):
    def __init__(self, opt):
        super(AutoDecoder, self).__init__()

        self.ndf = opt.ndf
        self.data_shape = opt.data_shape

        # With FC Layer
        def block(in_feat, out_feat, normalize=True):
            layers = [nn.ConvTranspose3d(in_feat, out_feat, 4, 2, 1)]
            if normalize:
                layers.append(nn.BatchNorm3d(out_feat, 0.8))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.fc = nn.Sequential(
            nn.Linear(opt.pos_encode_dim + opt.z_latent_dim, int((self.ndf*8)*int(self.data_shape/16)*int(self.data_shape/16)*int(self.data_shape/16))),#6*6
            nn.LeakyReLU(0.2, inplace=True),
        )
        self.decoder = nn.Sequential(
            *block(self.ndf*8, self.ndf*4),
            *block(self.ndf*4, self.ndf*2),
            *block(self.ndf*2, self.ndf)
        )

        self.toVoxelMd = nn.Sequential(
            nn.ConvTranspose3d(self.ndf , 1, 4, 2, 1, bias=False),
            nn.Tanh(),
        )

        self.toVoxelBig = nn.Sequential(
            *block(self.ndf, int(self.ndf/2)),
            nn.ConvTranspose3d(int(self.ndf/2), 1, 4, 2, 1, bias=False),
            nn.Tanh(),
        )

        self.latent_vectors = nn.Parameter(torch.FloatTensor(opt.train_dataset_size, opt.z_latent_dim))
        self.cookbook = nn.Parameter(torch.FloatTensor(opt.train_dataset_size, opt.pos_encode_dim + opt.z_latent_dim))

        init.xavier_normal_(self.latent_vectors)

    def Cook(self, x, y):
        input_x = self.embedding(x,y)
        distances = (
            (input_x ** 2).sum(1, keepdim=True)
            - 2 * input_x @ self.cookbook.transpose(0, 1)
            + (self.cookbook.transpose(0, 1) ** 2).sum(0, keepdim=True)
        )
        encoding_indices = distances.argmin(1)
        output = F.embedding(encoding_indices.view(input_x.shape[0],*input_x.shape[2:]), self.cookbook)
        distance = ((input_x - output.detach()) ** 2).mean()

        # quantized_x = input_x + (output - input_x).detach()

        return output, encoding_indices, distance

    def embedding(self, x, y):
        input_x = torch.concat((x, y), -1)
        return input_x

    def forward(self, x, y, t = "Middle"):
        input_x = self.embedding(x, y)
        if t == "Middle":
            return self.forwardMiddle(input_x)
        else:
            return self.forwardBig(input_x)

    def forwardMiddle(self, input_x):
        feature = self.fc(input_x).reshape(1, self.ndf*8, int(self.data_shape/16), int(self.data_shape/16), int(self.data_shape/16))
        output = self.decoder(feature)
        output = self.toVoxelMd(output)
        output = output.view(1,1,self.data_shape,self.data_shape,self.data_shape)

        return output
    def forwardBig(self, input_x):
        feature = self.fc(input_x).reshape(1, self.ndf*8, int(self.data_shape/16), int(self.data_shape/16), int(self.data_shape/16))
        output = self.decoder(feature)
        output = self.toVoxelBig(output)
        output = output.view(1,1,self.data_shape*2,self.data_shape*2,self.data_shape*2)

        return output

    def codes(self):
        return self.latent_vectors

import torch.nn as nn
from einops import rearrange

class Utils_network:
    @staticmethod
    def weights_init(m):
        classname = m.__class__.__name__
        if hasattr(m, 'weight') and (classname.find('Conv') != -1 or classname.find('Linear') != -1):
            nn.init.normal_(m.weight.data, 0.0, 0.02)
        elif classname.find('BatchNorm') != -1:
            nn.init.normal_(m.weight.data, 1.0, 0.02)
            nn.init.constant_(m.bias.data, 0)

    @staticmethod
    def set_requires_grad(net, requires_grad=False):
        """Set requies_grad=Fasle for all the networks to avoid unnecessary computations
        Parameters:
            nets (network list)   -- a list of networks
            requires_grad (bool)  -- whether the networks require gradients or not
        """
        for param in net.parameters():
            param.requires_grad = requires_grad

    @staticmethod
    def set_decoder_requires_grad(net, t, requires_grad=False):
        for name, param in net.named_parameters():
            if t == "Middle" and ("decoder" in name):
                    param.requires_grad = requires_grad
            if t == "all":
                param.requires_grad = requires_grad
            if "cookbook" in name:
                    param.requires_grad = False
        net.latent_vectors.requies_grad = requires_grad



    #    kernel_size=3,
    #    stride=1,
    #    padding=1)


    # embed_dim: 256
    # n_embed: 512
    # ddconfig:
    #   double_z: False
    #   z_channels: 256
    #   resolution: 64
    #   in_channels: 1
    #   out_ch: 1
    #   ch: 64


      # ch_mult: [1,1,2,2,4]  # num_down = len(ch_mult)-1
    #   ch_mult: [1,2,2,4]  # num_down = len(ch_mult)-1
        # self.cube_size = 2 ** n_down # patch_size
        # nC = resolution
        # self.cube_size = 2 ** n_down # patch_size
        # self.stride = self.cube_size
        # self.ncubes_per_dim = nC // self.cube_size
        # assert nC == 64, 'right now, only trained with sdf resolution = 64'
        # assert (nC % self.cube_size) == 0, 'nC should be divisable by cube_size'

    @staticmethod
    # def unfold_to_cubes(self, x, cube_size=8, stride=8):
    def unfold_to_cubes(x, cube_size=16, stride=16):
        """ 
            assume x.shape: b, c, d, h, w 
            return: x_cubes: (b cubes)
        """
        # print(" before unfold",x.shape)
        x_cubes = x.unfold(2, cube_size, stride).unfold(3, cube_size, stride).unfold(4, cube_size, stride)
        # print(" 1 unfold",x_cubes.shape)
        x_cubes = rearrange(x_cubes, 'b c p1 p2 p3 d h w -> b c (p1 p2 p3) d h w')
        # print(" 2 unfold",x_cubes.shape)
        x_cubes = rearrange(x_cubes, 'b c p d h w -> (b p) c d h w')
        # print(" after unfold",x_cubes.shape)

        return x_cubes

    @staticmethod
    # def fold_to_voxels(self, x_cubes, batch_size, ncubes_per_dim):
    def fold_to_voxels(x_cubes, batch_size, ncubes_per_dim):

        # print(" before fold",x_cubes.shape, batch_size)
        x = rearrange(x_cubes, '(b p) c d h w -> b p c d h w', b=batch_size) 
        # print(" fold",x.shape)
        x = rearrange(x, 'b (p1 p2 p3) c d h w -> b c (p1 d) (p2 h) (p3 w)',
                        p1=ncubes_per_dim, p2=ncubes_per_dim, p3=ncubes_per_dim)
        # print(" after fold",x.shape)
        return x

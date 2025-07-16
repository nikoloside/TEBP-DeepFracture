# Copy and just rewrite the parameters
import argparse
from Utils.utils_config import get_training_config

class Parser:
    def __init__(self):
        parser = argparse.ArgumentParser()
        # About Training
        parser.add_argument("--start_epoch", type=int, default=1, help="number of epochs of start training")
        parser.add_argument("--end_epoch", type=int, default=2000, help="number of epochs of end training")
        
        # Model Parameters
        parser.add_argument("--batch_size", type=int, default=1, help="size of the batches")
        parser.add_argument("--ndf", type=int, default=64, help="ndf default 64")
        parser.add_argument("--lr", type=float, default=0.000005, help="learning rate after 400 epoch, fist epoch is 0.002")
        parser.add_argument("--n_cpu", type=int, default=8, help="number of cpu threads to use during batch generation")

        # Network Details
        parser.add_argument("--z_latent_dim", type=int, default=8, help="dimensionality of the z latent space, 0 represent no latent dim")
        parser.add_argument("--pos_encode_dim", type=int, default=128, help="dimensionality of the x, y, z pos encode")
        parser.add_argument("--data_shape", type=int, default=128, help="dimensionality of data shape(shape, shape, shape)")
        parser.add_argument("--clusters_num", type=int, default=32, help="clusters num of total data")

        # Saving Details
        parser.add_argument("--sample_interval", type=int, default=50, help="interval between visualization epoches")
        parser.add_argument("--model_save_interval", type=int, default=200, help="interval between model stock epoches")

        # Training Details
        parser.add_argument("--phase", type=str, default="train", help="test phase not implemented yet")
        parser.add_argument('--save_bool', action='store_false', help='default true, if true, save the model')
        parser.add_argument('--continue_train', action='store_true', help='default false, if true, load the model')

        # Experiment Details
        parser.add_argument('--save_path', type=str, default="/nashome/******/Workspace/inputMap-result/", help="savepath")
        parser.add_argument('--projName', type=str, default="squirrel", help="projName")
        parser.add_argument('--runName', type=str, default="squirrel-VQVAE-0/", help="Run Name")
        parser.add_argument('--log_wandb', type=bool, default=True, help="default False，Enable wandb log")

        # DataSet Details
        parser.add_argument("--dataroot", type=str, default="/data/data-vox/_out_squirrel/", help="datapath")
        parser.add_argument("--workspace", type=str, default="/data/data-vox/", help="datapath")
        parser.add_argument('--nThreads', default=2, type=int, help='# threads for loading data')
        parser.add_argument('--serial_batches', action='store_true', help='default false, takes images in order to make batches. Otherwise takes them randomly if true.')
        parser.add_argument('--train_dataset_size', type=int, default=1, help='Maximum number of training sample allowed per dataset.')
        parser.add_argument('--train_cookbook_size', type=int, default=1, help='Maximum number of training sample allowed per dataset.')
        parser.add_argument('--test_dataset_size', type=int, default=0, help='How many test data will be loaded in dataset.')

        self.opt = parser

    def getOpt(self):
        config = get_training_config()
        opt = self.opt.parse_args()
        opt.projectName = "DeepFracture-demo"
        opt.architecture = "VQ-VAE"
        opt.description = "original-loss"
        opt.save_path = config.get("save_path", "/nashome/yhuang/yhuang/Workspace/inputMap-result/")
        opt.dataroot = config.get("dataroot", "/data/data-vox/_out_squirrel/")
        opt.runName = config.get("runName", "squirrel-VQVAE-0/")
        opt.projName = config.get("projName", "squirrel")
        opt.log_wandb = config.get("log_wandb", False)
        opt.use_cuda = config.get("use_cuda", True)
        opt.max_impulse = config.get("max_impulse", 304527)
        opt.train_dataset_size = config.get("train_dataset_size", 250)
        opt.train_cookbook_size = config.get("train_cookbook_size", 250)
        opt.test_dataset_size = config.get("test_dataset_size", 50)

        return opt

# import pymesh
import numpy as np
import nibabel as nib
import igl
import vedo as vd

def get_from_nib(file_name):
    img = nib.load(file_name)
    data = img.get_fdata() # Get the data object
    return data

# # path = "/Users/yuhanghuang/Dropbox/TempData/VQPoC/VQ-PG/test_epoch_250_ind_454-vq-poc-303-big.nii"
# path = "/Users/yuhanghuang/Dropbox/TempData/VQPoC/cook/pureVdb/test_epoch_950_ind_339-vq-poc-169.nii"
# path = "data/nii/VQ-PG/test_epoch_800_ind_454-vq-poc-303-big.nii"
# temp = "./data/"

# data = get_from_nib(path)
# vol = vd.Volume(data).isosurface(0.02)
# scale = 1/256*2.2
# vol = vol.shift(-128, -128, -128).scale(scale, scale, scale).rotate_x(180).rotate_y(-90).rotate_z(90)

ori = vd.Mesh('data/squirrel.obj').shift(2, 0, 0)
vol_1 = vd.Mesh('data/vol_1_1seg.obj').shift(-2, 0, 0).split()
vol_2 = vd.Mesh('data/vol_2_seg.obj').split()


vd.show(vol_1,vol_2, ori, axes=1)

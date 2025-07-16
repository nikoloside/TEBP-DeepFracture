
import nibabel as nib
import h5py
from PIL import Image
import numpy as np
from .animator3d import MedicalImageAnimator
import matplotlib.pyplot as plt

def get_from_h5py(file_name):
    data = h5py.File(file_name, 'r').get('data')[()]
    if len(data.shape) > 3:
        data = data[0,0,:,:,:]
    return data

def get_from_nib(file_name):
    img = nib.load(file_name)
    data = img.get_fdata() # Get the data object
    return data

def get_from_gif(file_name):
    data = plt.imread('image_file.gif') 
    return data

def save_as_h5py(file_name, variable):
    h5f = h5py.File(file_name, 'w')
    h5f.create_dataset('data', data=variable)
    h5f.close()

def save_as_nib(file_name, variable):
    ni_img = nib.Nifti1Image(variable, affine=np.eye(4))
    nib.save(ni_img, file_name)

def save_as_gif(file_name, data):
    animator = MedicalImageAnimator(data, [], 0, save=True)
    animate = animator.run(file_name)

def save_as_img(file_name, variable):
    data = variable[:,:,64]
    print(data)
    min = data.min()
    size = max(1, data.max() - data.min())
    data = (data + (0-min))/size
    print(np.uint8(data * 255))
    img = Image.fromarray(np.uint8(data * 255), 'L')
    img.save(file_name)
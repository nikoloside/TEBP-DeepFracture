import os
import numpy as np
import igl
import h5py
from scipy.ndimage import zoom
import yaml
from commonLib.animator3d import MedicalImageAnimator
import matplotlib.pyplot as plt

maxDist = 0
minDist = 0

def save_as_h5py(file_name, variable):
    h5f = h5py.File(file_name, 'w')
    h5f.create_dataset('data', data=variable)
    h5f.close()

def save_as_gif(file_name, data):
    animator = MedicalImageAnimator(data, [], 0, save=True)
    animate = animator.run(file_name)

def create_sdf_vox(obj_path, size=128, sizej=128j):

    # Read mesh
    V, F = igl.read_triangle_mesh(obj_path)

    minV = -1
    maxV = 1

    # convert
    x, y, z = np.mgrid[minV:maxV:sizej, minV:maxV:sizej, minV:maxV:sizej]
    positions = np.dstack([x.ravel(), y.ravel(),z.ravel()])

    s, i, c = igl.signed_distance(positions.squeeze(),V,F,igl.SIGNED_DISTANCE_TYPE_WINDING_NUMBER,False)

    s_3d = s.reshape((size,size,size))
    return -s_3d
    

def process_category(category_path, output_path):
    # Create output directories if they don't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Create seg and gif subfolders in output path
    output_seg_path = os.path.join(output_path, "seg")
    output_gif_path = os.path.join(output_path, "gif")
    os.makedirs(output_seg_path, exist_ok=True)
    os.makedirs(output_gif_path, exist_ok=True)
    
    # Create category directory if it doesn't exist
    os.makedirs(category_path, exist_ok=True)
    
    for obj_file in os.listdir(category_path):
        if obj_file.endswith('.obj'):
            obj_path = os.path.join(category_path, obj_file)
            print(f"Processing {obj_file}...")
            
            # Check if seg and gif files already exist
            obj_name = obj_file.replace('.obj', '')
            seg_path = os.path.join(output_seg_path, obj_name + ".seg")
            gif_path = os.path.join(output_gif_path, obj_name + ".gif")
            
            if os.path.exists(seg_path) and os.path.exists(gif_path):
                print(f"Skipping {obj_file} as both seg and gif files already exist")
                continue

            # Create SDF voxel grid
            sdf = create_sdf_vox(obj_path)
            
            save_as_h5py(seg_path, sdf)
            print(f"Saved input.seg to {seg_path}")
            
            # Save as GIF
            save_as_gif(gif_path, sdf)
            print(f"Saved GIF to {gif_path}")

            maxValue = np.max(sdf)
            minValue = np.min(sdf)
            print(maxValue, minValue)
            # if maxValue > maxDist:
            #     maxDist = maxValue

            # if minValue < minDist:
            #     minDist = minValue

if __name__ == "__main__":
    with open("./config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    category_path = os.path.join(config['data_norm_path'], config['shape_category'])
    output_path = os.path.join(config['data_inputSdf_path'], config['shape_category'])
    process_category(category_path, output_path)

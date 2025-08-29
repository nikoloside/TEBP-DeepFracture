import numpy as np
import os
import glob
import shutil
import datetime
import yaml
import re
from typing import Optional, Tuple
import igl
import nibabel as nib

# Import individual functions from commonLib
from commonLib.commonLib import (
    get_from_h5py, get_from_nib, get_from_gif,
    save_as_h5py, save_as_nib, save_as_gif, save_as_img
)

from commonLib.encoder_lib import (
    compute_sdf, save_sdf_to_nifti, split_components, 
    compute_component_sdf, save_slice_as_gif, analyze_sdf
)


def pack_sdf_with_position_encoding(SDF: np.ndarray, max_point: Optional[Tuple[float, float, float]] = None, 
                                  type: int = 1, normalize: bool = True) -> np.ndarray:
    """
    Pack SDF into a single channel volume
    
    Args:
        SDF (np.ndarray): Input SDF volume
        max_point (Optional[Tuple[float, float, float]]): Not used, kept for compatibility
        type (int): Not used, kept for compatibility
        normalize (bool): Whether to normalize the SDF values
        
    Returns:
        np.ndarray: Single channel SDF volume
    """
    # Get positive points mask
    positive_mask = SDF > 0
    
    # Normalize SDF
    max_sdf = np.max(SDF[positive_mask])
    normalized_sdf = SDF / max_sdf

    # Create single channel output
    packed_data = np.zeros((SDF.shape[0], SDF.shape[1], SDF.shape[2], 1))
    packed_data[..., 0] = normalized_sdf

    return packed_data

def encode_obj_to_nii(obj_path: str, encoding_type: int = 1, grid_size: int = 128, grid_sizej=128j, normalize: bool = True, withMinus: bool = True) -> None:
    """
    Encode OBJ file to a single-channel NIfTI file with SDF values
    
    Args:
        obj_path (str): Path to input OBJ file
        output_path (str): Path to output NIfTI file
        encoding_type (int): Not used, kept for compatibility
        grid_size (int): Size of the output volume grid
        normalize (bool): Whether to normalize the SDF values
        withMinus (bool): Whether to include negative values in the encoding
    """
    # Split mesh into components
    component_data = split_components(obj_path)
    
    # Compute full SDF for the entire model
    full_sdf_data = compute_sdf(obj_path, grid_size)
    full_SDF, _, _, _ = full_sdf_data
    
    # Initialize combined packed data
    combined_packed_data = np.zeros((grid_size, grid_size, grid_size, 1))
    filled_mask = np.zeros((grid_size, grid_size, grid_size), dtype=bool)
    
    # Process each component
    for vertices, faces in component_data:
        # Compute SDF for this component
        sdf_data = compute_component_sdf(vertices, faces, grid_size, grid_sizej)
        SDF, _, _, _ = sdf_data
        
        # Analyze SDF to get max point
        _, max_point = analyze_sdf(SDF)
        if max_point is None:
            continue
            
        # Pack SDF with position encoding
        packed_data = pack_sdf_with_position_encoding(SDF, max_point, type=encoding_type, normalize=normalize)

        # Combine packed data
        positive_mask = SDF > 0
        
        # For positions that haven't been filled yet, use current component's data
        new_positions = positive_mask & ~filled_mask
        combined_packed_data[..., 0][new_positions] = packed_data[..., 0][new_positions]
        
        # For overlapping positions, take the maximum value
        overlap_positions = positive_mask & filled_mask
        if np.any(overlap_positions):
            print(f"Overlap detected at positions: {np.sum(overlap_positions)}")
            quit
        
        # Update filled mask
        filled_mask |= positive_mask
    
    negative_mask = full_SDF < 0
    overlap_positions = negative_mask & ~filled_mask

    combined_packed_data[..., 0][overlap_positions] = full_SDF[overlap_positions]

    if not withMinus:
        combined_packed_data[combined_packed_data < 0] = 0
            
    
    return combined_packed_data

# Load config
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils_config import load_config

config = load_config()

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def convert(v, f, typec, size=256, sizej=256j):
    # calc sdf
    minV = -1
    maxV = 1

    # convert
    x, y, z = np.mgrid[minV:maxV:sizej, minV:maxV:sizej, minV:maxV:sizej]
    positions = np.dstack([x.ravel(), y.ravel(),z.ravel()])

    s = igl.signed_distance(positions.squeeze(),v,f,typec,False)[0]

    s_3d = s.reshape((size,size,size))

    return s_3d

def normalizeSeg_sdf(s_3d):
    return -s_3d

def main():
    maxDist = 0
    minDist = 0
    maxValue = 0  # Initialize maxValue
    minValue = 0  # Initialize minValue
    startTime = datetime.datetime.now()

    projectList = [config['shape_category']]

    folderPath = config['data_dataset_path'] # v2.0
    inputSaveFolder = config['data_input_path']
    outputSaveFolder = config['data_output_path']

    # Dynamically get spcList from subfolders in folderPath
    def get_spc_list(folder_path):
        """Get list of subfolders that match spc pattern"""
        if not os.path.exists(folder_path):
            print(f"Warning: {folder_path} does not exist")
            return []
        
        subfolders = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path) and (item.startswith('spc') or item.startswith('dpc')):
                subfolders.append(item + '/')
        
        return sorted(subfolders)

    spcList = get_spc_list(folderPath)
    print(f"Found spc folders: {spcList}")

    index = 0
    for project in projectList:
        objName = "obj_target"
        inputSavePath = os.path.join(inputSaveFolder, project)
        outputSavePath = os.path.join(outputSaveFolder, project)
        os.makedirs(inputSavePath, exist_ok=True)
        os.makedirs(outputSavePath, exist_ok=True)
        for spcName in spcList:
            spcPath = os.path.join(folderPath, spcName, project)

            fileExist = glob.glob(spcPath + "*")

            if len(fileExist) <= 0:
                print(fileExist, " not exist, skip.")
                continue

            os.makedirs(os.path.join(outputSavePath, "gssdf"), exist_ok=True)
            os.makedirs(os.path.join(outputSavePath, "ffbdf"), exist_ok=True)
            os.makedirs(os.path.join(outputSavePath, "obj"), exist_ok=True)
            os.makedirs(os.path.join(inputSavePath, "csv"), exist_ok=True)
            os.makedirs(os.path.join(inputSavePath, "impact"), exist_ok=True)
            os.makedirs(os.path.join(inputSavePath, "info"), exist_ok=True)

            targetList = objList=sorted(glob.glob(os.path.join(spcPath, "out_vdb", "*.obj")), key=os.path.getmtime)
            print(spcPath)

            for target in targetList:
                expTime = os.path.basename(target).split(".")[0]
                index += 1

                fileExist = glob.glob(os.path.join(outputSavePath, "obj", str(index) + ".obj"))

                if len(fileExist) > 0:
                    print(fileExist, " exist skip.")
                    continue

                # Write Output
                print(target)
                v, f = igl.read_triangle_mesh(target)

                # 128
                # SIGNED_DISTANCE_TYPE_UNSIGNED for usdf
                # SIGNED_DISTANCE_TYPE_WINDING_NUMBER for sdf
                s_3d = convert(v, f, igl.SIGNED_DISTANCE_TYPE_FAST_WINDING_NUMBER, 128, 128j)
                s_3d = normalizeSeg_sdf(s_3d)

                niiPath = os.path.join(outputSavePath, "gssdf", str(index) + ".nii")
                gifPath = os.path.join(outputSavePath, "gssdf", str(index) + ".gif")
                ffbdfPath = os.path.join(outputSavePath, "ffbdf", str(index) + ".nii")
                ffbdfGifPath = os.path.join(outputSavePath, "ffbdf", str(index) + ".gif")

                # Save GSSDF (Global Signed Distance Field)
                save_as_nib(niiPath, s_3d)
                save_as_gif(gifPath, s_3d)
                
                # Compute and save FFBDF (Fracture Fragment Boundary Distance Field)
                ffbdf_3d = encode_obj_to_nii(target, normalize=True)
                save_as_nib(ffbdfPath, ffbdf_3d)
                save_as_gif(ffbdfGifPath, ffbdf_3d)

                maxValue = np.max(s_3d)
                if maxValue > maxDist:
                    maxDist = maxValue

                minValue = np.min(s_3d)
                if minValue < minDist:
                    minDist = minValue

                print("max value ", maxDist, maxValue)
                print("min value ", minDist, minValue)

                # Write Csv
                fromCsvPath = os.path.join(spcPath, "csv", str(expTime) + ".csv")
                csvPath = os.path.join(inputSavePath, "csv", str(index) + ".csv")
                shutil.copyfile(fromCsvPath, csvPath)

                # Write Obj
                fromObjPath = os.path.join(spcPath, "out_vdb", str(expTime) + ".obj")
                objPath = os.path.join(outputSavePath, "obj", str(index) + ".obj")
                shutil.copyfile(fromObjPath, objPath)

                # Write Impact
                expPath = os.path.join(spcPath, str(expTime))
                print(expPath, os.path.join(expPath, objName + "-*-impact-fractured.txt"))
                fracturedCsvNameList = sorted(glob.glob(os.path.join(expPath, objName + "-*-impact-fractured.txt")), key=natural_keys)
                csvNameList = sorted(glob.glob(os.path.join(expPath, objName + "-*-impact.txt")), key=natural_keys)
                jsonName = os.path.join(inputSavePath, "impact", str(index) + ".txt")
                csvName = ""

                if (len(csvNameList)):
                    csvName = csvNameList[0]
                if (len(fracturedCsvNameList)):
                    csvName = fracturedCsvNameList[0]
                if csvName == "":
                    continue
                print(fracturedCsvNameList)
                print(csvName)

                lineCount = 0
                with open(csvName) as old, open(jsonName, 'w') as new:
                    oldLines = old.readlines()
                    if oldLines[0].find("[") == 0:
                        for line in oldLines:
                            newLine = line.replace("\n","")
                            new.write(newLine)
                            lineCount += 1
                    else:
                        for line in oldLines:
                            newLine = line.replace("\n","")
                            if(lineCount == 0):
                                newLine = "[" + newLine
                            if (lineCount >= len(oldLines) - 1):
                                newLine = newLine + "]\n"
                            else:
                                newLine = newLine + ",\n"
                            new.write(newLine)
                            lineCount += 1

                # Write Info
                infoPath = os.path.join(inputSavePath, "info", str(index) + ".txt")
                with open(infoPath, 'w') as newInfo:
                    newInfo.write(spcName + "," + str(expTime))

                # break

        stopTime = datetime.datetime.now()
        logPath = os.path.join(outputSavePath, project + "-maxmin.txt")
        with open(logPath, 'w') as log:
            log.write("max value: %f, %f " % (maxDist, maxValue))
            log.write(", min value: %f, %f " % (minDist, minValue))
            log.write(", start: %s" % (startTime.strftime("%Y-%m-%dT%H:%M:%S%z")))
            log.write(", stop: %s" % (stopTime.strftime("%Y-%m-%dT%H:%M:%S%z")))

    print("Finish")

if __name__ == "__main__":
    main()

import os
import numpy as np
import nibabel as nib
import shutil

def get_from_nib(file_name):
    img = nib.load(file_name)
    data = img.get_fdata() # Get the data object
    return data

def save_as_nib(file_name, variable):
    ni_img = nib.Nifti1Image(variable, affine=np.eye(4))
    nib.save(ni_img, file_name)


def getMaskForSdf(data):
    mask = data.copy()
    mask[data >= 0] = 1 # Interior region
    mask[data < 0] = 0 # Exterior
    return mask
    

def getNormForSdf(data):
    sdf = data.copy()
    print(sdf.min(), sdf.max())
    sdf[sdf < 0] *= -1 # Interior region
    # data = (data + gapRange) * innerRange
    sdf = 255 - (sdf + 1) / 2 * 255
    print(sdf.min(), sdf.max())
    return sdf
#endregion

#region Prepare segmentation
def processCagedSDFSeg(data_ori, work_path, obj_path, isBig = True, maxValue = 1.0):
    import yaml
    
    # Read config.yaml
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils_config import load_config

    config = load_config()
    sourcePath = config["fiji_path"]
    
    # Check if Fiji path exists
    if not os.path.exists(sourcePath):
        error_msg = f"Fiji path does not exist: {sourcePath}"
        print(f"ERROR: {error_msg}")
        raise FileNotFoundError(error_msg)
    
    #region Import section
    try:
        import imagej
    except ImportError as e:
        error_msg = f"ImageJ Python module not found. Please install it with: pip install imagej\nError: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise ImportError(error_msg)
    
    try:
        ij = imagej.init(sourcePath, mode="headless")
        print(f"ImageJ initialized successfully. Version: {ij.getVersion()}")
    except Exception as e:
        error_msg = f"Failed to initialize ImageJ with path: {sourcePath}\nError: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)

    if isBig == 2:
        isolevel = 0.03 / maxValue
        resolution = 256
        shift = resolution / 2
        filtNoisy = 500
        min_meshes = 400

    if isBig == 1:
        isolevel = 0.03 / maxValue
        resolution = 128
        shift = resolution / 2
        filtNoisy = 50
        min_meshes = 200

    if isBig == 0:
        isolevel = 0.03 / maxValue
        resolution = 64
        shift = resolution / 2
        filtNoisy = 50
        min_meshes = 50
        

    data = data_ori.copy()
    data = data + isolevel

    mask = getMaskForSdf(data)
    discrete = getNormForSdf(data)

    dataset = ij.py.to_java(discrete)
    #endregion

    #region Perform segmentation
    print("Start SegmentationProcess")
    script = """
    // @ImagePlus(label="Input image", description="Image to segment") imp
    // @OUTPUT ImagePlus resultImage

    import ij.IJ;
    import ij.ImagePlus;
    import ij.ImageStack;
    import inra.ijpb.binary.BinaryImages;
    import inra.ijpb.morphology.MinimaAndMaxima3D;
    import inra.ijpb.morphology.Morphology;
    import inra.ijpb.morphology.Strel3D;
    import inra.ijpb.watershed.Watershed;

    print("heeeeeeee");

    radius = 2;
    tolerance = 3;
    strConn = "6";
    dams = true;

    conn = Integer.parseInt( strConn );


    image = imp.getImageStack().duplicate();
    regionalMinima = MinimaAndMaxima3D.extendedMinima( image, tolerance, conn );
    imposedMinima = MinimaAndMaxima3D.imposeMinima( image, regionalMinima, conn );
    labeledMinima = BinaryImages.componentsLabeling( regionalMinima, conn, 32 );
    resultStack = Watershed.computeWatershed( imposedMinima, labeledMinima, conn, dams );
    
    resultImage = new ImagePlus( "watershed", resultStack );
    resultImage.setCalibration( imp.getCalibration() );
    """
    imp = ij.py.to_imageplus(dataset)
    args = {"imp": imp}
    import time
    time_start = time.time()
    result = ij.py.run_script("BeanShell", script, args)
    resultImp = result.getOutput("resultImage")
    time_end = time.time()
    with open(os.path.join(work_path, "log-FloodSeg.txt"), "a") as log_file:
        log_file.write(f"Segmentation Process time: {time_end - time_start:.2f} seconds\n")


    xr = ij.py.from_java(resultImp)

    import vedo as vd

    xr = np.array(xr)
    xr[mask == 0] = -1


    unique, counts = np.unique(xr, return_counts=True)
    for value in unique[counts < filtNoisy]:
        xr[xr == int(value)] = -1

    save_as_nib(os.path.join(work_path, "imj.nii"), xr)

    vol_1 = vd.Volume(xr).isosurface(isolevel).smooth()
    scale = 1/resolution*2
    vol_1 = vol_1.scale(scale).shift(-1, -1, -1).rotate_x(180).rotate_y(-90).rotate_z(90)

    os.makedirs(os.path.join(work_path, "seg"), exist_ok=True)
    vol_1.write(os.path.join(work_path, "seg/vol_1.obj"))

    # !!! Perform separate segmentation
    # vols_1 = vol_1.split()
    # count = 1
    # for vol in vols_1:
    #     vol.write(work_path + 'seg/vol_1_%d.obj' % (count))
    #     count+=1

    # !!! Direct isosurface restoration, no segmentation needed
    # vol_2 = vd.Volume(data_ori).isosurface(isolevel - 0.003)
    # scale = 1/resolution*2
    # vol_2 = vol_2.shift(-shift, -shift, -shift).scale(scale).rotate_x(180).rotate_y(-90).rotate_z(90)
    # vol_2.write('/Users/path/to/vol_2.obj')

    # ori = vd.Mesh(work_path + "squirrel.obj")

    os.makedirs(os.path.join(work_path, "out"), exist_ok=True) 
    os.makedirs(os.path.join(work_path, "objs"), exist_ok=True) 
    outputFolder = os.path.join(work_path, "out/*.obj")

    source_runtime_path = config['source_runtime_path']
    
    if not config['use_houdini']:
        #region python
        from MeshBoolean.pyMeshBool import process_mesh_split_boolean
        import glob
        inputFolder = os.path.join(work_path, "seg/*.obj")
        files = glob.glob(inputFolder)
        if len(files) == 0:
            raise FileNotFoundError("Error: No files found in the seg folder.")
        input_obj_a = files[0]
        input_obj_b = obj_path
        output_dir = os.path.join(work_path, "objs")
        process_mesh_split_boolean(
            input_obj_a, input_obj_b, output_dir, min_meshes, use_parallel = False
        )
        
        #endregion
    else:
        #region houdini
        import subprocess
        
        houdini_path = config['houdini_path']
        
        # Check if Houdini path exists
        if not os.path.exists(houdini_path):
            error_msg = f"Houdini path does not exist: {houdini_path}"
            print(f"ERROR: {error_msg}")
            raise FileNotFoundError(error_msg)
        
        # Check if Houdini Python executable is actually executable
        if not os.access(houdini_path, os.X_OK):
            error_msg = f"Houdini path is not executable: {houdini_path}"
            print(f"ERROR: {error_msg}")
            raise PermissionError(error_msg)
        
        file_path = os.path.join(source_runtime_path, "MeshBoolean/houdini_process.py")
        python_path = houdini_path

        # Check if Houdini process file exists
        if not os.path.exists(file_path):
            error_msg = f"Houdini process file does not exist: {file_path}"
            print(f"ERROR: {error_msg}")
            raise FileNotFoundError(error_msg)

        # Check if input obj file exists
        if not os.path.exists(obj_path):
            error_msg = f"Input obj file does not exist: {obj_path}"
            print(f"ERROR: {error_msg}")
            raise FileNotFoundError(error_msg)

        print("Start Houdini process: ", python_path, file_path, work_path, obj_path)
        args = (python_path, file_path, work_path, obj_path)
        
        try:
            # Run Houdini process with timeout and capture output
            result = subprocess.run(args, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True, 
                                timeout=300)  # 5 minute timeout
            
            if result.returncode != 0:
                error_msg = f"Houdini process failed with return code {result.returncode}\n"
                error_msg += f"STDOUT: {result.stdout}\n"
                error_msg += f"STDERR: {result.stderr}"
                print(f"ERROR: {error_msg}")
                raise RuntimeError(error_msg)
            else:
                print("Houdini process completed successfully")
                if result.stdout:
                    print("Houdini output:", result.stdout)
                
        except subprocess.TimeoutExpired:
            error_msg = "Houdini process timed out after 5 minutes"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Houdini process failed: {str(e)}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        #endregion

        import glob
        files = glob.glob(outputFolder)
        
        # Check if no files were found
        if len(files) == 0:
            error_msg = f"No output files found in: {outputFolder}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        
        print(f"Found {len(files)} output files to process")
        vols = []
        count = 1
        for file in files:
            vol = vd.Mesh(file).split()
            print(len(vol))
            vols.append(vol)
            for v in vol:
                if len(v.cells) >= min_meshes:
                    path = os.path.join(work_path, "objs/vol_%d.obj" % (count))
                    print(path)
                    v.write(path)
                    count += 1

def main():
    data_ori = get_from_nib('/Users/path/to/test_case/test_epoch_800_ind_453-vq-poc-351-big.nii')
    work_path = "/Users/path/to/run-time/squirrel-2/"

    import glob

    os.makedirs(work_path, exist_ok=True) 

    clean_folder = work_path + "*"
    files = glob.glob(clean_folder)
    if len(files) > 0:
        shutil.rmtree(work_path) 
        os.makedirs(work_path, exist_ok=True) 

    obj_path = "/Users/path/to/squirrel.obj"
    processCagedSDFSeg(data_ori, work_path, obj_path, True, 1.0)
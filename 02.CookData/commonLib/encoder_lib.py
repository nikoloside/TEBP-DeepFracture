import igl
import numpy as np
import nibabel as nib
import os
from vedo import load, merge, Volume, show
from typing import List, Tuple, Dict, Union, Optional
import imageio
from scipy.ndimage import zoom

def compute_sdf(obj_path, grid_size=128, grid_sizej=128j):
    """
    Convert OBJ mesh to SDF volume
    
    Args:
        obj_path (str): Path to input OBJ file
        grid_size (int): Size of the output volume grid
        
    Returns:
        tuple: (SDF volume, grid_spacing, bbox_center, bbox_size)
    """
    # Read the OBJ file
    V, F = igl.read_triangle_mesh(obj_path)

    # Create a grid for SDF computation with fixed bbox [-1, 1]
    bbox_min = np.array([-1, -1, -1])
    bbox_max = np.array([1, 1, 1])
    bbox_center = np.array([0, 0, 0])
    bbox_size = 2  # Distance from -1 to 1
    grid_spacing = bbox_size / grid_size


    minV = -1
    maxV = 1
    X, Y, Z = np.mgrid[minV:maxV:grid_sizej, minV:maxV:grid_sizej, minV:maxV:grid_sizej]
    grid_points = np.dstack([X.ravel(), Y.ravel(), Z.ravel()])

    # Compute SDF using winding number
    S = igl.signed_distance(grid_points.squeeze(), V, F, igl.SIGNED_DISTANCE_TYPE_FAST_WINDING_NUMBER, False)[0]

    # Reshape SDF to 3D grid
    SDF = S.reshape(grid_size, grid_size, grid_size)
    SDF = -SDF

    return SDF, grid_spacing, bbox_center, bbox_size

def save_sdf_to_nifti(SDF, nii_path, grid_spacing, bbox_center, bbox_size):
    """
    Save SDF volume to NIfTI file
    
    Args:
        SDF (numpy.ndarray): SDF volume data
        nii_path (str): Path to output NIfTI file
        grid_spacing (float): Spacing between grid points
        bbox_center (numpy.ndarray): Center of the bounding box
        bbox_size (float): Size of the bounding box
    """
    # Create NIfTI image
    affine = np.eye(4)
    affine[0,0] = grid_spacing
    affine[1,1] = grid_spacing
    affine[2,2] = grid_spacing
    affine[:3,3] = bbox_center - bbox_size/2

    nii_img = nib.Nifti1Image(SDF, affine)
    nib.save(nii_img, nii_path)

def split_components(obj_path: str) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Split OBJ mesh into connected components using vedo
    
    Args:
        obj_path (str): Path to input OBJ file
        
    Returns:
        List[Tuple[np.ndarray, np.ndarray]]: List of (vertices, faces) for each component
    """
    # Load mesh using vedo
    mesh = load(obj_path)
    
    # Split into connected components
    components = mesh.split()
    print(f"Found {len(components)} components")
    # Extract vertices and faces for each component
    component_data = []
    for comp in components:
        # Get vertices and faces as numpy arrays
        vertices = np.array(comp.points)
        faces = np.array(comp.cells)
        
        # Ensure faces are properly formatted (should be Nx3 array)
        if len(faces.shape) == 1:
            faces = faces.reshape(-1, 3)
        
        component_data.append((vertices, faces))
    
    return component_data

def compute_component_sdf(vertices: np.ndarray, faces: np.ndarray, grid_size: int = 128, grid_sizej=128j) -> Tuple[np.ndarray, float, np.ndarray, float]:
    """
    Compute SDF for a single component
    
    Args:
        vertices (np.ndarray): Vertices of the component
        faces (np.ndarray): Faces of the component
        grid_size (int): Size of the output volume grid
        
    Returns:
        Tuple: (SDF, grid_spacing, bbox_center, bbox_size)
    """
    # Create a temporary OBJ file for this component
    temp_obj = "/tmp/temp_component.obj"
    igl.write_triangle_mesh(temp_obj, vertices, faces)
    
    # Compute SDF for this component
    sdf_data = compute_sdf(temp_obj, grid_size, grid_sizej)
    
    # Clean up temporary file
    os.remove(temp_obj)
    
    return sdf_data

def save_slice_as_gif(volume, output_path, slice_axis=2):
    """
    Save volume slices as gif
    
    Args:
        volume (np.ndarray): 3D volume data
        output_path (str): Output gif path
        slice_axis (int): Axis to slice along (0, 1, or 2)
    """
    # Normalize to 0-255
    vmin, vmax = np.min(volume), np.max(volume)
    normalized = ((volume - vmin) / (vmax - vmin) * 255).astype(np.uint8)
    
    # Create frames
    frames = []
    for i in range(normalized.shape[slice_axis]):
        if slice_axis == 0:
            frame = normalized[i, :, :]
        elif slice_axis == 1:
            frame = normalized[:, i, :]
        else:
            frame = normalized[:, :, i]
        frames.append(frame)
    
    # Save as gif
    imageio.mimsave(output_path, frames, duration=0.1)

def analyze_sdf(SDF: np.ndarray, threshold: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
    """
    Analyze SDF volume to find centroid of positive values and max point closest to centroid
    
    Args:
        SDF (np.ndarray): SDF volume data
        threshold (float): Threshold for considering values as maximum
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: (centroid, closest_max_point) in normalized coordinates [-1, 1]
    """
    # Find positive values
    positive_mask = SDF > 0
    if not np.any(positive_mask):
        print("No positive values found in SDF")
        return None, None
    
    # Get coordinates of all positive points
    coords = np.where(positive_mask)
    points = np.stack(coords, axis=1)
    
    # Convert grid indices to normalized coordinates [-1, 1]
    grid_size = SDF.shape[0]
    normalized_points = 2 * points / grid_size - 1
    
    # Calculate centroid of positive values
    centroid = np.mean(normalized_points, axis=0)
    print(f"Centroid of positive values: {centroid}")
    
    # Find all points close to max value
    max_val = np.max(SDF)
    max_mask = np.abs(SDF - max_val) < threshold
    max_coords = np.where(max_mask)
    max_points = np.stack(max_coords, axis=1)
    
    # Convert max points to normalized coordinates
    normalized_max_points = 2 * max_points / grid_size - 1
    
    # Calculate distances to centroid for all max points
    distances = np.linalg.norm(normalized_max_points - centroid, axis=1)
    closest_idx = np.argmin(distances)
    closest_max_point = normalized_max_points[closest_idx]
    
    print(f"Max value: {max_val}")
    print(f"Number of points close to max value: {len(max_points)}")
    print(f"Closest max point to centroid: {closest_max_point}")
    print(f"Distance to centroid: {distances[closest_idx]}")
    
    return centroid, closest_max_point 
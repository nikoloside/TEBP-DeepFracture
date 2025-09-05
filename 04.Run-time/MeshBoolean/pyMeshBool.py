import numpy as np
import igl
import trimesh
import os
import vedo
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
import random

def process_mesh_boolean(trimesh_a_part, trimesh_b, part_id):
    """
    Perform boolean operations between a part of mesh A and mesh B
    Returns the intersection edges and the resulting mesh
    """
    try:
        # Check if meshes are valid volumes
        if not trimesh_a_part.is_volume:
            print(f"Part {part_id} is not a volume, attempting to make it watertight...")
            # Try to make it watertight
            trimesh_a_part = make_watertight(trimesh_a_part)
            if trimesh_a_part is None or not trimesh_a_part.is_volume:
                print(f"Part {part_id} could not be made into a valid volume, skipping...")
                return {
                    'part_id': part_id,
                    'intersection_edges': [],
                    'result_mesh': None,
                    'success': False,
                    'error': 'Mesh is not a valid volume'
                }
        
        if not trimesh_b.is_volume:
            print(f"Mesh B is not a volume, attempting to make it watertight...")
            trimesh_b = make_watertight(trimesh_b)
            if trimesh_b is None or not trimesh_b.is_volume:
                print(f"Mesh B could not be made into a valid volume")
                return {
                    'part_id': part_id,
                    'intersection_edges': [],
                    'result_mesh': None,
                    'success': False,
                    'error': 'Mesh B is not a valid volume'
                }
        
        # Perform boolean operations
        print(f"Part {part_id}: Performing intersection...")
        intersection = trimesh_a_part.intersection(trimesh_b)
        
        # Debug intersection result
        if intersection is None:
            print(f"Part {part_id}: Intersection is None - meshes may not overlap")
        elif len(intersection.vertices) == 0:
            print(f"Part {part_id}: Intersection has no vertices - meshes may not overlap")
        else:
            print(f"Part {part_id}: Intersection successful with {len(intersection.vertices)} vertices")
        
        # Collect intersection edges
        intersection_edges = []
        if intersection is not None and len(intersection.vertices) > 0:
            # Get edges from intersection mesh
            edges = intersection.edges_unique
            intersection_edges = edges.tolist()
            print(f"Part {part_id}: Found {len(intersection_edges)} intersection edges")
        
        # Create result mesh (you can modify this based on your needs)
        # For example, using intersection as the result
        result_mesh = intersection if intersection is not None else trimesh_a_part
        
        return {
            'part_id': part_id,
            'intersection_edges': intersection_edges,
            'result_mesh': result_mesh,
            'success': True
        }
        
    except Exception as e:
        print(f"Error in part {part_id}: {e}")
        return {
            'part_id': part_id,
            'intersection_edges': [],
            'result_mesh': None,
            'success': False,
            'error': str(e)
        }

def make_watertight(mesh):
    """Make mesh watertight"""
    if mesh is None:
        return None
    
    try:
        # Remove duplicate faces
        mesh.update_faces(mesh.unique_faces())
        # Remove degenerate faces
        mesh.update_faces(mesh.nondegenerate_faces())
        # Remove infinite values
        mesh.remove_infinite_values()
        # Fill holes
        mesh.fill_holes()
        # Ensure consistent winding
        mesh.fix_normals()
        # Remove unreferenced vertices
        mesh.remove_unreferenced_vertices()
        # Ensure watertight
        if not mesh.is_watertight:
            mesh.fill_holes()
            if not mesh.is_watertight:
                mesh.process(validate=True)
        return mesh
    except Exception as e:
        print(f"Error making mesh watertight: {e}")
        return mesh

def process_mesh_split_boolean(input_obj_path_a, input_obj_path_b, output_dir, min_meshes = 1, use_parallel = False):
    """
    Main function to split mesh A into n parts and perform boolean operations with mesh B
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load mesh A and B using vedo
    mesh_a = vedo.load(input_obj_path_a)
    mesh_b = vedo.load(input_obj_path_b)
    
    print(f"Loaded mesh A: {input_obj_path_a}")
    print(f"Loaded mesh B: {input_obj_path_b}")
    import time

    start_time = time.time()

    # Split mesh A into n parts using vedo split()
    mesh_a_parts = mesh_a.split()
    n_splits = len(mesh_a_parts)
    print(f"Splitting mesh A into {n_splits} parts...")
    
    print(f"Successfully split mesh A into {len(mesh_a_parts)} parts")
    
    # Convert all meshes to trimesh objects before parallel processing
    print("Converting meshes to trimesh objects...")
    trimesh_a_parts = []
    for i, part in enumerate(mesh_a_parts):
        try:
            vertices_a = np.array(part.points)
            faces_a = np.array(part.cells)
            trimesh_part = trimesh.Trimesh(vertices=vertices_a, faces=faces_a)
            
            # Check if the part is valid
            if len(trimesh_part.vertices) > 0 and len(trimesh_part.faces) > 0:
                trimesh_a_parts.append(trimesh_part)
                print(f"Converted part {i} to trimesh ({len(trimesh_part.faces)} faces)")
            else:
                print(f"Part {i} is empty, skipping...")
                
        except Exception as e:
            print(f"Error converting part {i}: {e}")
            # Skip this part instead of adding empty trimesh
    
    # Convert mesh B to trimesh
    vertices_b = np.array(mesh_b.points)
    faces_b = np.array(mesh_b.cells)
    trimesh_b = trimesh.Trimesh(vertices=vertices_b, faces=faces_b)
    print(f"Converted mesh B to trimesh ({len(trimesh_b.faces)} faces)")
    
    # Filter out invalid parts
    valid_parts = []
    for i, part in enumerate(trimesh_a_parts):
        if part is not None and len(part.vertices) > 0 and len(part.faces) > 0:
            valid_parts.append((i, part))
    
    print(f"Found {len(valid_parts)} valid parts out of {len(trimesh_a_parts)} total parts")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Splitting mesh A into parts python execution time: {elapsed_time:.2f} seconds")

    with open(os.path.join(output_dir, "log-mb-py.txt"), "w") as log_file:
        log_file.write(f"Splitting mesh A into parts python execution time: {elapsed_time:.2f} seconds\n")

    if len(valid_parts) == 0:
        print("No valid parts found, exiting...")
        return [], []
    
    # Perform parallel boolean operations
    print("Performing parallel boolean operations...")
    results = []
    
    if use_parallel:
        # Use ProcessPoolExecutor for parallel processing
        max_workers = min(len(valid_parts), mp.cpu_count(), 8)  # Limit max workers to avoid memory issues
        print(f"Using {max_workers} parallel workers")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_part = {
                executor.submit(process_mesh_boolean, part, trimesh_b, part_id): part_id 
                for part_id, part in valid_parts
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_part):
                result = future.result()
                results.append(result)
                completed += 1
                print(f"Completed part {result['part_id']} ({completed}/{len(valid_parts)})")
    else:
        for part_id, part in valid_parts:
            result = process_mesh_boolean(part, trimesh_b, part_id)
            results.append(result)
    
    
    # Sort results by part_id
    results.sort(key=lambda x: x['part_id'])
    
    # Collect all intersection edges
    all_intersection_edges = []
    successful_results = []
    
    for result in results:
        if result['success']:
            all_intersection_edges.extend(result['intersection_edges'])
            successful_results.append(result)
        else:
            print(f"Part {result['part_id']} failed: {result.get('error', 'Unknown error')}")
    
    print(f"Collected {len(all_intersection_edges)} intersection edges")
    print(f"Successfully processed {len(successful_results)} parts")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"intersection edges python execution time: {elapsed_time:.2f} seconds")
    with open(os.path.join(output_dir, "log-mb-py.txt"), "a") as log_file:
        log_file.write(f"intersection edges python execution time: {elapsed_time:.2f} seconds\n")

    # Create final shapes C through intersection operations
    print("Creating final shapes C...")
    final_shapes = []
    
    for i, result in enumerate(successful_results):
        if result['result_mesh'] is not None:
            # Make the result watertight
            watertight_mesh = make_watertight(result['result_mesh'])
            
            if watertight_mesh is not None and len(watertight_mesh.faces) >= min_meshes:
                # Save the final shape
                output_path = os.path.join(output_dir, f"vol_{i}.obj")
                watertight_mesh.export(output_path)
                final_shapes.append(watertight_mesh)
                print(f"Saved boolean result {i:03d} to {output_path}")
            else:
                print(f"Boolean result {i} could not be made watertight or has too few faces, skipping...")
        else:
            print(f"Boolean result {i} is None, skipping...")
    

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"saving objs python execution time: {elapsed_time:.2f} seconds")
    with open(os.path.join(output_dir, "log-mb-py.txt"), "a") as log_file:
        log_file.write(f"saving objs python execution time: {elapsed_time:.2f} seconds\n")

    # Save intersection edges information
    edges_file = os.path.join(output_dir, "intersection_edges.txt")
    with open(edges_file, 'w') as f:
        f.write(f"Total intersection edges: {len(all_intersection_edges)}\n")
        for i, edge in enumerate(all_intersection_edges):
            f.write(f"Edge {i}: {edge}\n")
    
    print(f"Saved intersection edges to {edges_file}")
    
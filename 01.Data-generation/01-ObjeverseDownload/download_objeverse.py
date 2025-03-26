import objaverse
import json
import os
import requests
import trimesh
import yaml
import multiprocessing
import igl
import numpy as np
import shutil
import glob
import csv

def DownloadProcess(shape_category, data_path, isSelect, start, end):
    # Prepare download directories
    download_folder = os.path.join(data_path, shape_category)
    os.makedirs(download_folder, exist_ok=True)

    download_objs_folder = os.path.join(download_folder, "objs")
    downloaded_materials_folder = os.path.join(download_folder, "materials")
    os.makedirs(download_objs_folder, exist_ok=True)
    os.makedirs(downloaded_materials_folder, exist_ok=True)

    # Load annotations and filter UIDs
    annotations = objaverse.load_annotations()
    cc_by_uids = [
        uid for uid, annotation in annotations.items()
        # if annotation["license"] == "by" and any(shape_category in tag["name"] for tag in annotation["tags"])
        if any(shape_category in tag["name"] and tag["name"] for tag in annotation["tags"])
    ]
    if isSelect:
        cc_by_uids = cc_by_uids[start:end]

    # Load objects
    objects = objaverse.load_objects(uids=cc_by_uids)
    print("len: ", len(objects.values()))

    # Prepare CSV file
    csv_file_path = os.path.join(download_folder, "downloaded_objects.csv")
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["UID", "Name", "Tag Name"])

        # Process each object
        for uid, obj_data in objects.items():
            glb_path = obj_data
            obj_path = os.path.join(download_folder, f"{uid}.obj")

            # Convert GLB to OBJ
            mesh = trimesh.load(glb_path)
            try:
                mesh.export(obj_path)
            except Exception as e:
                print(f"Error exporting mesh for {uid}: {e}")
                continue

            # Move OBJ and materials
            download_objs_path = os.path.join(download_objs_folder, f"{uid}.obj")
            if os.path.exists(download_objs_path):
                os.remove(download_objs_path)
            shutil.move(obj_path, download_objs_path)

            material_folder = os.path.join(downloaded_materials_folder, uid)
            os.makedirs(material_folder, exist_ok=True)
            for material_file in glob.glob(os.path.join(download_folder, "material*")):
                if os.path.isfile(material_file):
                    destination_file = os.path.join(material_folder, os.path.basename(material_file))
                    if os.path.exists(destination_file):
                        os.remove(destination_file)
                    shutil.move(material_file, material_folder)

            # Write to CSV
            annotation = annotations[uid]
            name = annotation.get("name", "Unknown")
            tag_names = [tag["name"] for tag in annotation["tags"] if tag["name"] in shape_category]
            csv_writer.writerow([uid, name, ", ".join(tag_names)])

            print(f"Converted {glb_path} to {obj_path} and moved materials to {material_folder}")

# Print version and run main
print(objaverse.__version__)

# Load configuration
with open("../../config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
shape_category = config.get("shape_category", "default_category")
data_path = config.get("data_path", "downloaded")

DownloadProcess(shape_category, data_path, True, 0, 300)

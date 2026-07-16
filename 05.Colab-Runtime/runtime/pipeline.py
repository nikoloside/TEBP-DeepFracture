"""Glue: collision -> embedding -> network -> segmentation -> fragments -> sim."""

import os
import tempfile

import numpy as np
import trimesh

from .collision import export_fragments_for_sim, run_fracture_sim
from .predictor import download_asset, predict_gssdf
from .segmentation import extract_fragments, segment_volume

PRESETS = {
    "squirrel-260": ("squirrel", "csv/squirrel-260.csv"),
    "squirrel-261": ("squirrel", "csv/squirrel-261.csv"),
    "bunny-260": ("bunny", "csv/bunny-260.csv"),
    "bunny-261": ("bunny", "csv/bunny-261.csv"),
    "base-261": ("base", "csv/base-261.csv"),
    "pot-79": ("pot", "csv/pot-79.csv"),
}


def parse_csv_preset(csv_file):
    """Line 2 of the runtime CSVs describes the sphere: pos [2:5], linVel [8:11]."""
    with open(csv_file) as f:
        lines = f.readlines()
    fields = lines[1].split(";")
    pos = [float(v) for v in fields[2:5]]
    vel = [float(v) for v in fields[8:11]]
    return pos, vel


def run_demo(shape, sphere_pos, sphere_vel, seed=42, resolution=128,
             gravity=-5.0, seconds_after=3.0, fps=25):
    """Run the full breakable-object runtime once.

    Returns dict with keys: video (mp4 path), glb (fragments path),
    info (collision embedding + stats) — or an "error" message.
    """
    target_obj = download_asset(f"objs/{shape}.obj")
    workdir = tempfile.mkdtemp(prefix="deepfracture-")
    result = {}

    def fragment_builder(pos_local, dir_local, imp_norm, imp_raw):
        volume, code_idx = predict_gssdf(shape, pos_local, dir_local, imp_norm,
                                         resolution=resolution, seed=seed)
        labels = segment_volume(volume)
        fragments = extract_fragments(labels)
        if not fragments:
            # fall back to the unbroken shell so the sim can continue
            fragments = [trimesh.load(target_obj, force="mesh")]
        result["fragments"] = fragments
        result["code_idx"] = code_idx
        scene = trimesh.Scene(fragments)
        glb_path = os.path.join(workdir, "fragments.glb")
        scene.export(glb_path)
        result["glb"] = glb_path
        return export_fragments_for_sim(fragments, os.path.join(workdir, "objs"))

    frames, info = run_fracture_sim(
        target_obj, fragment_builder, sphere_pos, sphere_vel,
        gravity=gravity, seconds_after=seconds_after)

    if info is None:
        return {"error": "The projectile missed the target (or the impact was "
                         "below the fracture threshold). Aim closer to the origin "
                         "or increase the speed."}

    import imageio.v2 as imageio
    video_path = os.path.join(workdir, "runtime.mp4")
    imageio.mimwrite(video_path, frames, fps=fps,
                     codec="libx264", quality=7,
                     pixelformat="yuv420p", macro_block_size=8)

    info["codebook_index"] = result.get("code_idx")
    return {"video": video_path, "glb": result.get("glb"), "info": info}

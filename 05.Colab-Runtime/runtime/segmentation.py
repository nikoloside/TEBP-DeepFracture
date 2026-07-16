"""Pure-Python fragment segmentation of the predicted GS-SDF volume.

Replaces the ImageJ/MorphoLibJ watershed used by
TEBP-DeepFracture 04.Run-time/MorphoImageJ.py (extendedMinima ->
imposeMinima -> componentsLabeling -> Watershed with dams) with
scikit-image h-minima markers + marker-controlled watershed, so the whole
runtime needs no Java.
"""

import numpy as np
import trimesh
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
from skimage.morphology import h_minima
from skimage.segmentation import watershed

# Same defaults as MorphoImageJ.processCagedSDFSeg
ISOLEVEL = 0.03
TOLERANCE = 3.0   # MorphoLibJ extended-minima tolerance (0..255 scale)
MIN_VOXELS = {64: 50, 128: 50, 256: 500}


def segment_volume(volume, max_value=1.0):
    """Label the fragments encoded in a GS-SDF volume.

    volume: [res,res,res] float in [-1,1] (tanh output; >=0 is interior)
    Returns labels ndarray [res,res,res] of int (0 = exterior / dams).
    """
    res = volume.shape[0]
    isolevel = ISOLEVEL / max_value

    data = volume + isolevel
    interior = data >= 0

    # MorphoImageJ.getNormForSdf: 255 - (|sdf|+1)/2*255
    # -> fragment boundaries bright (ridges), fragment cores dark (basins)
    sdf = np.abs(data)
    relief = 255.0 - (sdf + 1.0) / 2.0 * 255.0

    conn6 = ndi.generate_binary_structure(3, 1)
    minima = h_minima(relief, TOLERANCE, footprint=conn6)
    markers, n_markers = ndi.label(minima, structure=conn6)
    if n_markers == 0:
        labels = interior.astype(np.int32)
    else:
        labels = watershed(relief, markers=markers, mask=interior,
                           connectivity=conn6, watershed_line=True)

    # Drop noisy specks like the original (filtNoisy)
    min_voxels = MIN_VOXELS.get(res, 50)
    ids, counts = np.unique(labels[labels > 0], return_counts=True)
    for frag_id, count in zip(ids, counts):
        if count < min_voxels:
            labels[labels == frag_id] = 0
    return labels


def _fragment_palette(n):
    rng = np.random.default_rng(7)
    hues = np.linspace(0.0, 1.0, n, endpoint=False)
    rng.shuffle(hues)
    colors = []
    for h in hues:
        # simple HSV->RGB with s=0.75, v=0.95
        i = int(h * 6) % 6
        f = h * 6 - int(h * 6)
        v, s = 0.95, 0.75
        p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
        rgb = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
        colors.append([int(c * 255) for c in rgb] + [255])
    return colors


def extract_fragments(labels, smooth_sigma=1.0):
    """Marching-cubes one mesh per fragment label.

    Vertices are mapped to the same object frame as the runtime's vedo
    pipeline (scale to [-1,1] then rotate_x(180).rotate_y(-90).rotate_z(90),
    which reduces to the axis permutation (i,j,k) -> (j,k,i)).
    Returns list of trimesh.Trimesh with vertex colors.
    """
    res = labels.shape[0]
    ids = [i for i in np.unique(labels) if i > 0]
    palette = _fragment_palette(max(len(ids), 1))

    fragments = []
    for n, frag_id in enumerate(ids):
        binary = (labels == frag_id).astype(np.float32)
        if smooth_sigma > 0:
            binary = ndi.gaussian_filter(binary, sigma=smooth_sigma)
        if binary.max() <= 0.5:
            continue
        try:
            verts, faces, _, _ = marching_cubes(binary, level=0.5)
        except (ValueError, RuntimeError):
            continue
        verts = verts / res * 2.0 - 1.0
        verts = verts[:, [1, 2, 0]]
        mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
        if mesh.is_empty or len(mesh.faces) < 8:
            continue
        mesh.visual.vertex_colors = palette[n % len(palette)]
        fragments.append(mesh)
    return fragments

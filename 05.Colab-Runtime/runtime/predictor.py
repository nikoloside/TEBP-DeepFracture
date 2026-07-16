"""Neural fracture prediction: collision embedding -> GS-SDF voxel grid.

Follows TEBP-DeepFracture 04.Run-time/predictshapes.py.
"""

import os
import threading

import numpy as np
import torch
import torch.nn.init as init
from huggingface_hub import hf_hub_download

from .networks import register_for_unpickle

HF_REPO = "nikoloside/deepfracture"
SHAPES = ["squirrel", "bunny", "pot", "base", "lion"]

_lock = threading.Lock()
_models = {}


def download_asset(filename):
    return hf_hub_download(repo_id=HF_REPO, filename=filename,
                           cache_dir=os.environ.get("DF_CACHE", "hf-cache"))


def load_models(shape):
    """Load (and memoize) the encoder/decoder pair for a shape."""
    with _lock:
        if shape in _models:
            return _models[shape]
        register_for_unpickle()
        device = torch.device("cpu")
        encoder = torch.load(download_asset(f"{shape}/{shape}-encoder.pt"),
                             map_location=device, weights_only=False)
        decoder = torch.load(download_asset(f"{shape}/{shape}-decoder.pt"),
                             map_location=device, weights_only=False)
        encoder.eval()
        decoder.eval()
        _models[shape] = (encoder, decoder)
        return encoder, decoder


@torch.no_grad()
def predict_gssdf(shape, pos, direction, impulse, resolution=128, seed=None):
    """Predict the geometrically-segmented SDF voxel grid for one collision.

    pos:       impact point in the target's local frame (3,)
    direction: impact direction in the target's local frame (3,)
    impulse:   scalar already normalized to [-1, 1]
    resolution: 128 (Middle) or 256 (Big)
    Returns (volume ndarray [res,res,res], codebook index int)
    """
    encoder, decoder = load_models(shape)

    pos = torch.tensor(np.asarray(pos, dtype=np.float32))
    direction = torch.tensor(np.asarray(direction, dtype=np.float32))
    imp = torch.tensor(np.asarray([impulse], dtype=np.float32))

    feature = encoder.predict(pos, direction, imp).unsqueeze(0)

    if seed is not None:
        torch.manual_seed(int(seed))
    latent_z = torch.FloatTensor(1, 8)
    init.xavier_normal_(latent_z)

    input_x, min_index, _dist = decoder.Cook(feature, latent_z)

    if resolution >= 256:
        output = decoder.forwardBig(input_x)
    else:
        output = decoder.forwardMiddle(input_x)

    volume = output.squeeze().squeeze().cpu().numpy()
    return volume, int(min_index.item())

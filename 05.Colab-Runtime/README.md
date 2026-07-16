# 05. Web Runtime (Colab / Gradio)

<a href="https://colab.research.google.com/github/nikoloside/TEBP-DeepFracture/blob/main/05.Colab-Runtime/deepfracture_runtime.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=22.5></a>

Pure-Python web runtime for DeepFracture — neural brittle-fracture prediction
embedded in a rigid-body simulation, CPU only, no Java/ImageJ and no Houdini:

1. **Collision detection** — PyBullet simulates a projectile hitting the target
   and captures the strongest contact (point, normal, impulse), mirroring
   [`04.Run-time/`](../04.Run-time).
2. **Collision embedding** — the impact is transformed into the target's local
   frame and encoded as the paper's 7-D condition *(position, direction,
   normalized impulse)*.
3. **Neural prediction** — the per-shape VQ-VAE
   ([nikoloside/deepfracture](https://huggingface.co/nikoloside/deepfracture))
   maps the embedding to its discrete codebook and decodes a
   geometrically-segmented SDF volume.
4. **Segmentation** — a pure-Python watershed/flooding pass (scikit-image,
   replacing the ImageJ/MorphoLibJ step) extracts the fragment label field,
   and marching cubes produces one mesh per fragment.
5. **Back to the runtime** — the intact body is swapped for the predicted
   fragments, which inherit its velocity and keep simulating.

## Run it

**Colab (zero setup):** open the badge above and *Run all* (~2 min, free CPU).

**Locally:**

```bash
cd 05.Colab-Runtime
pip install -r requirements.txt gradio
python app.py          # Gradio UI at http://localhost:7860
python test_e2e.py     # headless smoke test
```

The same folder deploys unchanged as a Hugging Face Space
(`README_space.md` carries the Space metadata).

## Files

```
app.py                     Gradio interface
runtime/networks.py        MultiLatentEncoder / AutoDecoder (checkpoint classes)
runtime/predictor.py       HF Hub weights -> GS-SDF voxel prediction
runtime/segmentation.py    watershed + marching cubes fragment extraction
runtime/collision.py       PyBullet impact capture + fragment re-simulation
runtime/pipeline.py        end-to-end glue
deepfracture_runtime.ipynb Colab notebook
```

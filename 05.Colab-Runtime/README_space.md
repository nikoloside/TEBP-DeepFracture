---
title: DeepFracture Runtime
emoji: 💥
colorFrom: gray
colorTo: red
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
pinned: false
license: mit
models:
  - nikoloside/deepfracture
tags:
  - fracture
  - physics
  - simulation
  - graphics
---

# DeepFracture Runtime

Interactive web runtime for **DeepFracture** — neural brittle-fracture
prediction embedded in a rigid-body simulation, running fully in Python on CPU:

1. **Collision detection** — PyBullet simulates a projectile hitting the target
   and captures the strongest contact (point, normal, impulse), mirroring
   `04.Run-time/` of [TEBP-DeepFracture](https://github.com/nikoloside/TEBP-DeepFracture).
2. **Collision embedding** — the impact is transformed into the target's local
   frame and encoded as the paper's 7-D condition *(position, direction,
   normalized impulse)*.
3. **Neural prediction** — the per-shape VQ-VAE
   ([nikoloside/deepfracture](https://huggingface.co/nikoloside/deepfracture))
   maps the embedding to its discrete codebook and decodes a
   geometrically-segmented SDF volume.
4. **Segmentation** — a pure-Python watershed/flooding pass
   (scikit-image, replacing the paper's ImageJ/MorphoLibJ step) extracts the
   fragment label field, and marching cubes produces one mesh per fragment.
5. **Back to the runtime** — the intact body is swapped for the predicted
   fragments, which inherit its velocity and keep simulating.

## Papers

- **DeepFracture: A Generative Approach for Predicting Brittle Fractures with
  Neural Discrete Representation Learning** — Computer Graphics Forum, 2025.
  [Project page](https://nikoloside.graphics/deepfracture/)
- **Far-From-Boundary Fields for Learning Segmented Implicit Solids** —
  SMI 2026 / Computers & Graphics.
  [Project page](https://nikoloside.graphics/far-from-boundary-fields/)

## Citation

```bibtex
@article{huang2025deepfracture,
  author  = {Huang, Yuhang and Kanai, Takashi},
  title   = {DeepFracture: A Generative Approach for Predicting Brittle
             Fractures with Neural Discrete Representation Learning},
  journal = {Computer Graphics Forum},
  pages   = {e70002},
  year    = {2025},
  doi     = {https://doi.org/10.1111/cgf.70002}
}
```

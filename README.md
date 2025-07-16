<p align="center">

  <h2 align="center">DeepFracture: Code and Demo
    <p align="center" style="font-size: small;">  The Eye of  Breaking Perception </p>
  </h2>
  
  <p align="center">
    <a href="https://nikoloside.graphics/"><strong>Yuhang Huang</strong></a>
    ·
    <a href="https://graphics.c.u-tokyo.ac.jp/hp/en/kanai"><strong>Kanai Takashi</strong></a>
    <br>
    <br>
        <a href="https://onlinelibrary.wiley.com/doi/10.1111/cgf.70002"><img src="https://img.shields.io/badge/Journal-CGF-blue" height=22.5 alt='journal'></a>
        <a href='https://nikoloside.graphics/deepfracture/'><img src="https://img.shields.io/badge/Project_Page-DeepFracture-red" height=22.5 alt='Project Page'></a>
        <a href='https://github.com/nikoloside/TEBP'><img src="https://img.shields.io/badge/Demo-WIP-black" height=22.5 alt='Demo'></a>
        <a href='https://univtokyo-my.sharepoint.com/:f:/g/personal/7553042866_utac_u-tokyo_ac_jp/EnxALyErewNMhYWeqoGSa9ABfqw45H1UWYYHVcOuLQNovw?e=caddF5'><img src="https://img.shields.io/badge/Dataset-break4models-yellow" height=22.5 alt='Dataset'></a>
    <br>
    <b>The University of Tokyo &nbsp;
  </p>
  
  <table align="center">
    <tr>
    <td>
      <img src="teaser.jpg">
    </td>
    </tr>
  </table>

## Progress

- [x] Network Benchmark
- [x] 4 Models Drive Google
- [x] Release MeshBoolean Code (2025/7/15)
- [x] Release MorphoSeg Code  (2025/7/15)
- [x] Easy-Run Official Code Release
- [x] Release clean codebase.
- [x] Release pre-trained checkpoints.
- [x] Release 4 Models Drive Google.
- [x] Release Demo Codebase  (2025/7/15)
- [ ] Release pipeline with a public license.
- [ ] Release Demo Page.
- [ ] Release Evaluation Code

## Overview

This project serves as the code base for the DeepFracture and The Eye of Breaking Perception paper. It encompasses various components essential for generating, processing, and training models on fracture simulations. The following sections outline the key components of the code base.

### Components

1. **Data Generation**
   - **Download Obj** and **Create Bullet**This module is responsible for downloading and preparing the necessary 3D object files (OBJ) for the simulation. It includes scripts for normalizing and converting OBJ files into formats suitable for the fracture simulation.
   - **Running FractureRB Toolkits**
   - The FractureRB component is designed to simulate the behavior of fractured materials. This module allows users to run simulations using the Bullet Physics engine, providing insights into the dynamics of fractured objects.

3. **Cook Data**
   - This component processes the generated data, preparing it for training. It includes data cleaning, normalization, and formatting to ensure compatibility with the training algorithms.

4. **Training**
   - The training module implements machine learning algorithms to train models on the processed fracture data. It includes scripts for model selection, hyperparameter tuning, and evaluation metrics.

5. **Run-time**
   - This section encompasses various runtime environments for executing the simulations:
   - **Havok Version**: A runtime environment utilizing the Havok Physics engine for high-performance simulations.
   - **PyBullet Version**: A version that leverages the PyBullet physics engine, providing a flexible and easy-to-use interface for running simulations.
   - **Morpho Seg**: This component focuses on segmenting the mesh data based on morphological features, enhancing the simulation's realism.
   - **Mesh Boolean**: This module allows for complex boolean operations on meshes, enabling the creation of intricate fracture patterns.


## Getting started

### Installation

### Third-party Libraries

Before installing the main dependencies, you need to build the following third-party libraries:

1. **Manifold**
   - Clone the repository: `git clone https://github.com/elalish/manifold.git`
   - Follow the build instructions in the repository

pip install h5py pyyaml matplotlib libigl nibabel

2. **Others**
```bash
pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
pip install "numpy<2" siren_pytorch nibabel pyyaml imagej trimesh vedo
brew install --cask temurin
```

3. **Bullet3**
```bash
pip install pybullet==3.2.6
pip install "numpy<2"
```


After building these libraries, proceed with the main installation:

```bash
conda env create -f environment.yml
conda activate tebp
pip install -r requirements.txt --no-cache-dir
```

## Generating

### Datasets

We provide the generation method of pre-fracture data. 
However, we can not release the fracturerb code. You can find the generated 4 models data here:
[OneDrive link for dataset](https://univtokyo-my.sharepoint.com/:f:/g/personal/7553042866_utac_u-tokyo_ac_jp/EnxALyErewNMhYWeqoGSa9ABfqw45H1UWYYHVcOuLQNovw?e=caddF5)

We plan to provide the generated fractured datasets for all 7 categories separately.

## Training

Download the dataset above．

```json
# 01 Data Generation
shape_category: "mug"
foundation_path: "/Users/(Your Path)/TEBP"
```

Change the path.

```bash
python 03.Training/train.py
```

## Evaluation

### Pre-trained models

Pre-trained networks can be downloaded from this [OneDrive link for pretrained models](https://univtokyo-my.sharepoint.com/:f:/g/personal/7553042866_utac_u-tokyo_ac_jp/Em4-ksMVEBFBsAIycn7i-kYBmk8f-Hu8QyGicgcQhm7vFA?e=6Ucf03).
We stored them as `*.pt` files in `pre-trained-v2.zip`.

If you want to use the pre-trained model, please:
```python
from predict.Model.load_VQfinal2resolutionv2 import MultiLatentEncoder, AutoDecoder

models[i] = model_path

world.CreateBreakableObj(objName, pos, rot, lVel, aVel, paths[i], colors[i], staticsMass[i], frictions[i], restitutions[i], fracturePaths[i], garagePaths[i], models[i], isBig[i], maxValues[targetName[i]], False, ws)
```

Please refer to [`predict-runtime.py`](04.Run-time/predict-runtime.py) for seeking the whole code example.


### Run-time


### Usage Instructions


```bash
python 04.Run-time/predict-runtime.py
```

By following these instructions, you can effectively utilize the DeepFracture code base to explore and analyze fracture simulations.



## Acknowledgements

- The fracture code is created by [FractureRB](https://github.com/david-hahn/FractureRB). 


## Citation

If you found this code or paper useful, please consider citing:
```bibtex
@article{huang2025deepfracture,
        author = {Huang, Yuhang and Kanai, Takashi},
        title = {DeepFracture: A Generative Approach for Predicting Brittle Fractures with Neural Discrete Representation Learning},
        journal = {Computer Graphics Forum},
        pages = {e70002},
        year = {2025},
        keywords = {animation, brittle fracture, neural networks, physically based animation},
        doi = {https://doi.org/10.1111/cgf.70002},
        url = {https://onlinelibrary.wiley.com/doi/abs/10.1111/cgf.70002},
        eprint = {https://onlinelibrary.wiley.com/doi/pdf/10.1111/cgf.70002}
      }
```

## Contact

If you encounter any issues or have questions, please open an issue or reach out to `nikoloside@gmail.com`. 
Additionally, we do not have permission to release any code or built versions related to HyenaLib and FractureRB. Please contact the original providers of HyenaLib or FractureRB for further assistance.

Nonetheless, we utilized Docker to create an Ubuntu 14 environment and built the wrapper code for HyenaLib using the prebuilt g++-4.9 provided in FractureRB.

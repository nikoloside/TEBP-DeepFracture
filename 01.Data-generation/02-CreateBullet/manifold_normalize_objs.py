import shutil
import os, glob
import subprocess
import igl
import yaml

with open('../../config.yaml', 'r') as file:
    config = yaml.safe_load(file)

metaPath = os.path.join(config['data_path'], config['shape_category'], "output.txt")
fromPath = os.path.join(config['data_path'], config['shape_category'], "objs")
savePath = os.path.join(config['data_norm_path'], config['shape_category'])

if not os.path.exists(savePath):
    os.makedirs(savePath)



# targetList = sorted(glob.glob(os.path.join(fromPath, "*.obj"), key=os.path.getmtime))

defaultBand = 0.95 * 2
sphereBand = 0.4 * 2

lines = []
if metaPath:
    with open(metaPath) as f:
        lines = f.readlines()

# folders = os.listdir(fromPath) if fromPath else []

for line in lines:
    # normalize the model
    tar = os.path.join(fromPath, line.replace("\n", "") + ".obj")

    bandSize = defaultBand
    saveName =  os.path.join(savePath, os.path.basename(tar).split(".")[0] + ".obj")
    v, f = igl.read_triangle_mesh(tar)

    if os.path.basename(tar) == "sphere.obj":
        bandSize = sphereBand

    print(v.max(axis=0), v.min(axis=0))
    maxSize = (v.max(axis=0) - v.min(axis=0)).max()
    origin = (v.max(axis=0) + v.min(axis=0)) / 2
    print(origin)

    v = (v - origin) / maxSize * bandSize
    print(v.max(), v.min())
    print(v.max(axis=0), v.min(axis=0))
    igl.write_obj(saveName, v, f)

    # evaluate the manifold
    command = "../../00.third-party/Manifold/build/manifold {0} {1}".format(saveName, saveName)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print("succeded moanifolding")
    process.wait()

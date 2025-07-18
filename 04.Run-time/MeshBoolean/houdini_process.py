#!/Applications/Houdini/Houdini20.0.751/Frameworks/Python.framework/Versions/3.10/Python3
import sys
import os
import glob

houdini_path = "/Applications/Houdini/Houdini20.5.584/Frameworks/Python.framework/Versions/3.11/bin/python3.11"
houdini_libs = "/Applications/Houdini/Houdini20.5.584/Frameworks/Houdini.framework/Versions/Current/Resources/houdini/python3.11libs/"

sys.path.append(houdini_libs)
sys.path.append(houdini_path)

import hou

print(hou.applicationVersionString())

import hrpyc
import time

if sys.argv[1] != "":
    path = sys.argv[1]
if sys.argv[2] != "":
    objName = sys.argv[2]


inputFolder = os.path.join(path, "", "reconstructed.obj")
outputFolder = os.path.join(path, "out")
objFile = objName
logFile = os.path.join(path, "log-hou.txt")

connection, hou = hrpyc.import_remote_module()

hou.node('/obj').createNode('null', node_name='dnmd')
file1 = hou.node("/obj/geo1/file1")
file2 = hou.node("/obj/geo1/file2")
filecache = hou.node("/obj/geo1/filecache1")

file2 = hou.node("/obj/geo1/file2")
file2.parm("file").set(objFile)
print("ori obj name: %s" % (file2.parm('file').eval()))

t1 = time.time()

files = glob.glob(inputFolder)
for filename in files:
    file1.parm("file").set(filename)
    name = file1.parm('file').eval()
    outName = os.path.join(outputFolder, os.path.basename(filename))
    filecache.parm("file").set(outName)
    filecache.cook(force=True)
    filecache.parm("execute").pressButton()
    print(name)

log_file = open(logFile,"w")
t2 = time.time()
log_file.write("boolean time: %f" % ((t2 - t1)*1000))
log_file.close()
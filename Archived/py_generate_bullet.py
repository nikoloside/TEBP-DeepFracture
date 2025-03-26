import pybullet as p
import time
import pybullet_data
import os

objPath = "/Users/yuhanghuang/Workspaces/ShapeNetv2/Result/bowlObj_norm"

bulletPath = "/Users/yuhanghuang/Workspaces/ShapeNetv2/Result/bowlBullet"


files = os.listdir(objPath)

for file in files:
    if file == ".DS_Store" or file == "taxonomy.json":
        continue

    path = objPath + "/" + file
    savePath = bulletPath + "/" + file.split(".")[0] + ".bullet"

    # GUI 添加
    # physicsClient = p.connect(p.GUI)#or p.DIRECT for non-graphical version
    physicsClient = p.connect(p.DIRECT)
    datapath = pybullet_data.getDataPath()
    p.setAdditionalSearchPath(datapath) #optionally

    # 环境设置
    p.setGravity(0,0,0)
    p.setTimeStep(1 / 60, physicsClient)

    shift = [0,0,0]
    vid_sphere = p.createVisualShape(shapeType=p.GEOM_MESH,
                                        fileName="../../pybullet/models/sphere.obj",
                                        rgbaColor=[1,0,0,1],
                                        specularColor=[0, 0, 0],
                                        visualFramePosition=shift,
                                        meshScale=[1,1,1],
                                        physicsClientId=physicsClient)
    cid_sphere = p.createCollisionShape(shapeType=p.GEOM_MESH,
                                        fileName="../../pybullet/models/sphere.obj",
                                        collisionFramePosition=shift,
                                        meshScale=[1,1,1])

    mass = 1.0 # kg
    bid_sphere = p.createMultiBody(baseMass=mass,
                            baseInertialFramePosition=[0,0,0],
                            baseCollisionShapeIndex=cid_sphere,
                            baseVisualShapeIndex=vid_sphere,
                            basePosition=[0,3,0],
                            baseOrientation=[0,0,0],
                            physicsClientId=physicsClient)

    p.resetBaseVelocity(bid_sphere, [0, 0, 0], [0, 0, 0])



    vid_target = p.createVisualShape(shapeType=p.GEOM_MESH,
                                        fileName=path,
                                        rgbaColor=[0,1,0,1],
                                        specularColor=[0, 0, 0],
                                        visualFramePosition=shift,
                                        flags=p.GEOM_FORCE_CONCAVE_TRIMESH,
                                        meshScale=[1,1,1],
                                        physicsClientId=physicsClient)
    cid_target = p.createCollisionShape(shapeType=p.GEOM_MESH,
                                        fileName=path,
                                        flags=p.GEOM_FORCE_CONCAVE_TRIMESH,
                                        collisionFramePosition=shift,
                                        meshScale=[1,1,1])

    mass = 0.0 # kg
    bid_target = p.createMultiBody(baseMass=mass,
                            baseInertialFramePosition=[0,0,0],
                            baseCollisionShapeIndex=cid_target,
                            baseVisualShapeIndex=vid_target,
                            basePosition=[0,0,0],
                            baseOrientation=[0,0,0],
                            physicsClientId=physicsClient)

    print(bid_sphere, bid_target)
    p.resetBaseVelocity(bid_target, [0, 0, 0], [0, 0, 0])

    p.saveWorld(savePath)

    p.disconnect()

    # break

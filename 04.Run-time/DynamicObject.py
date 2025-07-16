import pybullet as p
import glob
from predictshapes import predict, judge
from MeshUtils import Quaternion
import numpy as np
import os


# Class Name Dynamic Objects
# Elements:
#   target Id, sphere Id, obj Parameter
# Functions:
#   Init()
#   Destroy()

class DynamicObject():
    def __init__(self, name, physicsClient):
        self.bid = -1
        self.vid = -1
        self.cid = -1
        self.name = name
        self.path = ""
        self.pos = [0, 0, 0]
        self.rot = [0, 0, 0, 1]
        self.lVel = [0, 0, 0]
        self.aVel = [0, 0, 0]
        self.color = [0, 0, 0, 1]
        self.mass = 1.0
        self.active = False
        self.physicsClient = physicsClient

    def setParameter(self, path, pos, rot, lVel, aVel, color, mass, friction, restitution):
        self.path = path
        self.pos = pos
        self.rot = rot
        self.lVel = lVel
        self.aVel = aVel
        self.color = color
        self.mass = mass
        self.friction = friction
        self.restitution = restitution
        self.active = False
        
    def setPos(self, pos, rot):
        self.pos = pos
        self.rot = rot

        if self.bid >= 0:
            p.resetBasePositionAndOrientation(self.bid, pos, rot)

    def setVel(self, lvel, avel):
        self.lVel = lvel
        self.aVel = avel

    def getPos(self):
        return (self.pos, self.rot)


    def createInstance(self, isActivate):
        # Sphere Load
        shift = [0,0,0]
        specularColor = [1,1,1]
        inertialFramePos = [0,0,0]
        scale = [1, 1, 1]
        print(self.path)
        
        if self.vid == -1:
            self.vid = p.createVisualShape(shapeType=p.GEOM_MESH,
                                                fileName=self.path,
                                                rgbaColor=self.color,
                                                specularColor=specularColor,
                                                visualFramePosition=shift,
                                                meshScale=scale,
                                                physicsClientId=self.physicsClient)
        if self.cid == -1:
            self.cid = p.createCollisionShape(shapeType=p.GEOM_MESH,
                                                fileName=self.path,
                                                collisionFramePosition=shift,
                                                meshScale=scale)
        if self.bid == -1:
            self.bid = p.createMultiBody(baseMass=self.mass,
                                    baseInertialFramePosition=inertialFramePos,
                                    baseCollisionShapeIndex=self.vid,
                                    baseVisualShapeIndex=self.cid,
                                    basePosition=self.pos,
                                    baseOrientation=self.rot,
                                    physicsClientId=self.physicsClient)
            if self.friction >= 0 and self.restitution >= 0:
                p.changeDynamics(
                    self.bid,
                    -1,
                    lateralFriction=self.friction,
                    restitution=self.restitution,
                    physicsClientId=self.physicsClient,
                )
        if isActivate:
            self.activate()


    def activate(self):
        p.resetBasePositionAndOrientation(self.bid, self.pos, self.rot)
        p.resetBaseVelocity(self.bid, self.lVel, self.aVel)
        self.active = True
        
    def deactivate(self):
        p.removeBody(self.bid)
        self.active = False

# Class Breakable Objects
# Elements:
#   name
#   oriObj
#   fraList
#   activeList *
#   pathList
#   bodyList
# Functions:
#   Init()
#   Destroy()
class BreakableObject():
    targetIndex = 0
    sphereIndex = 1
    defaultHidePos = [100, 100, 100]
    def __init__(self, name, pos, rot, lVel, aVel, path, color, staticMass, friction, restitution, fractureFolderPath, garagePath, model, isBig, maxValue, isMulShapes, ws, physicsClient):
        self.name = name

        self.oriObj = DynamicObject(name, physicsClient)
        self.oriObj.setParameter(path, pos, rot, lVel, aVel, color, staticMass, friction, restitution)
        # print(pos, lVel)
        self.oriObj.createInstance(False)
        self.fracList = []
        self.hasFractured = False
        self.physicsClient = physicsClient
        self.ws = ws
        self.model = model
        self.isBig = isBig
        self.garagePath = ""
        self.maxValue = maxValue
        self.friction = friction
        self.restitution = restitution
        self.isMulShapes = isMulShapes
        self.setLastVel(lVel, aVel)

        if fractureFolderPath != "":
            self.loadFragments(fractureFolderPath, physicsClient)
        else:
            self.garagePath = garagePath
    
    def setOriginPos(self, pos, orn):
        self.oriObj.setPos(pos, orn)

    def getOriginPos(self):
        pos, orn = self.oriObj.getPos()
        return (pos, orn)

    def setLastVel(self, lVel, aVel):
        self.lastLVel = lVel
        self.lastAVel = aVel

        self.oriObj.setVel(lVel, aVel)

    def getLastVel(self):
        return self.lastLVel, self.lastAVel

    def isStatic(self):
        if len(self.fracList) > 0 or self.garagePath != "":
            return False
        else:
            return True

    def loadFragments(self, fractureFolderPath, physicsClient):
        fracturePathList = glob.glob(fractureFolderPath)
        print(fractureFolderPath, fracturePathList)
        count = 1
        # print(fractureFolderPath, fracturePathList)
        # Add sub mass!!!!!
        for fracturePath in fracturePathList:
            subMass = 1 / len(fracturePathList)
            obj = DynamicObject("fra"+str(count), physicsClient)
            obj.setParameter(fracturePath, self.defaultHidePos, [0, 0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 1, 0, 1], subMass, self.friction, self.restitution)
            obj.createInstance(False)

            self.fracList.append(obj)
            count += 1

    def startFracturing(self, impacts, pos, iRot, index, collisionNum, impulseMax):
        # print(impact[5], pos)

        maxImpulse = impulseMax
        # Create quaternion from PyBullet quaternion (which is in [x,y,z,w] order)
        # and get its conjugate for transforming impact points to local space
        q = Quaternion(iRot, is_xyzw_order=True).conjugate()

        posList = []
        impList = []
        dirList = []

        collision = 0

        for ind in range(collisionNum):
            if len(impacts) - 1 >= ind:
                impact = impacts[ind]
                pos = np.array([impact[5][0] - pos[0], impact[5][1] - pos[1], impact[5][2] - pos[2]])
                imp = np.array( [min(impact[9], maxImpulse) / maxImpulse * 2 - 1] )
                direct = np.array([impact[7][0], impact[7][1], impact[7][2]])
                if index != impact[2]:
                    direct = -direct
                
                new_pos = q.rotate(pos)
                new_dir = q.rotate(direct)

                posList.append(new_pos)
                impList.append(imp)
                dirList.append(new_dir)
            else:
                posList.append(np.array([0, 0, 0]))
                impList.append(np.array([0]))
                dirList.append(np.array([0, 0, 0]))

        print(posList, impList, dirList)

        # if not judge(impList, posList, dirList, collisionNum):
        #     return False

        predict(self.garagePath, self.oriObj.path, self.model, impList, posList, dirList, self.isBig, self.maxValue, self.isMulShapes, self.name, collisionNum)

        print(os.path.join(self.garagePath, "objs", "*.obj"))
        print(os.getcwd())
        os.chdir(self.ws)
        self.loadFragments(os.path.join(self.garagePath, "objs", "*.obj"), self.physicsClient)

        return True


    def fractureFire(self, tarPos, tarOrn, linearVelocity, angularVelocity):
        self.hasFractured = True
        self.oriObj.deactivate()
        for fracObj in self.fracList:
            fracObj.pos = tarPos
            fracObj.rot = tarOrn
            fracObj.lVel = linearVelocity
            fracObj.aVel = angularVelocity

            fracObj.activate() # fracObj.

    def getVisualization(self):
        activeList = []
        pathList = []
        bodyList = []
        activeList.append(self.oriObj.active)
        pathList.append(self.oriObj.path)
        bodyList.append(self.oriObj.bid)
        for fraObj in self.fracList:
            activeList.append(fraObj.active)
            pathList.append(fraObj.path)
            bodyList.append(fraObj.bid)
        return activeList, pathList, bodyList
    
    def activate(self):
        if not self.hasFractured:
            self.oriObj.activate()
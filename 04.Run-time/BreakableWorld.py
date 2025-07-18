import pybullet as p
import time, os
import numpy as np
from DynamicObject import DynamicObject, BreakableObject
from predict.Model.load_VQfinal2resolutionv2 import MultiLatentEncoder, AutoDecoder
from MeshUtils import Quaternion, load_mesh, form_mesh, merge_meshes, save_mesh

def sort_impulse(e):
    return e[9]


class BreakableWorld():
    def __init__(self, isDirect, bulletFile = "", needOutput = True, allowAutoFracture = False, timeRange = 60, hasGravity = 0, collisionNum=1, impulseMax = 100000):
        self.BreakableList = []  # Move to instance variable
        self.nonPhysicsClient = -1

        # GUI setup
        if (not isDirect):
            self.physicsClient = p.connect(p.GUI)
        else:
            self.physicsClient = p.connect(p.DIRECT)
        if (bulletFile != ""):
            # Rebuild without using Bullet
            ids = p.loadBullet(bulletFile)
        
        p.setTimeStep(1 / 250, self.physicsClient)
        self.resultPath = ""
        self.needOutput = needOutput
        self.allowAutoFracture = allowAutoFracture
        self.timeRange = timeRange
        self.hasGravity = hasGravity
        self.collisionNum = collisionNum
        self.impulseMax = impulseMax

    def resetGravity(self):
        if self.hasGravity > 0:
            p.setGravity(0, -self.hasGravity, 0, self.physicsClient)
        else:
            p.setGravity(0, 0, 0, self.physicsClient)
            print("No Gravity.")

    def SetupDebugPage(self):
        if len(self.BreakableList) < 2:
            print("Warning: Not enough objects in BreakableList for debug setup")
            return False
            
        try:
            pos, orn = self.BreakableList[1].getOriginPos()
            lvel, avel = self.BreakableList[1].getLastVel()
            
            # Initialize all debug parameters
            self.debug_params = {}
            self.debug_params['x'] = p.addUserDebugParameter("x", -3, 3, pos[0])
            self.debug_params['y'] = p.addUserDebugParameter("y", -3, 3, pos[1])
            self.debug_params['z'] = p.addUserDebugParameter("z", -3, 3, pos[2])
            self.debug_params['roll'] = p.addUserDebugParameter("roll", -1.5, 1.5, orn[0])
            self.debug_params['pitch'] = p.addUserDebugParameter("pitch", -1.5, 1.5, orn[1])
            self.debug_params['yaw'] = p.addUserDebugParameter("yaw", -1.5, 1.5, orn[2])
            self.debug_params['v_x'] = p.addUserDebugParameter("v_x", -180, 180, lvel[0])
            self.debug_params['v_y'] = p.addUserDebugParameter("v_y", -180, 180, lvel[1])
            self.debug_params['v_z'] = p.addUserDebugParameter("v_z", -180, 180, lvel[2])
            
            # Add play button as a parameter with small range (0 to 1)
            self.debug_params['play'] = p.addUserDebugParameter("Start Simulation", 0, 1, 0)
            
            return True
        except Exception as e:
            print(f"Error setting up debug parameters: {e}")
            return False

    def Idle(self, auto_run=False):
        if not hasattr(self, 'debug_params'):
            print("Debug parameters not initialized. Call SetupDebugPage first.")
            return
            
        last_play_value = 0
        auto_run_triggered = False
        while True:
            try:
                objectIndex = 1

                # Read all debug parameters
                x = p.readUserDebugParameter(self.debug_params['x'])
                y = p.readUserDebugParameter(self.debug_params['y'])
                z = p.readUserDebugParameter(self.debug_params['z'])
                roll = p.readUserDebugParameter(self.debug_params['roll'])
                pitch = p.readUserDebugParameter(self.debug_params['pitch'])
                yaw = p.readUserDebugParameter(self.debug_params['yaw'])
                vx = p.readUserDebugParameter(self.debug_params['v_x'])
                vy = p.readUserDebugParameter(self.debug_params['v_y'])
                vz = p.readUserDebugParameter(self.debug_params['v_z'])
                
                # Check if play value changed from 0 to something else
                play_value = p.readUserDebugParameter(self.debug_params['play'])
                
                # Auto-run logic: set play to 1 on first iteration if auto_run is True
                if auto_run and not auto_run_triggered:
                    auto_run_triggered = True
                    return
                
                if play_value > 0 and last_play_value == 0:
                    return
                last_play_value = play_value

                # Get quaternion from Euler angles
                orn = p.getQuaternionFromEuler([roll, pitch, yaw])
                lVel = [float(vx), float(vy), float(vz)]
                
                # Set robot to specified "position/orientation"
                if len(self.BreakableList) > objectIndex:
                    self.BreakableList[objectIndex].setOriginPos([x,y,z], orn)
                    self.BreakableList[objectIndex].setLastVel(lVel, self.BreakableList[objectIndex].lastAVel)
                    
            except Exception as e:
                print(f"Error in Idle loop: {e}")
            
            time.sleep(1./240.)

    def SetCamera(self, cameraDist, cameraPitch):
        # Render settings
        self.upAxisIndex = 2

    def CreateBreakableObj(self, objName, pos, rot, lVel,aVel, path, color, staticMass, friction, restitution, fracturePath, garagePath, model, isBig, maxValue, isMulShapes, ws):
        if not self.allowAutoFracture:
            garagePath = ""
        obj = BreakableObject(objName, pos, rot, lVel, aVel, path, color, staticMass, friction, restitution, fracturePath, garagePath, model, isBig, maxValue, isMulShapes, ws, self.physicsClient)
        self.BreakableList.append(obj)
        (activeList, shapeList, bodyList) = obj.getVisualization()
        print(obj.name, activeList, bodyList, shapeList)


    threshold = 2000

    def catchImpact(self, timeFrame, impactList, bid_tar):
        print(str(timeFrame) + " : " + str(len(impactList)))
        if len(impactList) > 0:
            # print(impactList[0][9])
            totalImpulseList = []
            detailedImpulseList = []
            bodyList = []
            
            for i in range(len(self.BreakableList)):
                bodyList.append(self.BreakableList[i].oriObj.bid)
                totalImpulseList.append(0)
                detailedImpulseList.append([])

            for impact in impactList:
                for i in range(len(self.BreakableList)):
                    if bodyList[i] == impact[1] or bodyList[i] == impact[2]: # contactFlag bodyUniqueIdA bodyUniqueIdA linkIndexA linkIndexB positionOnA positionOnB contactNormalOnB contactDistance normalForce
                        totalImpulseList[i] += impact[9]
                    detailedImpulseList[i].append(impact)
                    sorted(detailedImpulseList[i], key=lambda x: x[9], reverse=True)

            print(bodyList)
            print(totalImpulseList)
            for i in range(len(totalImpulseList)):
                # All non-static breakable objects in the list will go through threshold
                if self.BreakableList[i].isStatic():
                    continue
                if totalImpulseList[i] > self.threshold:
                    # If breakable object is in the list, start Fire Fracturable Target
                    body_tar = bodyList[i]
                    if (bid_tar > -1 and body_tar == bid_tar) or (bid_tar < 0):
                        print("fire", body_tar)
                        tarPos, tarOrn = p.getBasePositionAndOrientation(body_tar)
                        print(tarPos, tarOrn)
                        # linearVelocity, angularVelocity = p.getBaseVelocity(body_tar)
                        linearVelocity, angularVelocity = self.BreakableList[i].getLastVel()
                        print(linearVelocity, angularVelocity)

                        print(detailedImpulseList[i])
                        if self.allowAutoFracture and len(self.BreakableList[i].fracList) <= 0:
                            result = self.BreakableList[i].startFracturing(detailedImpulseList[i], tarPos, tarOrn, body_tar, self.collisionNum, self.impulseMax)
                            if not result:
                                continue

                        # Fire trigger
                        self.resetGravity()
                        print(self.BreakableList[i].fracList)
                        fragments = max(len(self.BreakableList[i].fracList), 1)
                        angularVelocity = tuple(0/fragments for ti in angularVelocity)
                        self.BreakableList[i].fractureFire(tarPos, tarOrn, linearVelocity, angularVelocity)
                        linearVelocity, angularVelocity = p.getBaseVelocity(self.BreakableList[i].fracList[0].bid)
                        print(linearVelocity, angularVelocity)
        
        for breakable in self.BreakableList:
            if not breakable.isStatic and breakable.oriObj.active:
                # Save velocity from 1 or 2 frames ago
                linearVelocity, angularVelocity = p.getBaseVelocity(self.BreakableList[i].oriObj.bid)
                self.BreakableList[i].setLastVel(linearVelocity, angularVelocity)
                
    def exportObjByTime(self, timeStep):
        writeBreakableList = []
        nameList = []

        for i in range(len(self.BreakableList)):
            breakable = self.BreakableList[i]
            meshList = []
            (activeList, shapeList, bodyList) = breakable.getVisualization()
            nameList.append(breakable.name)
            print(shapeList, activeList)
            for j in range(len(activeList)):
                if activeList[j]:
                    vertices, faces = load_mesh(shapeList[j])
                    iPos, iRot = p.getBasePositionAndOrientation(bodyList[j])
                    
                    q = Quaternion(iRot, is_xyzw_order=True)

                    vOut = []
                    for v in vertices:
                        newV = np.add(q.rotate(v), iPos)
                        vOut.append(newV)
                    vOut = np.array(vOut)

                    transformedMesh = form_mesh(vOut, faces)
                    meshList.append(transformedMesh)
                    
            writeBreakableList.append(meshList)

        for i in range(len(writeBreakableList)):
            outMesh = merge_meshes(writeBreakableList[i])
            save_mesh(
                os.path.join(self.resultPath, f"{nameList[i]}_{timeStep}.obj"),
                outMesh
            )

    def StartRun(self):

        time.sleep(5.)

        for obj in self.BreakableList:
            obj.activate()
            # obj.activate()

        count = 0
        while (1):
            if count > self.timeRange:
                break
            p.stepSimulation()
            self.catchImpact(count, p.getContactPoints(), -1)

            time.sleep(1./240.)
            if self.needOutput:
                self.exportObjByTime(count)
            count += 1

    def StopRun(self):
        p.disconnect(self.physicsClient)

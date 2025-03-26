######################################################
## Mass OBJ exporter script (python)                ##
##--------------------------------------------------##
## Script Written by Lucas morgan.                  ##
##--------------------------------------------------##
## Email: lucasm@enviral-design.com                 ##
##--------------------------------------------------##
## Website: www.enviral-design.com                  ##
######################################################

# - Installation
## To run this script, copy all of the text in this
## window into the python tab of your maya script editor.

# - Usage
## 1. Select all polygon mesh objects in scene
## 2. Choose directory
## 3. BAM!

## Note: exporting anything other than polys may result in empty objs, or an error.

####----------------------------------------------####

import maya.cmds as cmds
import maya.mel as mel

import maya.app.mayabullet.BulletUtils as BulletUtils
import maya.app.mayabullet.RigidBody as RigidBody

#deletes old window and preference, if it still exists
if(cmds.window('uiWindow_objLoopExport', q=1, ex=1)):
	cmds.deleteUI('uiWindow_objLoopExport')
if(cmds.windowPref('uiWindow_objLoopExport', q=1, ex=1)):
	cmds.windowPref('uiWindow_objLoopExport', r=1)

def dirToPath(filePath, fileType):
	cmds.textFieldButtonGrp('toDir', edit=True, text=str(filePath))
	return 1

def dirFromPath(filePath, fileType):
	cmds.textFieldButtonGrp('fromDir', edit=True, text=str(filePath))
	return 1

def dirNowPath(filePath, fileType):
	cmds.textFieldButtonGrp('now', edit=True, text=str(filePath))
	return 1

def startExport(path):
	count = 0
	fromPathStr = cmds.textFieldButtonGrp('fromDir', query = True, text = True)
	toPathStr = cmds.textFieldButtonGrp('toDir', query = True, text = True)
	now = int(cmds.textFieldButtonGrp('now', query = True, text = True))
	fileType = "obj"
	extraFile = "12ddb18397a816c8948bef6886fb4ac.obj"
	files = cmds.getFileList(folder=fromPathStr, filespec='*.%s' % fileType)
	if len(files) == 0:
		cmds.warning("No files found")
	else:
		for f in files:
			try:
				cmds.select('|Mesh')
			except:
				print('no target')
			if count == now:
				cmds.delete() # doDelete;
				print('load ' + fromPathStr+'/'+extraFile)
				filename = cmds.file(fromPathStr + '/' + extraFile, i=True) # file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "a772d12b98ab61dc26651d9d35b77ca" -options "mo=1"  -pr  -importTimeRange "combine" "/Users/yuhanghuang/Workspaces/ShapeNetv2/Result/bowlObj_norm/6a772d12b98ab61dc26651d9d35b77ca.obj";
				print(filename)
				cmds.select('|Mesh')
				BulletUtils.checkPluginLoaded()
				resultList = RigidBody.CreateRigidBody().executeCommandCB()
				cmds.select( clear=True )# cmds.rename(resultList[0], 'targetShape')
				mel.eval('setAttr "bulletRigidBodyShape2.colliderShapeType" 5;')
				mel.eval('setAttr "bulletRigidBodyShape2.friction" 0.6;')
				mel.eval('setAttr "bulletRigidBodyShape2.restitution" 0.4;')
				mel.eval('setAttr "bulletRigidBodyShape2.mass" 8;')
				

				finalExportPath = toPathStr + "/" + extraFile.split('.')[0] + ".bullet"
				mel.eval('file -force -options "" -type "bullet" -pr -ea "'+finalExportPath+'";')# mel.eval('file -force -options "groups=0;ptgroups=0;materials=0;smoothing=1;normals=1" -typ "OBJexport" -pr -es "'+finalExportPath+'";')
				print('file -force -options "" -type "bullet" -pr -ea "'+finalExportPath+'";')
			count += 1
		print("Exporting Complete!")
		now += 1

def browseFrom():
	cmds.fileBrowserDialog( m=4, fc=dirFromPath, ft='directory', an='Choose Bullet Directory')
	return
def browseTo():
	cmds.fileBrowserDialog( m=4, fc=dirToPath, ft='directory', an='Choose Obj Directory')
	return

def makeGui():
	uiWindow_objLoopExport = cmds.window('uiWindow_objLoopExport', title="OBJ Bullet exporter", iconName='uiWindow_objLoopExport', widthHeight=(330, 160) )
	cmds.columnLayout('uiColWrapper', w = 375, adjustableColumn=False, parent = 'uiWindow_objLoopExport' )
	cmds.text( label='Settings', align='left', parent = 'uiColWrapper')
	cmds.textFieldButtonGrp('fromDir', label='From Directory Path', cw3 = [80,190,50], text='/Users/yuhanghuang/Workspaces/ShapeNetv2/Result/bowlObj_norm', buttonLabel='browse', buttonCommand=browseFrom, parent = 'uiColWrapper')
	cmds.textFieldButtonGrp('toDir', label='To Directory Path', cw3 = [80,190,50], text='/Users/yuhanghuang/Workspaces/ShapeNetv2/Result/bowlBullet', buttonLabel='browse', buttonCommand=browseTo, parent = 'uiColWrapper')
	cmds.textFieldButtonGrp('now', label='To Directory Path', cw3 = [80,190,50], text='0', buttonLabel='browse', buttonCommand=browseTo, parent = 'uiColWrapper')
	cmds.button('startExport', label = "Export Selected", parent = 'uiColWrapper', width = 322, command = startExport)
	cmds.showWindow( uiWindow_objLoopExport )


makeGui()




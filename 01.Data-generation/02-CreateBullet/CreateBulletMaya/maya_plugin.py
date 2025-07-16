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

def startConfigure(path):
	
	fromPathStr = cmds.textFieldButtonGrp('fromDir', query = True, text = True)
	now = int(cmds.textFieldButtonGrp('now', query = True, text = True))
	fileType = "obj"
	files = cmds.getFileList(folder=fromPathStr, filespec='*.%s' % fileType)
	if len(files) == 0:
		cmds.warning("No files found")
	else:
		try:
			cmds.select('|Mesh')
		except:
			print('no target')
			
		cmds.delete() 

		# Save next value
		print("load" + files[now])
		f = files[now]

		# Load mesh
		filename = cmds.file(fromPathStr + '/' + f, i=True)
		print(filename)

		# Setup Configuration
		cmds.select('|Mesh')
		BulletUtils.checkPluginLoaded()
		resultList = RigidBody.CreateRigidBody().executeCommandCB()
		cmds.select( clear=True )# cmds.rename(resultList[0], 'targetShape')
		mel.eval('setAttr "bulletRigidBodyShape2.colliderShapeType" 5;')
		mel.eval('setAttr "bulletRigidBodyShape2.friction" 0.6;')
		mel.eval('setAttr "bulletRigidBodyShape2.restitution" 0.4;')
		mel.eval('setAttr "bulletRigidBodyShape2.mass" 8;')

def startExport(path):
		
	fromPathStr = cmds.textFieldButtonGrp('fromDir', query = True, text = True)
	toPathStr = cmds.textFieldButtonGrp('toDir', query = True, text = True)
	now = int(cmds.textFieldButtonGrp('now', query = True, text = True))
	fileType = "obj"
	files = cmds.getFileList(folder=fromPathStr, filespec='*.%s' % fileType)

	# Double saving
	f = files[now]
	finalExportPath = toPathStr + "/" + f.split('.')[0] + ".bullet"
	mel.eval('file -force -options "" -type "bullet" -pr -ea "'+finalExportPath+'";')
	print('file -force -options "" -type "bullet" -pr -ea "'+finalExportPath+'";')
	print("Exporting Complete!")
	now += 1
	cmds.textFieldButtonGrp('now', edit=True, text=str(now))

def browseFrom():
	cmds.fileBrowserDialog( m=4, fc=dirFromPath, ft='directory', an='Choose Obj Directory')
	return

def browseTo():
	cmds.fileBrowserDialog( m=4, fc=dirToPath, ft='directory', an='Choose Bullet Directory')
	return

def makeGui():
	uiWindow_objLoopExport = cmds.window('uiWindow_objLoopExport', title="OBJ Bullet exporter", iconName='uiWindow_objLoopExport', widthHeight=(330, 160) )
	cmds.columnLayout('uiColWrapper', w = 375, adjustableColumn=False, parent = 'uiWindow_objLoopExport' )
	cmds.text( label='Settings', align='left', parent = 'uiColWrapper')
	cmds.textFieldButtonGrp('fromDir', label='From Directory Path', cw3 = [80,190,50], text='/Users/yuhanghuang/Workspaces/01.research-proj/TEBP/data/norm/abstract_animal', buttonLabel='browse', buttonCommand=browseFrom, parent = 'uiColWrapper')
	cmds.textFieldButtonGrp('toDir', label='To Directory Path', cw3 = [80,190,50], text='/Users/yuhanghuang/Workspaces/01.research-proj/TEBP/data/bullet/abstract_animal', buttonLabel='browse', buttonCommand=browseTo, parent = 'uiColWrapper')
	cmds.textFieldButtonGrp('now', label='To Directory Path', cw3 = [80,190,50], text='0', buttonLabel='browse', buttonCommand=browseTo, parent = 'uiColWrapper')
	cmds.button('startConfigure', label = "Configuration", parent = 'uiColWrapper', width = 322, command = startConfigure)
	cmds.button('startExport', label = "Export", parent = 'uiColWrapper', width = 322, command = startExport)
	cmds.showWindow( uiWindow_objLoopExport )

makeGui()

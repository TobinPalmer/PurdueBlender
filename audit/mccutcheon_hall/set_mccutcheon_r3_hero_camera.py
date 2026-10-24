import bpy,os,json
expected=os.path.normcase(os.path.abspath('modular/buildings/mccutcheon_hall.blend'))
assert os.path.normcase(os.path.abspath(bpy.data.filepath))==expected
cam=bpy.data.objects['Cam_Hero_Perspective']; cam.data.lens=30.0
bpy.ops.wm.save_as_mainfile(filepath=expected)
print('MCUT_R3_CAMERA_FRAME='+json.dumps({'lens_mm':cam.data.lens,'camera':cam.name,'file':expected}))

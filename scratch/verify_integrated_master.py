import bpy, os
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
scene=bpy.context.scene
inst=bpy.data.objects.get('Engineering_Mall_Groundwork_Patch_Instance')
print('MASTER',bpy.data.filepath,'SCENE',scene.name,'OBJECTS',len(scene.objects))
print('PATCH_INSTANCE',bool(inst),inst.instance_type if inst else None, inst.instance_collection.name if inst and inst.instance_collection else None,tuple(inst.location) if inst else None)
print('ENG_LIBS',[(l.name,l.filepath,Path(bpy.path.abspath(l.filepath)).exists()) for l in bpy.data.libraries if ('engineering_mall_groundwork_patch' in l.name.lower() or 'engineering_foliage_library' in l.name.lower())])
print('CAMPUS_SITE_SURFACES_LEFT',[o.name for o in bpy.data.objects if o.name.startswith(('Engineering_Fountain_Grand_Plaza_Arena','Engineering_Mall_Central_Concourse','Engineering_Mall_EastWest_Promenade','Engineering_Mall_Fountain_Plaza','Engineering_Mall_NorthSouth_Promenade','Engineering_Mall_Lawn_'))])
if not inst or inst.instance_collection is None: raise RuntimeError('Engineering Mall patch instance missing')
for l in bpy.data.libraries:
    if l.filepath and not Path(bpy.path.abspath(l.filepath)).exists():
        print('MISSING_LINK',l.name,l.filepath)
print('CAMERA',scene.camera.name if scene.camera else None)

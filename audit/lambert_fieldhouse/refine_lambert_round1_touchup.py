import bpy, json
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
interior=bpy.data.collections['LAMB_Interior']
rig=bpy.data.collections['Preview_Rig']

# The initial source model had a flat polygon spanning most of the fieldhouse;
# it overlapped the reconstructed track/infield. Remove that superseded panel.
for ob in list(interior.objects):
    if (ob.name.startswith('LAMB | schematic interior arena floor') or
        ob.name.startswith('LAMB | level 1 interior floor plate')):
        bpy.data.objects.remove(ob,do_unlink=True)
# The photo reference supports banners but not this layout; omit these floating
# banner boards from the open-roof cutaway while retaining the exterior library.
for ob in list(interior.objects):
    if ob.name.startswith('LAMB | schematic wall banner') or ob.name.startswith('LAMB | schematic banner gold stripe'):
        ob.hide_render=True

mat=bpy.data.materials.get('LAMB | infield competition floor')
if mat and mat.use_nodes:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(.255,.265,.27,1)
        bs.inputs['Roughness'].default_value=.9
        bs.inputs['Metallic'].default_value=0

cam=bpy.data.objects['LAMB | interior review camera']
cam.location=(-72,-108,68)
target=Vector((0,0,5.0))
cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
cam.data.lens=37
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
rig=bpy.data.collections['Preview_Rig']
interior=bpy.data.collections['LAMB_Interior']
cam=bpy.data.objects['LAMB | interior review camera']
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
hidden=[]
for name in ('LAMB_Structure','LAMB_Facade'):
    c=bpy.data.collections.get(name)
    if c:
        for ob in c.objects:
            hidden.append((ob,ob.hide_render)); ob.hide_render=True
if canopy:
    hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=cam
scene.render.filepath=OUT+r'/interior_round1.png'
bpy.ops.render.render(write_still=True)
for ob,val in hidden: ob.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lambert_fieldhouse']
summary={'reopen':'PASS','asset':'modular/buildings/lambert_fieldhouse.blend',
         'asset_object_count':sum(1 for o in asset.all_objects),
         'interior_object_count':len(bpy.data.collections['LAMB_Interior'].objects),
         'roof_object_count':len(bpy.data.collections['LAMB_Roof'].objects),
         'interior_render':'audit/lambert_fieldhouse/interior_round1.png',
         'saved_source_camera':bpy.context.scene.camera.name if bpy.context.scene.camera else None,
         'master_or_shared_files_edited':False}
open(OUT+r'/validation_round1.json','w').write(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

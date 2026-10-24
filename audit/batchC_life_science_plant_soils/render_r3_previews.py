import bpy
from mathutils import Vector
ASSET=r'modular/buildings/life_science_plant_and_soils_laboratory.blend'; OUT=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_life_science_plant_soils'
bpy.ops.wm.open_mainfile(filepath=ASSET); s=bpy.context.scene
cam=next((o for o in bpy.data.objects if o.type=='CAMERA'),None)
if cam is None:
 d=bpy.data.cameras.new('LSPS R3 evidence camera'); cam=bpy.data.objects.new('LSPS R3 evidence camera',d); s.collection.objects.link(cam)
s.camera=cam; cam.data.type='ORTHO'; s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=1500; s.render.resolution_y=1050; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'; s.render.film_transparent=False
# Hide interior and landscaping for roof comparison.
for c in [bpy.data.collections.get('LSPS_Interior'),bpy.data.collections.get('LSPS_Site')]:
 if c: c.hide_render=True
cam.location=(0,0,95); target=Vector((0,0,0)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=72; s.render.filepath=OUT+r'\roof_top_r3.png'; bpy.ops.render.render(write_still=True)
# A closer three-quarter west elevation preview.
site=bpy.data.collections.get('LSPS_Site')
if site: site.hide_render=False
cam.location=(-83,-4,25); target=Vector((0,-2,5)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=58; s.render.filepath=OUT+r'\exterior_west_r3.png'; bpy.ops.render.render(write_still=True)
# Cutaway view of source-backed basement cold-storage modules.
for name in ['LSPS_Structure','LSPS_Facade','LSPS_Roof','LSPS_Site']:
 c=bpy.data.collections.get(name)
 if c: c.hide_render=True
interior=bpy.data.collections['LSPS_Interior']; interior.hide_render=False
for o in interior.objects:
 keep=o.name.startswith('LSPS R3 | B cold room') or o.name=='LSPS R3 | level B below-grade floor plate'
 o.hide_render=not keep
for o in bpy.data.objects:
 if 'floor plate' in o.name and o.name!='LSPS R3 | level B below-grade floor plate': o.hide_render=True
cam.location=(41,-49,5); target=Vector((0,-2,-2.6)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=30; s.render.filepath=OUT+r'\basement_cutaway_r3.png'; bpy.ops.render.render(write_still=True)
print('R3 rendered roof/exterior/basement previews')



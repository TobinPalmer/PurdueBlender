import bpy
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.data.scenes['Building_massing_duhme_ophelia_residence_hall_1bb4e9c']
cam=scene.camera;target=Vector((-595,-212,7));cam.location=(-595,-260,15);cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=27
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.filepath=str(root/'audit/duhme_ophelia_residence_hall/front_candidate.png');bpy.ops.render.render(write_still=True)
# remove camera-related objects by visibility for cutaway top floor plan preview
hidden=[]
for o in bpy.data.objects:
 if o.name.startswith(('DUHME_Continuous_Red_Brick','DUHME_Continuous_GIS','DUHME_Continuous_Slate_Roof_Underlay','DUHME_Principal_Central_Gable','DUHME_West_Wing_Roof','DUHME_East_Wing_Roof','DUHME_Brick_Chimney','DUHME_Bay','DUHME_Front_Gable','DUHME_Roof')) or 'Exterior_Window' in o.name or 'Limestone' in o.name or 'Entry_' in o.name or 'Entrance_' in o.name:
  o.hide_render=True; hidden.append(o)
# Show only first-storey partition and furnishings for an honest schematic cutaway.
for o in bpy.data.objects:
 if any(k in o.name for k in ['Interior_Floor_2','Interior_Floor_3','Interior_Floor_4','_F2_','_F3_','_F4_']): o.hide_render=True
cam.location=(-595,-202,82);target=Vector((-595,-202,0));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=80
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.filepath=str(root/'audit/duhme_ophelia_residence_hall/interior_cutaway_candidate.png');bpy.ops.render.render(write_still=True)

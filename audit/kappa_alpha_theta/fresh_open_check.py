"""Fresh-open integrity and review render for Kappa Alpha Theta asset."""
import bpy
from mathutils import Vector
from pathlib import Path

asset = Path(__file__).resolve().parents[2] / "modular/buildings/massing_house_301840865_cbf7de2.blend"
preview = Path(__file__).resolve().parent / "fresh_open_preview.png"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.context.scene
coll = bpy.data.collections.get("Asset_massing_house_301840865_cbf7de2")
assert scene.name == "Building_massing_house_301840865_cbf7de2"
assert coll is not None
assert scene.get("asset_id") == "massing_house_301840865_cbf7de2"
assert scene.get("building") == "Kappa Alpha Theta (Purdue Alpha Chi), FID 786"
assert len(coll.objects) >= 300
assert all((o.type != 'MESH' or o.data is not None) for o in coll.objects)
bounds=[]
for obj in coll.objects:
    if obj.type == 'MESH':
        bounds.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
mins=tuple(min(v[i] for v in bounds) for i in range(3))
maxs=tuple(max(v[i] for v in bounds) for i in range(3))
print("FRESH_OPEN_OK",scene.name,coll.name,"objects",len(coll.objects),"meshes",sum(o.type=='MESH' for o in coll.objects))
print("LOCAL_BOUNDS",mins,maxs)
print("SCENE_ORIGIN",scene.get("geometry_origin"))
print("SCHEMATIC_NOTE",scene.get("interior_disclaimer"))

# Temporary camera and lights for an audit preview; these are not saved into the
# source asset, and are removed from Blender memory on process exit.
def aim(obj, point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(34,-42,34))
cam=bpy.context.object
cam.name="AUDIT_preview_camera"
aim(cam,(0,0,5.7))
cam.data.type='ORTHO'; cam.data.ortho_scale=48
scene.camera=cam
for name,loc,power,size in [
    ("AUDIT_key",(4,-22,30),4600,22),
    ("AUDIT_fill",(-22,-2,18),2600,18),
    ("AUDIT_rim",(8,22,24),3200,16),
]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=bpy.context.object; light.name=name; light.data.energy=power; light.data.shape='DISK'; light.data.size=size
    aim(light,(0,0,4))
scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(preview)
scene.render.film_transparent=False
scene.world.color=(0.35,0.35,0.35)
bpy.ops.render.render(write_still=True)
print("REVIEW_RENDER",preview)

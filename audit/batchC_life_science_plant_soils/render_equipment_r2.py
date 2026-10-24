import bpy
from mathutils import Vector

ASSET = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\life_science_plant_and_soils_laboratory.blend"
OUT = r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_life_science_plant_soils\interior_equipment_r2.png"
OUT_DRYER = r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_life_science_plant_soils\dryer_bank_close_r2.png"
OUT_GRINDER = r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_life_science_plant_soils\grinder_group_close_r2.png"
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
for name in ["LSPS_Structure", "LSPS_Facade", "LSPS_Roof", "LSPS_Site"]:
    c=bpy.data.collections.get(name)
    if c: c.hide_render=True
for o in scene.objects:
    if "interior floor plate" in o.name:
        o.hide_render=True
    if "official GIS footprint ground floor" in o.name:
        o.hide_render=False
print("R2 floor visibility", [(o.name,o.hide_render,tuple(round(v,2) for v in o.dimensions)) for o in scene.objects if "floor plate" in o.name or "ground floor" in o.name])
cam=bpy.data.objects.get("LSPS | three-quarter preview camera")
if cam is None:
    cd=bpy.data.cameras.new("LSPS R2 interior camera"); cam=bpy.data.objects.new("LSPS R2 interior camera",cd); scene.collection.objects.link(cam)
cam.location=(0,-54,49); target=Vector((0,0,0.4)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=72; scene.camera=cam
for o in list(scene.objects):
    if o.type=='LIGHT': bpy.data.objects.remove(o,do_unlink=True)
ld=bpy.data.lights.new("LSPS R2 softbox",'AREA'); ld.energy=7000; ld.shape='DISK'; ld.size=35
light=bpy.data.objects.new("LSPS R2 softbox",ld); scene.collection.objects.link(light); light.location=(-15,-20,35)
direction=Vector((0,0,0))-light.location; light.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1300; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=OUT
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0.3
if scene.world:
    scene.world.use_nodes=True; bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs['Color'].default_value=(0.30,0.34,0.38,1); bg.inputs['Strength'].default_value=0.55
bpy.ops.render.render(write_still=True)
for output, loc, target in [
    (OUT_DRYER, (12,-11,7), (12,2.7,0.9)),
    (OUT_GRINDER, (-18,-10,7), (-18,0.7,0.8)),
]:
    cam.location=loc
    cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=16
    scene.render.filepath=output
    bpy.ops.render.render(write_still=True)
print("Rendered R2 first-floor laboratory evidence", OUT, OUT_DRYER, OUT_GRINDER)

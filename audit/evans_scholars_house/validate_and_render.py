import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_house_301841610_b6ad6ed.blend'
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(asset))
col=bpy.data.collections.get('Asset_massing_house_301841610_b6ad6ed')
scene=bpy.data.scenes.get('Building_massing_house_301841610_b6ad6ed')
assert col and scene
assert bpy.context.scene==scene, (bpy.context.scene.name,scene.name)
assert len(col.objects)>100
assert all(o.get('building_id')=='massing_house_301841610_b6ad6ed' for o in col.objects)
mesh_objs=[o for o in col.objects if o.type=='MESH']
world=[]
for o in mesh_objs:
    for v in o.bound_box:
        world.append(o.matrix_world@Vector(v))
mins=[min(p[i] for p in world) for i in range(3)]
maxs=[max(p[i] for p in world) for i in range(3)]
missing=[]
for img in bpy.data.images:
    if img.source=='FILE' and img.filepath and not img.packed_file:
        p=bpy.path.abspath(img.filepath)
        if not Path(p).exists(): missing.append(str(p))

def uv(u,v):
    a=math.radians(-21.8)
    return (u*math.cos(a)-v*math.sin(a),u*math.sin(a)+v*math.cos(a))
def point(u,v,z):
    x,y=uv(u,v);return Vector((x,y,z))
def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,target);return o
def camera(name,loc,target,lens=45):
    d=bpy.data.cameras.new(name);d.lens=lens
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,target);scene.camera=o;return o

scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=48
scene.render.resolution_x=1400;scene.render.resolution_y=950;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-0.6;scene.view_settings.gamma=1
scene.world.color=(.12,.16,.20)
if scene.world.use_nodes:
    for n in scene.world.node_tree.nodes:
        if n.type=='BACKGROUND':
            n.inputs['Color'].default_value=(.12,.16,.20,1)
            n.inputs['Strength'].default_value=.22
scene.render.film_transparent=False
target=point(0,-1.5,3.3)
area('Large warm key',point(-34,-42,34),850,22,target)
area('Cool fill',point(30,-18,26),520,20,target)
area('Roof rim',point(8,28,30),650,16,target)
sun_data=bpy.data.lights.new('Late afternoon sun','SUN');sun_data.energy=.7
sun=bpy.data.objects.new('Late afternoon sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-35),math.radians(-24))
camera('Front approach camera',point(-3,-41,7.2),point(0,-1.5,2.65),42)
scene.render.filepath=str(out/'front_approach.png');bpy.ops.render.render(write_still=True)
# Source-based aerial: geometry and roof silhouette against GIS footprint, no landscape.
camera('Aerial roof camera',point(-32,-43,62),point(0,0,1.5),55)
scene.render.resolution_x=1500;scene.render.resolution_y=1150
scene.render.filepath=str(out/'roof_aerial.png');bpy.ops.render.render(write_still=True)
# Schematic interior cutaway: hide roof/portico and exterior walls, then show room program.
hidden=[]
for o in col.objects:
    if any(k in o.name.lower() for k in ('roof','gable','portico column','portico fascia','patio canopy','front brick wall','gis exterior brick wall')):
        o.hide_render=True;hidden.append(o)
camera('Interior schematic camera',point(-7,-15,13),point(-5,1,.5),43)
scene.render.resolution_x=1300;scene.render.resolution_y=1000
scene.render.filepath=str(out/'interior_schematic.png');bpy.ops.render.render(write_still=True)
for o in hidden:o.hide_render=False

payload={
 "fresh_open":True,"scene":scene.name,"collection":col.name,"objects":len(col.objects),
 "mesh_objects":len(mesh_objs),"material_count":len({m.name for o in col.objects for m in o.data.materials if m}) if any(hasattr(o.data,'materials') for o in col.objects) else None,
 "bounds_min_m":mins,"bounds_max_m":maxs,"unpacked_missing_external_images":missing,
 "render_paths":[str(out/'front_approach.png'),str(out/'roof_aerial.png'),str(out/'interior_schematic.png')],
 "asset_sha256":hashlib.sha256(asset.read_bytes()).hexdigest(),
}
(out/'fresh_open_validation.json').write_text(json.dumps(payload,indent=2))
print(json.dumps(payload,indent=2))

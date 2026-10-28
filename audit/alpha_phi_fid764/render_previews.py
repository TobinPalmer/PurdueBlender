import bpy, math, json, os
from mathutils import Vector

HERE=os.path.dirname(__file__)
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841331_735e92f.blend')
with open(os.path.join(HERE,'build_config.json'),encoding='utf8') as f: cfg=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
obj=bpy.data.objects[cfg['object_name']]
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=800; scene.render.resolution_y=600; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='WORLD'
world=bpy.data.worlds.new('AlphaPhi Preview World') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.45,0.53,0.62,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.65
for ob in list(scene.objects):
    if ob.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(ob,do_unlink=True)
def aim(camera,target): camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; aim(ob,target)
def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name); data.type='ORTHO'; data.ortho_scale=scale
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; aim(ob,target); scene.camera=ob
center=Vector(cfg['interior_module_center_xy'])
# The GIS polygon center provides a stable camera target across reruns.
ring=json.load(open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf8'))['features'][0]['geometry']['rings'][0][:-1]
R=6378137.0; lat0=cfg['coordinate_origin']['latitude']; lon0=cfg['coordinate_origin']['longitude']
pts=[]
for mx,my in ring:
    lon=mx/R*180/math.pi; lat=(2*math.atan(math.exp(my/R))-math.pi/2)*180/math.pi
    pts.append(Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0)))
center=sum(pts,Vector((0,0,0)))/len(pts)
target=center+Vector((0,0,4.5))
area('Large soft key',center+Vector((26,-34,45)),5200,24,target)
area('Cool fill',center+Vector((-35,-5,22)),2600,20,target)
area('Roof rim',center+Vector((5,36,32)),3600,18,target)
camloc=center+Vector((32,-42,27)); camera('Exterior Three Quarter',camloc,target,53)
scene.render.filepath=os.path.join(HERE,'exterior_three_quarter.png'); bpy.ops.render.render(write_still=True)

# Create a temporary interior-only mesh from the saved mesh. This is a viewing aid,
# not part of the exported one-object building collection.
src=obj.data; keep_names={'ALPHAPHI_Interior_Bordeaux_Carpet','ALPHAPHI_Interior_Warm_Plaster','ALPHAPHI_Interior_Furniture','ALPHAPHI_Bed_Linen','ALPHAPHI_Entry_Oak'}
preview_colors={'ALPHAPHI_Interior_Bordeaux_Carpet':(0.43,0.12,0.18,1),'ALPHAPHI_Interior_Warm_Plaster':(0.88,0.80,0.68,1),'ALPHAPHI_Interior_Furniture':(0.43,0.25,0.13,1),'ALPHAPHI_Bed_Linen':(0.98,0.94,0.82,1),'ALPHAPHI_Entry_Oak':(0.45,0.25,0.12,1)}
for m in src.materials:
    if m and m.name in preview_colors: m.diffuse_color=preview_colors[m.name]
mat_ids={i for i,m in enumerate(src.materials) if m and m.name in keep_names}
verts=[]; faces=[]; mids=[]; used=set()
upper_level=cfg['estimated_wall_height_m']/2+0.12
for p in src.polygons:
    if p.material_index not in mat_ids: continue
    coords=[src.vertices[i].co for i in p.vertices]
    if sum(v.z for v in coords)/len(coords) < cfg['estimated_wall_height_m']/2: continue
    base=len(verts); verts.extend(tuple(v) for v in coords); faces.append(tuple(range(base,base+len(coords)))); mids.append(p.material_index)
mesh=bpy.data.meshes.new('AlphaPhi_Schematic_Upper_Interior_Preview'); mesh.from_pydata(verts,[],faces)
for m in src.materials: mesh.materials.append(m)
for p,mi in zip(mesh.polygons,mids): p.material_index=mi
mesh.update(); interior=bpy.data.objects.new('Preview only — schematic upper rooms',mesh); scene.collection.objects.link(interior)
obj.hide_render=True
for ob in scene.objects:
    if ob.type=='LIGHT': bpy.data.objects.remove(ob,do_unlink=True)
area('Interior key',center+Vector((3,-4,24)),3800,18,center+Vector((0,0,3.8)))
area('Interior fill',center+Vector((-16,8,18)),1800,16,center+Vector((0,0,3.8)))
floor_z=cfg['estimated_wall_height_m']/2+0.18
interior_center=Vector((cfg['interior_module_center_xy'][0],cfg['interior_module_center_xy'][1],0))
camera('Upper Schematic Plan',interior_center+Vector((0,0,24)),interior_center+Vector((0,0,floor_z)),20)
scene.render.filepath=os.path.join(HERE,'schematic_upper_rooms.png'); bpy.ops.render.render(write_still=True)

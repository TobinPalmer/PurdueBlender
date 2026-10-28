import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/glenwood_fid794'
SRC=AUD/'sources'
ASSET=ROOT/'modular/buildings/massing_house_301841249_f827941.blend'
FEAT=json.loads((SRC/'purdue_gis_fid794_2026-10-28_4326.json').read_text(encoding='utf-8'))['features'][0]
ring_ll=FEAT['geometry']['rings'][0][:-1]
expected=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring_ll]

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_massing_house_301841249_f827941')
assert scene.name=='Building_massing_house_301841249_f827941'
assert col is not None
objects=list(col.objects)
assert len(objects)==1 and objects[0].name=='House_301841249' and objects[0].type=='MESH'
house=objects[0]
base=[v.co for v in house.data.vertices if abs(v.co.z)<1e-5]
assert len(base)>=len(expected)
nearest=[min(base,key=lambda v:math.hypot(v.x-x,v.y-y)) for x,y in expected]
errors=[math.hypot(v.x-x,v.y-y) for v,(x,y) in zip(nearest,expected)]
max_err=max(errors)
assert max_err<1e-4,max_err
xs=[v.co.x for v in house.data.vertices]; ys=[v.co.y for v in house.data.vertices]; zs=[v.co.z for v in house.data.vertices]
cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2

tmp=bpy.data.collections.new('FreshOpen_Temporary_Render'); scene.collection.children.link(tmp)
def aim(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def cam(name,loc,target,scale):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); tmp.objects.link(o); o.location=loc; d.type='ORTHO'; d.ortho_scale=scale; aim(o,target); scene.camera=o; return o
def light(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; o=bpy.data.objects.new(name,d); tmp.objects.link(o); o.location=loc; aim(o,target)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=80; scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'; scene.view_settings.view_transform='AgX'
world=scene.world or bpy.data.worlds.new('Glenwood_FreshOpen_World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.22,0.25,0.29,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.30
center=(cx,cy,4.3)
light('FreshOpen_Key',(cx-25,cy+30,35),1500,18,center); light('FreshOpen_Fill',(cx+32,cy-15,26),500,16,center); light('FreshOpen_Rim',(cx+8,cy-35,28),350,16,center)
def render(name,loc,target,scale,file):
    cam(name,loc,target,scale); scene.render.filepath=str(AUD/file); bpy.ops.render.render(write_still=True)
render('FreshOpen_Exterior_Camera',(cx-10,max(ys)+35,14),center,40,'fresh_open_exterior.png')
render('FreshOpen_Roof_Camera',(cx-20,max(ys)+43,24),center,50,'fresh_open_roof_oblique.png')
render('FreshOpen_Top_Camera',(cx,cy,76),(cx,cy,0),49,'fresh_open_top.png')
# Reproduce the interior-only cutaway from the saved one-mesh asset.
cut=house.copy(); cut.data=house.data.copy(); cut.name='FreshOpen_Interior_Cutaway'; tmp.objects.link(cut)
keep_names=('Glenwood_Interior_Floor_Schematic','Glenwood_Interior_Partition_Schematic','Glenwood_Interior_Wood_Schematic','Glenwood_Interior_Furnishing_Schematic')
allowed={i for i,m in enumerate(cut.data.materials) if m and any(q in m.name for q in keep_names)}
floor_indices={i for i,m in enumerate(cut.data.materials) if m and 'Interior_Floor_Schematic' in m.name}
partition_indices={i for i,m in enumerate(cut.data.materials) if m and 'Interior_Partition_Schematic' in m.name}
bm=bmesh.new(); bm.from_mesh(cut.data)
# Keep the lower-floor cutaway readable: remove the upper floor slab and upper-story partitions from this view.
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index not in allowed or (f.material_index in floor_indices and f.calc_center_median().z>1.0) or (f.material_index in partition_indices and f.calc_center_median().z>3.5)],context='FACES'); bm.to_mesh(cut.data); bm.free(); cut.data.update()
house.hide_render=True
for o in tmp.objects:
    if o.type=='LIGHT': o.data.energy*=0.45
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.18
render('FreshOpen_Interior_Camera',(cx-18,max(ys)+28,48),(cx,cy,0.5),40,'fresh_open_schematic_interior_cutaway.png')
# No helpers or duplicated geometry are retained in the saved deliverable.
for o in list(tmp.objects): bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(tmp)

materials=[m.name for m in house.data.materials if m]
external=[]
for mat in bpy.data.materials:
    if not mat.node_tree: continue
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and node.image.filepath and not node.image.packed_file:
            external.append({'material':mat.name,'image':node.image.name,'filepath':node.image.filepath})
bounds=[[min(xs),min(ys),min(zs)],[max(xs),max(ys),max(zs)]]
report={
 'result':'PASS' if len(objects)==1 and max_err<1e-4 and not external else 'FAIL',
 'validation_mode':'Blender 5.2.3 LTS fresh-open of saved Glenwood asset',
 'asset_relative_path':'modular/buildings/massing_house_301841249_f827941.blend',
 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'scene':scene.name,'asset_collection':col.name,'collection_object_count':len(objects),
 'object_names':[o.name for o in objects],'mesh_vertices':len(house.data.vertices),'mesh_faces':len(house.data.polygons),
 'source_outline_vertices':len(expected),'max_source_outline_vertex_error_m':max_err,
 'source_outline_project_local_bounds_m':[[min(x for x,y in expected),min(y for x,y in expected)],[max(x for x,y in expected),max(y for x,y in expected)]],
 'mesh_bounds_xyz_m':bounds,'mesh_dimensions_xyz_m':[bounds[1][i]-bounds[0][i] for i in range(3)],
 'materials':materials,'external_image_dependencies':external,
 'fresh_open_preview_files':['fresh_open_exterior.png','fresh_open_roof_oblique.png','fresh_open_top.png','fresh_open_schematic_interior_cutaway.png'],
 'limitations':['The GIS polygon is used as the lower wall perimeter by construction and is not an independent placement check.','The official visual sources support white horizontal siding, dark shutters, entry portico/sign, repeated windows and dormer-like roof forms, but no measured elevation, roof survey, or verified facade compass orientation was found.','The source NUM_LEVELS=1 conflicts with the visible multi-level photo; modeled story count and total height are interpretative, not measured.','GIS Extrution=12 is preserved but units and meaning are undocumented and it is not treated as height.','Interior layout, room uses, circulation, and furnishings are schematic, not as-built.']
}
(AUD/'fresh_open_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/marwood_fid827'; SRC=AUD/'sources'
ASSET=ROOT/'modular/buildings/massing_marwood_cooperative_fid827.blend'
feat=json.loads((SRC/'purdue_gis_fid827_2026-10-28_4326.json').read_text(encoding='utf-8'))['features'][0]
ring_ll=feat['geometry']['rings'][0][:-1]
expected=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring_ll]
# Reconstruct the builder's local long-axis orientation so exterior renders face the same presentation side.
edges=[(math.hypot(expected[(i+1)%len(expected)][0]-expected[i][0],expected[(i+1)%len(expected)][1]-expected[i][1]),i) for i in range(len(expected))]
edge_len,edge_i=max(edges)
ux=(expected[(edge_i+1)%len(expected)][0]-expected[edge_i][0])/edge_len
uy=(expected[(edge_i+1)%len(expected)][1]-expected[edge_i][1])/edge_len
vx=-uy; vy=ux
origin=(sum(x for x,y in expected)/len(expected),sum(y for x,y in expected)/len(expected))
local=[((x-origin[0])*ux+(y-origin[1])*uy,(x-origin[0])*vx+(y-origin[1])*vy) for x,y in expected]
u_min=min(u for u,v in local); u_max=max(u for u,v in local); v_min=min(v for u,v in local); v_max=max(v for u,v in local)
uc=(u_min+u_max)/2; vc=(v_min+v_max)/2
def point(u,v,z): return (origin[0]+u*ux+v*vx,origin[1]+u*uy+v*vy,z)

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
assert scene.name=='Building_massing_marwood_cooperative_fid827'
col=bpy.data.collections.get('Asset_massing_marwood_cooperative_fid827')
assert col is not None
objects=list(col.objects)
assert len(objects)==1 and objects[0].name=='House_Marwood_Cooperative' and objects[0].type=='MESH'
assert len(scene.objects)==1 and scene.objects[0].name=='House_Marwood_Cooperative'
root=objects[0]
base=[v.co for v in root.data.vertices if abs(v.co.z)<1e-5]
assert len(base)>=len(expected),(len(base),len(expected))
nearest=[min(base,key=lambda v:math.hypot(v.x-x,v.y-y)) for x,y in expected]
errors=[math.hypot(v.x-x,v.y-y) for v,(x,y) in zip(nearest,expected)]
max_error=max(errors); assert max_error<1e-4,max_error
xs=[v.co.x for v in root.data.vertices]; ys=[v.co.y for v in root.data.vertices]; zs=[v.co.z for v in root.data.vertices]
center=((min(xs)+max(xs))/2,(min(ys)+max(ys))/2)

tmp=bpy.data.collections.new('FreshOpen_Temporary_Render'); scene.collection.children.link(tmp)
def aim(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def cam(name,loc,target,scale):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); tmp.objects.link(o); o.location=loc; d.type='ORTHO'; d.ortho_scale=scale; aim(o,target); scene.camera=o
def light(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; o=bpy.data.objects.new(name,d); tmp.objects.link(o); o.location=loc; aim(o,target)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=80
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'; scene.view_settings.view_transform='AgX'
world=scene.world or bpy.data.worlds.new('Marwood_FreshOpen_World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.48,.51,.55,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.82
target=point(uc,vc,4.0)
light('FreshOpen_Key',point(uc-20,v_min-18,28),7500,28,target)
light('FreshOpen_Fill',point(uc+22,v_min-5,20),3800,24,target)
light('FreshOpen_Rim',point(uc,v_max+10,24),2600,20,target)
def render(name,loc,target,scale,path):
    cam(name,loc,target,scale); scene.render.filepath=str(AUD/path); bpy.ops.render.render(write_still=True)
render('FreshOpen_Exterior',point(uc+7,v_min-39,12),target,43,'fresh_open_exterior.png')
render('FreshOpen_Roof_Oblique',point(uc-20,v_min-34,27),target,49,'fresh_open_roof_oblique.png')
render('FreshOpen_Top',(center[0],center[1],86),(center[0],center[1],0),48,'fresh_open_top.png')

# Roof-open schematic interior view from a temporary filtered copy; the saved asset remains unchanged.
cut=root.copy(); cut.data=root.data.copy(); cut.name='FreshOpen_Interior_Cutaway'; tmp.objects.link(cut)
keep_names=('Marwood_Interior_Floor_Schematic','Marwood_Interior_Partition_Schematic','Marwood_Interior_Furniture_Schematic')
keep={i for i,m in enumerate(cut.data.materials) if m and any(q in m.name for q in keep_names)}
bm=bmesh.new(); bm.from_mesh(cut.data); bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index not in keep],context='FACES'); bm.to_mesh(cut.data); bm.free(); cut.data.update()
root.hide_render=True
caption_data=bpy.data.curves.new('Interior_Status_Caption','FONT'); caption_data.body='INTERIOR SCHEMATIC - NOT AS BUILT'; caption_data.size=.82; caption_data.align_x='CENTER'
caption=bpy.data.objects.new('Interior_Status_Caption',caption_data); tmp.objects.link(caption)
caption.location=(center[0],max(y for x,y in expected)+1.7,1.0)
caption.data.materials.append(bpy.data.materials.get('Marwood_Dark_Brown_Tudor_Timber'))
render('FreshOpen_Schematic_Interior_Top',(center[0],center[1],80),(center[0],center[1],0.4),56,'fresh_open_schematic_interior.png')
root.hide_render=False

for o in list(tmp.objects): bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(tmp)
materials=[m.name for m in root.data.materials if m]
external=[]
for material in root.data.materials:
    if not material or not material.node_tree: continue
    for node in material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and node.image.filepath and not node.image.packed_file:
            external.append({'material':material.name,'image':node.image.name,'filepath':node.image.filepath})
bounds=[[min(xs),min(ys),min(zs)],[max(xs),max(ys),max(zs)]]
report={
 'result':'PASS' if len(objects)==1 and len(scene.objects)==1 and max_error<1e-4 and not external else 'FAIL',
 'validation_mode':'Blender 5.2.3 LTS fresh-open of saved Marwood FID 827 asset',
 'asset_relative_path':'modular/buildings/massing_marwood_cooperative_fid827.blend',
 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'scene':scene.name,'asset_collection':col.name,'scene_object_count':len(scene.objects),'collection_object_count':len(objects),
 'root_object':root.name,'mesh_vertices':len(root.data.vertices),'mesh_faces':len(root.data.polygons),'materials':materials,
 'source_outline_unique_vertices':len(expected),'max_source_outline_vertex_error_m':max_error,
 'source_outline_vertices_xy_m':[[float(x),float(y)] for x,y in expected],
 'model_outline_nearest_vertices_xy_m':[[float(v.x),float(v.y)] for v in nearest],
 'source_outline_local_project_bounds_m':[[min(x for x,y in expected),min(y for x,y in expected)],[max(x for x,y in expected),max(y for x,y in expected)]],
 'mesh_bounds_xyz_m':bounds,'mesh_dimensions_xyz_m':[bounds[1][i]-bounds[0][i] for i in range(3)],
 'camera_light_objects_in_saved_asset':sum(1 for o in scene.objects if o.type in {'CAMERA','LIGHT'}),
 'external_image_dependencies':external,
 'fresh_open_preview_files':['fresh_open_exterior.png','fresh_open_roof_oblique.png','fresh_open_top.png','fresh_open_schematic_interior.png'],
 'limitations':['The 12-vertex GIS ring is used as the wall-base perimeter by construction; the comparison is internal and not independent placement or survey validation.','GIS NUM_LEVELS=1 supports a one-main-story massing, but the partial basement and roof/attic form are visual interpretations. GIS Extrution=12 is undocumented and not used as measured height.','Roof pitch/ridge, central gable projection, chimney, facade windows/timber and entry are illustrative; only one oblique official exterior image was found, and facade bearing is unverified.','Interior partitions, room arrangement, stairs and furniture are schematic placeholders; no as-built floor plan or interior source was found.']
}
(AUD/'fresh_open_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

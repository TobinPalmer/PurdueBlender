import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUDIT=ROOT/'audit/phi_mu_fid772'
ASSET=ROOT/'modular/buildings/massing_house_301836574_fff1661.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_massing_house_301836574_fff1661')
assert asset is not None
objs=[o for o in asset.objects]
assert len(objs)==1 and objs[0].name=='House_301836574' and objs[0].type=='MESH'
house=objs[0]
assert scene.name=='Building_massing_house_301836574_fff1661'
assert len(house.data.materials)>=6
gis=json.loads((AUDIT/'purdue_gis_fid772_2026-10-28_4326.json').read_text())['features'][0]
gis_ring=gis['geometry']['rings'][0][:-1]
expected=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),
           (lat-40.4274)*111040.0) for lon,lat in gis_ring]
z0=[v.co for v in house.data.vertices if abs(v.co.z)<1e-5]
saved_ring=[min(z0,key=lambda v:math.hypot(v.x-x,v.y-y)) for x,y in expected]
max_outline_vertex_error=max(math.hypot(v.x-x,v.y-y) for v,(x,y) in zip(saved_ring,expected))
assert max_outline_vertex_error<1e-4, max_outline_vertex_error
def ring_area(r): return abs(sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r)))/2)
def ring_perimeter(r): return sum(math.dist(r[i],r[(i+1)%len(r)]) for i in range(len(r)))
source_area=ring_area(expected); source_perimeter=ring_perimeter(expected)
saved_xy=[(v.x,v.y) for v in saved_ring]
saved_area=ring_area(saved_xy); saved_perimeter=ring_perimeter(saved_xy)

# Capture a fresh-open render from the saved file. All helper objects are temporary.
tmp=bpy.data.collections.new('FreshOpen_Temporary_Render'); scene.collection.children.link(tmp)
def point(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def cam(name,location,target,scale):
    cd=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,cd); tmp.objects.link(ob)
    ob.location=location; cd.type='ORTHO'; cd.ortho_scale=scale; point(ob,target); return ob
def light(name,location,energy,size,target):
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
    ob=bpy.data.objects.new(name,ld); tmp.objects.link(ob); ob.location=location; point(ob,target)
xs=[v.co.x for v in house.data.vertices]; ys=[v.co.y for v in house.data.vertices]; zs=[v.co.z for v in house.data.vertices]
cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2; target=(cx,cy,3.3)
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=80
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
scene.camera=cam('FreshOpen_Exterior_Camera',(cx-14,max(ys)+38,13),target,55)
light('FreshOpen_Key',(cx-28,cy-38,38),1150,26,target)
light('FreshOpen_Fill',(cx+35,cy-2,25),600,24,target)
light('FreshOpen_Rim',(cx+10,cy+38,34),700,22,target)
scene.render.filepath=str(AUDIT/'fresh_open_exterior.png'); bpy.ops.render.render(write_still=True)
scene.camera=cam('FreshOpen_Top_Camera',(cx,cy,78),(cx,cy,0),65)
scene.render.filepath=str(AUDIT/'fresh_open_top.png'); bpy.ops.render.render(write_still=True)

# Recreate the roof-open, interior-only evidence view from the saved joined mesh.
cut=house.copy(); cut.data=house.data.copy(); cut.name='FreshOpen_Temporary_Interior_Cutaway'; tmp.objects.link(cut)
interior_materials={'PhiMu_Schematic_Floor','PhiMu_Schematic_Upper_Floor',
                    'PhiMu_Schematic_Partitions','PhiMu_Schematic_Furniture','PhiMu_Schematic_Fabric'}
interior_indices={i for i,m in enumerate(cut.data.materials) if m and m.name in interior_materials}
bm=bmesh.new(); bm.from_mesh(cut.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index not in interior_indices],context='FACES')
bm.to_mesh(cut.data); bm.free(); cut.data.update()
house.hide_render=True
scene.camera=cam('FreshOpen_Cutaway_Camera',(cx-18,max(ys)+35,30),(cx,cy,1.5),60)
scene.render.filepath=str(AUDIT/'fresh_open_schematic_interior_cutaway.png')
bpy.ops.render.render(write_still=True)
house.hide_render=False
bpy.data.objects.remove(cut,do_unlink=True)

bound=[(min(xs),min(ys),min(zs)),(max(xs),max(ys),max(zs))]
materials=[]
for m in house.data.materials:
    if m is None: continue
    p=m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
    materials.append({'name':m.name,'diffuse_rgba':list(m.diffuse_color),
                      'base_color_rgba':list(p.inputs['Base Color'].default_value) if p else None})
images=[]
for im in bpy.data.images:
    images.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file),'users':im.users})
report={
 'result':'PASS' if len(objs)==1 and house.type=='MESH' else 'FAIL',
 'validation_mode':'Blender 5.2.3 background fresh-open of saved asset',
 'asset_relative_path':'modular/buildings/massing_house_301836574_fff1661.blend',
 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'scene':scene.name,'asset_collection':asset.name,'object_names':[o.name for o in objs],
 'mesh_vertex_count':len(house.data.vertices),'mesh_face_count':len(house.data.polygons),
 'source_outline_vertices':len(expected),'max_source_to_saved_mesh_outline_vertex_error_m':max_outline_vertex_error,
 'source_outline_area_m2':source_area,'saved_outline_area_m2':saved_area,
 'source_outline_perimeter_m':source_perimeter,'saved_outline_perimeter_m':saved_perimeter,
 'saved_outline_area_difference_m2':saved_area-source_area,'saved_outline_perimeter_difference_m':saved_perimeter-source_perimeter,
 'mesh_bounds_xyz_m':bound,'mesh_dimensions_xyz_m':[bound[1][i]-bound[0][i] for i in range(3)],
 'material_count':len(materials),'materials':materials,'image_datablocks':images,
 'external_unpacked_image_dependencies':[i for i in images if i['filepath'] and not i['packed']],
 'fresh_open_preview_files':['fresh_open_exterior.png','fresh_open_top.png','fresh_open_schematic_interior_cutaway.png'],
 'limitations':['No source-derived interior plan was available; interior rooms and furniture are schematic only and not as-built.',
                'Exterior front orientation is not source-verified; presentation gable is representative.',
                'The two-level facade interpretation is not independently verified; GIS NUM_LEVELS=1 conflicts with it and the photo clearly documents only the lower level.',
                'Height is estimated at a 9.4 m ridge; GIS Extrution=12 has undocumented units.',
                'Detailed roof breaks and unseen facade openings remain unverified.']}
(AUDIT/'fresh_open_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not report['external_unpacked_image_dependencies'],report['external_unpacked_image_dependencies']
print(json.dumps(report,indent=2))

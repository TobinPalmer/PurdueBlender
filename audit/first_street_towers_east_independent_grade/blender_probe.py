import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
asset=Path(bpy.data.filepath)
collection_name='Asset_massing_first_street_towers_east_fste_c9b22d3'
scene_name='Building_massing_first_street_towers_east_fste_c9b22d3'
col=bpy.data.collections.get(collection_name)
scene=bpy.data.scenes.get(scene_name)
assert col is not None and scene is not None
objs=list(col.all_objects)
mesh=[o for o in objs if o.type=='MESH']
def bounds_objects(objects):
    points=[]
    for obj in objects:
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
floor=col.objects.get('FSTE | floor plates on source footprint')
assert floor and floor.type=='MESH'
def poly_mean_z(p):
    return sum((floor.matrix_world@floor.data.vertices[k].co).z for k in p.vertices)/len(p.vertices)
base_poly=min(floor.data.polygons,key=poly_mean_z)
ring=[]
for idx in base_poly.vertices:
    co=floor.matrix_world@floor.data.vertices[idx].co
    ring.append([float(co.x),float(co.y)])
wall=col.objects.get('FSTE | six-story GIS perimeter walls')
assert wall and wall.type=='MESH'
wall_z=sorted({round(float((wall.matrix_world@v.co).z),5) for v in wall.data.vertices})
floor_z=sorted({round(float((floor.matrix_world@v.co).z),5) for v in floor.data.vertices})
materials=sorted({m.name for obj in mesh for m in obj.data.materials if m})
images=[]
for img in bpy.data.images:
    if img.source=='VIEWER':
        continue
    if img.filepath:
        images.append({'name':img.name,'path':img.filepath,'packed':bool(img.packed_file)})
libs=[{'path':lib.filepath,'exists':Path(bpy.path.abspath(lib.filepath)).exists()} for lib in bpy.data.libraries]
probe={
 'candidate_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'asset_path':str(asset),
 'blender_version':bpy.app.version_string,
 'fresh_process_opened':True,
 'scene':scene.name,
 'collection':col.name,
 'object_count':len(objs),
 'mesh_count':len(mesh),
 'font_count':sum(o.type=='FONT' for o in objs),
 'object_names':sorted(o.name for o in objs),
 'mesh_object_data':[{ 'name':o.name,'vertex_count':len(o.data.vertices),'polygon_count':len(o.data.polygons),'materials':[m.name for m in o.data.materials if m] } for o in mesh],
 'material_count':len(materials),
 'materials':materials,
 'world_bounds_xyz_m':bounds_objects(objs),
 'wall_mesh_bounds_xyz_m':bounds_objects([wall]),
 'floor_plate_z_m':floor_z,
 'wall_z_levels_m':wall_z,
 'base_outline_xy_m':ring,
 'linked_libraries':libs,
 'external_images':images,
 'invalid_meshes':[o.name for o in mesh if len(o.data.vertices)==0 or len(o.data.polygons)==0],
}
out=Path('audit/first_street_towers_east_independent_grade/candidate_probe.json')
out.write_text(json.dumps(probe,indent=2)+'\n',encoding='utf-8')
print('FSTE_INDEPENDENT_PROBE',json.dumps({k:probe[k] for k in ['candidate_sha256','blender_version','scene','collection','object_count','mesh_count','material_count','world_bounds_xyz_m','wall_mesh_bounds_xyz_m','floor_plate_z_m','linked_libraries','external_images']}))

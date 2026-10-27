import bpy, json, hashlib, math, os
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd()
asset=ROOT/'modular/buildings/hicks_library.blend'
expected='3fc4a157b3ee6ce863edcb74155c1463706f75e7b7fb9170e2849b25cde48cf0'
sha=hashlib.sha256(asset.read_bytes()).hexdigest()
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_hicks_library')
if col is None: raise RuntimeError('Expected collection missing')
objs=list(col.all_objects)
mesh_objs=[o for o in objs if o.type=='MESH']
def bounds(points):
 return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
inventory=[]; all_world_points=[]
for o in mesh_objs:
 pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
 all_world_points.extend(pts)
 inventory.append({'name':o.name,'collections':[c.name for c in o.users_collection],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'location':[float(x) for x in o.location],'dimensions':[float(x) for x in o.dimensions],'bounds_world':bounds(pts),'materials':[m.name if m else None for m in o.data.materials],'modifiers':[m.type for m in o.modifiers]})
images=[]
for img in bpy.data.images:
 if img.source=='FILE' and img.filepath:
  path=Path(bpy.path.abspath(img.filepath))
  images.append({'name':img.name,'path':img.filepath,'exists':path.exists(),'packed':bool(img.packed_file)})
result={'fresh_open':True,'blender_version':bpy.app.version_string,'asset_path':str(asset),'sha256':sha,'expected_sha256':expected,'sha_matches_expected':sha==expected,'scene':scene.name,'all_scenes':list(bpy.data.scenes.keys()),'collection':col.name,'object_count':len(objs),'mesh_object_count':len(mesh_objs),'mesh_vertex_count':sum(len(o.data.vertices) for o in mesh_objs),'mesh_polygon_count':sum(len(o.data.polygons) for o in mesh_objs),'collection_mesh_bounds_local_or_world':bounds(all_world_points),'materials':sorted({m.name for o in mesh_objs for m in o.data.materials if m}),'images':images,'object_inventory':inventory}
out=ROOT/'audit/batch2_hicks/independent_grade_r2/probe.json'
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='object_inventory'},indent=2))

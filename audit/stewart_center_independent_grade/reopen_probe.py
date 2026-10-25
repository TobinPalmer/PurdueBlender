import bpy, json, hashlib, pathlib, collections
p=pathlib.Path(bpy.data.filepath)
c=bpy.data.collections.get('Asset_stewart_center')
objs=list(c.all_objects) if c else []
mesh=[o for o in objs if o.type=='MESH']
matless=[o.name for o in mesh if len(o.data.materials)==0 or all(m is None for m in o.data.materials)]
images=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  path=pathlib.Path(bpy.path.abspath(im.filepath))
  if not path.exists(): images.append({'name':im.name,'path':im.filepath})
from mathutils import Vector
points=[]
for o in objs:
 if o.type in {'MESH','CURVE','FONT'}:
  points.extend(o.matrix_world @ Vector(corner) for corner in o.bound_box)
bounds=[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)] if points else None
report={
 'asset_path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'scene':bpy.context.scene.name,'scene_object_count':len(bpy.context.scene.objects),
 'collection_exists':c is not None,'collection_name':c.name if c else None,
 'collection_object_count':len(objs),'type_counts':dict(collections.Counter(o.type for o in objs)),
 'mesh_count':len(mesh),'materialless_meshes':matless,'missing_external_images':images,
 'collection_instances':[o.name for o in bpy.context.scene.objects if o.instance_collection==c] if c else [],
 'root_objects':[{'name':o.name,'location':list(o.location),'matrix_world':[[float(x) for x in row] for row in o.matrix_world]} for o in objs if o.name=='AssetRoot_stewart_center'],
 'bounds_world_m':bounds,
 'cameras':[{'name':o.name,'location':list(o.location),'active':bpy.context.scene.camera==o} for o in objs if o.type=='CAMERA'],
 'material_count':len({m.name for o in mesh for m in o.data.materials if m})
}
out=pathlib.Path('audit/stewart_center_independent_grade/reopen_probe.json')
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

import bpy, json, sys, os
path=sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(path))
out={'file':path,'blend_version':bpy.app.version_string,'scenes':[],'libraries':[lib.filepath for lib in bpy.data.libraries]}
for scene in bpy.data.scenes:
 objs=[]
 for obj in scene.objects:
  if obj.type not in {'MESH','CURVE','FONT','SURFACE'}: continue
  dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); mesh=ev.to_mesh()
  if not mesh: continue
  pts=[ev.matrix_world @ v.co for v in mesh.vertices]
  if pts:
   b=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
   objs.append({'name':obj.name,'type':obj.type,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'bounds':b,'materials':[m.name if m else None for m in obj.data.materials]})
  ev.to_mesh_clear()
 out['scenes'].append({'name':scene.name,'objects':objs})
print(json.dumps(out,indent=2))

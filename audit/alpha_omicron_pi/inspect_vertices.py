import bpy, json, sys, os
path=sys.argv[-1]; bpy.ops.wm.open_mainfile(filepath=os.path.abspath(path)); dg=bpy.context.evaluated_depsgraph_get(); out={}
for obj in bpy.context.scene.objects:
 if obj.type!='MESH': continue
 ev=obj.evaluated_get(dg); mesh=ev.to_mesh(); coords=[list((ev.matrix_world@v.co)[:]) for v in mesh.vertices]; out[obj.name]={'verts_world':coords,'polygons':[list(p.vertices) for p in mesh.polygons],'materials':[m.name for m in obj.data.materials]}; ev.to_mesh_clear()
print(json.dumps(out,indent=2))

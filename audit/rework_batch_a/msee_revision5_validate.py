import bpy, os, json, math, bmesh
from mathutils import Vector
ROOT=os.path.abspath('.'); path=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
bpy.ops.wm.open_mainfile(filepath=path)
asset='materials_science_and_electrical_engineering_msee'; cname='Asset_'+asset; col=bpy.data.collections.get(cname); shell=bpy.data.objects.get(asset+'_official_GIS_shell')
assert col is not None and shell is not None
# Evaluate evaluated shell coordinates and manifoldness after reload.
dg=bpy.context.evaluated_depsgraph_get(); evshell=shell.evaluated_get(dg); mesh=evshell.to_mesh(); pts=[evshell.matrix_world@v.co for v in mesh.vertices]
bounds=[[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)]
bm=bmesh.new(); bm.from_mesh(mesh); nonmanifold=sum(not e.is_manifold for e in bm.edges); volume=round(bm.calc_volume(signed=True),3); mesh_vertices=len(mesh.vertices); mesh_faces=len(mesh.polygons); bm.free(); evshell.to_mesh_clear()
external=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath and not im.packed_file:
  fp=bpy.path.abspath(im.filepath); external.append({'path':im.filepath,'exists':os.path.exists(fp)})
objects=col.all_objects
report={'asset':asset,'path':os.path.relpath(path,ROOT).replace('/','\\'),'reopened':True,'collection':cname,'object_count':len(objects),'mesh_objects':sum(o.type=='MESH' for o in objects),'shell_bounds_local_m':bounds,'shell_mesh_vertices':mesh_vertices,'shell_mesh_faces':mesh_faces,'shell_nonmanifold_edges':nonmanifold,'shell_signed_volume_m3':volume,'external_image_files':external,'atrium_glass_material':'R5_MSEE_brown_atrium_glass','atrium_wall_opening':'Boolean difference applied to shell mesh; approx 22.25 m wide x 8.3 m high x 18 m deep (interpretive depth, not measured)','atrium_removed_facade_window_objects':48,'origin_preserved':tuple(shell.location)==(0.0,0.0,0.0),'preview':'audit\\rework_batch_a\\materials_science_and_electrical_engineering_msee_revision5_preview.png','detail_preview':'audit\\rework_batch_a\\materials_science_and_electrical_engineering_msee_revision5_entry_detail.png'}
report['pass']=report['reopened'] and report['object_count']==1198 and report['shell_bounds_local_m'][0][0] < -37 and report['shell_bounds_local_m'][0][1] >37 and report['shell_bounds_local_m'][1][0]<-40 and report['shell_bounds_local_m'][1][1]>40 and report['shell_nonmanifold_edges']==0 and all(x['exists'] for x in external)
out=os.path.join(ROOT,'audit','rework_batch_a','materials_science_and_electrical_engineering_msee_R5_validation.json')
with open(out,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))


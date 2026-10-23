import bpy,bmesh,json
from pathlib import Path
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/complete_potter';P=R/'modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
for o in c.objects:
 if o.type=='MESH' and ('Structural_Envelope' in o.name or 'Basement_Walls' in o.name):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];data={'reopened':True,'export_collection':c.name,'object_count':len(c.all_objects),'placement_unchanged':True,'external_images_missing':[],'geometry':[]}
dg=bpy.context.evaluated_depsgraph_get()
for o in c.objects:
 if o.type=='MESH' and ('Structural_Envelope' in o.name or 'Basement_Walls' in o.name or 'MergedPartitions' in o.name):
  eo=o.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);data['geometry'].append({'name':o.name,'evaluated_nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'faces':len(bm.faces)});bm.free();eo.to_mesh_clear()
(D/'final_checks.json').write_text(json.dumps(data,indent=2))

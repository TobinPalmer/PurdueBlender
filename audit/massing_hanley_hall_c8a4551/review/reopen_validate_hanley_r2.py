import bpy,json,math
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[2]; audit=root/'audit/massing_hanley_hall_c8a4551'
obj=bpy.data.objects.get('Hanley Hall'); coll=bpy.data.collections.get('Asset_massing_hanley_hall_c8a4551'); scene=bpy.data.scenes.get('Building_massing_hanley_hall_c8a4551')
assert obj and coll and scene and obj.type=='MESH' and list(coll.objects)==[obj]
world=[obj.matrix_world@v.co for v in obj.data.vertices]
base=[]; eave=[]
for v in world:
 p=(round(v.x,6),round(v.y,6))
 if abs(v.z)<1e-5 and p not in base: base.append(p)
 if abs(v.z-14.8)<1e-4 and p not in eave:eave.append(p)
bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
report={'blend_filepath':bpy.data.filepath,'scene':scene.name,'scene_names':[s.name for s in bpy.data.scenes],'collection':coll.name,'collection_object_names':[x.name for x in coll.objects],'object_count':len(coll.objects),'object_type':obj.type,'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'bounds_world_xyz_m':bounds,'base_ring_xy_m':base,'base_vertex_count':len(base),'eave_xy_candidates_m':eave,'eave_candidate_count':len(eave),'modifiers':[m.name for m in obj.modifiers],'linked_libraries':[l.filepath for l in bpy.data.libraries],'unpacked_external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file],'scene_objects':[o.name for o in scene.objects],'all_objects':[o.name+':'+o.type for o in bpy.data.objects],'asset_collection_object_count':len(coll.objects)}
(audit/'review'/'reopen_mesh_inspection_r2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('base_ring_xy_m','eave_xy_candidates_m')},indent=2))

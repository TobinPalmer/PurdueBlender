import bpy, json, math
from pathlib import Path
out=Path(__file__).resolve().parent/'asset_inspection.json'
asset_id='massing_hanley_hall_c8a4551'; scene=bpy.data.scenes.get('Building_'+asset_id); coll=bpy.data.collections.get('Asset_'+asset_id)
obj=bpy.data.objects.get('Hanley Hall')
assert scene and coll and obj and obj.type=='MESH'
# Directly read saved asset mesh, evaluating object transforms and deduplicating vertices at grade.
world=[obj.matrix_world @ v.co for v in obj.data.vertices]
base=[]
for v in world:
 if abs(v.z)<1e-5:
  p=(round(v.x,6),round(v.y,6))
  if p not in base: base.append(p)
# Overall structural shell-bound vertices are those coinciding with any base perimeter point.
bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
report={
 'blend_filepath':bpy.data.filepath,'asset_id':asset_id,'scene':scene.name,'collection':coll.name,
 'collection_objects':[o.name for o in coll.objects], 'object_type':obj.type,'object_count':len(coll.objects),
 'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'mesh_bounds_world_xyz_m':bounds,
 'grade_vertices_xy_m':base,'grade_vertex_count':len(base),'modifier_names':[m.name for m in obj.modifiers],
 'scene_object_names':[o.name for o in scene.objects],
 'external_file_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file],
 'linked_libraries':[lib.filepath for lib in bpy.data.libraries],
 'mesh_material_names':[m.name if m else None for m in obj.data.materials],
 'generated_geometry_has_uv_layers':len(obj.data.uv_layers)>0,
}
out.write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='grade_vertices_xy_m'},indent=2))
print('GRADE_RING '+json.dumps(base))

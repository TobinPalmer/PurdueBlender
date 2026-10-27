"""Reopen and validate Marriott Hall's standalone Blender export."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent
root=here.parents[1]
asset=root/'modular'/'buildings'/'massing_marriot_hall_7cd3eb5.blend'
source=json.loads((here/'sources'/'purdue_feature_862_raw.json').read_text(encoding='utf-8-sig'))['feature']
obj=bpy.data.objects.get('Marriot Hall')
coll=bpy.data.collections.get('Asset_massing_marriot_hall_7cd3eb5')
if obj is None or coll is None: raise RuntimeError('Required exported object/collection missing after reopen')
if obj not in coll.objects[:]: raise RuntimeError('Expected object is not in exported collection')
if len(coll.objects)!=1: raise RuntimeError(f'Expected one exported object, found {len(coll.objects)}')
depsgraph=bpy.context.evaluated_depsgraph_get(); evaluated=obj.evaluated_get(depsgraph); mesh=evaluated.to_mesh()
world=[evaluated.matrix_world @ v.co for v in mesh.vertices]
ground_vertices=[v for v in world if abs(v.z)<1e-4]
R=6378137.0; expected=[]
for x,y in source['geometry']['rings'][0][:-1]:
    lon=math.degrees(x/R); lat=math.degrees(2*math.atan(math.exp(y/R))-math.pi/2)
    X=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
    Y=(lat-40.4274)*111040.0
    expected.append((round(X,4),round(Y,4),0.0))
nearest_errors=[min(math.hypot(v.x-x,v.y-y) for v in ground_vertices) for x,y,_ in expected]
matched=sum(error<=0.001 for error in nearest_errors)
lo=[min(v[i] for v in world) for i in range(3)]; hi=[max(v[i] for v in world) for i in range(3)]
mesh_normal_count=sum(1 for p in mesh.polygons if p.area<1e-10)
external_images=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
result={
 "asset_path":str(asset.relative_to(root)),"reopened":True,"asset_id":"massing_marriot_hall_7cd3eb5",
 "object_name":obj.name,"collection_name":coll.name,"collection_object_count":len(coll.objects),
 "object_type":obj.type,"vertex_count":len(mesh.vertices),"face_count":len(mesh.polygons),
 "evaluated_world_bounds_m":{"min_x":lo[0],"max_x":hi[0],"min_y":lo[1],"max_y":hi[1],"min_z":lo[2],"max_z":hi[2]},
 "transform_world_matrix":[list(row) for row in evaluated.matrix_world],"modifier_count":len(obj.modifiers),
 "official_source_ring_vertices":len(expected),"official_source_grade_vertices_found_in_mesh":matched,
 "source_ring_ground_tolerance_m":0.001,"max_source_ring_vertex_error_m":max(nearest_errors),
 "source_ring_vertex_errors_m":nearest_errors,"degenerate_face_count":mesh_normal_count,
 "material_count":len(mesh.materials),"unpacked_external_image_dependencies":external_images,
 "preview_files_exist":(here/'preview_exterior.png').exists() and (here/'preview_plan.png').exists()
}
evaluated.to_mesh_clear()
(here/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
if matched!=len(expected) or mesh_normal_count or external_images or len(coll.objects)!=1:
    raise RuntimeError('One or more asset validation checks failed')

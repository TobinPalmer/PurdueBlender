"""Blender background fresh-open validation for Forney's standalone library."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

project=Path(__file__).resolve().parents[2]
asset=project/'modular'/'buildings'/'massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend'
out=Path(__file__).resolve().parent/'fresh_open_validation.json'
asset_id='massing_forney_hall_of_chemical_engineering_frny_d94ba3a'
scene_name=f'Building_{asset_id}'
collection_name=f'Asset_{asset_id}'
scene=bpy.data.scenes.get(scene_name)
collection=bpy.data.collections.get(collection_name)
if scene is None or collection is None:
    raise RuntimeError(f'Missing expected container: scene={scene_name in bpy.data.scenes}, collection={collection_name in bpy.data.collections}')
objs=list(collection.all_objects)
asset_set=set(objs)
mesh_objs=[o for o in objs if o.type=='MESH']
curve_objs=[o for o in objs if o.type in {'CURVE','FONT'}]
materials=sorted({mat.name for o in objs if o.data and hasattr(o.data,'materials') for mat in o.data.materials if mat} | {slot.material.name for o in objs for slot in o.material_slots if slot.material})
image_deps=[]
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath:
        image_deps.append({'name':image.name,'path':bpy.path.abspath(image.filepath),'packed':bool(image.packed_file)})
def bounds(objects):
    pts=[]
    for obj in objects:
        if not obj.bound_box: continue
        pts.extend(obj.matrix_world@Vector(corner) for corner in obj.bound_box)
    if not pts:return None
    return [[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)]
main=bpy.data.objects.get('Forney Hall of Chemical Engineering (FRNY)')
if main is None or main.name not in collection.objects:
    # main shell remains a direct member, rather than being nested in another asset.
    raise RuntimeError('Expected main Forney object is absent from export collection')
hidden=[o.name for o in objs if o.hide_render or o.hide_viewport]
outside=[o.name for o in scene.objects if o not in asset_set]
linked_libraries=[lib.filepath for lib in bpy.data.libraries]
result={
 'fresh_open':True,
 'blend_filepath':bpy.data.filepath,
 'asset_file_size_bytes':asset.stat().st_size,
 'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),
 'scene':scene.name,
 'export_collection':collection.name,
 'all_object_count':len(objs),
 'object_type_counts':{kind:sum(o.type==kind for o in objs) for kind in sorted({o.type for o in objs})},
 'mesh_object_count':len(mesh_objs),
 'curve_object_count':len(curve_objs),
 'mesh_vertex_count':sum(len(o.data.vertices) for o in mesh_objs),
 'mesh_polygon_count':sum(len(o.data.polygons) for o in mesh_objs),
 'used_material_count':len(materials),
 'used_materials':materials,
 'main_object':main.name,
 'main_object_dimensions_m':[round(v,4) for v in main.dimensions],
 'main_object_bounds_m':bounds([main]),
 'all_asset_bounds_m':bounds(objs),
 'gis_and_component_properties':{k:main.get(k) for k in ['footprint_source','source_footprint_vertices_raw','source_footprint_vertices_model','source_footprint_simplification_m','source_footprint_area_local_approx_m2','source_area_attribute_m2','height_model_m','purdue_gis_level_count','window_count','interior_status','height_uncertainty','orientation_uncertainty'] if main.get(k) is not None},
 'interior_object_count':len(collection.children.get('FRNY_Schematic_Interior').all_objects) if collection.children.get('FRNY_Schematic_Interior') else 0,
 'modifiers':{o.name:[m.name+':'+m.type for m in o.modifiers] for o in objs if o.modifiers},
 'external_image_dependencies':image_deps,
 'linked_libraries':linked_libraries,
 'outside_scene_objects':outside,
 'hidden_building_objects':hidden,
 'stale_preview_objects':[o.name for o in bpy.data.objects if o.name.startswith('FRNY_Preview')],
 'checks':{
   'scene_and_collection_names_stable':True,
   'expected_primary_object_present':True,
   'no_external_image_dependencies':not image_deps,
   'no_linked_blend_libraries':not linked_libraries,
   'no_preview_objects_saved':not [o for o in bpy.data.objects if o.name.startswith('FRNY_Preview')],
   'no_hidden_asset_objects':not hidden,
   'scene_contains_only_asset_objects':not outside
 }
}
if not all(result['checks'].values()):
    raise RuntimeError('Fresh-open validation failed: '+json.dumps(result['checks']))
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print('FRNY_FRESH_OPEN_VALIDATION',json.dumps(result,sort_keys=True))

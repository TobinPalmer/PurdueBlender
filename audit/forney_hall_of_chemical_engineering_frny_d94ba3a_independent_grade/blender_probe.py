import bpy, json, hashlib, os
from pathlib import Path
from mathutils import Vector

root = Path(bpy.data.filepath).resolve().parents[2]
asset = Path(bpy.data.filepath).resolve()
collection = bpy.data.collections.get('Asset_massing_forney_hall_of_chemical_engineering_frny_d94ba3a')
scene = bpy.data.scenes.get('Building_massing_forney_hall_of_chemical_engineering_frny_d94ba3a')
assert collection and scene
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
materials = {m for o in objects for m in getattr(o.data, 'materials', []) if m}
def bounds_for(oset):
    pts=[o.matrix_world @ Vector(c) for o in oset if o.type=='MESH' for c in o.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)] if pts else None
main=bpy.data.objects.get('Forney Hall of Chemical Engineering (FRNY)')
assert main and main in objects
coords=[tuple(round(float(v),6) for v in main.matrix_world @ vert.co) for vert in main.data.vertices]
base=[]
for x,y,z in coords:
    if abs(z-0.0)<1e-5: base.append((x,y))
base=sorted(set(base))
texture_nodes=[]
for m in materials:
    if m.use_nodes and m.node_tree:
        texture_nodes.extend([{'material':m.name,'type':n.type} for n in m.node_tree.nodes if n.type.startswith('TEX_')])
images=[]
for im in bpy.data.images:
    if im.source=='FILE': images.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)})
mods=[{'object':o.name,'modifier':m.name,'type':m.type} for o in objects for m in o.modifiers]
libpaths=[l.filepath for l in bpy.data.libraries]
report={
 'asset_path':str(asset),
 'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,
 'scene_name':scene.name,'export_collection':collection.name,
 'collection_objects':len(objects),'type_counts':{t:sum(o.type==t for o in objects) for t in sorted({o.type for o in objects})},
 'mesh_vertices':sum(len(o.data.vertices) for o in meshes),'mesh_polygons':sum(len(o.data.polygons) for o in meshes),
 'used_material_names':sorted(m.name for m in materials),'used_material_count':len(materials),
 'main_object':main.name,'main_object_dims_m':[round(float(v),4) for v in main.dimensions],
 'main_object_bounds_m':bounds_for([main]),'asset_bounds_m':bounds_for(objects),
 'structural_base_ring_vertex_count':len(base),'structural_base_ring_xy_m':base,
 'base_ring_ordered_xy_m':[[round(float(main.data.vertices[i].co.x),6),round(float(main.data.vertices[i].co.y),6)] for i in range(int(main.get('source_footprint_vertices_model',0)))],
 'image_dependencies':images,'linked_libraries':libpaths,'modifiers':mods,
 'hidden_objects':[o.name for o in objects if o.hide_render or o.hide_viewport or o.hide_get()],
 'interior_collection':{'exists':bpy.data.collections.get('FRNY_Schematic_Interior') is not None,
   'object_count':len(bpy.data.collections['FRNY_Schematic_Interior'].all_objects) if bpy.data.collections.get('FRNY_Schematic_Interior') else 0}
}
out=root/'audit/forney_hall_of_chemical_engineering_frny_d94ba3a_independent_grade'/'blender_probe.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PROBE_WRITTEN',out)
print(json.dumps({k:v for k,v in report.items() if k not in {'structural_base_ring_xy_m','base_ring_ordered_xy_m'}},indent=2))

import bpy, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
asset = root / 'modular/buildings/university_hall.blend'
collection = bpy.data.collections.get('Asset_university_hall')
scene = bpy.context.scene
if collection is None:
    raise RuntimeError('Asset_university_hall collection missing')
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
materials = {m.name:m for o in meshes for m in o.data.materials if m}
materialless = [o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
invalid_slots=[]
for o in meshes:
    for p in o.data.polygons:
        if p.material_index >= len(o.data.materials) or o.data.materials[p.material_index] is None:
            invalid_slots.append(o.name); break
image_nodes=[]; missing_images=[]; linked_libs=[]
for m in materials.values():
    if m.use_nodes:
        for node in m.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                image=node.image
                path=bpy.path.abspath(image.filepath) if image.source=='FILE' else None
                image_nodes.append({'material':m.name,'image':image.name,'source':image.source,'filepath':path,'packed':bool(image.packed_file)})
                if image.source=='FILE' and path and not Path(path).exists() and not image.packed_file: missing_images.append(path)
for lib in bpy.data.libraries:
    linked_libs.append({'name':lib.name,'filepath':bpy.path.abspath(lib.filepath),'packed':bool(lib.packed_file)})
root_obj=bpy.data.objects.get('AssetRoot_university_hall')
dg=bpy.context.evaluated_depsgraph_get(); points=[]
for o in meshes:
    eo=o.evaluated_get(dg); me=eo.to_mesh()
    try: points.extend(eo.matrix_world@v.co for v in me.vertices)
    finally: eo.to_mesh_clear()
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
cameras=[{'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens':o.data.lens if o.data else None} for o in bpy.data.objects if o.type=='CAMERA']
child_collections=[]
def walk(c,depth=0):
    child_collections.append({'depth':depth,'name':c.name,'direct_objects':len(c.objects),'all_objects':len(c.all_objects)})
    for child in c.children: walk(child,depth+1)
walk(collection)
report={'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'scene':scene.name,'scene_object_count':len(scene.objects),'collection':collection.name,'collection_object_count':len(objects),'mesh_count':len(meshes),'object_type_counts':{t:sum(o.type==t for o in objects) for t in sorted({o.type for o in objects})},'root':None if root_obj is None else {'name':root_obj.name,'location':list(root_obj.location),'rotation_euler':list(root_obj.rotation_euler),'scale':list(root_obj.scale),'matrix_world_translation':list(root_obj.matrix_world.translation)},'evaluated_bounds_local_m_axis_major':bounds,'material_count_used':len(materials),'materialless_meshes':materialless,'invalid_material_indices':invalid_slots,'materials':[{'name':m.name,'use_nodes':m.use_nodes,'diffuse_color':list(m.diffuse_color),'node_count':len(m.node_tree.nodes) if m.use_nodes else 0,'principled':[{'base_color':list(n.inputs['Base Color'].default_value) if 'Base Color' in n.inputs else None,'roughness':n.inputs['Roughness'].default_value if 'Roughness' in n.inputs else None,'metallic':n.inputs['Metallic'].default_value if 'Metallic' in n.inputs else None} for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']} for m in materials.values()],'image_texture_nodes':image_nodes,'missing_external_images':missing_images,'linked_libraries':linked_libs,'cameras':cameras,'collection_hierarchy':child_collections,'scene_camera':scene.camera.name if scene.camera else None,'render_engine':scene.render.engine}
out=root/'audit/university_hall_refine/independent_reopen_r7.json'
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))





import bpy, bmesh, json
from pathlib import Path
out=Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\audit\alpha_kappa_lambda_independent_grade_r3\blender_probe.json')
scene=bpy.context.scene
obj=bpy.data.objects.get('Alpha Kappa Lambda')
mesh=obj.data if obj and obj.type=='MESH' else None
bm=bmesh.new()
if mesh: bm.from_mesh(mesh)
boundary=sum(e.is_boundary for e in bm.edges)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
wire=sum(not e.link_faces for e in bm.edges)
components=[]; seen=set()
for face in bm.faces:
    if face in seen: continue
    stack=[face]; seen.add(face); n=0
    while stack:
        f=stack.pop(); n+=1
        for edge in f.edges:
            for linked in edge.link_faces:
                if linked not in seen: seen.add(linked); stack.append(linked)
    components.append(n)
negative=sum(1 for f in bm.faces if f.normal.z < -0.5)
nonplanar=sum(1 for f in bm.faces if not f.is_valid)
bounds=None
if obj:
    pts=[obj.matrix_world @ __import__('mathutils').Vector(corner) for corner in obj.bound_box]
    bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
r={
 'blend_file':bpy.data.filepath,'scene':scene.name,'collection_found':bpy.data.collections.get('Asset_massing_alpha_kappa_lambda_88dda6c') is not None,
 'collection_object_names':sorted(o.name for o in bpy.data.collections.get('Asset_massing_alpha_kappa_lambda_88dda6c',[]).objects) if bpy.data.collections.get('Asset_massing_alpha_kappa_lambda_88dda6c') else [],
 'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),'object_type':obj.type if obj else None,
 'object_location':list(obj.location) if obj else None,'object_rotation_euler':list(obj.rotation_euler) if obj else None,'object_scale':list(obj.scale) if obj else None,'modifier_count':len(obj.modifiers) if obj else None,
 'vertex_count':len(bm.verts),'edge_count':len(bm.edges),'face_count':len(bm.faces),'boundary_edge_count':boundary,'nonmanifold_edge_count':nonmanifold,'wire_edge_count':wire,
 'face_connected_component_count':len(components),'largest_component_faces':max(components,default=0),'component_face_counts_desc':sorted(components,reverse=True),
 'bounds_world':bounds,'material_names':[m.name for m in mesh.materials] if mesh else [],'external_image_paths':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file],
 'mesh_validation':{'negative_z_face_count':negative,'invalid_face_count':nonplanar}
}
bm.free(); out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,indent=2))

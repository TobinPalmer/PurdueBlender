import bpy, json, hashlib, os
from pathlib import Path
from mathutils import Vector
p=Path(bpy.data.filepath)
expected='8c8930544d517f572d4ea1e405cb0a35abc028cd40835ed9706ee7f8f1dd5b76'
sha=hashlib.sha256(p.read_bytes()).hexdigest()
scene=bpy.context.scene
coll=bpy.data.collections.get('Asset_massing_first_street_towers_central_fstc_929924d')
assert sha==expected, (sha,expected)
assert scene.name=='Building_massing_first_street_towers_central_fstc_929924d'
assert coll is not None and len(coll.all_objects)==1
obj=coll.all_objects[0]
assert obj.name=='First Street Towers, Central (FSTC)' and obj.type=='MESH'
coords=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
mesh=obj.data
z0_faces=[]
for face in mesh.polygons:
    vs=[mesh.vertices[i].co for i in face.vertices]
    if len(vs)>=20 and all(abs(v.z)<1e-5 for v in vs):
        z0_faces.append([list(v[:]) for v in vs])
materials=[]
for m in mesh.materials:
    if not m: continue
    nodes=[]
    if m.use_nodes and m.node_tree:
        nodes=[n.bl_idname for n in m.node_tree.nodes]
    materials.append({'name':m.name,'node_types':nodes})
images=[]
for im in bpy.data.images:
    if im.source=='FILE': images.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)})
libs=[l.filepath for l in bpy.data.libraries]
report={
 'candidate_sha256':sha,'fresh_opened':True,'blender_version':bpy.app.version_string,'file':str(p),
 'scene':scene.name,'collection':coll.name,'collection_object_count':len(coll.all_objects),'object':obj.name,'object_type':obj.type,
 'vertex_count':len(mesh.vertices),'face_count':len(mesh.polygons),'material_count':len(mesh.materials),
 'bounds_world_m':bounds,'ground_faces':z0_faces,'uv_layers':[u.name for u in mesh.uv_layers],
 'materials':materials,'libraries':libs,'file_images':images,
 'mesh_has_external_data':False
}
out=Path(r'audit/first_street_towers_central_fstc_independent_grade/candidate_probe.json')
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print('FSTC_INDEPENDENT_PROBE',json.dumps({k:report[k] for k in ['candidate_sha256','scene','collection','vertex_count','face_count','material_count','bounds_world_m','uv_layers','libraries','file_images']}))

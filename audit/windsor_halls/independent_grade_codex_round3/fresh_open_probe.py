import bpy, json, os, hashlib, collections
path = bpy.data.filepath
h=hashlib.sha256(open(path,'rb').read()).hexdigest()
collection=bpy.data.collections.get('Asset_massing_windsor_halls_80aeb51')
objects=list(collection.all_objects) if collection else []
meshes=[o for o in objects if o.type=='MESH']
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
libs=[l.filepath for l in bpy.data.libraries]
images=[]
for im in bpy.data.images:
    images.append({'name': im.name, 'filepath': im.filepath, 'packed': bool(im.packed_file), 'exists': bool(im.filepath and os.path.exists(bpy.path.abspath(im.filepath)))})
report={
 'blender_version': bpy.app.version_string,
 'filepath': path,
 'sha256': h,
 'scene_names': list(bpy.data.scenes.keys()),
 'collection_found': bool(collection),
 'object_count': len(objects),
 'type_counts': dict(collections.Counter(o.type for o in objects)),
 'mesh_vertex_count': sum(len(o.data.vertices) for o in meshes),
 'mesh_face_count': sum(len(o.data.polygons) for o in meshes),
 'material_count': len(materials), 'materials': materials,
 'library_paths': libs, 'images': images,
 'object_names': sorted(o.name for o in objects),
}
out=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fresh_open_probe.json')
out=os.path.abspath(out)
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='object_names'},indent=2))


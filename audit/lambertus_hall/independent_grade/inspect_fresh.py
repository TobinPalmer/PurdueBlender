import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[3]
asset = root / 'modular' / 'buildings' / 'lambertus_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll = bpy.data.collections.get('Asset_lambertus_hall')
scene = bpy.data.scenes.get('Building_lambertus_hall')
shell = bpy.data.objects.get('Lambertus Hall | GIS perimeter shell')
assert coll and scene and shell

def bounds_world(obj):
    pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]

shell_coords=[shell.matrix_world @ v.co for v in shell.data.vertices]
materials={m.name: {'library': str(m.library.filepath) if m.library else None,
                    'image_paths': [str(n.image.filepath) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []}
           for m in bpy.data.materials}
objects=[]
for o in sorted(coll.objects, key=lambda q:q.name):
    objects.append({'name':o.name,'type':o.type,'loc':list(o.location),'dims':list(o.dimensions),
                    'bounds':bounds_world(o),'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],
                    'modifiers':[m.name for m in o.modifiers]})
libs=[l.filepath for l in bpy.data.libraries]
out={
 'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),
 'scene':scene.name,'collection':coll.name,
 'scene_names':sorted(s.name for s in bpy.data.scenes),
 'objects':objects,
 'shell':{'name':shell.name,'vertex_count':len(shell.data.vertices),'polygon_count':len(shell.data.polygons),
          'local_vertices':[list(v.co) for v in shell.data.vertices],
          'local_bounds':[[min(v.co[i] for v in shell.data.vertices),max(v.co[i] for v in shell.data.vertices)] for i in range(3)],
          'world_bounds':bounds_world(shell),'location':list(shell.location),'scale':list(shell.scale),
          'polygon_vertex_counts':[len(p.vertices) for p in shell.data.polygons],
          'tagged_source':{k:shell.get(k) for k in shell.keys()}},
 'collection_object_count':len(coll.objects),
 'mesh_object_count':sum(o.type=='MESH' for o in coll.objects),
 'unique_mesh_material_count':len({m.name for o in coll.objects if o.type=='MESH' for m in o.data.materials}),
 'material_specs':materials,'library_paths':libs,
 'asset_textures_missing':[p for d in materials.values() for p in d['image_paths'] if not Path(p).is_absolute() or not Path(p).exists()],
 'scene_collection_children':[c.name for c in scene.collection.children]
}
Path(root/'audit'/'lambertus_hall'/'independent_grade'/'fresh_probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ('asset_sha256','scene','collection','collection_object_count','mesh_object_count','unique_mesh_material_count','library_paths','asset_textures_missing','shell')},indent=2))

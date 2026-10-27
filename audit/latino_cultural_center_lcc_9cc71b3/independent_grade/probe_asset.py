import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[3]
asset=root/'modular'/'buildings'/'massing_latino_cultural_center_lcc_9cc71b3.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll=bpy.data.collections.get('Asset_massing_latino_cultural_center_lcc_9cc71b3')
scene=bpy.data.scenes.get('Building_massing_latino_cultural_center_lcc_9cc71b3')
assert coll and scene

def bounds(obj):
    p=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]

objects=[]
for obj in coll.objects:
    item={'name':obj.name,'type':obj.type,'location':list(obj.location),'scale':list(obj.scale),
          'dimensions':list(obj.dimensions),'bounds':bounds(obj),'library':str(obj.library.filepath) if obj.library else None}
    if obj.type=='MESH':
        item.update({'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),
                     'mesh_vertices_world':[list(obj.matrix_world @ v.co) for v in obj.data.vertices] if obj.name=='LCC_FID925_Footprint_Floor' else [],
                     'materials':[m.name for m in obj.data.materials],
                     'modifiers':[m.name for m in obj.modifiers]})
    elif obj.type=='CURVE':
        item['materials']=[m.name for m in obj.data.materials]
    objects.append(item)
materials={m.name:{'library':str(m.library.filepath) if m.library else None,
                   'external_images':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []}
           for m in bpy.data.materials}
out={'sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),
     'scene':scene.name,'collection':coll.name,'objects':objects,
     'collection_bounds':[[min(o['bounds'][i][0] for o in objects),max(o['bounds'][i][1] for o in objects)] for i in range(3)],
     'collection_object_count':len(objects),'mesh_count':sum(o['type']=='MESH' for o in objects),
     'curve_count':sum(o['type']=='CURVE' for o in objects),'other_count':sum(o['type'] not in ('MESH','CURVE') for o in objects),
     'material_specs':materials,'library_paths':[lib.filepath for lib in bpy.data.libraries],
     'scene_objects':len(scene.objects),'child_collections':[c.name for c in scene.collection.children]}
dest=root/'audit'/'latino_cultural_center_lcc_9cc71b3'/'independent_grade'/'fresh_probe.json'
dest.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ('sha256','scene','collection','collection_bounds','collection_object_count','mesh_count','curve_count','other_count','library_paths','scene_objects','child_collections')},indent=2))

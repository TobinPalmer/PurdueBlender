import bpy, json, os
from mathutils import Vector
root = r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender'
asset = os.path.join(root, 'modular', 'buildings', 'massing_joyful_journeys_abaf5c3.blend')
out = os.path.join(root, 'audit', 'massing_joyful_journeys_abaf5c3', 'independent_grade', 'r2', 'independent_reopen.json')
bpy.ops.wm.open_mainfile(filepath=asset)
sc=bpy.context.scene
objs=list(sc.objects)
colls=[c.name for c in bpy.data.collections]
def bounds(o):
    pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
result={'opened_directly':True,'blender_version':bpy.app.version_string,'asset':os.path.relpath(asset,root).replace('\\','/'),'scene':sc.name,'scene_collection_children':[c.name for c in sc.collection.children],'collections':colls,'objects':[],'linked_libraries':[l.filepath for l in bpy.data.libraries],'external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]}
for o in objs:
    result['objects'].append({'name':o.name,'type':o.type,'bounds_world_m':bounds(o),'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'vertex_count':len(o.data.vertices) if o.type=='MESH' else None,'face_count':len(o.data.polygons) if o.type=='MESH' else None,'modifiers':[m.name for m in o.modifiers],'properties':{k:o[k] for k in o.keys()}})
result['checks']={'expected_scene':sc.name=='Building_massing_joyful_journeys_abaf5c3','expected_collection':'Asset_massing_joyful_journeys_abaf5c3' in colls,'one_mesh':len(objs)==1 and objs[0].type=='MESH','identity_transform':len(objs)==1 and all(abs(v)<1e-6 for v in objs[0].location) and all(abs(v)<1e-6 for v in objs[0].rotation_euler) and all(abs(v-1)<1e-6 for v in objs[0].scale),'no_modifiers':all(not o.modifiers for o in objs),'no_linked_libraries':len(result['linked_libraries'])==0,'no_external_images':len(result['external_images'])==0}
with open(out,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))

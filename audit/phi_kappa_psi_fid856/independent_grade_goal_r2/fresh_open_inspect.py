import bpy, json, hashlib, os
from pathlib import Path
asset_path = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\phi_kappa_psi_fid856.blend')
out_path = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\phi_kappa_psi_fid856\independent_grade_goal_r2\fresh_open_inspection.json')
collection = bpy.data.collections.get('Asset_phi_kappa_psi_fid856')
scene = bpy.data.scenes.get('Building_phi_kappa_psi_fid856')
assert collection and scene, 'expected asset collection/scene missing'
# evaluate each object through the active depsgraph, collection-only inventory
bpy.context.window.scene = scene if bpy.context.window else bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
objects=[]
for ob in collection.all_objects:
    eo=ob.evaluated_get(dg)
    bbox=[eo.matrix_world @ __import__('mathutils').Vector(c) for c in eo.bound_box]
    if bbox:
      bounds=[[min(v[i] for v in bbox),max(v[i] for v in bbox)] for i in range(3)]
    else: bounds=None
    objects.append({'name':ob.name,'type':ob.type,'bounds':bounds,'parent':ob.parent.name if ob.parent else None})
# category inventories and geometry bounds
allpts=[p for o in objects if o['bounds'] for p in [[o['bounds'][i][j] for i in range(3)] for j in (0,1)]]
bounds=[[min(p[i] for p in allpts),max(p[i] for p in allpts)] for i in range(3)]
interior=[o for o in objects if any(t in o['name'].lower() for t in ['interior','lounge','stair','partition','upper room','room','corridor','sofa','bookcase','table','chair','landing','guardrail','wall'])]
materials=[]
for m in bpy.data.materials:
    materials.append({'name':m.name,'nodes':m.use_nodes})
images=[i.filepath for i in bpy.data.images if i.source=='FILE']
with open(asset_path,'rb') as f: digest=hashlib.sha256(f.read()).hexdigest()
res={'asset':str(asset_path),'sha256':digest,'scene':scene.name,'collection':collection.name,'collection_object_count':len(objects),'types':{t:sum(o['type']==t for o in objects) for t in sorted(set(o['type'] for o in objects))},'world_bounds':bounds,'objects_with_interior_related_names':interior,'external_images':images,'materials':materials}
out_path.write_text(json.dumps(res,indent=2),encoding='utf-8')
print('INDEPENDENT_FRESH_OPEN_JSON='+str(out_path))
print(json.dumps({k:res[k] for k in ['sha256','scene','collection','collection_object_count','types','world_bounds','external_images']},indent=2))

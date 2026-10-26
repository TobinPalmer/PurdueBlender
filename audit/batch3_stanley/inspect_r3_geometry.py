import bpy, json
from pathlib import Path
from mathutils import Vector

blend = r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=blend)
root = bpy.data.objects['AssetRoot_stanley_coulter_hall']
def bounds(o):
    pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
    return [[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)]
data=[]
for o in bpy.data.collections['Asset_stanley_coulter_hall'].all_objects:
    if any(k in o.name.lower() for k in ('foundation','brick_masonry','historic_slate_roof','window','glasspane','limestone','portico','roof','cornice','floor','lobby')):
        data.append({'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection], 'bounds':bounds(o), 'materials':[m.name for m in o.data.materials if m] if o.type=='MESH' else []})
out={'filepath':bpy.data.filepath,'asset_object_count':len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),'root':{'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale)},'objects':data}
Path(r'audit/batch3_stanley/geometry_r3.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('wrote geometry inventory',len(data),'objects')

import bpy, json, math
from pathlib import Path
ASSET='massing_grant_street_parking_garage_pgg_f46c894'
COL='Asset_'+ASSET
SCENE='Building_'+ASSET
scene=bpy.data.scenes.get(SCENE)
collection=bpy.data.collections.get(COL)
if not scene or not collection: raise RuntimeError('Expected scene or collection missing')
objs=list(collection.objects)
coords=[]
verts=0
faces=0
for o in objs:
    if o.type!='MESH':
        if o.type!='FONT': raise RuntimeError(f'Unexpected asset object type: {o.name} {o.type}')
        continue
    verts += len(o.data.vertices); faces += len(o.data.polygons)
    for corner in o.bound_box:
        coords.append(o.matrix_world @ __import__('mathutils').Vector(corner))
bounds={k:[min(v[i] for v in coords),max(v[i] for v in coords)] for i,k in enumerate(('x','y','z'))}
mods={o.name:[m.name for m in o.modifiers] for o in objs if o.modifiers}
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath]
result={'file':bpy.data.filepath,'blender_version':bpy.app.version_string,'scene':scene.name,'collection':collection.name,'object_count':len(objs),'object_types':sorted({o.type for o in objs}),'vertices':verts,'faces':faces,'bounds_world_m':bounds,'modifiers':mods,'external_images':external,'scenes':sorted(s.name for s in bpy.data.scenes)}
print(json.dumps(result,indent=2))
out=Path(__file__).parent/'reopen_validation.json'
out.write_text(json.dumps(result,indent=2))

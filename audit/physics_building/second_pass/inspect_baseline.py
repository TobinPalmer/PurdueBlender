"""Read the exact Physics baseline without saving it or changing a live scene."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector

D=Path(__file__).resolve().parent
P=Path(bpy.data.filepath);sha=hashlib.sha256(P.read_bytes()).hexdigest()
assert sha=='7dc4f484c84cb0f7c5e6c5c676cf4d3e0e7fb80f434fe4862c1efd4fb342a7f5'
C=bpy.data.collections['Asset_physics_building']
objects=[]
for o in C.all_objects:
    corners=[o.matrix_world@Vector(v) for v in o.bound_box]
    objects.append({'name':o.name,'type':o.type,'bounds':[[min(v[i] for v in corners) for i in range(3)],[max(v[i] for v in corners) for i in range(3)]],'materials':[m.name for m in o.data.materials if m] if hasattr(o.data,'materials') else [],'modifiers':[m.type for m in o.modifiers]})
report={'revision':'second_pass_baseline','asset_sha256':sha,'export_collection':C.name,'objects':len(objects),'object_inventory':objects,'external_libraries':[x.filepath for x in bpy.data.libraries],'external_unpacked_images':[x.filepath for x in bpy.data.images if x.filepath and not x.packed_file],'source_saved':False,'visual_score':None,'accepted':False}
(D/'baseline/inspection.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('asset_sha256','export_collection','objects','external_libraries','external_unpacked_images','source_saved')}))

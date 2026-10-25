import bpy, json, math
from pathlib import Path

scene = bpy.context.scene
col = bpy.data.collections.get('Asset_neil_armstrong_hall')
assert col

def bounds(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not pts:
        return None
    return {
        'min': [round(min(p[i] for p in pts), 3) for i in range(3)],
        'max': [round(max(p[i] for p in pts), 3) for i in range(3)],
        'dims': [round(max(p[i] for p in pts)-min(p[i] for p in pts), 3) for i in range(3)],
        'vertices': len(obj.data.vertices),
        'polygons': len(obj.data.polygons),
        'materials': [m.name if m else None for m in obj.data.materials],
    }

selected = []
terms = ('shell','wall','roof','canopy','atrium','glass','brick','façade','facade','window','entry','parapet','r5_coarse')
for obj in sorted(col.objects, key=lambda o: o.name.lower()):
    if obj.type == 'MESH' and any(t in obj.name.lower() for t in terms):
        selected.append({'name':obj.name,'hide_render':obj.hide_render,'hide_get':obj.hide_get(),**bounds(obj)})

res = {
 'blend':bpy.data.filepath,
 'scene':scene.name,
 'collection':col.name,
 'object_count':len(col.objects),
 'objects':selected,
 'active_camera':scene.camera.name if scene.camera else None,
}
out = Path(bpy.data.filepath).parent.parent.parent / 'audit' / 'neil_armstrong_hall_refine' / 'geometry_inventory_r12.json'
out.write_text(json.dumps(res,indent=2),encoding='utf-8')
print('WROTE',out)
print(json.dumps(res,indent=2))

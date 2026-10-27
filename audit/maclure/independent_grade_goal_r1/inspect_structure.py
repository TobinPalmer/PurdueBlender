import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\maclure_cooperative.blend')
ob=bpy.data.objects['GIS footprint walls | FID 822']
print('wall mesh XY unique')
print(json.dumps(sorted({(round(v.co.x,4),round(v.co.y,4),round(v.co.z,4)) for v in ob.data.vertices})))
for key in ['Main north-south gable roof | estimated profile','Front cross-gable wall | estimated','Front cross-gable shingles | estimated','Roof ridge cap (estimated)','Front chimney (estimated)']:
 o=bpy.data.objects.get(key)
 print(key, bool(o), list(o.dimensions) if o else None)
print('ROOMS')
for o in bpy.data.collections['Asset_maclure_cooperative'].objects:
 if any(t in o.name.lower() for t in ['partition','room','floor slab','living','dining','foyer']): print(o.name, list(o.dimensions),list(o.location),o.hide_render)

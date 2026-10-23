import bpy,json
from pathlib import Path
src=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/math_sciences.blend')
bpy.ops.wm.open_mainfile(filepath=str(src))
c=bpy.data.collections['Asset_math_sciences']
out=[]
for o in c.all_objects:
 if o.type!='MESH': continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 if not vs: continue
 out.append({'name':o.name,'verts':len(vs),'faces':len(o.data.polygons),'bounds':[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)],'hidden':o.hide_render})
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_math/asset_geometry.json').write_text(json.dumps(out,indent=2))
print('OBJECTS',len(out))
for x in out:
 if 'GIS' in x['name'] or 'Wall' in x['name'] or 'Shell' in x['name'] or 'Foot' in x['name']:print(x)

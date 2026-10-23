import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/math_sciences.blend')
mesh=bpy.data.meshes.get('MATH_2026_Envelope_Source_Backup')
if mesh is None: raise RuntimeError('Saved asset is missing its source shell backup')
rows=[]
for i in range(len(mesh.vertices)//8):
    vv=[mesh.vertices[i*8+j].co for j in range(8)]
    rows.append({'i':i,'x':[min(v.x for v in vv),max(v.x for v in vv)],
                 'y':[min(v.y for v in vv),max(v.y for v in vv)],
                 'z':[min(v.z for v in vv),max(v.z for v in vv)]})
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_math/wall_components.json').write_text(json.dumps(rows,indent=2))
print('SOURCE BACKUP PRISMS',len(rows),'CURRENT ENVELOPE COMPONENTS',len(bpy.data.objects['MATH_Corrected_GIS_Wall_Envelope'].data.vertices)//8)

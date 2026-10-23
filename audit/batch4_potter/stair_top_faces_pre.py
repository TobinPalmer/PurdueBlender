import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');c=bpy.data.collections['Asset_potter_engineering'];o=c.objects['POTR_2016_StairCore3_Level0_Flight'];
out=[]
for p in o.data.polygons:
 if p.normal.z>.99 and p.area>.08:
  co=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
  out.append({'z':round(sum(v.z for v in co)/len(co),4),'area':round(p.area,3),'x': [round(min(v.x for v in co),3),round(max(v.x for v in co),3)],'y':[round(min(v.y for v in co),3),round(max(v.y for v in co),3)]})
out.sort(key=lambda r:r['z']);Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter/stair_top_faces_pre.json').write_text(json.dumps(out,indent=2));print(json.dumps(out[:5]+out[-5:],indent=2))

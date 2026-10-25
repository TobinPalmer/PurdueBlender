import bpy,json,pathlib
from mathutils import Vector
c=bpy.data.collections['Asset_stewart_center']; objs=[o for o in c.all_objects if o.name.startswith('STEW_Ext_Wall')]
rows=[]
for o in sorted(objs,key=lambda o:o.name):
 v=[o.matrix_world@vert.co for vert in o.data.vertices]
 rows.append({'name':o.name,'type':o.type,'bounds':[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)],'verts':len(v),'faces':len(o.data.polygons)})
out={'structural_wall_object_count':len(rows),'walls':rows,'all_walls_bounds':[[min(r['bounds'][i][0] for r in rows),max(r['bounds'][i][1] for r in rows)] for i in range(3)]}
pathlib.Path('audit/stewart_center_independent_grade/structural_wall_probe.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))

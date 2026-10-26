import bpy,json,os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); path=os.path.join(root,'modular','buildings','massing_yue_kong_pao_hall_a3cb766.blend'); bpy.ops.wm.open_mainfile(filepath=path)
col=bpy.data.collections['Asset_massing_yue_kong_pao_hall_a3cb766']; rows=[]
for o in col.objects:
 if o.type=='MESH' and o.name.startswith('Perimeter brick wall '):
  xy=[]
  for v in o.data.vertices:
   p=o.matrix_world@v.co; xy.append([round(p.x,6),round(p.y,6)])
  rows.append({'name':o.name,'xy':xy})
pathout=os.path.join(root,'audit','yue_kong_pao_hall','independent_grade_r1_wall_vertices.json')
with open(pathout,'w') as f:json.dump({'asset':path,'sha256':__import__('hashlib').sha256(open(path,'rb').read()).hexdigest(),'walls':rows},f)
print('WALLS',len(rows),'verts',sum(len(x['xy']) for x in rows),'file',pathout)

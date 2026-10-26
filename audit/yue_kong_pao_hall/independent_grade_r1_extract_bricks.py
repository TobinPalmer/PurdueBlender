import bpy,json,os,hashlib
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); p=os.path.join(root,'modular','buildings','massing_yue_kong_pao_hall_a3cb766.blend'); bpy.ops.wm.open_mainfile(filepath=p)
col=bpy.data.collections['Asset_massing_yue_kong_pao_hall_a3cb766']; rows=[]
for o in col.objects:
 if o.type=='MESH' and any(m and m.name=='Purdue_Red_Brick' for m in o.data.materials):
  vv=[o.matrix_world@v.co for v in o.data.vertices]
  rows.append({'name':o.name,'z_bounds':[min(v.z for v in vv),max(v.z for v in vv)],'xy':[[round(v.x,6),round(v.y,6)] for v in vv]})
out={'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'brick_meshes':rows}
outp=os.path.join(root,'audit','yue_kong_pao_hall','independent_grade_r1_brick_vertices.json'); open(outp,'w').write(json.dumps(out))
print('red brick objects',len(rows),'base objects',sum(1 for o in rows if o['z_bounds'][0]<0.1),'vertices',sum(len(o['xy']) for o in rows))

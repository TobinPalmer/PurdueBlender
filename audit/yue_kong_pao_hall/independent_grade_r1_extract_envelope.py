import bpy,json,os,hashlib
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); p=os.path.join(root,'modular','buildings','massing_yue_kong_pao_hall_a3cb766.blend'); bpy.ops.wm.open_mainfile(filepath=p)
col=bpy.data.collections['Asset_massing_yue_kong_pao_hall_a3cb766']; prefixes=('Perimeter brick wall ','South brick pier ','South facade limestone base','South facade brick course','Glazing | glazed bay','Glazing | lobby entry','Lobby double door','Entry canopy column')
rows=[]
for o in col.objects:
 if o.type!='MESH': continue
 if not o.name.startswith(prefixes): continue
 vv=[o.matrix_world@v.co for v in o.data.vertices]
 rows.append({'name':o.name,'z_bounds':[min(v.z for v in vv),max(v.z for v in vv)],'xy':[[round(v.x,6),round(v.y,6)] for v in vv]})
outp=os.path.join(root,'audit','yue_kong_pao_hall','independent_grade_r1_envelope_components.json'); open(outp,'w').write(json.dumps({'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'components':rows}))
print('components',len(rows),'ground',sum(1 for x in rows if x['z_bounds'][0]<.1),'vertices',sum(len(x['xy']) for x in rows))

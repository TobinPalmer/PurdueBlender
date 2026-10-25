import bpy,json,hashlib
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend1'
bpy.ops.wm.open_mainfile(filepath=p)
rows=[]
for name in ['ARMS_East_Roof_Penthouse','ARMS_East_Penthouse_Louvers','ARMS_West_Roof_Penthouse','ARMS_West_Penthouse_Louvers']:
 o=bpy.data.objects[name]
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 b=[[float(min(v[i] for v in pts)),float(max(v[i] for v in pts))] for i in range(3)]
 rows.append({'name':name,'bounds_local_m':b,'horizontal_extent_m':[b[0][1]-b[0][0],b[1][1]-b[1][0]],'height_range_m':b[2][1]-b[2][0]})
print(json.dumps({'asset_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'objects':rows},indent=2))

import bpy, json
from mathutils import Vector
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
asset=root+r'\modular\buildings\neil_armstrong_hall.blend'
out=root+r'\audit\complete_neil_armstrong\sources\shell_wall_edges_r3.json'
bpy.ops.wm.open_mainfile(filepath=asset)
col=bpy.data.collections['Asset_neil_armstrong_hall']
rows=[]
for o in col.objects:
    if o.type!='MESH' or 'Wall' not in o.name: continue
    mat=o.matrix_world
    pts=[list((mat@v.co)[:]) for v in o.data.vertices]
    edges=[[int(e.vertices[0]),int(e.vertices[1])] for e in o.data.edges]
    rows.append({'name':o.name,'vertices':pts,'edges':edges})
with open(out,'w') as f: json.dump(rows,f)
print('EXPORTED',len(rows),sum(len(x['vertices']) for x in rows),out)

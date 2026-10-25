import bpy,json
from mathutils import Vector
out={}
for name in ['LWSN_Foundation_Base','LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Rotunda_Curtain_Glass']:
 o=bpy.data.objects.get(name); mw=o.matrix_world
 vv=[mw@v.co for v in o.data.vertices]
 z0=min(v.z for v in vv)
 out[name]={'z0':z0,'edges':[[[round(vv[e.vertices[0]].x,6),round(vv[e.vertices[0]].y,6)],[round(vv[e.vertices[1]].x,6),round(vv[e.vertices[1]].y,6)]] for e in o.data.edges if abs(vv[e.vertices[0]].z-z0)<1e-4 and abs(vv[e.vertices[1]].z-z0)<1e-4]}
with open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/r7_shell_edges.json','w') as f:json.dump(out,f,indent=2)
print({k:(v['z0'],len(v['edges'])) for k,v in out.items()})

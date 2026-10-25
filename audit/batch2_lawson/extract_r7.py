import bpy,json,math
from mathutils import Vector
out={}
for name in ['LWSN_Foundation_Base','LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Rotunda_Curtain_Glass','LWSN_Rotunda_Spandrel_Panels']:
 o=bpy.data.objects.get(name)
 if not o or o.type!='MESH': continue
 mw=o.matrix_world
 verts=[mw@v.co for v in o.data.vertices]
 zmin=min(v.z for v in verts); zmax=max(v.z for v in verts)
 out[name]={'z_range':[zmin,zmax], 'vertex_count':len(verts),'edge_count':len(o.data.edges),'face_count':len(o.data.polygons),'vertices_below_1m':[[round(v.x,5),round(v.y,5),round(v.z,5)] for v in verts if v.z<1.01]}
with open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/r7_shell_vertices.json','w') as f:json.dump(out,f,indent=2)
print({k:{x:y for x,y in v.items() if x!='vertices_below_1m'} for k,v in out.items()})

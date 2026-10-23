import bpy,math,pathlib
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(p/'audit/batch3_elliott/before_resume.blend'));w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];N=len(w.data.vertices)//2;ring=[(v.co.x,v.co.y) for v in w.data.vertices[:N]]
for name,tgt in [('hovde_infill',(70.52,15.98)),('hovde_bridge_southwall',(61.197+9.3,28.344-15)),('hovde_main_portico',(61.197,28.344))]:
 best=(1e9,None,None,None)
 for i,a in enumerate(ring):
  b=ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((tgt[0]-a[0])*dx+(tgt[1]-a[1])*dy)/den)) if den else 0;q=(a[0]+dx*t,a[1]+dy*t);d=math.dist(tgt,q)
  if d<best[0]:best=(d,i,t,q)
 print(name,best)

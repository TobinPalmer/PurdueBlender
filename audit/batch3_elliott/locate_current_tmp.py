import bpy,math
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']; N=188; r=[(v.co.x,v.co.y) for v in w.data.vertices[:N]]
for tgt in [(70.5,16),(61.197+9.3,28.344-15),(61.197+6.77,28.344-14.38),(61.197+6.77,28.344-19.5)]:
 best=(1e9,0,0,None)
 for i,a in enumerate(r):
  b=r[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((tgt[0]-a[0])*dx+(tgt[1]-a[1])*dy)/den)) if den else 0;q=(a[0]+dx*t,a[1]+dy*t);d=math.dist(tgt,q)
  if d<best[0]:best=(d,i,t,q)
 print(tgt,best)

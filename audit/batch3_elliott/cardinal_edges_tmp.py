import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_elliott/before_resume.blend')
o=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];n=len(o.data.vertices)//2;pts=[(v.co.x,v.co.y) for v in o.data.vertices[:n]]
for mode in ['N','S']:
 i=(max if mode=='N' else min)(range(n),key=lambda i:pts[i][1]);p=pts[i];print(mode,'idx',i,'point',p)
 for d in range(-4,5):
  q=pts[(i+d)%n];print(d,tuple(round(x,2) for x in q))

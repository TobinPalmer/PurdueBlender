import bpy
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
obj=bpy.data.objects['AQUA R3 | subtle standing seams on estimated roof']; c=obj.data
original=list(c.splines)
# Mirror the evenly spaced seams onto the opposite estimated roof plane.
for s in original:
 n=c.splines.new('POLY'); n.points.add(len(s.points)-1)
 for dst,src in zip(n.points,s.points):
  dst.co=(-src.co.x,src.co.y,src.co.z,src.co.w)
# Mirror seam shading across both roof planes.
bpy.ops.wm.save_as_mainfile(filepath=str(p));print('Mirrored seams across both estimated roof planes:',len(c.splines))

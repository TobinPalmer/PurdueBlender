import bpy, collections
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\brown_laboratory_of_chemistry.blend')
for n in ('Exterior_Brickwork_EW','Exterior_Concrete_Piers_and_Coping','Exterior_Glazing','Exterior_Window_Frames'):
 o=bpy.data.objects.get(n); by=collections.defaultdict(list)
 for p in o.data.polygons:
  c=p.center
  if p.normal.y<-.8 and .1<c.z<16: by[round(c.y,1)].append(c.x)
 vals=sorted(by.items())
 print(n,[(y,round(min(xs),1),round(max(xs),1),len(xs)) for y,xs in vals if y<0])

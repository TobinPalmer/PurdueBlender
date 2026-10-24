import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_knoy_hall'];pts=[]
for o in c.objects:
 if o.type=='MESH': pts += [o.matrix_world@v.co for v in o.data.vertices]
print('bounds',min(v.x for v in pts),max(v.x for v in pts),min(v.y for v in pts),max(v.y for v in pts),min(v.z for v in pts),max(v.z for v in pts))
print('object examples')
for n in ['KNOY_FloorSlab_L2','KNOY_FloorSlab_L4','KNOY_Exterior_Walls','KNOY_Roof','KNOY_Roof_Parapet']:
 o=bpy.data.objects.get(n)
 if o and o.type=='MESH':
  pts=[o.matrix_world@v.co for v in o.data.vertices];print(n,(min(v.x for v in pts),max(v.x for v in pts),min(v.y for v in pts),max(v.y for v in pts),min(v.z for v in pts),max(v.z for v in pts)))

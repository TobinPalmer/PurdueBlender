import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\krannert_building.blend';bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects['KRAN_FloorSlab_Roof_Deck']
for i,v in enumerate(o.data.vertices):
 print(i,tuple(round(float(a),4) for a in v.co))

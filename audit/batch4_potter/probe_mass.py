import bpy
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=P);o=bpy.data.collections['Asset_potter_engineering'].objects['POTR_Historic2016_Room401_Penthouse_Massing'];v=o.data.vertices
for x in sorted(set(round(p.co.x,3) for p in v)):
 ys=sorted(set(round(p.co.y,3) for p in v if abs(p.co.x-x)<.001));print(x,ys)

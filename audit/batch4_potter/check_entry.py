import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
o=next(o for o in bpy.data.collections['Asset_potter_engineering'].objects if 'Structural_Envelope' in o.name)
for p in o.data.polygons:
 pts=[o.data.vertices[i].co for i in p.vertices];cx=sum(v.x for v in pts)/len(pts);cy=sum(v.y for v in pts)/len(pts);cz=sum(v.z for v in pts)/len(pts)
 if 19<cx<22 and 54<cy<56 and cz<4.5: print('FACE',p.index,tuple(round(v,3) for v in (cx,cy,cz)),[(round(v.x,3),round(v.y,3),round(v.z,3)) for v in pts])

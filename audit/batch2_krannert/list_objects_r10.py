import bpy
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/krannert_building.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.collections['Asset_krannert_building'].all_objects:
 if 'KRAN' in o.name: print(o.name,o.type,len(o.data.vertices) if o.type=='MESH' else '')

import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');c=bpy.data.collections['Asset_hovde_hall']
inside=set(c.all_objects)
for o in bpy.context.scene.objects:
 if o not in inside and o.type=='MESH':print('outside',o.name,tuple(o.location),tuple(o.dimensions),'hide',o.hide_render,'colls',[x.name for x in o.users_collection])

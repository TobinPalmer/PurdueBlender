import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');
for n in ['AssetRoot_rawls_hall','RAWL_Masonry_Exterior_Walls','RAWL_North_Windows_Glass','RAWL_FloorSlab_L1_Ground']:
 o=bpy.data.objects[n];print(n,'hide_render',o.hide_render,'hide_viewport',o.hide_viewport,'location',list(o.location))
for n in bpy.data.scenes:
 print('scene',n.name,'collection children',[c.name for c in n.collection.children])

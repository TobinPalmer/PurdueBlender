import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/massing_house_301840872_582df9d.blend')
c=bpy.data.collections.get('Asset_massing_house_301840872_582df9d')
for o in c.objects:print(o.name,o.type,list(o.location),list(o.dimensions),len(o.data.vertices) if o.type=='MESH' else '')

import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/massing_house_301841601_7ae6159.blend')
c=bpy.data.collections.get('Asset_massing_house_301841601_7ae6159')
for o in c.objects: print(o.name,o.type,list(o.location),list(o.dimensions),len(o.data.vertices) if o.type=='MESH' else '')

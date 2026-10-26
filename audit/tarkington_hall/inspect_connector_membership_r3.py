import bpy,json
for name in ['Asset_tarkington_hall','AssetRoot_tarkington_hall']:
 o=bpy.data.collections.get(name) if name.startswith('Asset_') else bpy.data.objects.get(name)
 print(name, o.name if o else None, len(o.objects) if hasattr(o,'objects') else None, o.users_collection if hasattr(o,'users_collection') else None)
for o in bpy.data.objects:
 if o.name.startswith(('Tark_West_Connector_','Tark_East_Connector_')):
  print(o.name, [c.name for c in o.users_collection], o.parent.name if o.parent else None, tuple(round(x,3) for x in o.matrix_world.translation))

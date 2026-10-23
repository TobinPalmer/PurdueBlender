import bpy,json
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_Atrium_Mezzanine_Balustrades','RAWL_Atrium_Structural_Columns','RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5','RAWL_Roof_Main_Deck','RAWL_Roof_Arched_Penthouse']:
 o=bpy.data.objects.get(n)
 if o:
  polys=len(o.data.polygons) if o.type=='MESH' else 0
  mats=[m.name for m in o.data.materials]
  print(n,o.type,'polys',polys,'mats',mats,'hide',o.hide_render, 'parent', o.parent.name if o.parent else None)
  if o.type=='MESH':
   print('bbox',o.dimensions[:],'location',o.location[:])

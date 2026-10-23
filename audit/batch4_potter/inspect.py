import bpy
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_potter_engineering']
print('root',[(x.name,tuple(x.location),tuple(x.dimensions),x.parent.name if x.parent else None) for x in c.objects if 'AssetRoot' in x.name])
for o in c.objects:
 if any(t in o.name for t in ['MergedPartitions','Lab','Window','Precast','Overhang','Roof','Slab','Floor','Camera','Entry','Stair']):
  print(o.name,o.type,tuple(round(v,2) for v in o.dimensions),tuple(round(v,2) for v in o.location),len(o.data.polygons) if o.type=='MESH' else '')

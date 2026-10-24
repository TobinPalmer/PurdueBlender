import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
c=bpy.data.collections.get('Asset_knoy_hall');print('count',len(c.objects))
for o in sorted(c.objects,key=lambda o:o.name):
 if o.type!='MESH':continue
 if any(k in o.name.lower() for k in ['facade','brick','wall','band','masonry','window','glaz','spandrel','curtain']):
  mats=[m.name if m else None for m in o.data.materials]
  print(o.name,'verts',len(o.data.vertices),'polys',len(o.data.polygons),'materials',mats,'matcounts', {m.name:sum(1 for p in o.data.polygons if p.material_index < len(o.data.materials) and o.data.materials[p.material_index]==m) for m in o.data.materials if m})

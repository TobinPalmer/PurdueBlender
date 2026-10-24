import bpy, os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/niswonger_aviation_tech.blend'))
for mn in ['NISW_Roof_Membrane','NISW_StandingSeam_Roof','NISW_Bedford_Limestone','NISW_Photographic_Terracotta_Panels','NISW_Plaza_Concrete','NISW_Campus_Turf_Grass']:
 m=bpy.data.materials.get(mn); print('\nMAT',mn, 'exists',bool(m))
 if m:
  for o in bpy.data.objects:
   if o.type=='MESH' and any(x==m for x in o.data.materials):
    print(o.name,tuple(round(v,2) for v in o.dimensions),'coll',[c.name for c in o.users_collection])


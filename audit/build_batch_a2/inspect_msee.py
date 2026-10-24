import bpy,os,json
p='modular/buildings/materials_science_and_electrical_engineering_msee.blend';bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p));c=bpy.data.collections.get('Asset_materials_science_and_electrical_engineering_msee')
for o in c.all_objects:
 if any(s in o.name.lower() for s in ('atrium','entry','portal','header','skylight','gis_outline','shell')):
  if o.type=='MESH':
   cs=[o.matrix_world@v.co for v in o.data.vertices];b=[[round(min(v[i] for v in cs),2),round(max(v[i] for v in cs),2)] for i in range(3)]
  else:b=[]
  print(o.name,o.type,b)

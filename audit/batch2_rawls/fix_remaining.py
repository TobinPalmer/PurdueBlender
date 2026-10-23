import bpy,os
col=bpy.data.collections['Asset_rawls_hall']
for o in list(col.all_objects):
 if o and '2026_1086_Chair' in o.name:
  p=o.location.copy()
  for x in [-.16,.16]:
   for y in [-.16,.16]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(p.x+x,p.y+y,.215));q=bpy.context.object;q.name='RAWL_2026_ChairLeg';q.dimensions=(.035,.035,.43);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(q.users_collection):c.objects.unlink(q)
    col.objects.link(q);q.data.materials.append(bpy.data.materials['RAWL_Dark_Bronze_Metal'])
# Avoid coplanar overlap between plaza and apron without moving structural walls.
o=bpy.data.objects.get('RAWL_Site_North_Plaza')
if o:o.location.z-=.018
o=bpy.data.objects.get('RAWL_Site_Sidewalk_Apron')
if o:o.location.z+=.012
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

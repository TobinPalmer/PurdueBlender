import bpy,os
C=bpy.data.collections['Asset_krannert_building'];root=bpy.data.objects['AssetRoot_krannert_building'];m=bpy.data.materials['KRAN_Furniture_Chrome']
for desk in list(C.objects):
 if not desk.name.startswith('KRAN_New_Parrish_StudyDesk'):continue
 x,y,z=desk.location
 for dx in [-.67,.67]:
  for dy in [-.27,.27]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(x+dx,y+dy,8.55+.355));o=bpy.context.object;o.name='KRAN_New_Parrish_DeskLeg';o.dimensions=(.035,.035,.71);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
   for c in list(o.users_collection):c.objects.unlink(o)
   C.objects.link(o);o.parent=root;o.data.materials.append(m)
bpy.context.scene['batch2_review_status']='5.7/10 independent;24 desk supports fixed after review'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

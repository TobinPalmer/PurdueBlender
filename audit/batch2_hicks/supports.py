import bpy
c=bpy.data.collections['HIKS_2013_Study_Furnishing_Interpretation'];m=bpy.data.materials['HIKS_Study_Satin_Metal']
def box(n,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for a in list(o.users_collection):a.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m);o['evidence']='Estimated functional supports for photo-supported furnishing'
for x in [-10.5,-8.7,-6.9]:
 for dx in [-.58,.58]:
  for y in [5.55,6.05]:box('HIKS_Study_ComputerDeskLeg',(x+dx,y,-4.927),(.045,.045,.754))
for x in [-8.5,8.5]:
 for y in [-4,0,4]:
  for dx in [-.4,.4]:box('HIKS_Study_LuminaireSuspension',(x+dx,y,.14),(.008,.008,4.58))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

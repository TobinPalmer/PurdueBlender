import bpy,json,os
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_earhart_hall_0f14209.blend'; out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\earhart_hall_independent_grade'
bpy.ops.wm.open_mainfile(filepath=p); sc=bpy.context.scene
keep={'ERHT_Interior_Standard_Room_Floors','ERHT_Interior_Standard_Room_Partitions','ERHT_Interior_Standard_Room_Furniture','ERHT_Interior_Standard_Room_Bedding'}
pts=[]
for ob in bpy.data.objects:
 ob.hide_render=ob.name not in keep
 if ob.name in keep and ob.type=='MESH':
  for c in ob.bound_box: pts.append(ob.matrix_world@Vector(c))
mi=[min(v[i] for v in pts) for i in range(3)]; ma=[max(v[i] for v in pts) for i in range(3)]; cen=[(mi[i]+ma[i])/2 for i in range(3)]
cd=bpy.data.cameras.new('IndependentInteriorCamera'); cam=bpy.data.objects.new('IndependentInteriorCamera',cd); sc.collection.objects.link(cam)
cam.location=(cen[0],cen[1],ma[2]+8); cam.rotation_euler=(0,0,0); cam.data.type='ORTHO'; cam.data.ortho_scale=max(ma[0]-mi[0],ma[1]-mi[1])*1.25; sc.camera=cam
sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.filepath=os.path.join(out,'isolated_room_plan.png'); sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
bpy.ops.render.render(write_still=True)
json.dump({'room_object_names':sorted(keep),'bounds_m':[mi,ma],'center_m':cen,'review_method':'in-memory isolate of saved representative standard double-room geometry, camera/render added after fresh opening; no asset file saved'},open(os.path.join(out,'interior_review.json'),'w'),indent=2)

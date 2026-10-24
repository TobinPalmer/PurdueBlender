import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
scene=bpy.context.scene; cd=bpy.data.cameras.new('tmp'); c=bpy.data.objects.new('tmp',cd); scene.collection.objects.link(c); c.location=(21.7115,193.0986,12); c.rotation_euler=(Vector((-39.6,97.8,-16))-c.location).to_track_quat('-Z','Y').to_euler(); cd.lens=24; cd.clip_end=1200; scene.camera=c; bpy.context.view_layer.update()
cam=(21.7115,193.0986); fx,fy=-39.6,97.8; dx=fx-cam[0]; dy=fy-cam[1]; n=math.hypot(dx,dy); ux,uy=dx/n,dy/n
for o in bpy.data.objects:
 if not o.name.startswith('Plant_'): continue
 d=math.hypot(o.location.x-cam[0],o.location.y-cam[1]); along=(o.location.x-cam[0])*ux+(o.location.y-cam[1])*uy
 h=float(o.get('height_m',5)); p=world_to_camera_view(scene,c,Vector((o.location.x,o.location.y,h*.8)))
 name=o.get('common_name',''); dbh=float(o.get('inventory_dbh_in') or 0); spread=float(o.get('inventory_spread_ft') or 0)
 if ('Oak' in name or 'Gum' in name or dbh>=30):
  print(o.name, 'xy',round(o.location.x,1),round(o.location.y,1),'depth',round(along,1),'d',round(d,1),'screen',round(p.x,2),round(p.y,2),'dbh',dbh,'spread',spread,'h',h,name)

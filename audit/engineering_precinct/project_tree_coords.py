import bpy
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;c=s.camera
for o in s.objects:
 if o.name.startswith('Plant_') and o.type=='MESH':
  p=world_to_camera_view(s,c,o.matrix_world.translation)
  if .25<=p.x<=.7 and .1<=p.y<=.85:
   print(o.name,round(p.x,2),round(p.y,2),'db',o.get('inventory_dbh_in'),'sp',o.get('inventory_spread_ft'),'ht',o.get('height_m'),'scale',round(o.scale.x,1))

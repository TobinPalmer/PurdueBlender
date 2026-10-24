import bpy
for o in bpy.context.scene.objects:
 if o.name.startswith('Plant_') and o.type=='MESH' and (o.get('inventory_spread_ft') or 0)>=45:
  print(o.name,'base',o.get('reference_frame_x'),o.get('reference_frame_y'),'crown',o.get('reference_crown_x'),o.get('reference_crown_y'),'scale',o.get('visual_crown_scale_xy'))

import bpy,json
from pathlib import Path
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');c=bpy.data.collections['Asset_mechanical_engineering'];rc=bpy.data.collections.new('ME_Unregistered_Plan_Study');bpy.context.scene.collection.children.link(rc);rc.hide_render=True;rc.hide_viewport=True
for o in list(c.objects):
 if o.name.startswith('ME_Slide12_Partition_'):c.objects.unlink(o);rc.objects.link(o)
c['interior_status']='Estimated floor slabs only; safety floorplan tracing archived because affine registration fails official footprint check'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'modular/buildings/mechanical_engineering.blend'))

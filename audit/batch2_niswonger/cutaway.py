import bpy
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;c=bpy.data.collections['Asset_niswonger_aviation_tech']
for o in c.all_objects:
 if o and any(x in o.name for x in ['Roof','Ceiling','ClerestoryClosure']):o.hide_render=True
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True
s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
ca=bpy.data.cameras.new('ReviewPlan');ob=bpy.data.objects.new('ReviewPlan',ca);s.collection.objects.link(ob);s.camera=ob;ca.type='ORTHO';ca.ortho_scale=85;ob.location=(-8,7,100);ob.rotation_euler=(0,0,0);s.render.filepath=str(Path('audit/batch2_niswonger/cutaway.png').resolve());bpy.ops.render.render(write_still=True)


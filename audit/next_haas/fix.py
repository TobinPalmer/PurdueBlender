import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
D=Path('audit/next_haas');fp=Path(bpy.data.filepath);shutil.copy2(fp,D/'before.blend')
c=bpy.data.collections['Asset_felix_haas_hall'];changes=[]
for m in bpy.data.materials:
 if not m.name.startswith('HAAS_') or not m.node_tree:continue
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if p and not p.inputs['Base Color'].is_linked and max(abs(a-b) for a,b in zip(m.diffuse_color,p.inputs['Base Color'].default_value))>.00001:
  changes.append({'material':m.name,'before':list(m.diffuse_color),'after':list(p.inputs['Base Color'].default_value),'objects':[o.name for o in c.all_objects if o.type=='MESH' and m.name in [x.name for x in o.data.materials]]});m.diffuse_color=p.inputs['Base Color'].default_value
bpy.ops.wm.save_as_mainfile(filepath=str(fp));bpy.ops.wm.open_mainfile(filepath=str(fp))
c=bpy.data.collections['Asset_felix_haas_hall'];s=bpy.context.scene
camd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',camd);s.collection.objects.link(cam);cam.location=(65,-85,65);cam.rotation_euler=(Vector((0,0,4))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=90;s.camera=cam;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.view_settings.view_transform='Standard';s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.filepath=str(D/'after.png');bpy.ops.render.render(write_still=True)
(D/'changes.json').write_text(json.dumps({'changes':changes,'reopened':True,'count':len(c.all_objects),'images':[(i.name,i.filepath,bool(i.packed_file)) for i in bpy.data.images if i.source=='FILE'],'geometry_changed':False},indent=2))

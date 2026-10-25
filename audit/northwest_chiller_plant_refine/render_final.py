import bpy, os
from mathutils import Vector
p=os.path.abspath('modular/buildings/northwest_chiller_plant.blend'); out=os.path.abspath('audit/northwest_chiller_plant_refine')
bpy.ops.wm.open_mainfile(filepath=p); s=bpy.context.scene;old=s.camera
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
w=bpy.data.worlds.new('NWCP_refine_temp_world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.28,.33,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w
def camera(name,pos,target,scale):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;return o
def area(name,loc,target,power,size):
 d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.size=size;return o
lights=[area('temp_key',(-25,-35,40),(1,0,7),4200,24),area('temp_fill',(25,-5,28),(1,0,7),2600,20),area('temp_rim',(5,32,32),(1,0,7),3300,18)]
c=camera('temp_preview_cam',(48,-58,42),(1,0,7),66);s.camera=c;s.render.filepath=os.path.join(out,'northwest_chiller_plant_refine_overview.png');bpy.ops.render.render(write_still=True)
s.render.filepath=os.path.join(out,'northwest_chiller_plant_refine_detail.png');c.location=(35,-43,18);c.data.ortho_scale=32;c.rotation_euler=(Vector((1,-4,7))-c.location).to_track_quat('-Z','Y').to_euler();bpy.ops.render.render(write_still=True)
s.camera=old
for o in [c,*lights]: bpy.data.objects.remove(o,do_unlink=True)
bpy.data.cameras.remove(c.data) if c.data else None

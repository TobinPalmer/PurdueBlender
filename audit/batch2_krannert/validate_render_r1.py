import bpy,os,json
from mathutils import Vector
path=os.path.abspath('modular/buildings/krannert_building.blend');P=os.path.abspath('audit/batch2_krannert')
bpy.ops.wm.open_mainfile(filepath=path)
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100
s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.55,.62,.75,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.45
made=[]
def addcam(name,loc,target,lens=21):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name='TEMP_'+name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;made.append(o);return o
def light(name,loc,energy,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='TEMP_'+name;o.data.energy=energy;o.data.shape='RECTANGLE';o.data.size=size;o.data.size_y=size*.7;made.append(o)
light('drawing_fill',(-14,-3,7.1),1600,8);light('parrish_fill',(-14,-1,11.2),1800,9)
s.camera=addcam('drawingroom',(-18,-7,5.5),(-10,-.5,5),21);s.render.filepath=os.path.join(P,'drawingroom_r1.png');bpy.ops.render.render(write_still=True)
s.camera=addcam('parrish',(-18,-7,10.1),(-10,-.5,9.6),21);s.render.filepath=os.path.join(P,'parrish_r1.png');bpy.ops.render.render(write_still=True)
for o in made:bpy.data.objects.remove(o,do_unlink=True)

import bpy,os
from mathutils import Vector
HERE=os.path.dirname(__file__); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841601_7ae6159.blend')
bpy.ops.wm.open_mainfile(filepath=ASSET); scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1100; scene.render.resolution_y=850; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new('DZ preview world'); scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.5,.58,.68,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
for o in list(scene.objects):
 if o.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(o,do_unlink=True)
obj=bpy.data.objects['House_301841601']; b=obj.bound_box; corners=[obj.matrix_world@Vector(v) for v in b]; lo=Vector((min(p.x for p in corners),min(p.y for p in corners),min(p.z for p in corners))); hi=Vector((max(p.x for p in corners),max(p.y for p in corners),max(p.z for p in corners))); c=(lo+hi)/2
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
ld=bpy.data.lights.new('Legacy key','AREA');ld.energy=75000;ld.shape='DISK';ld.size=48;light=bpy.data.objects.new('Legacy key',ld);scene.collection.objects.link(light);light.location=c+Vector((40,-70,65));aim(light,c)
cd=bpy.data.cameras.new('Legacy camera');cd.type='ORTHO';cd.ortho_scale=90;cam=bpy.data.objects.new('Legacy camera',cd);scene.collection.objects.link(cam);cam.location=c+Vector((45,-70,38));aim(cam,c);scene.camera=cam
scene.render.filepath=os.path.join(HERE,'legacy_exterior.png');bpy.ops.render.render(write_still=True)
print('LEGACY_RENDER='+scene.render.filepath)

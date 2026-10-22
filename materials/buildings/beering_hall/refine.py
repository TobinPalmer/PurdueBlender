import bpy,sys,os,math
from mathutils import Vector
R=os.path.abspath('.');sys.path.insert(0,os.path.join(R,'materials'));import pbr_upgrade as pbr
c=bpy.data.collections['Asset_beering_hall']
for mn in ['Beering_Purdue_Red_Brick','Beering_Plaza_Brick_Pavers']:pbr.upgrade_brick(bpy.data.materials[mn],tint=(1,.85,.72,1),tile_m=1.4,texture_set='red_brick')
for o in c.all_objects:
 if o.type=='MESH' and any(m and m.name in ['Beering_Purdue_Red_Brick','Beering_Plaza_Brick_Pavers'] for m in o.data.materials):pbr.metric_uv(o,1.4)
s=bpy.context.scene;cam=s.camera;cam.location=(-116,-124,53);cam.rotation_euler=(Vector((0,0,12))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=47
s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.12
bpy.data.objects['Beering_Review_Sun'].data.energy=1.7
s.view_settings.exposure=-.7
pbr.pack_textures();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.render.filepath=os.path.join(R,'materials/buildings/beering_hall/hero.png');bpy.ops.render.render(write_still=True)
cam.location=(-50,-42,9);cam.rotation_euler=(Vector((-36,-22,7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=54
s.render.filepath=os.path.join(R,'materials/buildings/beering_hall/closeup.png');bpy.ops.render.render(write_still=True)

import bpy,os,math
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); p=os.path.join(root,'modular','buildings','massing_yue_kong_pao_hall_a3cb766.blend'); bpy.ops.wm.open_mainfile(filepath=p)
s=bpy.context.scene; col=bpy.data.collections['Asset_massing_yue_kong_pao_hall_a3cb766']; w=s.world or bpy.data.worlds.new('PAO grade world'); s.world=w; w.use_nodes=True; w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.3,.38,.49,1); w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.4
ld=bpy.data.lights.new('Audit Sun','SUN'); lo=bpy.data.objects.new('Audit Sun',ld); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(28),0,math.radians(-24)); ld.energy=1.25
def render(label,loc,target):
 data=bpy.data.cameras.new('Grade '+label); cam=bpy.data.objects.new('Grade '+label,data); s.collection.objects.link(cam); cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); data.lens=45; s.camera=cam; s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=1100; s.render.resolution_y=800; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.render.filepath=os.path.join(os.path.dirname(__file__),f'independent_grade_r1_{label}.png'); s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'; bpy.ops.render.render(write_still=True); bpy.data.objects.remove(cam,do_unlink=True); bpy.data.cameras.remove(data)
render('north_oblique',(115,-470,36),(61,-538,8))
render('west_oblique',(-50,-545,30),(60,-538,8))
print('GRADED_VIEWS',s.render.filepath)

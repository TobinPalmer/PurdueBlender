import bpy,os,json
from mathutils import Vector
OUT=os.path.dirname(__file__); col=bpy.data.collections['Asset_rawls_hall']
# Render-only inspection settings, not saved.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.new('ReviewWorld');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.8,1,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
ld=bpy.data.lights.new('ReviewSun','SUN');ld.energy=2.5;lo=bpy.data.objects.new('ReviewSun',ld);s.collection.objects.link(lo);lo.rotation_euler=(.35,-.45,-.4)
cam=bpy.data.objects.new('ReviewCam',bpy.data.cameras.new('ReviewCam'));s.collection.objects.link(cam);s.camera=cam
def render(n,p,t,ortho=None):
 cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.ortho_scale=ortho or 50;cam.data.lens=25;s.render.filepath=os.path.join(OUT,n+'.png');bpy.ops.render.render(write_still=True)
render('exterior',(75,70,55),(7,0,10))
for o in list(bpy.data.objects):
 if o and not o.name.startswith('RAWL_2026_') and o.type=='MESH':o.hide_render=True
render('interior_plan',(6,0,85),(6,0,0),95)
render('classroom',(30,4,3.4),(32,-6,1))
json.dump({'export_collection':col.name,'objects':len(col.all_objects),'added_objects':len([o for o in col.all_objects if o.name.startswith('RAWL_2026_')]),'missing_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]},open(os.path.join(OUT,'checks.json'),'w'),indent=2)

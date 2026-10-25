import bpy,os,json,hashlib
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","purdue_memorial_union.blend")
OUT=os.path.join(ROOT,"audit","purdue_memorial_union_refine","south_refine_preview_r3.png")
bpy.ops.wm.open_mainfile(filepath=ASSET); scene=bpy.context.scene; col=bpy.data.collections['Asset_purdue_memorial_union']
def point(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('PMU_R3_ReviewCamera');cam=bpy.data.objects.new('PMU_R3_ReviewCamera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=130
cam.location=(0,-155,35);point(cam,(0,-40,13))
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=48;scene.render.resolution_x=1500;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=OUT;scene.render.film_transparent=False
world=scene.world or bpy.data.worlds.new('PMU_R3_ReviewWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.055,.075,.11,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
def area(n,loc,power,size,color):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);scene.collection.objects.link(o);o.location=loc;point(o,(0,-42,10))
area('PMU_R3_Key',(-45,-100,85),2600,65,(1,.84,.68));area('PMU_R3_Fill',(48,-75,42),1600,52,(.68,.79,1));area('PMU_R3_Front',(0,-115,12),850,48,(1,.91,.78));scene.view_settings.view_transform='AgX'
bpy.ops.render.render(write_still=True)
detail=os.path.join(ROOT,'audit','purdue_memorial_union_refine','south_facade_detail_r3.png');cam.location=(10.25,-120,22);point(cam,(10.25,-45,11));cd.ortho_scale=29;scene.render.resolution_x=1300;scene.render.resolution_y=1200;scene.render.filepath=detail;bpy.ops.render.render(write_still=True)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
print(json.dumps({'asset_sha256':sha(ASSET),'preview':OUT,'preview_sha256':sha(OUT),'detail':detail,'detail_sha256':sha(detail)},indent=2))

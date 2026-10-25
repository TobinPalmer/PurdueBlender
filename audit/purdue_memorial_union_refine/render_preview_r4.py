import bpy,os,hashlib,json
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap";ASSET=os.path.join(ROOT,"modular","buildings","purdue_memorial_union.blend");OUT=os.path.join(ROOT,"audit","purdue_memorial_union_refine")
bpy.ops.wm.open_mainfile(filepath=ASSET);scene=bpy.context.scene
def point(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('PMU_R4_ReviewCamera');cam=bpy.data.objects.new('PMU_R4_ReviewCamera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=145
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=40;scene.render.resolution_x=1450;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.view_settings.view_transform='AgX'
world=scene.world or bpy.data.worlds.new('PMU_R4_ReviewWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.055,.075,.11,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
def area(n,loc,power,size,color,target=(0,-35,12)):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);scene.collection.objects.link(o);o.location=loc;point(o,target)
area('PMU_R4_Key',(-55,-100,90),2600,65,(1,.84,.68));area('PMU_R4_Fill',(65,-70,55),1800,55,(.72,.82,1));area('PMU_R4_Rim',(0,65,85),1700,60,(1,.9,.78));area('PMU_R4_Front',(0,-115,12),850,48,(1,.91,.78))
def render(name,loc,target,scale,size=(1450,1000)):
 cam.location=loc;point(cam,target);cd.ortho_scale=scale;scene.render.resolution_x=size[0];scene.render.resolution_y=size[1];scene.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
render('south_refine_preview_r4',(0,-165,48),(0,-5,12),145)
render('south_facade_detail_r4',(10.25,-115,23),(10.25,-45,12),31,(1300,1150))
render('courtyard_roof_detail_r4',(85,-130,70),(5,10,14),115)
render('roof_r4',(0,-20,220),(0,0,10),145)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
print(json.dumps({'asset_sha256':sha(ASSET),'renders':{n:sha(os.path.join(OUT,n+'.png')) for n in ('south_refine_preview_r4','south_facade_detail_r4','courtyard_roof_detail_r4','roof_r4')}},indent=2))

import bpy, os, json, hashlib
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","purdue_memorial_union.blend")
OUT=os.path.join(ROOT,"audit","purdue_memorial_union_refine","south_refine_preview_r2.png")
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; col=bpy.data.collections["Asset_purdue_memorial_union"]
def point(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new("PMU_R2_ReviewCamera"); cam=bpy.data.objects.new("PMU_R2_ReviewCamera",cam_data); scene.collection.objects.link(cam)
cam.location=(0,-155,42); point(cam,(0,-40,13)); cam_data.type='ORTHO'; cam_data.ortho_scale=130; scene.camera=cam
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=48
scene.render.resolution_x=1500; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=OUT; scene.render.film_transparent=False
world=scene.world or bpy.data.worlds.new("PMUR2ReviewWorld"); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.055,0.075,0.11,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
def area(name,loc,power,size,color):
 d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color
 o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; point(o,(0,-42,10))
area('PMUR2_Key',(-45,-100,85),4000,65,(1.0,.84,.68)); area('PMUR2_Fill',(48,-75,42),2400,52,(.68,.79,1.0)); area('PMUR2_Front',(0,-115,12),1200,48,(1.0,.91,.78))
scene.view_settings.view_transform='AgX'; bpy.ops.render.render(write_still=True)
detail=os.path.join(ROOT,"audit","purdue_memorial_union_refine","south_facade_detail_r2.png")
cam.location=(10.25,-120,24); point(cam,(10.25,-45,11)); cam_data.ortho_scale=29
scene.render.resolution_x=1300; scene.render.resolution_y=1200; scene.render.filepath=detail; bpy.ops.render.render(write_still=True)
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
print(json.dumps({"asset_sha256":sha(ASSET),"south_preview":OUT,"south_preview_sha256":sha(OUT),"detail_preview":detail,"detail_preview_sha256":sha(detail)},indent=2))

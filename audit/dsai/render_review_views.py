import bpy, math, os, json, hashlib
from mathutils import Vector
path=os.path.abspath('modular/buildings/massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend')
bpy.ops.wm.open_mainfile(filepath=path)
coll=bpy.data.collections['Asset_massing_hall_of_data_science_and_ai_dsai_c8a41cc']
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=0
scene.world=bpy.data.worlds.new('DSAI audit world'); scene.world.use_nodes=True; scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.29,.34,.43,1); scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.35
# hide exterior for a documented cutaway-style view (no file save): facade, roof, glazing and limestone.
for ob in coll.objects:
    n=ob.name.lower(); mats=' '.join(m.name.lower() for m in ob.data.materials) if ob.type=='MESH' else ''
    if n.startswith('masonry shell face') or any(k in mats for k in ['terracotta clay tile roof','dark bronze roof edge','pale indiana limestone','warm purdue red brick','dark blue reflective glazing']): ob.hide_render=True
sun_data=bpy.data.lights.new('DSAI interior audit area','AREA'); sun=bpy.data.objects.new('DSAI interior audit area',sun_data); scene.collection.objects.link(sun); sun.location=(-90,170,22); sun_data.energy=1800; sun_data.shape='DISK'; sun_data.size=18
cam_data=bpy.data.cameras.new('DSAI interior review camera'); cam=bpy.data.objects.new('DSAI interior review camera',cam_data); scene.collection.objects.link(cam); cam.location=(-112,160,7.5); target=Vector((-98,175,4.4)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=25; scene.camera=cam
scene.render.filepath=os.path.abspath('audit/dsai/dsai_interior_review.png'); bpy.ops.render.render(write_still=True)
# top-down roof/registered-outline comparison; curve is render-only, exact converted polygon vertices.
for ob in coll.objects: ob.hide_render=False
poly=[[-105.1055554921,139.6623759815],[-129.8574812718,169.0494189073],[-121.4517435019,176.1368369213],[-120.862789908,175.4375375711],[-108.9553903955,185.4773717061],[-108.4073444327,184.8266677789],[-99.8583321061,192.0347865176],[-100.4063779495,192.6854352583],[-99.0911738841,193.7943472559],[-104.9188945366,200.713343829],[-92.7954324192,210.9352418796],[-80.9613156624,196.8850626865],[-80.84487848,196.9832351274],[-80.1884533429,196.2038823099],[-80.8545741478,195.5757923119],[-79.2533893944,193.6747304039],[-78.5217985532,194.2251550395],[-77.8674517673,193.4482430816],[-77.9838890426,193.3500148768],[-74.8612960894,189.6426416264],[-70.4974147597,184.4614921191],[-67.7653468293,181.2178707554],[-65.9003974601,179.0036295992],[-69.3947568227,176.0573858697],[-78.0238442771,168.7818303518],[-84.5802652216,176.5660970634],[-89.0315962993,173.120265264],[-84.1441790774,167.3176169374],[-89.9680763739,162.4072078555],[-85.5510120191,157.1629361171],[-86.3760312661,156.4673013859],[-86.8586593405,157.0402674972],[-91.1197817841,153.4475299664],[-90.6760402537,152.8417656594],[-91.3749190937,152.252525881],[-91.8574727992,152.8255473349],[-97.6813538878,147.9150762932],[-96.6997717475,146.7497106381],[-105.1055554921,139.6623759815]]
cu=bpy.data.curves.new('GIS outline comparison','CURVE'); cu.dimensions='3D'; cu.bevel_depth=.10; cu.bevel_resolution=2; sp=cu.splines.new('POLY'); sp.points.add(len(poly)-1)
for i,(x,y) in enumerate(poly): sp.points[i].co=(x,y,13.6,1)
sp.use_cyclic_u=True; outline=bpy.data.objects.new('Render-only GIS outline',cu); scene.collection.objects.link(outline)
mat=bpy.data.materials.new('GIS ring comparison line'); mat.diffuse_color=(.95,.75,.05,1); outline.data.materials.append(mat)
cam.location=(-98,175,150); cam.rotation_euler=(0,0,0); cam.rotation_euler=(Vector((-98,175,10))-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=90
# hide interior pieces for clear top-down roof registration view
for ob in coll.objects:
    if ob.type=='MESH' and any(k in ' '.join(m.name.lower() for m in ob.data.materials) for k in ['wood','concrete','green roof']): ob.hide_render=True
scene.render.filepath=os.path.abspath('audit/dsai/dsai_alignment_review.png'); bpy.ops.render.render(write_still=True)
print('Interior and registered-footprint review renders saved.')

import bpy, math, os, json
from mathutils import Vector
p=os.path.abspath('modular/buildings/massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend'); bpy.ops.wm.open_mainfile(filepath=p)
coll=bpy.data.collections.get('Asset_massing_hall_of_data_science_and_ai_dsai_c8a41cc')
# identify aggregate geometry and validate envelope
verts=[]; meshobjs=[]
for ob in coll.objects:
 if ob.type=='MESH':
  meshobjs.append(ob)
  for v in ob.data.vertices: verts.append(ob.matrix_world@v.co)
mins=[min(v[i] for v in verts) for i in range(3)]; maxs=[max(v[i] for v in verts) for i in range(3)]
print('OBJECTS',len(coll.objects),'MESHES',len(meshobjs),'MATERIALS',len(bpy.data.materials),'VERTS',len(verts),'BOUNDS',mins,maxs)
# Render-only setup, never saved into source asset.
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32
scene.render.resolution_x=1500; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.abspath('audit/dsai/dsai_exterior_review.png')
scene.render.film_transparent=False; scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
world=bpy.data.worlds.new('DSAI review world') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.20,.30,.47,1); world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.25
ld=bpy.data.lights.new('Review sun','SUN'); lo=bpy.data.objects.new('Review sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(27),math.radians(-22),math.radians(-35)); ld.energy=1.4; ld.angle=math.radians(12)
target=Vector((-98,175,6)); camd=bpy.data.cameras.new('Review camera'); cam=bpy.data.objects.new('Review camera',camd); scene.collection.objects.link(cam); cam.location=(-156,105,17); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=97; scene.camera=cam
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath)
with open('audit/dsai/validation.json','w',encoding='utf-8') as f: json.dump({'asset':p,'collection':coll.name,'source_fid':196,'objects':len(coll.objects),'mesh_objects':len(meshobjs),'vertices':len(verts),'world_bounds_m':{'min':mins,'max':maxs},'fresh_reopen':True,'render':'audit/dsai/dsai_exterior_review.png','blender':bpy.app.version_string},f,indent=2)

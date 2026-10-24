import bpy,os,math
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'; OUT=r'C:\Users\Tobin\Documents\Blender\PurdueMap\renders\material_review_next'
FILES=[
('rawls_hall.blend',lambda n:n.startswith('RAWL_') and not any(k in n for k in ['Site_Sidewalk_Apron','Footprint_Reference'])),
('stanley_coulter_hall.blend',lambda n:n.startswith('SC_') and not any(k in n for k in ['Campus_Lawn_Base','Official_GIS_Footprint'])),
('wiley_hall.blend',lambda n:n.startswith(('Wiley |','Common block |','Window recess |','Interior |','Glazing |','Blind |'))),
('winifred_parker_hall.blend',lambda n:n.startswith('Parker_')),
('benjamin_harrison_hall.blend',lambda n:n.startswith('HARR_'))]
for fn,include in FILES:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,fn)); scene=bpy.context.scene
 objs=[o for o in bpy.data.objects if o.type=='MESH' and include(o.name)]
 pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box]
 if not pts: print(fn,'NO FILTERED OBJECTS'); continue
 mn=Vector(tuple(min(p[i] for p in pts) for i in range(3))); mx=Vector(tuple(max(p[i] for p in pts) for i in range(3))); center=(mn+mx)*.5; dims=mx-mn; span=max(dims)
 print(fn,'filtered meshes',len(objs),'bounds',tuple(round(v,2) for v in dims),'center',tuple(round(v,2) for v in center))
 # Review only the building surface group; lights/camera are temporary and never saved.
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
  if o.type=='MESH' and not include(o.name): o.hide_render=True
 camd=bpy.data.cameras.new('Focused Material QA Camera'); cam=bpy.data.objects.new('Focused Material QA Camera',camd); scene.collection.objects.link(cam); cam.location=center+Vector((span*0.9,-span*1.25,span*0.70)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=span*1.2; scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('Material QA World')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.22,0.27,0.34,1); bg.inputs['Strength'].default_value=0.55
 ld=bpy.data.lights.new('Material QA Sun','SUN'); lo=bpy.data.objects.new('Material QA Sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(24),math.radians(-18),math.radians(-35)); ld.energy=2.2; ld.angle=math.radians(12)
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=900; scene.render.resolution_y=650; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,fn.replace('.blend','_focused.png')); scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
 bpy.ops.render.render(write_still=True)

import bpy,os,math
from mathutils import Vector
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
fp=os.path.join(root,'modular','buildings','rawls_hall.blend')
out=os.path.join(root,'renders','material_review_next','rawls_hall_building_focused.png')
bpy.ops.wm.open_mainfile(filepath=fp)
scene=bpy.context.scene
objs=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('RAWL_'): continue
 if any(k in o.name for k in ['Site_Sidewalk','Footprint_Reference']): continue
 c=o.matrix_world.translation
 if abs(c.x-9.5)<90 and abs(c.y+1.8)<80: objs.append(o)
pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box]
mn=Vector(tuple(min(p[i] for p in pts) for i in range(3))); mx=Vector(tuple(max(p[i] for p in pts) for i in range(3))); center=(mn+mx)*.5; dims=mx-mn; span=max(dims)
print('Included',len(objs),'bounds',tuple(round(v,2) for v in dims),'center',tuple(round(v,2) for v in center),flush=True)
for o in bpy.data.objects:
 if o.type=='LIGHT': o.hide_render=True
 if o.type=='MESH' and o not in objs: o.hide_render=True
camd=bpy.data.cameras.new('Focused Material QA Camera'); cam=bpy.data.objects.new('Focused Material QA Camera',camd); scene.collection.objects.link(cam); cam.location=center+Vector((span*.9,-span*1.25,span*.7)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=span*1.22; scene.camera=cam
if not scene.world: scene.world=bpy.data.worlds.new('Material QA World')
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.22,.27,.34,1); bg.inputs['Strength'].default_value=.55
ld=bpy.data.lights.new('Material QA Sun','SUN'); lo=bpy.data.objects.new('Material QA Sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(24),math.radians(-18),math.radians(-35)); ld.energy=2.2; ld.angle=math.radians(12)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1000; scene.render.resolution_y=750; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=out; scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
bpy.ops.render.render(write_still=True)

import bpy, bmesh, math, os
from mathutils import Vector

ASSET = bpy.data.objects['Smalley Center']
OUT = os.path.dirname(os.path.abspath(__file__))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False
scene.render.resolution_percentage = 70
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0.0
world=scene.world
world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Strength'].default_value=0.22

def aim(obj, point):
    obj.rotation_euler = (Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()

def prepare_camera(name, location, target, lens=55):
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam)
    cam.location=location; data.lens=lens; aim(cam,target); scene.camera=cam; return cam

def area(name, location, energy, size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=energy; data.shape='DISK'; data.size=size
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=location; aim(obj,(-807,-40,3)); return obj

area('Smalley preview key',(-840,-70,55),900,32)
area('Smalley preview fill',(-760,-87,42),1100,28)
sun_data=bpy.data.lights.new('Smalley preview daylight','SUN'); sun_data.energy=1.6; sun_data.angle=math.radians(18); sun_data.color=(1.0,0.94,0.85)
sun=bpy.data.objects.new('Smalley preview daylight',sun_data); scene.collection.objects.link(sun); sun.location=(-835,-75,45); aim(sun,(-807,-40,0))
ground_mat=bpy.data.materials.new('Smalley preview ground'); ground_mat.diffuse_color=(0.20,0.23,0.20,1); ground_mat.use_nodes=True
bsdf=next(n for n in ground_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bsdf.inputs['Base Color'].default_value=(0.20,0.23,0.20,1); bsdf.inputs['Roughness'].default_value=1.0
bpy.ops.mesh.primitive_plane_add(size=160,location=(-808,-40,-0.09)); ground=bpy.context.object; ground.name='Preview-only ground'; ground.data.materials.append(ground_mat)
ASSET.hide_render=False
target=Vector((-808.4,-40.0,3.2))
cam=prepare_camera('Smalley exterior camera',(-755,-87,37),target,55)
scene.render.filepath=os.path.join(OUT,'preview_exterior.png')
bpy.ops.render.render(write_still=True)

# Render a separate roof-open cutaway without altering the saved building library.
cut=ASSET.copy(); cut.data=ASSET.data.copy(); cut.name='Smalley Center interior review cutaway'; scene.collection.objects.link(cut)
bm=bmesh.new(); bm.from_mesh(cut.data)
roof_index=next((i for i,m in enumerate(cut.data.materials) if m and m.name.endswith('_Roof')),None)
if roof_index is not None:
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==roof_index],context='FACES')
bm.to_mesh(cut.data); bm.free(); cut.data.update()
ASSET.hide_render=True; cut.hide_render=False
cam.location=(-765,-66,55); aim(cam,target); cam.data.lens=40
scene.render.filepath=os.path.join(OUT,'preview_interior_cutaway.png')
bpy.ops.render.render(write_still=True)

# Ground-floor view with the second-floor slab removed for inspection.
ground_cut=ASSET.copy(); ground_cut.data=ASSET.data.copy(); ground_cut.name='Smalley Center ground-floor review cutaway'; scene.collection.objects.link(ground_cut)
bm=bmesh.new(); bm.from_mesh(ground_cut.data)
floor_index=next((i for i,m in enumerate(ground_cut.data.materials) if m and m.name.endswith('_Interior_Floor')),None)
partition_index=next((i for i,m in enumerate(ground_cut.data.materials) if m and m.name.endswith('_Interior_Partition')),None)
roof_index=next((i for i,m in enumerate(ground_cut.data.materials) if m and m.name.endswith('_Roof')),None)
wood_index=next((i for i,m in enumerate(ground_cut.data.materials) if m and m.name.endswith('_Interior_Wood')),None)
metal_index=next((i for i,m in enumerate(ground_cut.data.materials) if m and m.name.endswith('_Metal')),None)
upper_detail={i for i in (partition_index,wood_index,metal_index) if i is not None}
remove=[]
for f in bm.faces:
    z=f.calc_center_median().z
    if (roof_index is not None and f.material_index==roof_index) or (floor_index is not None and f.material_index==floor_index and z>3.0) or (f.material_index in upper_detail and z>3.0): remove.append(f)
if remove: bmesh.ops.delete(bm,geom=remove,context='FACES')
bm.to_mesh(ground_cut.data); bm.free(); ground_cut.data.update()
ground_cut.hide_render=False; cut.hide_render=True
cam.location=(-765,-66,42); aim(cam,target); cam.data.lens=40
scene.render.filepath=os.path.join(OUT,'preview_first_floor_cutaway.png')
bpy.ops.render.render(write_still=True)

# An approach view shows the west-facing, address-side doorway hypothesis separately.
ASSET.hide_render=False; ground_cut.hide_render=True
cam.location=(-862,-42,10); aim(cam,(-808,-40,2.4)); cam.data.lens=52
scene.render.filepath=os.path.join(OUT,'preview_entry.png')
bpy.ops.render.render(write_still=True)

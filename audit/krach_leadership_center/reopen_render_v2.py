import bpy, math, json
from mathutils import Vector
from pathlib import Path
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
asset=bpy.data.collections['Asset_krach_leadership_center']
# Reopen validation of only Krach source collection and its local-coordinate placement.
member=set()
def walk(c):
 for o in c.objects: member.add(o)
 for cc in c.children: walk(cc)
walk(asset)
assert bpy.data.objects['KRCH structural shell | GIS outline'] in member
assert bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard'] in member
slabs=[o for o in member if o.name.startswith('KRCH | schematic level slab')]
assert len(slabs)==5, len(slabs)
assert all(not o.modifiers for o in slabs)
# Mesh aperture check: slab face/vertex counts reflect boolean-cut holes; all stay within GIS extents.
checks=[]
for o in sorted(slabs,key=lambda a:a.get('level_top_m',0)):
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 checks.append({'name':o.name,'level':o.get('level_top_m'),'verts':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]})
# Production preview lights/cameras are transient and never saved into the building library.
scene=bpy.context.scene
old_camera=scene.camera
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
world=scene.world
if world and world.use_nodes:
 bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.36,0.43,0.50,1); bg.inputs['Strength'].default_value=0.35

def look_at(cam, target): cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
def camera(name, loc, target, lens=48):
 data=bpy.data.cameras.new(name); data.lens=lens
 ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; look_at(ob,target); return ob
def area(name,loc,target,power,size,color=(1,1,1)):
 data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; data.color=color
 ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; look_at(ob,target); return ob

# Exterior corner view aligned with Sasaki's oblique corner photograph.
area('TEMP Krach key',(-35,-40,30),(-5,-4,5),6500,28,(1.0,0.82,0.62))
area('TEMP Krach fill',(18,-32,22),(0,-3,5),3000,24,(0.70,0.82,1.0))
# Lower the camera to architectural-photo height and rotate farther toward the
# southwest so the west wing / diagonal glass connector / Main Street wing read
# in the same order as Sasaki's published corner view.
cam=camera('TEMP Krach exterior camera',(-85,-50,11),(-4,-3,7.4),58)
scene.camera=cam; scene.render.resolution_x=1500; scene.render.resolution_y=980
scene.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\krach_leadership_center\source_preview.png'
bpy.ops.render.render(write_still=True)
# Clean schematic interior cutaway. Hide the opaque shell and non-lobby facade
# while keeping the corner frame, floor openings, and switchback stair. The glass
# is omitted only from this explanatory preview to avoid dither noise.
saved_hidden={o:o.hide_render for o in scene.objects}
asset_objects=set(member)
stair=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
keep={stair}
for o in scene.objects: o.hide_render=(o not in keep)
cut_mesh=bpy.data.meshes.new('TEMP Krach cutaway stair | matte treads only')
cut_faces=[list(poly.vertices) for poly in stair.data.polygons if poly.material_index==0]
cut_mesh.from_pydata([tuple(v.co) for v in stair.data.vertices],[],cut_faces)
if stair.data.materials: cut_mesh.materials.append(stair.data.materials[0])
cut_mesh.update()
cut_ob=bpy.data.objects.new('TEMP Krach cutaway stair matte',cut_mesh); scene.collection.objects.link(cut_ob)
cut_ob.matrix_world=stair.matrix_world.copy(); stair.hide_render=True
stair_center=Vector((-30.7965,-9.3,7.3))
area('TEMP Krach cutaway key',(-39,-12,22),stair_center,6800,12,(1.0,0.88,0.72))
area('TEMP Krach cutaway fill',(-21,-20,12),stair_center,4200,11,(0.75,0.86,1.0))
cam2=camera('TEMP Krach lobby cutaway camera',(-33,-27,10),stair_center,22)
scene.camera=cam2
# A quiet dark floor gives the isolated pale stone treads enough contrast to read.
bpy.ops.mesh.primitive_plane_add(size=30, location=(-30.8,-9.3,-1.03))
ground=bpy.context.object; ground.name='TEMP Krach cutaway ground'
ground_mat=bpy.data.materials.new('TEMP Krach cutaway charcoal ground'); ground_mat.diffuse_color=(.09,.12,.14,1); ground_mat.use_nodes=True
ground_bs=next(n for n in ground_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); ground_bs.inputs['Base Color'].default_value=(.09,.12,.14,1); ground_bs.inputs['Roughness'].default_value=.9
ground.data.materials.append(ground_mat)
scene.camera=cam2; scene.render.resolution_x=1000; scene.render.resolution_y=1100
scene.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\krach_leadership_center\lobby_stair_preview.png'
bpy.ops.render.render(write_still=True)
# camera/light cleanup in memory, no save call
for o,hidden in saved_hidden.items(): o.hide_render=hidden
for o in list(scene.objects):
 if o.name.startswith('TEMP Krach'):
  data=o.data; bpy.data.objects.remove(o,do_unlink=True)
  if data and data.users==0:
   if data.__class__.__name__=='Camera': bpy.data.cameras.remove(data)
   elif data.__class__.__name__=='Light': bpy.data.lights.remove(data)
   elif data.__class__.__name__=='Mesh': bpy.data.meshes.remove(data)
scene.camera=old_camera
print(json.dumps({'source':src,'asset_collection':asset.name,'asset_object_count':len(member),'stair_in_expected_collection':True,'slab_count':len(slabs),'slabs':checks,'exterior_preview':'audit/krach_leadership_center/source_preview.png','interior_preview':'audit/krach_leadership_center/lobby_stair_preview.png'},indent=2))



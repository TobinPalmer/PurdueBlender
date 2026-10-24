import bpy, math, os, json
from mathutils import Vector
ROOT=os.path.abspath('.')
ASSET=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
OUT=os.path.join(ROOT,'audit','rework_batch_a')
bpy.ops.wm.open_mainfile(filepath=ASSET)
COL=bpy.data.collections.get('Asset_materials_science_and_electrical_engineering_msee')
assert COL and len(COL.all_objects)>1000
# Evidence-backed brick facade based on Purdue ECN's MSEE exterior photograph.
fac=bpy.data.materials['materials_science_and_electrical_engineering_msee_facade']
fac.diffuse_color=(0.24,0.085,0.055,1)
fac.use_nodes=True
nt=fac.node_tree
nodes=nt.nodes; links=nt.links
bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(0.24,0.085,0.055,1)
bs.inputs['Roughness'].default_value=0.84
bs.inputs['Metallic'].default_value=0.0
# Stable meter-scale running bond; GIS wall mesh stays untouched.
g=next((n for n in nodes if n.type=='NEW_GEOMETRY'),None)
if g is None:
 g=nodes.new('ShaderNodeNewGeometry')
g.location=(-800,200)
bt=next((n for n in nodes if n.type=='TEX_BRICK'),None)
if bt is None: bt=nodes.new('ShaderNodeTexBrick')
bt.name='MSEE running-bond brick (photo-derived appearance)'; bt.label='Brick facade, meter-scale'; bt.location=(-530,220)
bt.inputs['Scale'].default_value=1.65
bt.inputs['Color1'].default_value=(0.22,0.065,0.038,1)
bt.inputs['Color2'].default_value=(0.31,0.105,0.064,1)
bt.inputs['Mortar'].default_value=(0.095,0.082,0.071,1)
bt.inputs['Mortar Size'].default_value=0.012
bt.inputs['Mortar Smooth'].default_value=0.015
bt.inputs['Brick Width'].default_value=0.5
bt.inputs['Row Height'].default_value=0.24
# replace only the old color source feeding the facade BSDF
for lk in list(links):
 if lk.to_node==bs and lk.to_socket==bs.inputs['Base Color']:
  links.remove(lk)
links.new(g.outputs['Position'],bt.inputs['Vector'])
links.new(bt.outputs['Color'],bs.inputs['Base Color'])
# Subtle brick relief: retain procedural variation but combine with brick joints.
bump=next((n for n in nodes if n.type=='BUMP'),None)
if bump:
 bump.inputs['Strength'].default_value=0.16
 bump.inputs['Distance'].default_value=0.004
 for lk in list(links):
  if lk.to_node==bump and lk.to_socket==bump.inputs['Height']:
   links.remove(lk)
 links.new(bt.outputs['Fac'],bump.inputs['Height'])
# Atrium glass becomes transparent enough to reveal the documented open two-storey space.
mat=bpy.data.materials.get('R5_MSEE_brown_atrium_glass') or bpy.data.materials.new('R5_MSEE_brown_atrium_glass')
mat.diffuse_color=(0.25,0.43,0.48,0.34); mat.use_nodes=True
mat.surface_render_method='DITHERED'
mat.node_tree.nodes.clear()
out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial'); out.location=(420,0)
pr=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled'); pr.location=(60,90)
pr.inputs['Base Color'].default_value=(0.22,0.43,0.49,1)
pr.inputs['Roughness'].default_value=0.17
pr.inputs['Metallic'].default_value=0.16
pr.inputs['Transmission Weight'].default_value=0.24
tr=mat.node_tree.nodes.new('ShaderNodeBsdfTransparent'); tr.location=(60,-120)
mix=mat.node_tree.nodes.new('ShaderNodeMixShader'); mix.location=(260,0); mix.inputs[0].default_value=0.18
mat.node_tree.links.new(pr.outputs['BSDF'],mix.inputs[1]); mat.node_tree.links.new(tr.outputs['BSDF'],mix.inputs[2]); mat.node_tree.links.new(mix.outputs['Shader'],out.inputs['Surface'])
screen=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']
screen.data.materials.clear(); screen.data.materials.append(mat)
# A restrained, photo-supported arched entrance insert, aligned to the existing angled atrium facade.
# Screen endpoints yield tangent (0.627,-0.779); outward normal points away from building center.
t=Vector((0.627,-0.779,0)).normalized(); n=Vector((-t.y,t.x,0))
# use actual midpoint derived from the screen's mesh bounds
verts=[screen.matrix_world@v.co for v in screen.data.vertices]
lo=Vector((min(v.x for v in verts),min(v.y for v in verts),min(v.z for v in verts)))
hi=Vector((max(v.x for v in verts),max(v.y for v in verts),max(v.z for v in verts)))
# Center of the diagonal plane is the mean of the four unique corners (not its AABB center by accident).
center=sum((screen.matrix_world@v.co for v in screen.data.vertices),Vector())/len(screen.data.vertices)
# Slight exterior offset avoids z-fighting with the glass plane.
center += n*0.10
angle=math.atan2(t.y,t.x)
metal=bpy.data.materials.get('materials_science_and_electrical_engineering_msee_painted_metal')
wood=bpy.data.materials.get('R2_MSEE_interior_wood')
# helper: cube axes local X along facade, local Y normal, Z vertical
def cube(name, loc, dims, material, bevel=0.0):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
 o=bpy.context.object; o.name=name; o.dimensions=dims; o.rotation_euler[2]=angle
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if material:o.data.materials.clear();o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Soft edge highlight','BEVEL'); mod.width=bevel; mod.segments=2
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 for c in list(o.users_collection): c.objects.unlink(o)
 COL.objects.link(o)
 return o
# Door assembly proportions are an informed estimate, not a surveyed dimension.
width=6.2; radius=width/2; spring=3.05; zbase=0.52; depth=0.14
# Two dark, glazed door leaves behind a graphite frame.
door_mat=bpy.data.materials.get('R5_MSEE_entry_door_glass') or bpy.data.materials.new('R5_MSEE_entry_door_glass')
door_mat.diffuse_color=(0.10,0.22,0.26,0.82); door_mat.use_nodes=True
p=next(x for x in door_mat.node_tree.nodes if x.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(0.10,0.22,0.26,1); p.inputs['Roughness'].default_value=0.22; p.inputs['Metallic'].default_value=0.18
# Since the background is itself glazed, the door sheets remain tinted and only subtly translucent.
for side in (-1,1):
 x=side*width*0.25
 loc=center + t*x + n*0.10 + Vector((0,0,zbase+spring/2))
 cube(f'R5_MSEE_entry_door_leaf_{side}',loc,(width*0.49,depth,spring),door_mat,0.035)
# metal jambs, center stile, and horizontal transom
frame=(0.18,0.20,0.19,1)
frame_mat=bpy.data.materials.get('R5_MSEE_entry_frame') or bpy.data.materials.new('R5_MSEE_entry_frame')
frame_mat.diffuse_color=frame; frame_mat.use_nodes=True
fp=next(x for x in frame_mat.node_tree.nodes if x.type=='BSDF_PRINCIPLED'); fp.inputs['Base Color'].default_value=frame; fp.inputs['Metallic'].default_value=.55; fp.inputs['Roughness'].default_value=.3
for x in (-radius,radius,0):
 cube(f'R5_MSEE_entry_frame_vertical_{x:+.2f}',center+t*x+n*.23+Vector((0,0,zbase+spring/2)),(.09,depth,.09+spring),frame_mat,.018)
cube('R5_MSEE_entry_transom',center+n*.23+Vector((0,0,zbase+spring)),(width,depth,.11),frame_mat,.02)
# semicircular head plus radial fanlight bars, matching the arched doorway visible in Purdue's photo.
curve=bpy.data.curves.new('R5_MSEE_arch_head','CURVE'); curve.dimensions='3D'; curve.resolution_u=1; curve.bevel_depth=.055; curve.bevel_resolution=3
spl=curve.splines.new('POLY'); count=48; spl.points.add(count-1)
for i,pt in enumerate(spl.points):
 a=math.pi - math.pi*i/(count-1); x=radius*math.cos(a); z=zbase+spring+radius*math.sin(a)
 q=center+t*x+n*.24+Vector((0,0,z)); pt.co=(q.x,q.y,q.z,1)
arch=bpy.data.objects.new('R5_MSEE_entry_arched_head',curve); COL.objects.link(arch); arch.data.materials.append(frame_mat)
# radial spokes rise from the spring line into the fanlight.
for deg in (30,60,90,120,150):
 a=math.radians(deg); x=radius*math.cos(a); z=zbase+spring+radius*math.sin(a)
 p0=center+t*0+n*.245+Vector((0,0,zbase+spring))
 p1=center+t*x+n*.245+Vector((0,0,z))
 cdata=bpy.data.curves.new(f'R5_MSEE_fanlight_spoke_{deg}','CURVE'); cdata.dimensions='3D'; cdata.bevel_depth=.028; cdata.bevel_resolution=2
 s=cdata.splines.new('POLY'); s.points.add(1); s.points[0].co=(p0.x,p0.y,p0.z,1); s.points[1].co=(p1.x,p1.y,p1.z,1)
 obj=bpy.data.objects.new(f'R5_MSEE_fanlight_spoke_{deg}',cdata); COL.objects.link(obj); obj.data.materials.append(frame_mat)
# Camera render uses the existing saved preview camera, but file remains the modular asset.
scene=bpy.context.scene
scene.render.image_settings.file_format='PNG'; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision5_preview.png')
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.render.render(write_still=True)
# save after rendering too, ensuring packed/stable render settings and asset state.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('R5 saved',len(COL.all_objects),'objects',scene.render.filepath)

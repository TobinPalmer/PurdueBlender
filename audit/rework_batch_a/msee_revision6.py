import bpy, math, os, json
from mathutils import Vector

ROOT=os.path.abspath('.')
ASSET=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
OUT=os.path.join(ROOT,'audit','rework_batch_a')
bpy.ops.wm.open_mainfile(filepath=ASSET)
COL=bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee']
screen=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']
shell=bpy.data.objects['materials_science_and_electrical_engineering_msee_official_GIS_shell']

# Replace only the prior MSEE entry insert. Its elevated R5 origin put the fanlight
# into the upper window band; R6 anchors the arch and paired doors at grade.
for o in list(COL.all_objects):
    if o.name.startswith(('R5_MSEE_entry_','R6_MSEE_entry_','R5_MSEE_fanlight_spoke_','R6_MSEE_fanlight_spoke_')) or o.name in ('R5_MSEE_arch_head','R6_MSEE_arch_head'):
        bpy.data.objects.remove(o,do_unlink=True)

points=[screen.matrix_world@v.co for v in screen.data.vertices]
screen_center=sum(points,Vector())/len(points)
t=Vector((.627,-.779,0)).normalized()
n=Vector((-t.y,t.x,0))
outward=-n
angle=math.atan2(t.y,t.x)
base_z=min(v.z for v in points)+0.08
entry_center=Vector((screen_center.x,screen_center.y,base_z))+outward*0.20

# Tone down the window tint and make its surface read as glass rather than opaque cyan panels.
window_mat=bpy.data.materials['materials_science_and_electrical_engineering_msee_glazing']
window_mat.diffuse_color=(.12,.19,.21,.72)
window_mat.use_nodes=True
wn=window_mat.node_tree.nodes; wl=window_mat.node_tree.links
wp=next((x for x in wn if x.type=='BSDF_PRINCIPLED'),None)
if wp:
    wp.inputs['Base Color'].default_value=(.12,.19,.21,1)
    wp.inputs['Roughness'].default_value=.21
    wp.inputs['Metallic'].default_value=.12
    if 'Transmission Weight' in wp.inputs: wp.inputs['Transmission Weight'].default_value=.10
# The source photo supports dark, reflective glazing but not a specific tint or reflectance.

# Atrium screen becomes a subdued neutral blue-gray; reflection remains visible but interior is legible.
glass=bpy.data.materials['R5_MSEE_brown_atrium_glass']
glass.diffuse_color=(.16,.24,.25,.58)
glass.use_nodes=True
gn=glass.node_tree.nodes; gl=glass.node_tree.links
gp=next(x for x in gn if x.type=='BSDF_PRINCIPLED')
gp.inputs['Base Color'].default_value=(.15,.23,.25,1)
gp.inputs['Roughness'].default_value=.20
gp.inputs['Metallic'].default_value=.10
if 'Transmission Weight' in gp.inputs: gp.inputs['Transmission Weight'].default_value=.12
mix=next((x for x in gn if x.type=='MIX_SHADER'),None)
if mix: mix.inputs[0].default_value=.42

# The ECN exterior photo shows the highest course as much smaller openings than
# the repeated lower bays. Reduce the four top-course assemblies uniformly.
for o in list(COL.all_objects):
    if o.get('msee_r6_top_course_compact'): continue
    name=o.name
    if not name.startswith(('MSEE_window_','MSEE_mullion_','MSEE_sill_')): continue
    parts=name.split('_')
    if len(parts)<5 or parts[3]!='3' or o.type!='MESH': continue
    verts=o.data.vertices
    if not verts: continue
    lo=[min(v.co[i] for v in verts) for i in range(3)]
    hi=[max(v.co[i] for v in verts) for i in range(3)]
    mid=[(lo[i]+hi[i])*.5 for i in range(3)]
    is_sill=name.startswith('MSEE_sill_')
    horizontal=.78 if is_sill else .80
    vertical=1.0 if is_sill else .48
    for v in verts:
        v.co.x=mid[0]+(v.co.x-mid[0])*horizontal
        v.co.y=mid[1]+(v.co.y-mid[1])*horizontal
        v.co.z=mid[2]+(v.co.z-mid[2])*vertical
    o['msee_r6_top_course_compact']=True

frame_mat=bpy.data.materials.get('R6_MSEE_entry_frame') or bpy.data.materials.new('R6_MSEE_entry_frame')
frame_mat.diffuse_color=(.12,.14,.14,1); frame_mat.use_nodes=True
fp=next(x for x in frame_mat.node_tree.nodes if x.type=='BSDF_PRINCIPLED')
fp.inputs['Base Color'].default_value=(.12,.14,.14,1); fp.inputs['Metallic'].default_value=.42; fp.inputs['Roughness'].default_value=.34

door_mat=bpy.data.materials.get('R6_MSEE_entry_door_glass') or bpy.data.materials.new('R6_MSEE_entry_door_glass')
door_mat.diffuse_color=(.07,.10,.10,.55); door_mat.use_nodes=True
door_mat.node_tree.nodes.clear()
dn=door_mat.node_tree.nodes; dl=door_mat.node_tree.links
dp=dn.new('ShaderNodeBsdfPrincipled'); dp.inputs['Base Color'].default_value=(.12,.16,.16,1)
dp.inputs['Roughness'].default_value=.20; dp.inputs['Metallic'].default_value=.12
if 'Transmission Weight' in dp.inputs: dp.inputs['Transmission Weight'].default_value=.08
dtr=dn.new('ShaderNodeBsdfTransparent')
dmix=dn.new('ShaderNodeMixShader'); dmix.inputs[0].default_value=.12
dout=dn.new('ShaderNodeOutputMaterial')
dl.new(dp.outputs['BSDF'],dmix.inputs[1]); dl.new(dtr.outputs['BSDF'],dmix.inputs[2]); dl.new(dmix.outputs['Shader'],dout.inputs['Surface'])
door_mat.surface_render_method='DITHERED'

def cube(name,loc,dims,material,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims; o.rotation_euler[2]=angle
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material: o.data.materials.clear(); o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Small edge highlight','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    for c in list(o.users_collection): c.objects.unlink(o)
    COL.objects.link(o)
    return o

# The photo shows a central low door below a fanlight. The overall entry width/height
# are proportional estimates from an oblique archival photo, not measured dimensions.
width=7.4; radius=width/2; spring=2.85; depth=.12
for side in (-1,1):
    x=side*width*.25
    cube(f'R6_MSEE_entry_door_leaf_{side}',entry_center+t*x+outward*.06+Vector((0,0,spring/2)),
         (width*.49,depth,spring),door_mat,.022)

for x in (-radius,0,radius):
    cube(f'R6_MSEE_entry_frame_vertical_{x:+.2f}',entry_center+t*x+outward*.13+Vector((0,0,spring/2)),
         (.085,.15,spring+.06),frame_mat,.012)
cube('R6_MSEE_entry_transom',entry_center+outward*.13+Vector((0,0,spring)),(width,.15,.09),frame_mat,.012)

curve=bpy.data.curves.new('R6_MSEE_arch_head','CURVE'); curve.dimensions='3D'; curve.resolution_u=1
curve.bevel_depth=.045; curve.bevel_resolution=3
spl=curve.splines.new('POLY'); count=64; spl.points.add(count-1)
for i,pt in enumerate(spl.points):
    a=math.pi-math.pi*i/(count-1); x=radius*math.cos(a); z=spring+radius*math.sin(a)
    q=entry_center+t*x+outward*.13+Vector((0,0,z)); pt.co=(q.x,q.y,q.z,1)
arch=bpy.data.objects.new('R6_MSEE_entry_arched_head',curve); COL.objects.link(arch); arch.data.materials.append(frame_mat)
for deg in (30,60,90,120,150):
    a=math.radians(deg); x=radius*math.cos(a); z=spring+radius*math.sin(a)
    p0=entry_center+outward*.14+Vector((0,0,spring)); p1=entry_center+t*x+outward*.14+Vector((0,0,z))
    cdata=bpy.data.curves.new(f'R6_MSEE_fanlight_spoke_{deg}','CURVE'); cdata.dimensions='3D'
    cdata.bevel_depth=.022; cdata.bevel_resolution=2
    s=cdata.splines.new('POLY'); s.points.add(1)
    s.points[0].co=(p0.x,p0.y,p0.z,1); s.points[1].co=(p1.x,p1.y,p1.z,1)
    obj=bpy.data.objects.new(f'R6_MSEE_fanlight_spoke_{deg}',cdata); COL.objects.link(obj); obj.data.materials.append(frame_mat)

# Quiet door hardware gives the pair of leaves scale without inventing signage or text.
handle_mat=frame_mat
for side in (-1,1):
    x=side*.19
    cube(f'R6_MSEE_entry_pull_{side}',entry_center+t*x+outward*.14+Vector((0,0,spring*.46)),(.045,.035,.34),handle_mat,.015)

scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision6_preview.png')
bpy.ops.render.render(write_still=True)
oldcam=scene.camera
loc=Vector((entry_center.x,entry_center.y,base_z))+outward*37+Vector((0,0,7.0))
target=entry_center+Vector((0,0,3.4))
bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.name='TEMP_MSEE_R6_entry_camera'
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=58; scene.camera=cam
scene.render.resolution_x=1300; scene.render.resolution_y=900
scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision6_entry_detail.png')
bpy.ops.render.render(write_still=True)
scene.camera=oldcam; bpy.data.objects.remove(cam,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('MSEE R6 saved; entry base z=',round(base_z,3),'arch top z=',round(base_z+spring+radius,3),'objects=',len(COL.all_objects))

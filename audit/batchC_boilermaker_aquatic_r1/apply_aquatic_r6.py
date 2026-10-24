import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
rig=bpy.data.collections['Preview_Rig']
# Remove only R6 additions if script is re-run.
old=bpy.data.collections.get('AQUA_R6 | exposed natatorium structure and display banners')
if old:
    for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(old)
for o in list(bpy.data.objects):
    if o.name.startswith('AQUA R6 | pool-hall longitudinal interior camera'):
        data=o.data
        bpy.data.objects.remove(o,do_unlink=True)
        if data and data.users==0: bpy.data.cameras.remove(data)
col=bpy.data.collections.new('AQUA_R6 | exposed natatorium structure and display banners')
asset.children.link(col)
# Purdue Athletics/structural-engineer imagery shows a white exposed steel roof-truss interior.
steel=bpy.data.materials.get('AQUA R6 | warm white painted natatorium steel') or bpy.data.materials.new('AQUA R6 | warm white painted natatorium steel')
steel.diffuse_color=(.91,.92,.89,1); steel.use_nodes=True
pbs=steel.node_tree.nodes.get('Principled BSDF'); pbs.inputs['Base Color'].default_value=(.91,.92,.89,1); pbs.inputs['Metallic'].default_value=.04; pbs.inputs['Roughness'].default_value=.64
if 'Emission Color' in pbs.inputs:
    pbs.inputs['Emission Color'].default_value=(.55,.57,.53,1);pbs.inputs['Emission Strength'].default_value=.32
trusses=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | schematic clear-span roof truss')]
for o in trusses:
    o.data.materials.clear(); o.data.materials.append(steel)
    o['r6_evidence']='Exposed painted steel roof-truss character supported qualitatively by Purdue Athletics facility photos and Arsee Engineers project photo; member layout, spacing, sizes and roof elevations remain schematic.'
# The official pool-hall photographs also show bright overhead fixtures. Model restrained linear high-bay luminaires between truss bays.
light_mat=bpy.data.materials.get('AQUA R6 | high-bay light diffuser') or bpy.data.materials.new('AQUA R6 | high-bay light diffuser')
light_mat.diffuse_color=(.92,.88,.73,1);light_mat.use_nodes=True
lp=light_mat.node_tree.nodes.get('Principled BSDF');lp.inputs['Base Color'].default_value=(.92,.88,.73,1);lp.inputs['Roughness'].default_value=.36
if 'Emission Color' in lp.inputs:
    lp.inputs['Emission Color'].default_value=(1.0,.83,.54,1);lp.inputs['Emission Strength'].default_value=1.25
# An understated pair of hanging competition banners conveys the prominent pool-hall branding visible in official facility photographs.
black=bpy.data.materials.get('AQUA R6 | black competition banner fabric') or bpy.data.materials.new('AQUA R6 | black competition banner fabric')
black.diffuse_color=(.018,.021,.026,1); black.use_nodes=True; bp=black.node_tree.nodes.get('Principled BSDF');bp.inputs['Base Color'].default_value=(.018,.021,.026,1);bp.inputs['Roughness'].default_value=.85
banner_gold=bpy.data.materials.get('AQUA R6 | Purdue gold banner lettering') or bpy.data.materials.new('AQUA R6 | Purdue gold banner lettering')
banner_gold.diffuse_color=(.78,.49,.10,1);banner_gold.use_nodes=True; gp=banner_gold.node_tree.nodes.get('Principled BSDF');gp.inputs['Base Color'].default_value=(.78,.49,.10,1);gp.inputs['Metallic'].default_value=.08;gp.inputs['Roughness'].default_value=.52

def cube(name,loc,dims,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o);o.data.materials.append(mat);return o

for row,x in enumerate((-17.0,0.0,17.0),1):
    for bay,y in enumerate((-32.7,-16.35,0.0,16.35,32.7),1):
        lum=cube(f'AQUA R6 | schematic natatorium high-bay luminaire {row}-{bay}',(x,y,8.84),(.95,.62,.12),light_mat)
        lum['r6_evidence']='Overhead lighting is visible in Purdue Athletics facility photography; this repeated fixture layout is an approximate interior presentation detail, not a measured lighting plan.'

def cyl_between(name,a,b,r,mat):
    a=Vector(a);b=Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y')
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);o.data.materials.append(mat);return o
# Two modest suspended wall-facing displays. Their dimensions/locations are visual estimates, not measured.
for i,y in enumerate((-16.4,16.4),1):
    cube(f'AQUA R6 | suspended black Purdue banner {i}',(0,y,8.08),(6.4,.16,1.72),black)
    # suspension rods connect to the roof-truss bottom chord around z=9.2.
    for x in (-2.55,2.55): cyl_between(f'AQUA R6 | banner hanger {i}-{x}',(x,y,9.26),(x,y,8.94),.035,steel)
    txt=bpy.data.curves.new(f'AQUA R6 | PURDUE banner lettering {i}','FONT');txt.body='PURDUE';txt.align_x='CENTER';txt.align_y='CENTER';txt.size=.78;txt.extrude=.008;txt.bevel_depth=.004;txt.bevel_resolution=2
    ob=bpy.data.objects.new(f'AQUA R6 | PURDUE banner lettering {i}',txt); col.objects.link(ob);ob.location=(0,y-.091,8.08);ob.rotation_euler=(math.radians(90),0,0);ob.data.materials.append(banner_gold)
    ob['r6_evidence']='Brand/banner presence is visible in Purdue Athletics facility photographs; copy placement, size and exact number are visual presentation estimates.'
# Purpose-built interior angle from the south pool-deck corner, looking through the competition hall to the opposite end.
cam_data=bpy.data.cameras.new('AQUA R6 | pool-hall longitudinal interior camera');cam=bpy.data.objects.new('AQUA R6 | pool-hall longitudinal interior camera',cam_data);rig.objects.link(cam)
cam.location=(-24,-42,8.5); target=Vector((3,4,4.2));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cam.data.lens=35;cam.data.dof.use_dof=False
cam['r6_note']='Interior presentation camera; camera placement is for visualization only and is not a surveyed viewpoint.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print({'saved':str(ASSET),'new_collection_objects':len(col.objects),'trusses_retreated':len(trusses),'banner_panels':2,'camera':cam.name})

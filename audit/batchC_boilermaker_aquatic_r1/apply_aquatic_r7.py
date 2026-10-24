import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; rig=bpy.data.collections['Preview_Rig']
# Replace R6 display/lighting pass, preserving the source-supported building truss meshes.
for old_name in ('AQUA_R6 | exposed natatorium structure and display banners','AQUA_R7 | integrated natatorium lighting and seating'):
    old=bpy.data.collections.get(old_name)
    if old:
        for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(old)
for o in list(bpy.data.objects):
    if o.name.startswith(('AQUA R6 | pool-hall longitudinal interior camera','AQUA R7 | pool hall integrated interior camera','AQUA R7 | north entry close approach camera')):
        data=o.data;is_camera=o.type=='CAMERA';bpy.data.objects.remove(o,do_unlink=True)
        if data and data.users==0 and is_camera:bpy.data.cameras.remove(data)
col=bpy.data.collections.new('AQUA_R7 | integrated natatorium lighting and seating');asset.children.link(col)
# White-painted structural steel is photo-supported; a slightly quieter finish keeps the roof frames legible without dominating the pool view.
steel=bpy.data.materials.get('AQUA R7 | neutral painted natatorium steel') or bpy.data.materials.new('AQUA R7 | neutral painted natatorium steel')
steel.diffuse_color=(.52,.54,.53,1);steel.use_nodes=True;sp=steel.node_tree.nodes.get('Principled BSDF');sp.inputs['Base Color'].default_value=(.52,.54,.53,1);sp.inputs['Metallic'].default_value=.08;sp.inputs['Roughness'].default_value=.82
if 'Emission Strength' in sp.inputs:sp.inputs['Emission Strength'].default_value=0.0
trusses=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | schematic clear-span roof truss')]
for o in trusses:o.data.materials.clear();o.data.materials.append(steel);o['r7_evidence']='Warm/light painted exposed steel truss character supported by Purdue Athletics and engineer photographs; member sections, spacing and exact shape remain schematic.'
# Photo-supported overhead LED fixtures sit in the clear bays between cross-trusses; their exact positions and spacing are schematic.
light_mat=bpy.data.materials.get('AQUA R7 | restrained warm-white LED diffuser') or bpy.data.materials.new('AQUA R7 | restrained warm-white LED diffuser')
light_mat.diffuse_color=(.90,.86,.72,1);light_mat.use_nodes=True;lp=light_mat.node_tree.nodes.get('Principled BSDF');lp.inputs['Base Color'].default_value=(.90,.86,.72,1);lp.inputs['Roughness'].default_value=.45
if 'Emission Color' in lp.inputs:lp.inputs['Emission Color'].default_value=(.82,.72,.52,1);lp.inputs['Emission Strength'].default_value=.45

def box(name,loc,dims,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);o.data.materials.append(mat);return o
for xi,x in enumerate((-17.0,0.0,17.0),1):
    for yi,y in enumerate((-40.95,-24.55,-8.2,8.2,24.55,40.95),1):
        fixture=box(f'AQUA R7 | LED high-bay fixture {xi}-{yi}',(x,y,8.88),(.82,.42,.10),light_mat)
        fixture['r7_evidence']='Purdue Aquatic Center lighting installer documents replacement LED fixtures above competition and diving pools; count/spacing/size are estimated, not an as-built lighting schedule.'
        ld=bpy.data.lights.new(f'AQUA R7 | integrated overhead LED {xi}-{yi}','AREA');ld.energy=650;ld.shape='RECTANGLE';ld.size=2.8;ld.size_y=1.35;ld.use_shadow=False
        lo=bpy.data.objects.new(f'AQUA R7 | integrated overhead LED {xi}-{yi}',ld);col.objects.link(lo);lo.location=(x,y,8.72);lo.rotation_euler=(0,0,0);lo['r7_evidence']='Representative luminous output aligned to a modeled high-bay housing; exact fixture spacing is schematic.'
# One restrained pair of hanging black/gold Purdue banners; hanger rods meet a roof-truss lower chord.
black=bpy.data.materials.get('AQUA R7 | black banner fabric') or bpy.data.materials.new('AQUA R7 | black banner fabric');black.diffuse_color=(.015,.018,.022,1);black.use_nodes=True;bp=black.node_tree.nodes.get('Principled BSDF');bp.inputs['Base Color'].default_value=(.015,.018,.022,1);bp.inputs['Roughness'].default_value=.9
gold=bpy.data.materials.get('AQUA R7 | Purdue gold display lettering') or bpy.data.materials.new('AQUA R7 | Purdue gold display lettering');gold.diffuse_color=(.72,.43,.09,1);gold.use_nodes=True;gp=gold.node_tree.nodes.get('Principled BSDF');gp.inputs['Base Color'].default_value=(.72,.43,.09,1);gp.inputs['Metallic'].default_value=.05;gp.inputs['Roughness'].default_value=.62
for i,y in enumerate((-16.4,16.4),1):
    box(f'AQUA R7 | suspended Purdue banner {i}',(0,y,8.10),(5.4,.075,1.40),black)
    for x in (-2.15,2.15):
        a=Vector((x,y,9.20));b=Vector((x,y,8.80));d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.022,depth=d.length,location=(a+b)/2);rod=bpy.context.object;rod.name=f'AQUA R7 | banner hanger {i}';rod.rotation_mode='QUATERNION';rod.rotation_quaternion=d.to_track_quat('Z','Y')
        for c in list(rod.users_collection):c.objects.unlink(rod)
        col.objects.link(rod);rod.data.materials.append(steel)
    for face,sign in enumerate((-1,1),1):
        txt=bpy.data.curves.new(f'AQUA R7 | Purdue banner text {i}-{face}','FONT');txt.body='PURDUE';txt.align_x='CENTER';txt.align_y='CENTER';txt.size=.64;txt.extrude=.004;txt.bevel_depth=.002;txt.bevel_resolution=2
        ob=bpy.data.objects.new(f'AQUA R7 | Purdue banner text {i}-{face}',txt);col.objects.link(ob);ob.location=(0,y+sign*.041,8.10);ob.rotation_euler=(math.radians(-90*sign),0,0);ob.data.materials.append(gold)
        ob['r7_evidence']='Purdue Athletics facility photos show black/gold suspended pool-hall branding. The size and exact suspended position are presentation estimates.'
# Existing Purdue wall lettering is supported by facility photos; apply a compatible warm-gold face so it reads as mounted lettering.
walltext=bpy.data.objects.get('AQUA | Purdue pool-hall sign lettering')
if walltext and walltext.type=='FONT':walltext.data.materials.clear();walltext.data.materials.append(gold)
# Replace the old boxy seat mesh with a joined set of curved molded pan/back shells in the same approximate stepped stand.
seats=bpy.data.objects['AQUA R2 | 300 individual schematic spectator seats']; seatmat=seats.data.materials[0] if seats.data.materials else bpy.data.materials.get('AQUA | Purdue gold anodized metal')
verts=[];faces=[]
def prism(profile,yc,width):
    n=len(profile);base=len(verts)
    verts.extend([(x,yc-width/2,z) for x,z in profile]);verts.extend([(x,yc+width/2,z) for x,z in profile])
    faces.append(tuple(base+i for i in range(n-1,-1,-1)));faces.append(tuple(base+n+i for i in range(n)))
    for i in range(n):j=(i+1)%n;faces.append((base+i,base+j,base+n+j,base+n+i))
for row in range(12):
    x=15.6+row*.68;z=.5+row*.28
    for seat in range(25):
        if seat==12:continue
        y=-20.0+seat*1.65
        # A gently scooped pan and a slanted/rounded-back profile read as molded spectator chairs, not stacked cubes.
        prism([(x-.05,z+.29),(x+.19,z+.29),(x+.34,z+.35),(x+.33,z+.40),(x+.18,z+.43),(x-.04,z+.37)],y,.40)
        prism([(x+.14,z+.38),(x+.27,z+.37),(x+.43,z+.76),(x+.40,z+.81),(x+.33,z+.79),(x+.10,z+.43)],y,.40)
new=bpy.data.meshes.new('AQUA R7 | modeled molded-seat pan and curved back shells');new.from_pydata(verts,[],faces);new.materials.clear();new.materials.append(seatmat);new.validate(clean_customdata=False);new.update();oldmesh=seats.data;seats.data=new
for mod in list(seats.modifiers):seats.modifiers.remove(mod)
bev=seats.modifiers.new('AQUA R7 | softened molded seat edges','BEVEL');bev.width=.022;bev.segments=3;bev.limit_method='ANGLE';bev.angle_limit=.62;bev.harden_normals=True
seats['modeled_count']=288;seats['r7_geometry']='288 representative molded seat pans and slanted backs rebuilt as curved/extruded profiles; seat arrangement remains schematic and capacity is not verified.'
if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
# New interior/full building views are preview cameras only; no surveyed camera locations are implied.
def camera(name,loc,target,lens):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);rig.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return o
cam=camera('AQUA R7 | pool hall integrated interior camera',(-23,-37,5.2),(5,2,4.4),44);cam['r7_note']='Interior presentation viewpoint only; not surveyed.'
ext=camera('AQUA R7 | north entry close approach camera',(34,95,7.4),(0,50,4.2),58);ext['r7_note']='Exterior presentation viewpoint only; not surveyed.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET));print({'saved':str(ASSET),'seat_pan_back_profiles':288,'LED_fixture_meshes':18,'area_lights':18,'banners':2,'trusses':len(trusses),'new_collection_objects':len(col.objects)})

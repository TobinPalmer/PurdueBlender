import bpy, math
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; rig=bpy.data.collections['Preview_Rig']
# Replace the R7 presentation pass and preserve the stable building shell/placement.
for old_name in ('AQUA_R6 | exposed natatorium structure and display banners','AQUA_R7 | integrated natatorium lighting and seating','AQUA_R8 | integrated bleachers, banners, lighting, facade reveals'):
    old=bpy.data.collections.get(old_name)
    if old:
        for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(old)
for o in list(bpy.data.objects):
    if o.name.startswith(('AQUA R6 | pool-hall longitudinal interior camera','AQUA R7 | pool hall integrated interior camera','AQUA R7 | north entry close approach camera','AQUA R8 | pool hall bleacher and lighting camera','AQUA R8 | bleacher side detail camera','AQUA R8 | north facade close camera','AQUA R8 | north entry approach camera')):
        data=o.data;is_camera=o.type=='CAMERA';bpy.data.objects.remove(o,do_unlink=True)
        if data and data.users==0 and is_camera:bpy.data.cameras.remove(data)
col=bpy.data.collections.new('AQUA_R8 | integrated bleachers, banners, lighting, facade reveals');asset.children.link(col)
steel=bpy.data.materials.get('AQUA R7 | neutral painted natatorium steel') or bpy.data.materials.new('AQUA R7 | neutral painted natatorium steel')
trusses=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | schematic clear-span roof truss')]
for o in trusses:o['r8_evidence']='White/light exposed steel truss character supported by Arsee Engineers and Purdue Athletics facility photos; exact dimensions/layout remain schematic.'
# The Arsee project photo shows long bright strip fixtures integrated around the exposed roof structure.
light_mat=bpy.data.materials.get('AQUA R8 | luminous linear diffuser') or bpy.data.materials.new('AQUA R8 | luminous linear diffuser')
light_mat.diffuse_color=(.96,.94,.86,1);light_mat.use_nodes=True;lp=light_mat.node_tree.nodes.get('Principled BSDF');lp.inputs['Base Color'].default_value=(.96,.94,.86,1);lp.inputs['Roughness'].default_value=.28
if 'Emission Color' in lp.inputs:lp.inputs['Emission Color'].default_value=(1.0,.92,.72,1);lp.inputs['Emission Strength'].default_value=2.0

def box(name,loc,dims,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);o.data.materials.append(mat);return o
for xi,x in enumerate((-17.0,0.0,17.0),1):
    for yi,y in enumerate((-40.95,-24.55,-8.2,8.2,24.55,40.95),1):
        fixture=box(f'AQUA R8 | linear LED high-bay diffuser {xi}-{yi}',(x,y,8.88),(.22,3.0,.12),light_mat)
        fixture['r8_evidence']='Long rectangular pool-hall fixtures are visible in Arsee Engineers project photography; this modeled count and exact spacing are estimates, not an as-built lighting schedule.'
        ld=bpy.data.lights.new(f'AQUA R8 | integrated linear pool light {xi}-{yi}','AREA');ld.energy=850;ld.shape='RECTANGLE';ld.size=2.7;ld.size_y=.45;ld.use_shadow=False
        lo=bpy.data.objects.new(f'AQUA R8 | integrated linear pool light {xi}-{yi}',ld);col.objects.link(lo);lo.location=(x,y,8.70);lo.rotation_euler=(0,0,0);lo['r8_evidence']='Balanced representative illumination aligned to a linear diffuser; exact output, aiming, and spacing remain unverified.'
# Wall-mounted black/gold letters follow the giant Purdue banner motif in the Arsee pool-hall photo.
black=bpy.data.materials.get('AQUA R8 | black wall-banner fabric') or bpy.data.materials.new('AQUA R8 | black wall-banner fabric');black.diffuse_color=(.012,.015,.019,1);black.use_nodes=True;bp=black.node_tree.nodes.get('Principled BSDF');bp.inputs['Base Color'].default_value=(.012,.015,.019,1);bp.inputs['Roughness'].default_value=.88
gold=bpy.data.materials.get('AQUA R8 | Purdue gold banner lettering') or bpy.data.materials.new('AQUA R8 | Purdue gold banner lettering');gold.diffuse_color=(.92,.59,.13,1);gold.use_nodes=True;gp=gold.node_tree.nodes.get('Principled BSDF');gp.inputs['Base Color'].default_value=(.92,.59,.13,1);gp.inputs['Metallic'].default_value=.03;gp.inputs['Roughness'].default_value=.56
wall_rotation=Matrix(((0,0,-1),(-1,0,0),(0,1,0))).to_euler()
for i,(letter,y,x) in enumerate(zip('EUDRUP',(-18.0,-10.0,-2.0,6.0,14.0,22.0),(22.60,22.80,23.00,23.20,23.40,23.60)),1):
    panel=box(f'AQUA R8 | wall-mounted Purdue banner panel {i}',(x,y,7.75),(.14,5.15,3.80),black)
    panel['r8_evidence']='One field in a large black-and-gold Purdue wall banner, based on the Arsee Engineers interior photograph. Panel dimensions and location are visual estimates.'
    for dy in (-2.0,2.0):
        for z in (6.12,9.38):
            box(f'AQUA R8 | banner wall standoff {i}',(x+.37,y+dy,z),(.58,.12,.10),steel)
    txt=bpy.data.curves.new(f'AQUA R8 | PURDUE banner glyph {i}','FONT');txt.body=letter;txt.align_x='CENTER';txt.align_y='CENTER';txt.size=3.15;txt.extrude=.018;txt.bevel_depth=.004;txt.bevel_resolution=2
    ob=bpy.data.objects.new(f'AQUA R8 | PURDUE banner glyph {i}',txt);col.objects.link(ob);ob.location=(x-.12,y,7.75);ob.rotation_euler=wall_rotation;ob.data.materials.append(gold)
    ob['r8_evidence']='Large gold Purdue lettering on dark wall-mounted panels is photo-supported. Letter height and position are estimated.'
# Existing Purdue wall lettering is supported by facility photos; apply a compatible warm-gold face so it reads as mounted lettering.
walltext=bpy.data.objects.get('AQUA | Purdue pool-hall sign lettering')
if walltext and walltext.type=='FONT':walltext.data.materials.clear();walltext.data.materials.append(gold)
# Source photographs show continuous aluminum bleacher banks. Replace the tan individual chair blocks with supported, two-part continuous bench tiers and a center aisle gap.
seats=next(o for o in bpy.data.objects if o.name in ('AQUA R2 | 300 individual schematic spectator seats','AQUA R8 | 24 continuous aluminum spectator bench tiers'))
seatmat=bpy.data.materials.get('AQUA R8 | satin aluminum bleacher bench') or bpy.data.materials.new('AQUA R8 | satin aluminum bleacher bench');seatmat.diffuse_color=(.39,.43,.45,1);seatmat.use_nodes=True;seatp=seatmat.node_tree.nodes.get('Principled BSDF');seatp.inputs['Base Color'].default_value=(.39,.43,.45,1);seatp.inputs['Metallic'].default_value=.42;seatp.inputs['Roughness'].default_value=.42
nosmat=bpy.data.materials.get('AQUA R8 | graphite bleacher nosing') or bpy.data.materials.new('AQUA R8 | graphite bleacher nosing');nosmat.diffuse_color=(.055,.07,.08,1);nosmat.use_nodes=True;nosp=nosmat.node_tree.nodes.get('Principled BSDF');nosp.inputs['Base Color'].default_value=(.055,.07,.08,1);nosp.inputs['Metallic'].default_value=.24;nosp.inputs['Roughness'].default_value=.62
verts=[];faces=[]
matids=[]
def prism(profile,yc,width,matid=0):
    n=len(profile);base=len(verts)
    verts.extend([(x,yc-width/2,z) for x,z in profile]);verts.extend([(x,yc+width/2,z) for x,z in profile])
    faces.append(tuple(base+i for i in range(n-1,-1,-1)));faces.append(tuple(base+n+i for i in range(n)))
    for i in range(n):j=(i+1)%n;faces.append((base+i,base+j,base+n+j,base+n+i))
    matids.extend([matid]*(n+2))
for row in range(12):
    x=15.6+row*.68;z=.5+row*.28
    for y0,y1 in ((-20.0,-1.7),(1.7,20.0)):
        yc=(y0+y1)/2;width=y1-y0
        # Sloped aluminum bench plank across each half-row; a dark nosing strip adds a readable edge instead of repeating individual tan cuboids.
        prism([(x-.13,z+.36),(x+.45,z+.50),(x+.45,z+.59),(x-.13,z+.45)],yc,width,0)
        prism([(x-.15,z+.34),(x-.13,z+.36),(x-.13,z+.45),(x-.15,z+.43)],yc,width,1)
new=bpy.data.meshes.new('AQUA R8 | continuous aluminum spectator bench tiers');new.from_pydata(verts,[],faces);new.materials.clear();new.materials.append(seatmat);new.materials.append(nosmat)
for p,mi in zip(new.polygons,matids):p.material_index=mi
new.validate(clean_customdata=False);new.update();oldmesh=seats.data;seats.data=new;seats.name='AQUA R8 | 24 continuous aluminum spectator bench tiers'
for mod in list(seats.modifiers):seats.modifiers.remove(mod)
bev=seats.modifiers.new('AQUA R8 | softened aluminum bench edges','BEVEL');bev.width=.025;bev.segments=3;bev.limit_method='ANGLE';bev.angle_limit=.62;bev.harden_normals=True
seats['modeled_count']=24;seats['r8_geometry']='24 continuous two-sided bleacher bench rows with a 3.4 m center aisle gap, modeled from qualitative aluminum bleacher rows in the building-specific project photo. Exact geometry/layout/capacity remain schematic.'
if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
# Deepened head and jamb reveals around the north-facing ribbon glazing seen in the north-approach Street View; existing glazing, mullions, and sills remain in place.
glass=bpy.data.materials.get('AQUA R1 | blue-gray reflective ribbon glazing')
if glass and glass.node_tree:
    glass.diffuse_color=(.085,.16,.19,1);node=glass.node_tree.nodes.get('Principled BSDF')
    if node:
        node.inputs['Base Color'].default_value=(.075,.145,.18,1);node.inputs['Metallic'].default_value=.16;node.inputs['Roughness'].default_value=.16;node.inputs['IOR'].default_value=1.46
        if 'Transmission Weight' in node.inputs:node.inputs['Transmission Weight'].default_value=.06
frame=bpy.data.materials.get('AQUA | charcoal anodized metal')
if frame:
    for win in [o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | facade bay') and o.name.endswith('glazing') and o.location.y>43 and o.dimensions.x>1 and o.dimensions.y<.2]:
        w=win.dimensions.x;h=win.dimensions.z;x=win.location.x;y=win.location.y+.08;z=win.location.z
        box(f'AQUA R8 | north glazing head reveal {win.name}',(x,y,z+h/2+.06),(w+.14,.16,.12),frame)
        for side in (-1,1):box(f'AQUA R8 | north glazing jamb reveal {win.name} {side}',(x+side*(w/2+.01),y,z),(.12,.16,h+.12),frame)
# New interior/full building views are preview cameras only; no surveyed camera locations are implied.
def camera(name,loc,target,lens):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);rig.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return o
cam=camera('AQUA R8 | pool hall bleacher and lighting camera',(-20,1,7.5),(24,1,6.8),27);cam['r8_note']='Interior presentation viewpoint only; not surveyed.'
seatcam=camera('AQUA R8 | bleacher side detail camera',(3,-16,4.8),(21,1,4.0),38);seatcam['r8_note']='Interior bleacher detail viewpoint only; not surveyed.'
ext=camera('AQUA R8 | north entry approach camera',(34,95,7.4),(0,50,4.2),58);ext['r8_note']='Exterior presentation viewpoint only; not surveyed.'
fac=camera('AQUA R8 | north facade close camera',(18,78,6.0),(0,50,4.7),68);fac['r8_note']='Closer north facade presentation only; not a surveyed camera or dimensional reference.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET));print({'saved':str(ASSET),'continuous_bleacher_rows':24,'LED_linear_diffusers':18,'area_lights':18,'wall_banner_panels':6,'north_window_reveals':len([o for o in col.objects if 'north glazing' in o.name]),'trusses':len(trusses),'new_collection_objects':len(col.objects)})

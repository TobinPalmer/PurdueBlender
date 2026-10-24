import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batchC_national_soil_erosion'
ASSET=ROOT/'modular'/'buildings'/'national_soil_erosion_laboratory.blend'
COL=bpy.data.collections['Asset_national_soil_erosion_laboratory']
FACADE=bpy.data.collections['SOIL_Facade']
INTERIOR=bpy.data.collections['SOIL_Interior']

def material(name,color,roughness=.45,metallic=0.0,transmission=0.0):
    mat=bpy.data.materials.get(name)
    if not mat: mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1.0);mat.use_nodes=True
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(*color,1.0)
    bsdf.inputs['Roughness'].default_value=roughness
    bsdf.inputs['Metallic'].default_value=metallic
    if 'Transmission Weight' in bsdf.inputs: bsdf.inputs['Transmission Weight'].default_value=transmission
    return mat

def set_material_ramp(name,low,high):
    mat=bpy.data.materials[name]
    for node in mat.node_tree.nodes:
        if node.type=='VALTORGB':
            node.color_ramp.elements[0].color=(*low,1)
            node.color_ramp.elements[1].color=(*high,1)
            return

# Improve the source library's material response without replacing its procedural
# finishes. The older look was dark and brown-red under the saved preview setup.
set_material_ramp('SOIL | mottled Purdue red-brown brick',(0.30,0.075,0.043),(0.50,0.19,0.115))
set_material_ramp('SOIL | warm gray limestone / precast',(0.53,0.51,0.46),(0.72,0.69,0.62))
set_material_ramp('SOIL | weathered membrane / standing seam',(0.49,0.52,0.55),(0.67,0.70,0.73))
glass=bpy.data.materials['SOIL | schematic clear facade glazing']
glass_bsdf=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
glass_bsdf.inputs['Base Color'].default_value=(0.34,0.56,0.65,1)
glass_bsdf.inputs['Roughness'].default_value=0.17
glass_bsdf.inputs['Metallic'].default_value=0.08
# Give the blank entrance elevation visible brick coursing while retaining a
# small color variation from the existing procedural finish.
brick_mat=bpy.data.materials['SOIL | mottled Purdue red-brown brick']
brick_bsdf=next(n for n in brick_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
texcoord=next(n for n in brick_mat.node_tree.nodes if n.type=='TEX_COORD')
separate=brick_mat.node_tree.nodes.new('ShaderNodeSeparateXYZ');separate.label='wall coordinates'
combine=brick_mat.node_tree.nodes.new('ShaderNodeCombineXYZ');combine.label='horizontal x / vertical z'
bricktex=brick_mat.node_tree.nodes.new('ShaderNodeTexBrick');bricktex.label='approximate running-bond brick courses'
bricktex.inputs['Scale'].default_value=3.0
bricktex.inputs['Brick Width'].default_value=.7
bricktex.inputs['Row Height'].default_value=.2
bricktex.inputs['Mortar Size'].default_value=.018
bricktex.inputs['Mortar Smooth'].default_value=.04
bricktex.inputs['Color1'].default_value=(.43,.17,.10,1)
bricktex.inputs['Color2'].default_value=(.32,.105,.062,1)
bricktex.inputs['Mortar'].default_value=(.075,.069,.061,1)
links=brick_mat.node_tree.links
links.new(texcoord.outputs['Object'],separate.inputs['Vector'])
links.new(separate.outputs['X'],combine.inputs['X']);links.new(separate.outputs['Z'],combine.inputs['Y'])
links.new(combine.outputs['Vector'],bricktex.inputs['Vector'])
links.new(bricktex.outputs['Color'],brick_bsdf.inputs['Base Color'])

frame_mat=bpy.data.materials['SOIL | charcoal anodized metal']
sill_mat=bpy.data.materials['SOIL | warm gray limestone / precast']
blue_glass=material('SOIL | R2 pale blue flume glazing',(0.34,0.64,0.70),.2,.05,.32)
steel=material('SOIL | R2 brushed hydraulic steel',(0.27,0.34,0.38),.34,.68)
water=material('SOIL | R2 flume water',(0.035,0.26,0.36),.22,.12,.16)
soil=material('SOIL | R2 damp test soil',(0.20,0.105,0.055),.92)
sign_mat=material('SOIL | R2 raised entrance lettering',(0.74,0.75,0.71),.3,.38)

def box_mesh(name,center,dims,mat,collection,rotation=None):
    dx,dy,dz=dims;cx,cy,cz=center
    vs=[(x,y,z) for x in (-dx/2,dx/2) for y in (-dy/2,dy/2) for z in (-dz/2,dz/2)]
    # index order: x-major, y-middle, z-inner
    fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    mesh=bpy.data.meshes.new(name+' | mesh');mesh.from_pydata(vs,[],fs);mesh.update()
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj)
    obj.location=center
    if rotation is not None: obj.rotation_euler=rotation
    if mat: obj.data.materials.append(mat)
    return obj

def multi_box(name,boxes,materials,collection,location,rotation):
    vs=[];fs=[];mis=[]
    for cx,cy,cz,dx,dy,dz,mi in boxes:
        start=len(vs)
        vs.extend([(cx+x*dx/2,cy+y*dy/2,cz+z*dz/2) for x in (-1,1) for y in (-1,1) for z in (-1,1)])
        fs.extend([tuple(start+i for i in f) for f in ((0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3))])
        mis.extend([mi]*6)
    mesh=bpy.data.meshes.new(name+' | mesh');mesh.from_pydata(vs,[],fs);mesh.update()
    for mat in materials:mesh.materials.append(mat)
    for p,mi in zip(mesh.polygons,mis):p.material_index=mi
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj);obj.location=location;obj.rotation_euler=rotation
    return obj

def beam(name,start,end,width,depth,mat,collection):
    a=Vector(start);b=Vector(end);d=b-a
    obj=box_mesh(name,(0,0,0),(width,depth,d.length),mat,collection)
    obj.location=(a+b)/2;obj.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return obj

# Rerunnable R2 script: remove its generated detail objects before rebuilding.
for obj in list(COL.all_objects):
    if obj.name.startswith('SOIL | R2 '): bpy.data.objects.remove(obj,do_unlink=True)
# The clear reference entrance photo shows a long, mostly blank brick wall. Remove
# the unsupported continuous glass ribbon and service shutters from this side;
# retain the repeated windows on other elevations and articulate them modestly.
removed_front=[];brick_infill=[]
for obj in list(FACADE.all_objects):
    n=obj.name.lower()
    if n=='soil lab | research ribbon window'.lower() or 'schematic service-side shutter' in n or 'schematic service shutter louver' in n:
        if 'schematic service-side shutter' in n:
            brick_infill.append((tuple(obj.location),tuple(obj.dimensions)))
        removed_front.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
        continue
    if 'facade bay 8-' in n and obj.location.y < -24.0:
        removed_front.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True);continue
    if 'vertical glazing mullion' in n and obj.location.y < -24.0:
        removed_front.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
brick_mat=bpy.data.materials['SOIL | mottled Purdue red-brown brick']
# Continuous running-bond brick skins fill the modeled openings on this
# photographed elevation, with a true gap retained at the entrance.
front_angle=-0.040643
front_line=lambda x:-25.560637+front_angle*(x-20.253156)
front_rot=(0,0,front_angle)
door_left=.79;door_right=4.39;high_break=-6.49;front_end=20.253156;low_z=5.20;high_z=7.32
west_mid=(-32.434+high_break)/2;left_mid=(high_break+door_left)/2;right_mid=(door_right+front_end)/2;door_mid=(door_left+door_right)/2
box_mesh('SOIL | R2 continuous blank brick elevation west wing',(west_mid,front_line(west_mid),high_z/2),(high_break+32.434,.10,high_z),brick_mat,FACADE,front_rot)
box_mesh('SOIL | R2 continuous blank brick elevation east left',(left_mid,front_line(left_mid),low_z/2),(door_left-high_break,.10,low_z),brick_mat,FACADE,front_rot)
box_mesh('SOIL | R2 continuous blank brick elevation east right',(right_mid,front_line(right_mid),low_z/2),(front_end-door_right,.10,low_z),brick_mat,FACADE,front_rot)
box_mesh('SOIL | R2 brick lintel above recessed entry',(door_mid,front_line(door_mid),(3.24+low_z)/2),(door_right-door_left,.10,low_z-3.24),brick_mat,FACADE,front_rot)
for obj in list(FACADE.all_objects):
    if obj.name.lower().startswith('soil | glazing sill') and obj.location.y<-24.0:
        bpy.data.objects.remove(obj,do_unlink=True)
for obj in list(INTERIOR.all_objects):
    if obj.name.startswith('Soil Lab | schematic visible research workbench') or obj.name.startswith('Soil Lab | schematic sample tray'):
        if obj.location.y<-24.0: obj.location.y+=1.5
for obj in list(COL.all_objects):
    if 'horizontal datum' in obj.name.lower() and obj.name.endswith('.008'):
        bpy.data.objects.remove(obj,do_unlink=True)

# Add discreet dark frames and projecting limestone sills to remaining glazed
# openings. This is an approximate architectural treatment, not measured joinery.
glazing=[o for o in list(FACADE.all_objects) if o.type=='MESH' and o.name.startswith('SOIL | facade bay') and 'glazing' in o.name.lower()]
window_count=0
for bay in glazing:
    if bay.location.z>5.25 and bay.location.x>-6.49: continue
    w,h=bay.dimensions.x,bay.dimensions.z
    ny=(-math.sin(bay.rotation_euler.z),math.cos(bay.rotation_euler.z))
    outward=-1.0 if (ny[0]*bay.location.x+ny[1]*bay.location.y)<0 else 1.0
    face_y=outward*(bay.dimensions.y/2+0.025)
    rail=.045; frame_depth=.095
    parts=[
      (-w/2+rail/2,face_y,0,rail,frame_depth,h+rail),
      ( w/2-rail/2,face_y,0,rail,frame_depth,h+rail),
      (0,face_y,-h/2+rail/2,w,frame_depth,rail),
      (0,face_y, h/2-rail/2,w,frame_depth,rail),
      (0,outward*(bay.dimensions.y/2+.075),-h/2-.075,w+.12,.22,.10)
    ]
    boxes=[(*p,0 if i<4 else 1) for i,p in enumerate(parts)]
    multi_box(f'SOIL | R2 window frame and sill {window_count:03d}',boxes,[frame_mat,sill_mat],FACADE,bay.location,bay.rotation_euler)
    window_count+=1

# Reuse the front door position as a recessed main entry. The photo supplies its
# brick surround/sign/address relationship, while modeled dimensions stay explicit
# estimates rather than survey-derived sizes.
door=bpy.data.objects['Soil Lab | loading / equipment door']
door.name='Soil Lab | approximate recessed main entrance surround'
door.location=(2.59,front_line(2.59)+.10,1.62);door.rotation_euler.z=front_angle;door.dimensions=(3.6,.24,3.24)
if door.data.materials: door.data.materials[0]=bpy.data.materials['SOIL | deep shadow / reveals']
threshold=bpy.data.objects['SOIL | entrance threshold']
threshold.location=(2.59,front_line(2.59)-.625,.105);threshold.rotation_euler.z=front_angle;threshold.dimensions=(4.7,1.35,.21)

# Two glazed door leaves, side lights and transom set slightly forward of the dark
# recessed reveal. Frame/sign sizes are approximate from the entrance photograph.
cx=2.59;front_y=front_line(cx)-.12;door_z=1.48
for i,xoff in enumerate((-.76,.76)):
    localx=cx+xoff
    box_mesh(f'SOIL | R2 glazed entry door leaf {i+1}',(localx,front_line(localx)-.12,door_z),(1.46,.08,2.58),blue_glass,FACADE,front_rot)
for xoff in (-1.53,0,1.53):
    localx=cx+xoff
    box_mesh('SOIL | R2 entrance vertical metal stile',(localx,front_line(localx)-.18,door_z),(.055,.12,2.62),frame_mat,FACADE,front_rot)
box_mesh('SOIL | R2 entrance head frame',(cx,front_line(cx)-.18,2.79),(3.12,.12,.07),frame_mat,FACADE,front_rot)
box_mesh('SOIL | R2 entrance transom glazing',(cx,front_line(cx)-.12,2.98),(3.0,.075,.34),blue_glass,FACADE,front_rot)
box_mesh('SOIL | R2 entrance transom top rail',(cx,front_line(cx)-.18,3.17),(3.12,.12,.06),frame_mat,FACADE,front_rot)
for xoff in (-1.79,1.79):
    localx=cx+xoff
    box_mesh('SOIL | R2 entrance reveal return',(localx,front_line(localx),1.7),(.18,.45,3.25),bpy.data.materials['SOIL | cast concrete'],FACADE,front_rot)

# Raised sign lettering and address plaque follow the photographed arrangement:
# long lab name left of the recessed opening; street address above the entry.
old_letter=bpy.data.objects.get('SOIL | facade identification lettering')
if old_letter:
    bpy.data.objects.remove(old_letter,do_unlink=True)
panel=bpy.data.objects.get('SOIL | dark entrance name panel')
if panel: bpy.data.objects.remove(panel,do_unlink=True)
def add_text(name,body,center,z,size):
    data=bpy.data.curves.new(name+' | type','FONT');data.body=body;data.size=size;data.align_x='CENTER';data.extrude=.004;data.bevel_depth=.001
    obj=bpy.data.objects.new(name,data);FACADE.objects.link(obj)
    obj.location=(center,front_line(center)-.06,z);obj.rotation_euler=(math.pi/2,0,front_angle);obj.data.materials.append(sign_mat)
    return obj
add_text('SOIL | R2 entrance sign main line','NATIONAL SOIL EROSION RESEARCH LABORATORY',-7.5,4.48,.255)
add_text('SOIL | R2 entrance sign service line','AGRICULTURAL RESEARCH SERVICE',-7.5,4.10,.18)
add_text('SOIL | R2 entrance sign agency line','U.S. DEPARTMENT OF AGRICULTURE',-7.5,3.82,.18)
add_text('SOIL | R2 entrance address plaque','275 SOUTH RUSSELL STREET',2.59,3.76,.15)

# Add a clearly identifiable research flume in the taller west high-bay zone.
# Its visible configuration follows USDA K7567-11; all dimensions are approximate.
fcx=-25.4;len_y=28.0;half_len=len_y/2;channel_z=1.32
box_mesh('SOIL | R2 flume bed tray',(fcx,0,channel_z),(1.32,len_y,.16),steel,INTERIOR)
box_mesh('SOIL | R2 flume damp soil test bed',(fcx,0,channel_z+.102),(1.12,len_y-.6,.045),soil,INTERIOR)
box_mesh('SOIL | R2 flume water surface',(fcx,0,channel_z+.145),(1.04,len_y-.8,.025),water,INTERIOR)
for side in (-1,1):
    x=fcx+side*.64
    box_mesh(f'SOIL | R2 transparent flume side {side}',(x,0,channel_z+.40),(.055,len_y,.62),blue_glass,INTERIOR)
    beam(f'SOIL | R2 flume steel top rail {side}',(x, -half_len,channel_z+.74),(x,half_len,channel_z+.74),.055,.07,steel,INTERIOR)
    beam(f'SOIL | R2 longitudinal underframe rail {side}',(fcx+side*.8,-half_len,channel_z-.12),(fcx+side*.8,half_len,channel_z-.12),.10,.12,steel,INTERIOR)

# Repeated A-frame trestles visibly carry the channel at manageable scale.
for idx,y in enumerate((-12,-7,-2,3,8,13)):
    for side in (-1,1):
        beam(f'SOIL | R2 flume A-frame leg {idx}-{side}',(fcx+side*1.15,y,.18),(fcx+side*.80,y,channel_z-.18),.12,.13,steel,INTERIOR)
    beam(f'SOIL | R2 flume A-frame tie {idx}',(fcx-1.15,y,.20),(fcx+1.15,y,.20),.12,.12,steel,INTERIOR)

# Safety rail and adjustable sensor bridge are modeled as simple recognisable rig
# parts rather than architectural claims.
walk_x=fcx+1.48
beam('SOIL | R2 flume safety handrail upper',(walk_x,-half_len,1.38),(walk_x,half_len,1.38),.045,.05,steel,INTERIOR)
beam('SOIL | R2 flume safety handrail mid',(walk_x,-half_len,.88),(walk_x,half_len,.88),.035,.045,steel,INTERIOR)
for idx,y in enumerate((-13,-8,-3,2,7,12)):
    beam(f'SOIL | R2 flume safety post {idx}',(walk_x,y,.48),(walk_x,y,1.45),.045,.045,steel,INTERIOR)
for side in (-1,1):
    beam(f'SOIL | R2 overhead instrument rail {side}',(fcx+side*1.55,-half_len,3.35),(fcx+side*1.55,half_len,3.35),.06,.06,steel,INTERIOR)
for idx,y in enumerate((-12,0,12)):
    beam(f'SOIL | R2 adjustable instrument crossbar {idx}',(fcx-1.62,y,3.35),(fcx+1.62,y,3.35),.075,.075,steel,INTERIOR)
    for side in (-1,1):
        beam(f'SOIL | R2 instrument gantry column {idx}-{side}',(fcx+side*1.55,y,2.25),(fcx+side*1.55,y,3.35),.075,.075,steel,INTERIOR)
box_mesh('SOIL | R2 flume collection sump',(fcx,15.4,.67),(2.7,2.2,1.30),steel,INTERIOR)
box_mesh('SOIL | R2 flume pump/control cabinet',(fcx+2.25,14.2,.78),(.9,1.4,1.55),bpy.data.materials['SOIL | charcoal anodized metal'],INTERIOR)
box_mesh('SOIL | R2 flume data console',(fcx+2.1,-11.5,1.0),(1.0,.7,1.25),bpy.data.materials['SOIL | warm gray limestone / precast'],INTERIOR)
box_mesh('SOIL | R2 flume monitor',(fcx+2.1,-11.9,1.68),(.68,.1,.48),blue_glass,INTERIOR)

# Brighten the local preview lighting and moderate the cool cast. These lights are
# outside the exported asset collection; material changes remain portable.
scene=bpy.context.scene
scene.view_settings.exposure=.45
scene.view_settings.gamma=1.05
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass
if scene.world and scene.world.use_nodes:
    bg=next((n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND'),None)
    if bg:
        bg.inputs['Color'].default_value=(.26,.31,.36,1);bg.inputs['Strength'].default_value=.55
for light in [o for o in bpy.data.objects if o.type=='LIGHT']:
    if light.name.startswith('SOIL Preview key'):light.data.energy*=1.18
    elif light.name.startswith('SOIL Preview fill'):light.data.energy*=1.45
    elif light.name.startswith('SOIL Preview top'):light.data.energy*=1.15

# Save the source asset only after all modifications are applied.
bpy.context.view_layer.update()
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'

result={
 'revision':'R2','score_received':'6.9/10','source':['https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg','https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/'],
 'photo_supported_changes':['removed unsupported front glass ribbon and service shutters from the photographed blank brick entrance elevation','restored raised laboratory/USDA lettering, street plaque, recessed glazed double door and side lights','added approximate full-length experimental flume, A-frame supports, safety handrail, overhead sensor bridge and sump in hydraulics high-bay zone','added approximate window frames and sills on remaining glazed elevations','improved brick/stone/roof/glazing material response and preview lighting'],
 'removed_front_objects':removed_front,'articulated_glazing_bays':window_count,
 'facade_registration':{'basis':'FID 242 south perimeter edge','local_edge_endpoints_m':[[20.253156,-25.560637],[-32.434018,-23.418094]],'wall_angle_degrees':math.degrees(front_angle),'blank_brick_panels_follow_GIS_edge':True,'door_dimensions_approximate':True},
 'roof_edge_validation':'Symmetric sampled boundary distance to FID 242, sampled every 0.2 m; detailed result in nsel_revision_r2_validation.json.',
 'entrance_dimensions_approximate_m':{'recess_opening':[3.6,3.24],'double_door_pair':[2.92,2.58],'sign_span_estimate':8.5,'address_plaque_estimate':[3.8,.3]},
 'flume_dimensions_approximate_m':{'length':len_y,'channel_width':1.32,'top_of_side_glass_z':channel_z+.71,'location':'west/high-bay area; exact room location and equipment size unverified'},
 'limitations':['R1 roof-height split remains approximate from 5-ft DSM and interpolated DTM.','Entrance photo is a 2018 visitor group photo, not an architectural elevation; entrance/window dimensions and door details are approximated.','The USDA flume photograph verifies equipment type but not this building’s exact internal layout or flume dimensions.','Window frames/sills are an approximate articulation treatment; no measured facade schedule was located.']
}
(AUDIT/'nsel_revision_r2.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

# R2 camera renders: fitted exterior, entry close-up, roof and cutaway hydraulics bay.
def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.location=loc;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;return obj
oldcam=scene.camera
cam=camera('TEMP | NSEL R2 render camera',(74,-112,62),(0,0,3.0),88)
scene.camera=cam;scene.render.filepath=str(AUDIT/'nsel_revision_r2_exterior.png');bpy.ops.render.render(write_still=True)
cam.location=(4,-72,13);cam.rotation_euler=(Vector((-3,-25.4,3.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=27
scene.render.filepath=str(AUDIT/'nsel_revision_r2_entry_detail.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,110);cam.rotation_euler=Vector((0,0,-1)).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=82
scene.render.filepath=str(AUDIT/'nsel_revision_r2_roof_outline.png');bpy.ops.render.render(write_still=True)
hide=[]
for obj in bpy.data.objects:
    if obj is None:continue
    hide.append((obj,obj.hide_render))
    obj.hide_render=not (obj.name.startswith('SOIL | R2 flume') or obj.name.startswith('SOIL | R2 overhead instrument') or obj.name.startswith('SOIL | R2 adjustable instrument') or obj.name.startswith('SOIL | R2 instrument gantry') or (obj.type=='LIGHT' and obj.name.startswith('SOIL Preview')))
cam.location=(-45,-23,23);cam.rotation_euler=(Vector((-25.4,0,1.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=43
cam.data.ortho_scale=38
scene.render.filepath=str(AUDIT/'nsel_revision_r2_hydraulics_cutaway.png');bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
for obj,old in hide:obj.hide_render=old
scene.camera=oldcam;camdata=cam.data;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps(result,indent=2))

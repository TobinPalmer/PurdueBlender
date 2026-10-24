import bpy, math, json
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections['Asset_lambert_fieldhouse']
interior=bpy.data.collections['LAMB_Interior']
facade=bpy.data.collections['LAMB_Facade']
site=bpy.data.collections['LAMB_Site']
rig=bpy.data.collections['Preview_Rig']

def getmat(name, rgba, rough=.7, metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=rgba; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=rgba
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metallic
    return m

def make_mesh(name, verts, faces, mat, col):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob

def box_mesh_append(v,f,center,size):
    x,y,z=center; sx,sy,sz=(q*.5 for q in size); n=len(v)
    v.extend([(x-sx,y-sy,z-sz),(x+sx,y-sy,z-sz),(x+sx,y+sy,z-sz),(x-sx,y+sy,z-sz),
              (x-sx,y-sy,z+sz),(x+sx,y-sy,z+sz),(x+sx,y+sy,z+sz),(x-sx,y+sy,z+sz)])
    f.extend([tuple(n+i for i in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])

def append_transformed_box(v,f,matrix,center,size):
    x,y,z=center; sx,sy,sz=(q*.5 for q in size); n=len(v)
    local=[(x-sx,y-sy,z-sz),(x+sx,y-sy,z-sz),(x+sx,y+sy,z-sz),(x-sx,y+sy,z-sz),
           (x-sx,y-sy,z+sz),(x+sx,y-sy,z+sz),(x+sx,y+sy,z+sz),(x-sx,y+sy,z+sz)]
    v.extend([tuple(matrix@Vector(p)) for p in local])
    f.extend([tuple(n+i for i in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])

# Remove the revision-1 mullion/seating items before rebuilding in a more
# structured, accessible layout. Keep the track and its measured path unchanged.
for ob in list(facade.objects):
    if ob.name.startswith('LAMB | glass-block joint grid') or ob.name.startswith('LAMB | facade piers round2'):
        bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(interior.objects):
    if any(ob.name.startswith(s) for s in ('LAMB | stepped spectator stand structure',
        'LAMB | individual charcoal spectator seats','LAMB | gold spectator seat blocks',
        'LAMB | spectator aisle steps','LAMB | schematic event high-jump mat',
        'LAMB | schematic portable high-jump mat','LAMB | high-jump mat padded top',
        'LAMB | schematic high-jump standard','LAMB | schematic high-jump crossbar',
        'LAMB | tiered spectator stand banks','LAMB | spectator circulation aisles',
        'LAMB | individual dark seats','LAMB | gold accent seat blocks')):
        bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(site.objects):
    if ob.name.startswith('LAMB | Stadium entrance step') or ob.name.startswith('LAMB | Stadium entrance handrail'):
        bpy.data.objects.remove(ob,do_unlink=True)

# Remove the long rectangular specular hotspot from the saved exterior preview.
# The actual roof material/assembly remains schematic: no measured elevation or
# roof-covering specification has been found in the available documentation.
roofmat=bpy.data.materials.get('LAMB | weathered membrane / standing seam')
if roofmat:
    roofmat.use_nodes=True
    bs=roofmat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Metallic'].default_value=0.0
        bs.inputs['Roughness'].default_value=.97
        if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value=.03
        if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value=0.0
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=.012
    # Very low relief helps read as matte sheet without making fake deep ridges.
    bump=next((n for n in roofmat.node_tree.nodes if n.type=='BUMP'),None)
    if bump:
        bump.inputs['Strength'].default_value=.035
        bump.inputs['Distance'].default_value=.006

# The existing roof arches are still the strongest available form evidence.
# Preserve them; the campus archive/photo record does not document exact rise.
# The seam object stays shallow and schematic, not a new roof profile.

# Convert the wall material to a scale-consistent running-bond brick and reduce
# oversized mottling. The tile pattern is a material detail; wall openings and
# footprint geometry remain untouched.
brick=bpy.data.materials.get('LAMB | mottled Purdue red-brown brick')
if brick:
    nt=brick.node_tree; bs=nt.nodes.get('Principled BSDF')
    coord=next((n for n in nt.nodes if n.type=='TEX_COORD'),None)
    noise=next((n for n in nt.nodes if n.type=='TEX_NOISE'),None)
    ramp=next((n for n in nt.nodes if n.type=='VALTORGB'),None)
    bump=next((n for n in nt.nodes if n.type=='BUMP'),None)
    if coord and noise:
        for l in list(nt.links):
            if l.to_node==noise and l.to_socket.name=='Vector': nt.links.remove(l)
        nt.links.new(coord.outputs['Object'],noise.inputs['Vector'])
        noise.inputs['Scale'].default_value=1.7
        noise.inputs['Detail'].default_value=2.0
    if bs:
        bs.inputs['Roughness'].default_value=.86
    bricktex=next((n for n in nt.nodes if n.type=='TEX_BRICK'),None)
    if bricktex is None:
        bricktex=nt.nodes.new('ShaderNodeTexBrick'); bricktex.name='LAMB | real-scale running-bond masonry'
    bricktex.inputs['Color1'].default_value=(.44,.16,.095,1)
    bricktex.inputs['Color2'].default_value=(.34,.11,.065,1)
    bricktex.inputs['Mortar'].default_value=(.23,.22,.19,1)
    bricktex.inputs['Scale'].default_value=3.4
    bricktex.inputs['Brick Width'].default_value=.68
    bricktex.inputs['Row Height'].default_value=.27
    bricktex.inputs['Mortar Size'].default_value=.035
    bricktex.inputs['Mortar Smooth'].default_value=.02
    if coord: nt.links.new(coord.outputs['Object'],bricktex.inputs['Vector'])
    if bs:
        # The color ramp retains restrained material variation over the brick field.
        mix=next((n for n in nt.nodes if n.type=='MIX_RGB' and n.name=='LAMB | brick variation blend'),None)
        if mix is None:
            mix=nt.nodes.new('ShaderNodeMixRGB'); mix.name='LAMB | brick variation blend'; mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=.14
        # use brick tone as the dominant output; mortar remains visible from Brick Texture.
        for l in list(nt.links):
            if l.to_node==bs and l.to_socket.name=='Base Color': nt.links.remove(l)
        nt.links.new(bricktex.outputs['Color'],bs.inputs['Base Color'])
        if bump:
            for l in list(nt.links):
                if l.to_node==bump and l.to_socket.name=='Height': nt.links.remove(l)
            nt.links.new(bricktex.outputs['Fac'],bump.inputs['Height'])
            bump.inputs['Strength'].default_value=.08; bump.inputs['Distance'].default_value=.018

# Fine mortar joints make the documented glass-block facade read as masonry
# glazing rather than featureless gray panels. Only apply where an existing
# pane already identifies the glazing opening.
mortar=getmat('LAMB | glass-block mortar joints',(.50,.52,.49,1),.72,0)
grid_v=[]; grid_f=[]; grid_count=0
for ob in list(facade.objects):
    if ob.type!='MESH' or not ob.name.startswith('LAMB | facade bay') or not ob.name.endswith('glazing'):
        continue
    w=ob.dimensions.x; h=ob.dimensions.z
    # 0.4-0.45 m units are a visual estimate, not an as-built block module.
    nx=max(2,int(w/.42)); nz=max(2,int(h/.40))
    y=-ob.dimensions.y*.5-.009
    for i in range(1,nx):
        x=-w*.5+w*i/nx
        append_transformed_box(grid_v,grid_f,ob.matrix_world,(x,y,0),(.026,.018,h-.05))
        grid_count+=1
    for j in range(1,nz):
        z=-h*.5+h*j/nz
        append_transformed_box(grid_v,grid_f,ob.matrix_world,(0,y,z),(w-.05,.018,.026))
        grid_count+=1
if grid_f:
    make_mesh('LAMB | glass-block joint grid',grid_v,grid_f,mortar,facade)

# Beef up the existing documented concrete pier rhythm slightly on longer
# public elevations; these remain low-detail massing cues, not measured widths.
concrete=bpy.data.materials.get('LAMB | cast concrete')
for ob in list(facade.objects):
    if ob.name=='LAMB | pale concrete facade pier' and ob.type=='MESH':
        ob.dimensions.x=.58
        bpy.context.view_layer.objects.active=ob; ob.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        ob.select_set(False)

# Stadium Ave is the documented main entrance side (south in this local model).
# Add a short accessible-context stair/landing and simple handrails at the
# existing entrance threshold; dimensions are schematic and do not alter origin.
stepmat=concrete or getmat('LAMB | cast concrete',(.4,.42,.41,1),.85)
step_v=[]; step_f=[]; railmat=bpy.data.materials.get('LAMB | charcoal anodized metal')
for i in range(4):
    # Steps rise toward the existing Stadium Ave threshold: outside is the
    # lowest tread and the door-side tread is highest.
    yy=-49.23+i*.46
    zz=.06+i*.11
    box_mesh_append(step_v,step_f,(0,yy,zz),(8.0,.50,.12))
make_mesh('LAMB | Stadium entrance steps',step_v,step_f,stepmat,site)
# Railings are smooth thin tube paths from street level toward the threshold.
for side in (-1,1):
    curve=bpy.data.curves.new('LAMB | Stadium entrance handrail curve','CURVE')
    curve.dimensions='3D'; curve.resolution_u=1; curve.bevel_depth=.035; curve.bevel_resolution=3
    spline=curve.splines.new('POLY'); spline.points.add(1)
    spline.points[0].co=(side*4.35,-49.45,.93,1)
    spline.points[1].co=(side*4.35,-47.63,1.36,1)
    ob=bpy.data.objects.new('LAMB | Stadium entrance handrail',curve); site.objects.link(ob)
    if railmat: ob.data.materials.append(railmat)

# Interior seating with visible aisles and clear access paths. Break each row
# into four banks; aisle positions and capacities are schematic, while the
# existence of spectator seating is photo-supported.
seat_dark=getmat('LAMB | charcoal spectator seat',(.055,.065,.072,1),.5,.1)
seat_gold=getmat('LAMB | Purdue gold accent seat',(.82,.48,.055,1),.5,.05)
stand_concrete=getmat('LAMB | exposed stepped concrete bleacher',(.42,.43,.41,1),.84)
stand_v=[]; stand_f=[]; dark_v=[]; dark_f=[]; gold_v=[]; gold_f=[]; aisle_v=[]; aisle_f=[]
seat_count=34; seat_pitch=1.24; row_count=8; x0=-(seat_count-1)*seat_pitch/2
aisles=(-11.5,0,11.5); aisle_half=1.05
for side in (-1,1):
    ybase=side*(6*1.22+5.8)
    for row in range(row_count):
        y=ybase+side*row*.94; z=.40+row*.34
        for lo,hi in [(-seat_count*seat_pitch/2,aisles[0]-aisle_half),
                      (aisles[0]+aisle_half,aisles[1]-aisle_half),
                      (aisles[1]+aisle_half,aisles[2]-aisle_half),
                      (aisles[2]+aisle_half,seat_count*seat_pitch/2)]:
            center=(lo+hi)*.5; width=max(.1,hi-lo)
            box_mesh_append(stand_v,stand_f,(center,y,z-.16),(width,.90,.32))
        # Tread surfaces in each aisle give clear vertical circulation lines.
        for ax in aisles:
            box_mesh_append(aisle_v,aisle_f,(ax,y,z-.145),(2.0,.90,.29))
        for j in range(seat_count):
            x=x0+j*seat_pitch
            if any(abs(x-a)<aisle_half+.3 for a in aisles): continue
            target=(gold_v,gold_f) if (j//8)%2 else (dark_v,dark_f)
            box_mesh_append(target[0],target[1],(x,y,z+.045),(.96,.56,.11))
            box_mesh_append(target[0],target[1],(x,y-side*.25,z+.24),(.96,.09,.34))
make_mesh('LAMB | tiered spectator stand banks',stand_v,stand_f,stand_concrete,interior)
make_mesh('LAMB | spectator circulation aisles',aisle_v,aisle_f,stand_concrete,interior)
make_mesh('LAMB | individual dark seats',dark_v,dark_f,seat_dark,interior)
make_mesh('LAMB | gold accent seat blocks',gold_v,gold_f,seat_gold,interior)

# High-jump mat/pit is a meet-use cue seen in Lambert interior event photos.
# Its location and equipment proportions are portable/event-specific estimates.
mat_top=getmat('LAMB | event high-jump mat top',(.13,.20,.24,1),.92)
mat_side=getmat('LAMB | event high-jump mat side',(.07,.10,.12,1),.87)
mat_v=[]; mat_f=[]; box_mesh_append(mat_v,mat_f,(-3,0,.55),(8.0,4.2,.75))
make_mesh('LAMB | schematic portable high-jump mat',mat_v,mat_f,mat_side,interior)
top_v=[]; top_f=[]; box_mesh_append(top_v,top_f,(-3,0,.945),(7.7,3.9,.04))
make_mesh('LAMB | high-jump mat padded top',top_v,top_f,mat_top,interior)
for x in (-7.3,1.3):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.045,depth=2.4,location=(x,0,2.15))
    ob=bpy.context.object; ob.name='LAMB | schematic high-jump standard'
    for c in list(ob.users_collection): c.objects.unlink(ob)
    interior.objects.link(ob)
    if railmat: ob.data.materials.append(railmat)
bar=getmat('LAMB | high-jump crossbar',(.84,.82,.72,1),.58,.1)
bar_v=[]; bar_f=[]; box_mesh_append(bar_v,bar_f,(-3,0,3.28),(8.7,.045,.045))
make_mesh('LAMB | schematic high-jump crossbar',bar_v,bar_f,bar,interior)

# Clear aisles on both sides with a low wall/walkway line remains unresolved;
# the interior arrangement is explicitly event-layout schematic.

# Replace default exterior camera angle with lower, street-scale framing to show
# the entrance, brick piers and windows instead of letting the roof dominate.
extcam=bpy.data.objects.get('LAMB | three-quarter preview camera')
if extcam:
    extcam.location=(78,-130,30)
    target=Vector((0,0,7.0))
    extcam.rotation_euler=(target-Vector(extcam.location)).to_track_quat('-Z','Y').to_euler()
    extcam.data.lens=42
    scene.camera=extcam

# Save and reopen before any preview render.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections['Asset_lambert_fieldhouse']
exterior_camera=bpy.data.objects['LAMB | three-quarter preview camera']
scene.camera=exterior_camera
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.filepath=OUT+r'/exterior_round2.png'
bpy.ops.render.render(write_still=True)

# Interior cutaway preview (hide only outer envelope and roof skin temporarily).
hidden=[]
for name in ('LAMB_Structure','LAMB_Facade'):
    c=bpy.data.collections.get(name)
    if c:
        for ob in c.objects: hidden.append((ob,ob.hide_render)); ob.hide_render=True
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
if canopy: hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']
scene.render.filepath=OUT+r'/interior_round2.png'
bpy.ops.render.render(write_still=True)
for ob,val in hidden: ob.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)

# Directly measure the lane-one centerline from the saved track mesh: average
# paired inner/outer boundary vertices and sum the actual closed polygon edges.
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']
n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
measured=sum((center[(i+1)%n]-center[i]).length for i in range(n))
asset=bpy.data.collections['Asset_lambert_fieldhouse']
record={
 'revision':2,
 'reopen':'PASS',
 'asset_file':'modular/buildings/lambert_fieldhouse.blend',
 'collection':'Asset_lambert_fieldhouse',
 'asset_object_count':len(list(asset.all_objects)),
 'mesh_measured_track_lane1_centerline_perimeter_m':measured,
 'track_lanes':6,
 'track_boundary_lines':sum(o.name.startswith('LAMB | lane boundary ') for o in bpy.data.objects),
 'glass_block_grid_segments':grid_count,
 'entrance_steps':1,
 'spectator_access_aisles':3,
 'interior_seating':'eight tier rows on each side, separated into four banks by three aisles',
 'event_mat':'portable high-jump mat represented schematically from meet-photo evidence',
 'roof_material':'matte, low-specular neutral roof treatment; cover/profile remain unverified estimates',
 'default_camera':bpy.context.scene.camera.name if bpy.context.scene.camera else None,
 'previews':['audit/lambert_fieldhouse/exterior_round2.png','audit/lambert_fieldhouse/interior_round2.png'],
 'master_manifest_shared_files_edited':False
}
with open(OUT+r'/validation_round2.json','w') as f: json.dump(record,f,indent=2)
print(json.dumps(record,indent=2))

import bpy, math, json
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/lambert_fieldhouse.blend'
OUT = ROOT + r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
asset = bpy.data.collections['Asset_lambert_fieldhouse']
interior = bpy.data.collections['LAMB_Interior']
roof = bpy.data.collections['LAMB_Roof']
rig = bpy.data.collections['Preview_Rig']

def ensure_collection(name, parent):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        parent.children.link(col)
    return col

def material(name, rgba, roughness=0.65, metallic=0.0, emission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = rgba
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value = rgba
        bs.inputs['Roughness'].default_value = roughness
        bs.inputs['Metallic'].default_value = metallic
        if 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value = rgba
            bs.inputs['Emission Strength'].default_value = emission
    return m

def mesh_object(name, verts, faces, mat, col):
    me = bpy.data.meshes.new(name + ' mesh')
    me.from_pydata(verts, [], faces)
    me.materials.append(mat)
    me.update()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob

def append_box(v, f, center, size):
    x,y,z = center; sx,sy,sz = [q*.5 for q in size]; n=len(v)
    v.extend([(x-sx,y-sy,z-sz),(x+sx,y-sy,z-sz),(x+sx,y+sy,z-sz),(x-sx,y+sy,z-sz),
              (x-sx,y-sy,z+sz),(x+sx,y-sy,z+sz),(x+sx,y+sy,z+sz),(x-sx,y+sy,z+sz)])
    f.extend([tuple(n+i for i in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])

# The original generic ellipse and bench slabs were schematic. Replace those
# objects with a source-constrained 200 m stadium oval and readable spectator
# stands. The official facility page documents six lanes and a 200 m Rekortan track;
# exact infield dimensions and seating layout remain estimated from photography.
replace_prefixes = ('LAMB | schematic indoor oval running track',
                    'LAMB | schematic interior bleacher tier',
                    'LAMB | track lane boundary ', 'LAMB | track finish line')
for ob in list(interior.objects):
    if any(ob.name.startswith(prefix) for prefix in replace_prefixes):
        bpy.data.objects.remove(ob, do_unlink=True)

track_mat = material('LAMB | Rekortan-like red synthetic track', (.39,.095,.055,1), .73)
lane_mat = material('LAMB | track lane marking warm white', (.88,.82,.65,1), .58)
field_mat = material('LAMB | infield competition floor', (.42,.40,.35,1), .82)
seat_dark = material('LAMB | charcoal spectator seat', (.055,.065,.072,1), .48, .15)
seat_gold = material('LAMB | Purdue gold accent seat', (.82,.48,.055,1), .48, .05)
stand_concrete = material('LAMB | exposed stepped concrete bleacher', (.42,.43,.41,1), .82)
fixture_mat = material('LAMB | bright linear fieldhouse luminaire', (.92,.85,.68,1), .32, .0, 1.7)
banner_dark = material('LAMB | dark athletic banner', (.035,.045,.05,1), .65)
banner_gold = material('LAMB | gold banner band', (.84,.51,.08,1), .58)

# Stadium-shaped loop: two 45 m straights and two 180-degree turns. For a
# 200 m measured lap, centerline radius is solved as (200 - 2*straight)/(2*pi).
straight = 45.0
radius = (200.0 - 2.0*straight) / (2.0*math.pi)
lane_width = 1.22
lane_total = lane_width * 6.0
half_track = lane_total * .5
straight_samples, arc_samples = 40, 64

def stadium_path(r):
    pts=[]
    for i in range(straight_samples+1):
        pts.append((-straight/2 + straight*i/straight_samples, r))
    for i in range(1,arc_samples+1):
        a=math.pi/2 - math.pi*i/arc_samples
        pts.append((straight/2+r*math.cos(a), r*math.sin(a)))
    for i in range(1,straight_samples+1):
        pts.append((straight/2 - straight*i/straight_samples, -r))
    for i in range(1,arc_samples):
        a=-math.pi/2 - math.pi*i/arc_samples
        pts.append((-straight/2+r*math.cos(a), r*math.sin(a)))
    return pts

outer = stadium_path(radius+half_track)
inner = stadium_path(radius-half_track)
assert len(outer)==len(inner)
verts=[]; faces=[]; n=len(outer)
for x,y in outer: verts.append((x,y,.245))
for x,y in inner: verts.append((x,y,.245))
for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
mesh_object('LAMB | 6-lane 200 m stadium track surface',verts,faces,track_mat,interior)

# Lines follow equal-radius stadium loops; the dimension is constrained by the
# documented lap length while lane width is a standard schematic athletics value.
for lane in range(7):
    offset = -half_track + lane_width*lane
    rline=radius+offset
    path=stadium_path(rline)
    line_verts=[]; line_faces=[]
    for x,y in path:
        line_verts.extend([(x,y-.045,.262),(x,y+.045,.262)])
    for i in range(len(path)):
        j=(i+1)%len(path); line_faces.append((2*i,2*j,2*j+1,2*i+1))
    mesh_object('LAMB | lane boundary '+str(lane+1),line_verts,line_faces,lane_mat,interior)

# Mark the common finish zone across the six lanes without fabricating venue text.
verts=[]; faces=[]; line_x=straight/2-1.5
for y in (-half_track,half_track):
    verts.extend([(line_x-.09,y,.269),(line_x+.09,y,.269)])
faces=[(0,2,3,1)]
mesh_object('LAMB | cross-track finish marking',verts,faces,lane_mat,interior)

# Replace the flat ellipse backdrop with a clean, softly textured warm-gray infield.
def stadium_disc(r, z, mat, name):
    path=stadium_path(r); v=[(x,y,z) for x,y in path]
    faces=[tuple(range(len(v)))]
    # Stadium outline is concave-free; Blender triangulates the polygon at mesh update.
    ob=mesh_object(name,v,faces,mat,interior)
    return ob
stadium_disc(radius-half_track-.18,.205,field_mat,'LAMB | stadium oval infield finish')

# Raised stepped seating along both long sides. Each bank is built as one joined
# mesh for clean inspection and a light exported object count.
stand_v=[]; stand_f=[]; seat_v=[]; seat_f=[]; gold_v=[]; gold_f=[]
seat_count=34; row_count=8; seat_pitch=1.24
seat_x0=-(seat_count-1)*seat_pitch/2
for side in (-1,1):
    ybase=side*(half_track+5.8)
    for row in range(row_count):
        y=ybase+side*row*.94
        z=.40+row*.34
        # Solid concrete riser/tread under each row gives the stands legible depth.
        append_box(stand_v,stand_f,(0,y,z-.16),(seat_count*seat_pitch+.7,.90,.32))
        for j in range(seat_count):
            x=seat_x0+j*seat_pitch
            target_v,target_f=(gold_v,gold_f) if (j//8)%2==1 else (seat_v,seat_f)
            append_box(target_v,target_f,(x,y,z+.045),(.96,.56,.11))
            # Low backrest: restrained geometry, no unsupported seat branding.
            append_box(target_v,target_f,(x,y-side*.25,z+.24),(.96,.09,.34))
mesh_object('LAMB | stepped spectator stand structure',stand_v,stand_f,stand_concrete,interior)
mesh_object('LAMB | individual charcoal spectator seats',seat_v,seat_f,seat_dark,interior)
mesh_object('LAMB | gold spectator seat blocks',gold_v,gold_f,seat_gold,interior)

# Roof finish is deliberately treated as an unverified metal/membrane surface.
# Tame the prior over-bright emission and add subtle longitudinal seam cues.
roofmat=bpy.data.materials.get('LAMB | weathered membrane / standing seam')
if roofmat and roofmat.use_nodes:
    bs=roofmat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(.22,.245,.26,1)
        bs.inputs['Roughness'].default_value=.78
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=.035
        noise=next((n for n in roofmat.node_tree.nodes if n.type=='TEX_NOISE'),None)
        if noise:
            noise.inputs['Scale'].default_value=8.0
            noise.inputs['Detail'].default_value=2.0

canopy = bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
roof_seam_mat=material('LAMB | roof standing seam highlight',(.105,.125,.14,1),.52,.58)
if canopy:
    r=canopy.dimensions[1]*.5
    # Roof curve is the source model's existing half-cylinder profile.
    z_eave=11.2; rise=canopy.dimensions.z
    long=canopy.dimensions.x
    seam_v=[]; seam_f=[]
    for j in range(25):
        y=-r + (2*r*j/24)
        z=z_eave+rise*math.sqrt(max(0.0,1.0-(y/r)**2))+.025
        b=len(seam_v); width=.045
        seam_v.extend([(-long*.5,y-width,z),(long*.5,y-width,z),
                       (long*.5,y+width,z),(-long*.5,y+width,z)])
        seam_f.append((b,b+1,b+2,b+3))
    mesh_object('LAMB | schematic longitudinal roof seams',seam_v,seam_f,roof_seam_mat,roof)

# Long linear lights hang below the arch; photographic references show a bright
# interior and curved ceiling, while exact luminaire count/spacing is unknown.
light_v=[]; light_f=[]
roof_span=min(99.31,93.84)*.95
roof_r=roof_span*.5
for y in (-20,-10,0,10,20):
    z=11.2+rise*math.sqrt(max(0.0,1.0-(y/roof_r)**2))-.52
    append_box(light_v,light_f,(0,y,z),(70,.17,.12))
mesh_object('LAMB | schematic overhead linear luminaires',light_v,light_f,fixture_mat,interior)

# Discreet athletic banners along the long walls, kept generic because the
# available photographs do not establish the exact banner set or wording.
for side in (-1,1):
    for i,x in enumerate((-34,-23,-12,0,12,23,34)):
        y=side*45.9
        z=8.0
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y,z))
        ob=bpy.context.object; ob.name='LAMB | schematic wall banner'
        ob.dimensions=(4.5,.12,2.1); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(ob.users_collection): c.objects.unlink(ob)
        interior.objects.link(ob); ob.data.materials.append(banner_dark)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y-side*.08,z-0.72))
        band=bpy.context.object; band.name='LAMB | schematic banner gold stripe'
        band.dimensions=(4.5,.035,.15); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(band.users_collection): c.objects.unlink(band)
        interior.objects.link(band); band.data.materials.append(banner_gold)

# Dedicated open-roof interior inspection camera and softboxes live outside the
# exported Asset collection. They are also reused in the building-only preview.
cam_data=bpy.data.cameras.new('LAMB | interior review camera')
cam=bpy.data.objects.new('LAMB | interior review camera',cam_data); rig.objects.link(cam)
cam.location=(-48,-62,12.5); target=Vector((0,0,5.0)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
cam_data.lens=39; cam_data.dof.use_dof=False

def area_light(name, loc, energy, size, color, aim):
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.shape='DISK'; d.size=size; d.color=color
    o=bpy.data.objects.new(name,d); rig.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(aim)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o
area_light('LAMB | interior ceiling softbox A',(-16,-28,15),10000,26,(1.0,.82,.62),(0,0,1))
area_light('LAMB | interior ceiling softbox B',(22,12,15),8500,28,(.75,.84,1.0),(0,0,1))
area_light('LAMB | interior track fill',(0,-4,10),5000,20,(1.0,.9,.76),(0,0,0))

# Keep original exterior camera/settings for the asset's default open state.
original_camera=scene.camera
old_resolution=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1100; scene.render.resolution_y=760; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(.20,.20,.20)
bpy.context.view_layer.update()

# Save first, then reopen the actual saved source before rendering previews.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections['Asset_lambert_fieldhouse']
rig=bpy.data.collections['Preview_Rig']
cam=bpy.data.objects['LAMB | interior review camera']
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')

# Exterior refresh with the persisted default camera.
scene.camera=bpy.data.objects.get('LAMB | three-quarter preview camera') or scene.camera
scene.render.filepath=OUT+r'/exterior_round1.png'
bpy.ops.render.render(write_still=True)

# Interior cutaway preview: hide only outer shell and roof skin for this render;
# restore these flags before final save so the source asset opens complete.
hide_objects=[]
for name in ('LAMB_Structure','LAMB_Facade'):
    col=bpy.data.collections.get(name)
    if col:
        for ob in col.objects:
            hide_objects.append((ob,ob.hide_render)); ob.hide_render=True
if canopy:
    hide_objects.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=cam
scene.render.filepath=OUT+r'/interior_round1.png'
bpy.ops.render.render(write_still=True)
for ob,old in hide_objects: ob.hide_render=old

# Reopen again after preview-only visibility changes, confirming the saved asset
# remains complete and opens with the standard exterior review camera.
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections['Asset_lambert_fieldhouse']
summary={
  'reopen':'PASS',
  'asset_file':'modular/buildings/lambert_fieldhouse.blend',
  'asset_collection':'Asset_lambert_fieldhouse',
  'source_object_count':sum(1 for o in asset.all_objects),
  'interior_object_count':len(bpy.data.collections['LAMB_Interior'].objects),
  'roof_object_count':len(bpy.data.collections['LAMB_Roof'].objects),
  'default_camera':scene.camera.name if scene.camera else None,
  'preview_files':['audit/lambert_fieldhouse/exterior_round1.png','audit/lambert_fieldhouse/interior_round1.png'],
  'track_centerline_m':200.0,
  'track_lanes':6,
  'track_lane_width_estimate_m':lane_width,
  'track_straight_estimate_m':straight,
  'track_radius_derived_m':round(radius,4),
  'unmeasured_roof_and_seating':'schematic; roof material/profile and seating placement lack measured drawings',
  'master_or_manifest_edited':False
}
with open(OUT+r'/validation_round1.json','w') as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2))

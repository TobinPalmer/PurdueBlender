import bpy, json, math, os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/lambert_fieldhouse.blend'
OUT = ROOT + r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
facade = bpy.data.collections['LAMB_Facade']
roof = bpy.data.collections['LAMB_Roof']
interior = bpy.data.collections['LAMB_Interior']

# Make the source script safe to rerun while tuning saved cameras/materials.
for o in list(bpy.data.objects):
    if 'round6' in o.name.lower(): bpy.data.objects.remove(o, do_unlink=True)

def material(name, color, rough=0.7, metal=0.0, emission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = color; m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = color
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    if emission and 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value = color
        bs.inputs['Emission Strength'].default_value = emission
    return m

def cube(name, center, dims, mat, collection):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object; o.name = name; o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o)
    if mat: o.data.materials.append(mat)
    return o

# The archive gives a 303 x 172 ft one-story fieldhouse and a separate 210 x
# 110 ft four-story gym. Convert only those measured plan dimensions. The archive
# and GIS do not register either interior volume to the campus outline, so the
# local allocation below is explicitly illustrative.
fieldhouse_x = 303 * 0.3048
fieldhouse_y = 172 * 0.3048
gym_x = 210 * 0.3048
gym_y = 110 * 0.3048
gym_height = 13.2  # schematic four-level envelope; not a measured height
gym_x0, gym_x1 = -gym_x/2, gym_x/2
gym_y0, gym_y1 = 13.42, 13.42 + gym_y

# Resize the old broad canopy to the archive's fieldhouse dimensions and align
# its northern eave to the illustrative gym connection. The track mesh is not
# edited; its saved 199.989 m centerline perimeter remains unchanged.
canopy = bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy') or bpy.data.objects['LAMB | archival-dimension arched one-story fieldhouse roof (placement schematic)']
old_x = canopy.dimensions.x; old_y = canopy.dimensions.y
old_y_center = sum(v.co.y for v in canopy.data.vertices) / len(canopy.data.vertices)
new_y_center = gym_y0 - fieldhouse_y/2
for v in canopy.data.vertices:
    v.co.x *= fieldhouse_x / old_x
    v.co.y = (v.co.y - old_y_center) * (fieldhouse_y / old_y) + new_y_center
canopy.data.update()
canopy.name = 'LAMB | archival-dimension arched one-story fieldhouse roof (placement schematic)'
for m in canopy.data.materials:
    # The previous HASHED setting let the facade bands/rails show through the
    # roof in the exterior view. The building source supports a covered roof.
    if hasattr(m,'blend_method'): m.blend_method='OPAQUE'
    if m.use_nodes:
        bs=m.node_tree.nodes.get('Principled BSDF')
        if bs and 'Alpha' in bs.inputs: bs.inputs['Alpha'].default_value=1.0

# Remove the former decorative ribs/seams that were generated for the old wide
# roof and no longer fit the archive-sized span; round-six trusses replace them.
for o in list(roof.objects):
    if o.name in ('LAMB | repeated steel roof arch rib','LAMB | schematic longitudinal roof seams'):
        bpy.data.objects.remove(o, do_unlink=True)

# Re-register the pale facade bands to the actual GIS edge directions. The old
# bands had useful segment centers/counts but remained axis-aligned; this rebuild
# computes each segment tangent and normal from the retained footprint mesh.
for o in list(bpy.data.objects):
    if o.name.startswith('LAMB | round5 GIS-edge stone band'):
        bpy.data.objects.remove(o,do_unlink=True)
footprint=bpy.data.objects['Lambert Fieldhouse | official GIS footprint ground floor']
low_ids=[i for i,v in enumerate(footprint.data.vertices) if v.co.z<.08]
neighbors={i:[] for i in low_ids}
for edge in footprint.data.edges:
    a,b=edge.vertices
    if a in neighbors and b in neighbors: neighbors[a].append(b); neighbors[b].append(a)
start=min(low_ids,key=lambda i:(footprint.data.vertices[i].co.x,-footprint.data.vertices[i].co.y))
ring=[start]; previous=None; current=start
while True:
    nxt=next(i for i in neighbors[current] if i!=previous)
    if nxt==start: break
    ring.append(nxt); previous,current=current,nxt
outline=[(footprint.data.vertices[i].co.x,footprint.data.vertices[i].co.y) for i in ring]
area=sum(outline[i][0]*outline[(i+1)%len(outline)][1]-outline[(i+1)%len(outline)][0]*outline[i][1] for i in range(len(outline)))/2
band_mat=bpy.data.materials.get('LAMB | warm pale limestone concrete round5') or material('LAMB | GIS-registered stone bands round6',(.60,.61,.58,1),.82)
band_v=[]; band_f=[]
def append_edge_box(a,b,z,outward_sign=1):
    ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay; length=math.hypot(dx,dy)
    if length<.05:return
    tx,ty=dx/length,dy/length
    # For a CCW boundary, outward is the right-hand normal.
    nx,ny=((ty,-tx) if area>0 else (-ty,tx))
    center_x=(ax+bx)/2+nx*.20; center_y=(ay+by)/2+ny*.20
    half_l=length/2+.05; half_t=.16; half_h=.10; base=len(band_v)
    for s,u,w in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
        band_v.append((center_x+tx*s*half_l+nx*u*half_t,center_y+ty*s*half_l+ny*u*half_t,z+w*half_h))
    band_f.extend([tuple(base+i for i in f) for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
for z in (3.34,5.48,8.75,11.04):
    for i,a in enumerate(outline): append_edge_box(a,outline[(i+1)%len(outline)],z)
band_mesh=bpy.data.meshes.new('LAMB | round6 GIS-registered stone bands mesh')
band_mesh.from_pydata(band_v,[],band_f); band_mesh.materials.append(band_mat); band_mesh.update()
band_obj=bpy.data.objects.new('LAMB | round6 GIS-registered segmented perimeter stone bands',band_mesh)
facade.objects.link(band_obj)

# Replace round-five trusses/purlins with members fitted to the resized canopy.
for o in list(roof.objects):
    if any(key in o.name for key in ('round5 steel arch trusses', 'round5 roof arch purlins')):
        bpy.data.objects.remove(o, do_unlink=True)
steel = material('LAMB | round6 steel roof trusses', (.075,.10,.12,1), .58, .22)
def beam_geom(vs, fs, a, b, width, height=None):
    a, b = Vector(a), Vector(b); d = b-a
    if d.length < .001: return
    h = height if height is not None else width
    q = d.to_track_quat('Z','Y'); center=(a+b)*.5; n=len(vs)
    local=[Vector((sx*width/2, sy*h/2, sz*d.length/2)) for sx,sy,sz in
           ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
    vs.extend([tuple(center+q@p) for p in local])
    fs.extend([tuple(n+i for i in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
def mesh_object(name, vs, fs, mat, col):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(vs,[],fs); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob
roof_ymin, roof_ymax = new_y_center-fieldhouse_y/2, new_y_center+fieldhouse_y/2
roof_xmin, roof_xmax = -fieldhouse_x/2, fieldhouse_x/2
eave, rise = 11.2, 6.46
def roof_z(y):
    dy=y-new_y_center
    return eave + rise*math.sqrt(max(0.0,1.0-(dy/(fieldhouse_y/2))**2)) - .34
trv=[]; trf=[]; ystations=[roof_ymin+i*fieldhouse_y/12 for i in range(13)]
for x in [roof_xmin+4+i*(fieldhouse_x-8)/8 for i in range(9)]:
    top=[(x,y,roof_z(y)-.9) for y in ystations]
    bot=[(x,y,10.55) for y in ystations]
    for i in range(12):
        beam_geom(trv,trf,top[i],top[i+1],.18,.22); beam_geom(trv,trf,bot[i],bot[i+1],.18,.22)
    for i in range(13): beam_geom(trv,trf,bot[i],top[i],.15,.17)
    for i in range(12):
        beam_geom(trv,trf,bot[i],top[i+1],.13,.15) if i%2==0 else beam_geom(trv,trf,top[i],bot[i+1],.13,.15)
mesh_object('LAMB | round6 trusses fitted to archival fieldhouse span',trv,trf,steel,roof)
pv=[]; pf=[]
for dy in (-22,-15,-7.5,0,7.5,15,22):
    y=new_y_center+dy
    if roof_ymin < y < roof_ymax:
        beam_geom(pv,pf,(roof_xmin+1,y,roof_z(y)-1.15),(roof_xmax-1,y,roof_z(y)-1.15),.11,.13)
mesh_object('LAMB | round6 fieldhouse arch purlins',pv,pf,steel,roof)

# Four-story gym wing, with individually readable glazing rows, brick spandrels,
# pale concrete piers and flat roof/parapet. The exact plan allocation is an
# illustration constrained by the archive dims and the broad north GIS region.
brick = bpy.data.materials.get('LAMB | mottled Purdue red-brown brick') or material('LAMB | round6 gym brick',(.39,.14,.085,1),.78)
stone = material('LAMB | round6 gym limestone',(.62,.63,.60,1),.82)
glass = material('LAMB | round6 gym glazing',(.10,.20,.25,1),.24,.08,.03)
metal = material('LAMB | round6 gym window frames',(.17,.20,.21,1),.42,.65)
roofmat = material('LAMB | round6 gym flat roof',(.23,.26,.27,1),.78)
gcol = facade
# Floor slab edges are visible through the repeated window rows, giving the gym
# credible four-level depth without asserting room uses or circulation dimensions.
for floor in range(1,4):
    z=floor*3.25
    cube('LAMB | round6 gym interior floor plate '+str(floor),(0,(gym_y0+gym_y1)/2,z),(gym_x-.7,gym_y-.7,.28),stone,interior)
cube('LAMB | round6 gym roof slab',(0,(gym_y0+gym_y1)/2,gym_height),(gym_x+.7,gym_y+.7,.45),roofmat,gcol)
cube('LAMB | round6 gym parapet north',(0,gym_y1+.18,gym_height+.42),(gym_x+.6,.36,.85),stone,gcol)
cube('LAMB | round6 gym parapet west',(gym_x0-.18,(gym_y0+gym_y1)/2,gym_height+.42),(.36,gym_y+.3,.85),stone,gcol)
cube('LAMB | round6 gym parapet east',(gym_x1+.18,(gym_y0+gym_y1)/2,gym_height+.42),(.36,gym_y+.3,.85),stone,gcol)

# Long public north elevation: transparent main-level storefront plus three upper
# window rows. Repeated bays are shown as visual evidence, not measured spacing.
def facade_long(side_y, outward, label):
    zbase=0
    for x in [gym_x0+i*8 for i in range(9)]:
        cube('LAMB | round6 '+label+' brick pier',(x,side_y,zbase+gym_height/2),(.48,.48,gym_height),brick,gcol)
    # storefront / doors; five clear glazed bays at the public floor
    floor_y=side_y + outward*.27
    for i in range(8):
        x=gym_x0+4+i*8
        if label=='south' and i in (3,4):
            cube('LAMB | round6 gym entry door '+str(i),(x,floor_y,.0+1.35),(5.2,.10,2.7),glass,gcol)
            for dx in (-2.7,2.7): cube('LAMB | round6 gym entry stile',(x+dx,floor_y-outward*.08,1.35),(.12,.16,2.82),metal,gcol)
        else:
            cube('LAMB | round6 gym level one storefront '+str(i),(x,floor_y,1.55),(6.6,.10,2.85),glass,gcol)
            cube('LAMB | round6 storefront transom',(x,floor_y-outward*.08,2.95),(6.72,.12,.12),metal,gcol)
        for level in range(1,4):
            z=level*3.25+1.68
            cube('LAMB | round6 gym '+label+' window L'+str(level)+' B'+str(i),(x,floor_y,z),(4.8,.10,1.62),glass,gcol)
            for dx in (-2.48,2.48): cube('LAMB | round6 gym window jamb',(x+dx,floor_y-outward*.08,z),(.11,.12,1.78),metal,gcol)
            cube('LAMB | round6 gym window head',(x,floor_y-outward*.08,z+.88),(5.08,.12,.12),stone,gcol)
            cube('LAMB | round6 gym window sill',(x,floor_y-outward*.08,z-.88),(5.08,.15,.18),stone,gcol)
    for z in (3.12,6.37,9.62,12.88):
        cube('LAMB | round6 '+label+' story band',(0,side_y+outward*.2,z),(gym_x,.32,.22),stone,gcol)
facade_long(gym_y1,1,'north')
facade_long(gym_y0,-1,'south')

# The short end walls have four-story window groups at a finer bay cadence.
for side_x, label in ((gym_x0-.12,'west'),(gym_x1+.12,'east')):
    for y in [gym_y0+4+i*8 for i in range(4)]:
        cube('LAMB | round6 gym '+label+' brick pier',(side_x,y,gym_height/2),(.48,.5,gym_height),brick,gcol)
        for level in range(4):
            z=level*3.25+1.65
            cube('LAMB | round6 gym '+label+' window L'+str(level),(side_x,y,z),(.10,4.8,1.55),glass,gcol)
            for dy in (-2.48,2.48): cube('LAMB | round6 gym end jamb',(side_x+(.1 if label=='east' else -.1),y+dy,z),(.12,.12,1.72),metal,gcol)
            cube('LAMB | round6 gym end lintel',(side_x,y,z+.85),(.13,5.05,.13),stone,gcol)

# Convert both historical sizes to feet in a sidecar and attach every uncertainty
# to the asset/evidence rather than claiming surveyed positions or story heights.
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']; n=len(track.data.vertices)//2
centers=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((centers[(i+1)%n]-centers[i]).length for i in range(n))

# Identify historic tower as conjecture and lower its prominence, keeping postcard
# evidence visible but unambiguously non-current/unverified.
tower=bpy.data.objects.get('LAMB | round5 schematic historic entrance tower') or bpy.data.objects.get('LAMB | historic-only postcard tower conjecture — current survival unverified')
for o in bpy.data.objects:
    if 'round5 tower' in o.name.lower() or 'historic-only postcard tower' in o.name.lower():
        if o is tower: o.name='LAMB | historic-only postcard tower conjecture — current survival unverified'
        o.hide_render=True; o.hide_set(True)

# Keep the source-supported balcony hint inside the narrowed hall span instead
# of leaving its rails outside the roof on both long sides.
for o in bpy.data.objects:
    if 'balcony' not in o.name.lower(): continue
    positive=o.location.y>0
    if 'upper spectator balcony deck' in o.name:
        o.location.y=10.8 if positive else -35.5
    else:
        o.location.y=9.0 if positive else -33.6

# More legible view down the hall toward the open connection/gym frontage.
cam=bpy.data.objects.get('LAMB | interior review camera')
if cam:
    cam.location=(42,-55,20); target=Vector((0,0,7)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=30

bpy.context.scene.render.engine='CYCLES' if bpy.context.scene.render.engine=='CYCLES' else bpy.context.scene.render.engine
bpy.context.scene.render.resolution_x=1280; bpy.context.scene.render.resolution_y=800; bpy.context.scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
roof=bpy.data.collections['LAMB_Roof']
exterior_cam=bpy.data.objects['LAMB | three-quarter preview camera']
exterior_cam.location=(112,118,50); exterior_target=Vector((0,0,7)); exterior_cam.rotation_euler=(exterior_target-Vector(exterior_cam.location)).to_track_quat('-Z','Y').to_euler(); exterior_cam.data.lens=48
scene.camera=exterior_cam
# The covering is opaque in this view; suppress the internal steel in the
# exterior render so that it reads as structure below the roof, not as lines
# floating through the roof skin.
roof_visibility=[(o,o.hide_render) for o in roof.objects]
canopy=bpy.data.objects['LAMB | archival-dimension arched one-story fieldhouse roof (placement schematic)']
for o in roof.objects:
    if o is not canopy: o.hide_render=True
scene.render.filepath=OUT+r'/exterior_round6.png'; bpy.ops.render.render(write_still=True)
# Cutaway: hide outer shell and roof, but retain facade wing and interior plates,
# track, balconies and lighting to show the connected building at eye level.
hidden=[]
for cname in ('LAMB_Structure','LAMB_Facade'):
    c=bpy.data.collections.get(cname)
    if c:
        for o in c.objects: hidden.append((o,o.hide_render)); o.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']
canopy=bpy.data.objects.get('LAMB | archival-dimension arched one-story fieldhouse roof (placement schematic)')
if canopy: hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
for o in roof.objects:
    if o is not canopy: o.hide_render=False
for o in bpy.data.objects:
    if o.name.startswith('LAMB | round6 gym interior floor plate') or o.name.startswith('LAMB | round5 generic meet display') or o.name.startswith('LAMB | round5 display segment'):
        hidden.append((o,o.hide_render)); o.hide_render=True
    if o.type=='LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower()): o.hide_render=False
scene.render.filepath=OUT+r'/interior_round6.png'; bpy.ops.render.render(write_still=True)
for o,val in hidden: o.hide_render=val
for o,val in roof_visibility: o.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)

report={'revision':6,'saved_and_reopened':'PASS','asset_file':'modular/buildings/lambert_fieldhouse.blend',
 'archive_documented_volumes':{'one_story_fieldhouse_plan_m':{'length':fieldhouse_x,'width':fieldhouse_y},'four_story_gym_plan_m':{'length':gym_x,'width':gym_y},'gym_height_m':'schematic, four-level envelope only'},
 'illustrative_local_allocation':{'gym_bounds_xy_m':[gym_x0,gym_x1,gym_y0,gym_y1],'fieldhouse_roof_bounds_xy_m':[roof_xmin,roof_xmax,roof_ymin,roof_ymax], 'registration':'GIS footprint constrains outer campus plan; archive records do not place the internal volumes. This arrangement is illustrative, not surveyed.'},
 'historic_tower':'historical postcard conjecture only; present survival/location/dimensions unverified',
 'track':{'lane_count':6,'boundary_count':7,'measured_lane_one_centerline_perimeter_m':perimeter,'geometry_changed':False},
 'previews':['audit/lambert_fieldhouse/exterior_round6.png','audit/lambert_fieldhouse/interior_round6.png'],
 'master_manifest_shared_files_edited':False}
with open(OUT+r'/validation_round6.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))

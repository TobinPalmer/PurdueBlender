"""Build a source-informed detailed Yue-Kong Pao Hall asset.

Run with Blender 5.2:
  blender --background modular/buildings/massing_yue_kong_pao_hall_a3cb766.blend \
    --python modular/buildings/build_massing_yue_kong_pao_hall_a3cb766.py

This is intentionally an asset-local builder; it does not open or edit the campus master.
The source footprint remains in the campus coordinate frame used by the existing massing
library. Interior room arrangement is illustrative because no floor plan was available.
"""
import bpy, math, json, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET_ID = 'massing_yue_kong_pao_hall_a3cb766'
ASSET_FILE = os.path.join(os.path.dirname(__file__), ASSET_ID + '.blend')
AUDIT = os.path.join(ROOT, 'audit', 'yue_kong_pao_hall')
os.makedirs(AUDIT, exist_ok=True)
scene = bpy.context.scene
col_name = 'Asset_' + ASSET_ID
col = bpy.data.collections.get(col_name)
if col is None:
    raise RuntimeError('Expected stable asset collection is missing: ' + col_name)
base = bpy.data.objects.get('Yue-Kong Pao Hall')
if base is None or base.type != 'MESH':
    raise RuntimeError('Expected original massing mesh is missing')

# Read and preserve the pre-existing massing outline. The first 32 vertices are its ground ring.
bottom = [v.co.copy() for v in base.data.vertices if abs(v.co.z) < 1e-5]
if len(bottom) < 16:
    raise RuntimeError('Unexpectedly small source footprint ring')
footprint = [(float(v.x), float(v.y)) for v in bottom]
if footprint[0] == footprint[-1]:
    footprint.pop()
N = len(footprint)
old_bounds = [[min(x for x, y in footprint), max(x for x, y in footprint)],
              [min(y for x, y in footprint), max(y for x, y in footprint)],
              [0.0, max(float(v.co.z) for v in base.data.vertices)]]

# Keep the project's familiar material names while replacing the massing library's untextured
# default node color with portable, procedural PBR materials. These are asset-local copies.
brick = bpy.data.materials.get('Purdue_Red_Brick')
limestone = bpy.data.materials.get('Indiana_Bedford_Limestone')

def mat(name, color, metallic=0.0, rough=0.5, transmission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    if 'Transmission Weight' in bs.inputs:
        bs.inputs['Transmission Weight'].default_value = transmission
    elif 'Transmission' in bs.inputs:
        bs.inputs['Transmission'].default_value = transmission
    nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    return m

brick = mat('Purdue_Red_Brick', (.30, .105, .065), rough=.84)
limestone = mat('Indiana_Bedford_Limestone', (.69, .64, .52), rough=.72)
# Object-space brick pattern (physical-scale brick units) with shallow mortar relief; this works
# on every generated wall panel without UV unwraps or external image paths.
nt=brick.node_tree
bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
tc=nt.nodes.new('ShaderNodeTexCoord'); tc.location=(-820,180)
mapping=nt.nodes.new('ShaderNodeMapping'); mapping.location=(-630,180)
mapping.inputs['Scale'].default_value=(1.0,1.0,1.0)
uv=nt.nodes.new('ShaderNodeUVMap'); uv.location=(-830,80); uv.uv_map='PAO_WallUV'
nt.links.new(uv.outputs['UV'],mapping.inputs['Vector'])
bt=nt.nodes.new('ShaderNodeTexBrick'); bt.location=(-400,240)
bt.offset=0.5; bt.offset_frequency=2; bt.squash=1.0; bt.squash_frequency=2
bt.inputs['Color1'].default_value=(.34,.115,.068,1)
bt.inputs['Color2'].default_value=(.245,.065,.042,1)
bt.inputs['Mortar'].default_value=(.18,.145,.12,1)
bt.inputs['Scale'].default_value=2.5
bt.inputs['Mortar Size'].default_value=.014
bt.inputs['Mortar Smooth'].default_value=.004
bt.inputs['Brick Width'].default_value=.50
bt.inputs['Row Height'].default_value=.24
nt.links.new(mapping.outputs['Vector'],bt.inputs['Vector'])
nt.links.new(bt.outputs['Color'],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump'); bump.location=(-100,-30)
bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.035
nt.links.new(bt.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
glass = mat('PAO | blue-gray reflective glazing', (.035, .11, .19), metallic=.28, rough=.24, transmission=.05)
frame = mat('PAO | anodized silver mullions', (.66, .69, .68), metallic=.72, rough=.28)
roofmat = mat('PAO | charcoal standing-seam roof', (.12, .12, .115), metallic=0.0, rough=.96)
concrete = limestone
interior_wall = mat('PAO | warm gallery plaster', (.72, .67, .56), rough=.86)
dark = mat('PAO | theatre acoustic black', (.025, .03, .035), rough=.9)
wood = mat('PAO | maple studio floor', (.52, .30, .13), rough=.55)
seatmat = mat('PAO | theatre seat burgundy', (.32, .035, .045), rough=.72)
lightmat = mat('PAO | warm interior light', (1.0, .67, .29), rough=.3)
signmat = mat('PAO | warm white lettering', (.88, .83, .69), metallic=.25, rough=.32)

# Remove old single extrusion and generated details from a prior run, retaining original materials.
for obj in list(col.objects):
    if obj == base:
        continue
    bpy.data.objects.remove(obj, do_unlink=True)
old_data = base.data
bpy.data.objects.remove(base, do_unlink=True)
if old_data.users == 0:
    bpy.data.meshes.remove(old_data)

def link_mesh(name, verts, faces, material, bevel=0.0, uvs=None):
    me = bpy.data.meshes.new(name + 'Mesh')
    me.from_pydata(verts, [], faces); me.materials.append(material); me.update()
    if uvs is not None:
        layer=me.uv_layers.new(name='PAO_WallUV')
        for loop in me.loops:
            layer.data[loop.index].uv=uvs[loop.vertex_index]
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    if bevel > 0:
        mod = ob.modifiers.new('Soft arris', 'BEVEL'); mod.width=bevel; mod.segments=2
        mod2=ob.modifiers.new('Weighted architectural normals','WEIGHTED_NORMAL')
    return ob

def box(name, center, dims, material, angle=0.0, bevel=0.0):
    x,y,z=center; sx,sy,sz=[float(v) for v in dims]
    a=angle; c=math.cos(a); s=math.sin(a)
    corners=[]
    for dz in (-sz/2,sz/2):
        for dy in (-sy/2,sy/2):
            for dx in (-sx/2,sx/2):
                corners.append((x+dx*c-dy*s,y+dx*s+dy*c,z+dz))
    # corner order: bottom back-left, bottom back-right, bottom front-left, bottom front-right,
    # then same top. Build six consistently closed quad faces.
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    uvs=[]
    for dz in (-sz/2,sz/2):
        for dy in (-sy/2,sy/2):
            for dx in (-sx/2,sx/2): uvs.append((dx+sx/2,dz+sz/2))
    return link_mesh(name,corners,faces,material,bevel,uvs if material==brick else None)

def oriented_wall(name, p1, p2, z0, z1, thickness, material):
    dx=p2[0]-p1[0]; dy=p2[1]-p1[1]; L=math.hypot(dx,dy)
    if L < .02 or z1 <= z0: return None
    return box(name,((p1[0]+p2[0])/2,(p1[1]+p2[1])/2,(z0+z1)/2),(L+.025,thickness,z1-z0),material,math.atan2(dy,dx))

def surface(name, points, z, material):
    return link_mesh(name,[(x,y,z) for x,y in points],[tuple(range(len(points)))],material)

def point_on_south(x):
    # Main public-plaza edge, reconstructed from the source footprint's east-west arc.
    # Use only the ordered southern footprint arc; the long north wall has similar X values and
    # would otherwise drag right-hand windows onto the rear elevation.
    candidates=sorted([(footprint[i][0],footprint[i][1]) for i in range(6,21)],key=lambda p:p[0])
    # Collapse tiny x reversals along the curved edge to its southernmost point.
    grouped={}
    for px,py in candidates:
        key=round(px,2); grouped[key]=min(py,grouped.get(key,py))
    candidates=sorted(grouped.items())
    if x <= candidates[0][0]: return candidates[0][1]
    for (x1,y1),(x2,y2) in zip(candidates,candidates[1:]):
        if x1 <= x <= x2:
            return y1+(y2-y1)*(x-x1)/(x2-x1)
    return candidates[-1][1]

def add_south_wall_segment(i, p1, p2, ztop, window_intervals):
    # South wall ground edge includes very shallow points and a few step-backs. Build each
    # segment as a physically thin masonry wall and leave real apertures for glazed bays.
    x1,y1=p1; x2,y2=p2
    if x2 < x1:
        x1,y1,x2,y2=x2,y2,x1,y1
    if x2-x1 < .05:
        return oriented_wall('South masonry return %02d'%i,(x1,y1),(x2,y2),0,ztop,.38,brick)
    ts={0.0,1.0}
    for left,right,bottomz,topz,tag in window_intervals:
        for xx in (left,right):
            if x1+0.001 < xx < x2-0.001: ts.add((xx-x1)/(x2-x1))
    ts=sorted(ts)
    angle=math.atan2(y2-y1,x2-x1)
    for j,(ta,tb) in enumerate(zip(ts,ts[1:])):
        xa=x1+(x2-x1)*ta; xb=x1+(x2-x1)*tb
        ya=y1+(y2-y1)*ta; yb=y1+(y2-y1)*tb
        mid=(xa+xb)/2
        active=[(bz,tz,tag) for l,r,bz,tz,tag in window_intervals if l-1e-4 <= mid <= r+1e-4]
        ranges=[(0,ztop)] if not active else [(0,active[0][0]),(active[0][1],ztop)]
        for k,(z0,z1) in enumerate(ranges):
            if z1-z0<.04: continue
            oriented_wall('South brick pier %02d_%02d_%02d'%(i,j,k),(xa,ya),(xb,yb),z0,z1,.44,brick)

# The facade apertures are placed where the visible official south elevation has a long band of
# vertically extended reflective glazing. The west lobby entry is documented in the photo.
window_intervals=[]
door=(22.0,26.2,0.0,3.4,'lobby entry')
window_intervals.append(door)
for idx,cx in enumerate([39.5,46.0,52.5,59.0,65.5,72.0,78.5,85.0,91.0]):
    window_intervals.append((cx-2.05,cx+2.05,1.35,9.55,'glazed bay %02d'%idx))

H=16.0
SOUTH_ROOF=11.5
ROOF_STEP_Y=-541.0
def roof_height_at(y):
    # Exterior reference shows a low south/plaza wing with a taller, set-back performance volume.
    if y <= -560.0: return SOUTH_ROOF
    if y >= ROOF_STEP_Y: return H
    return SOUTH_ROOF+(H-SOUTH_ROOF)*(y+560.0)/(ROOF_STEP_Y+560.0)

def variable_wall(name,p1,p2,thickness,material):
    dx=p2[0]-p1[0]; dy=p2[1]-p1[1]; L=math.hypot(dx,dy)
    if L<.02:return None
    nx=-dy/L*thickness/2; ny=dx/L*thickness/2
    x1,y1=p1; x2,y2=p2; h1=roof_height_at(y1); h2=roof_height_at(y2)
    vs=[(x1+nx,y1+ny,0),(x2+nx,y2+ny,0),(x2-nx,y2-ny,0),(x1-nx,y1-ny,0),
        (x1+nx,y1+ny,h1),(x2+nx,y2+ny,h2),(x2-nx,y2-ny,h2),(x1-nx,y1-ny,h1)]
    fs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return link_mesh(name,vs,fs,material)

# Build perimeter as thin walls, retaining the pre-existing campus placement and footprint.
# Segments spanning indexes 6..19 form the south/plaza elevation; all others are solid masonry.
for i,(p1,p2) in enumerate(zip(footprint,footprint[1:]+footprint[:1])):
    if 6 <= i <= 19 and p2[0] > p1[0]-0.01 and p1[0] < 100 and p2[0] > 17:
        add_south_wall_segment(i,p1,p2,SOUTH_ROOF,window_intervals)
    else:
        variable_wall('Perimeter brick wall %02d'%i,p1,p2,.42,brick)

# One central and two side roof tiers break up the mass instead of leaving a featureless slab.
# The imagery shows a low public frontage and taller backstage/theatre volume behind it.
def clip_horizontal(poly,yclip,keep_north):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ina=(a[1]>=yclip) if keep_north else (a[1]<=yclip)
        inb=(b[1]>=yclip) if keep_north else (b[1]<=yclip)
        if ina: result.append(a)
        if ina != inb:
            t=(yclip-a[1])/(b[1]-a[1]); result.append((a[0]+(b[0]-a[0])*t,yclip))
    # Drop coincident points introduced by vertices exactly on the clipping line.
    clean=[]
    for p in result:
        if not clean or math.dist(p,clean[-1])>.01: clean.append(p)
    if len(clean)>2 and math.dist(clean[0],clean[-1])<.01: clean.pop()
    return clean
south_roof=clip_horizontal(footprint,ROOF_STEP_Y,False)
north_roof=clip_horizontal(footprint,ROOF_STEP_Y,True)
if len(south_roof)<3 or len(north_roof)<3: raise RuntimeError('Roof-step clipping did not produce valid plan polygons')
box('Low south wing roof slab',(63.5,-555.5,SOUTH_ROOF),(88,29,.38),roofmat,0,.06)
box('High north performance roof slab',(60.5,-524.25,H),(94,32.5,.38),roofmat,0,.06)
box('Step-back theater wall',(60.5,ROOF_STEP_Y+.15,(SOUTH_ROOF+H)/2),(94,.42,H-SOUTH_ROOF),brick,0,.03)
for seam_y in (-560,-552,-544):
    box('Low roof standing seam',(63.5,seam_y,SOUTH_ROOF+.20),(87,.055,.045),frame,0,.01)
box('Roof penthouse | stage and rehearsal volume',(66,-534.0,17.35),(40,23,2.7),brick,0,.22)
box('Roof penthouse standing seam cap',(66,-534.0,18.78),(40.5,23.5,.18),roofmat,0,.05)
box('Roof equipment screen west',(37,-527.0,16.75),(12,7,1.5),roofmat,0,.12)
box('Roof equipment screen east',(91,-525.0,16.65),(10,8,1.3),roofmat,0,.12)
for x in (33,36,39,93,96):
    box('Rooftop mechanical louver',(x,-523.5,16.7),(1.5,2.6,1.2),frame,0,.05)

# Floors are simple polished concrete planes within the shell. Exact historic plan layouts were not
# located; the room arrangements below are explicitly illustrative and only serve to add readable
# interior depth behind the south glazing.
for floor,z in enumerate([.25,3.25,6.25,9.25,12.25,15.25]):
    if z<=SOUTH_ROOF:
        surface('Interior floor plate %02d'%floor,footprint,z,concrete)
    else:
        box('Interior floor plate %02d'%floor,(60.5,-524.25,z),(92,30,.18),concrete,0,.02)

# Clearly readable first-floor arts/public zone: lobby, gallery and flexible rehearsal / theatre.
# We keep the room groups schematic and avoid asserting undocumented room positions.
box('Entry lobby ceiling soffit',(25,-552,3.05),(13,16,.22),interior_wall,0,.03)
box('Lobby welcome desk',(26,-560.3,1.4),(4.6,1.1,1.2),wood,0,.08)
box('Gallery display wall',(41,-548,1.8),(.22,19,2.9),interior_wall,0,.01)
box('Flexible studio floor',(69,-541,1.0),(25,22,.12),wood,0,.02)
box('Studio mirror wall',(80,-552,2.5),(.08,13,2.2),glass,0)
box('Black-box theatre acoustic room',(75,-520,2.25),(25,20,4.0),dark,0,.04)
box('Black-box stage',(75,-512,1.2),(15,3.5,.45),wood,0,.03)
# A modest set of audience seating rows gives the small practice/studio theatre readable scale.
for row in range(5):
    yy=-526+row*1.45
    for colidx in range(9):
        xx=66+colidx*2.15
        box('Studio theatre seat %02d-%02d'%(row,colidx),(xx,yy,1.45+row*.20),(1.25,.68,.68),seatmat,0,.05)
# Upper dance and instruction levels, represented with studios, a small classroom and support rooms.
for level,zbase in enumerate((4.4,7.4,10.4)):
    # Two shared dance studio floors with mirrors and barre lines.
    box('Dance studio maple floor %02d'%level,(44,-538,zbase),(24,23,.12),wood,0,.02)
    box('Dance studio mirror %02d'%level,(56,-548,zbase+1.5),(.08,18,2.2),glass,0)
    box('Dance barre %02d'%level,(55,-548.5,zbase+.75),(0.15,15,.10),frame,0)
    # Classroom / music teaching room hints further to the east.
    box('Music classroom floor %02d'%level,(92,-543,zbase),(12,19,.10),interior_wall,0,.01)
    for n in range(4):
        box('Classroom worktable %02d-%02d'%(level,n),(90+n%2*4,-538+(n//2)*4,zbase+.48),(2.7,1.3,.1),wood,0,.03)

# Assemble glazing units with aluminum frames, mullions and horizontal transoms.
south_windows=[]
for a,b,bz,tz,tag in window_intervals:
    cx=(a+b)/2; yy=point_on_south(cx)-.28
    width=b-a; height=tz-bz; zc=(bz+tz)/2
    # Tinted insulated glass in the true wall opening.
    box('Glazing | '+tag,(cx,yy,zc),(width-.16,.10,height-.12),glass,math.atan2(point_on_south(min(b,99))-point_on_south(max(a,15)),max(.001,b-a)),.015)
    ang=math.atan2(point_on_south(min(b,99))-point_on_south(max(a,15)),max(.001,b-a))
    # frame geometry is aligned to the approximate east-west elevation
    for xoff in (-width/2,width/2):
        box('Window jamb',(cx+xoff,yy-.065,zc),(.12,.16,height+.08),frame,ang,.015)
    for zoff in (-height/2,height/2):
        box('Window head-sill',(cx,yy-.065,zc+zoff),(width,.16,.13),frame,ang,.015)
    if 'entry' not in tag:
        # Two vertical mullions and two transoms create the observed tall multi-storey rhythm.
        for xoff in (-width/6,width/6):
            box('Glazing vertical mullion',(cx+xoff,yy-.09,zc),(.085,.17,height),frame,ang,.01)
        for zfrac in (-.16,.16):
            box('Glazing horizontal transom',(cx,yy-.09,zc+height*zfrac),(width,.17,.095),frame,ang,.01)
    else:
        box('Lobby double door split',(cx,yy-.10,zc),(.08,.18,height),frame,ang,.01)
        box('Lobby pull bar',(cx-.55,yy-.15,zc),(0.05,.08,1.0),signmat,ang,.01)
        box('Lobby pull bar',(cx+.55,yy-.15,zc),(0.05,.08,1.0),signmat,ang,.01)
    south_windows.append({'label':tag,'center_xy_m':[round(cx,3),round(yy,3)],'width_m':round(width,2),'height_m':round(height,2),'z_m':[round(bz,2),round(tz,2)]})

# Regular punched windows on the north and east service elevations, consistent with the exterior
# photographs while keeping the southern facade's distinctive continuous glazing as the focus.
for side_y in (-510.0,):
    for x in (31,38,45,87,94):
        for z in (4.4,7.4,10.4,13.4):
            box('North clerestory glass',(x,side_y,z),(2.5,.10,1.3),glass,0,.01)
            for dx in (-1.30,1.30): box('North window jamb',(x+dx,side_y-.07,z),(.09,.16,1.42),frame,0,.01)

# Thin facade banding, Bedford limestone plinth, sill, coping, and vertical pilaster rhythm.
for x in (30,35.7,43.3,49.8,56.3,62.8,69.3,75.8,82.3,88.8,95):
    y=point_on_south(x)-.22
    box('South facade limestone base',(x,y,.34),(5.2,.22,.46),limestone,0,.025)
for x in (36.6,42.4,49.0,55.5,62.0,68.5,75.0,81.5,88.0,94.5):
    y=point_on_south(x)-.26
    box('Brick pier limestone cap',(x,y,9.72),(0.24,.28,.28),limestone,0,.015)
    box('South facade brick course',(x,y,10.05),(.28,.16,.10),brick,0,.008)
for x in (18.0,31.0,91.5,102.0):
    # facade vertical expansion joints are a visible detail in the official exterior photo
    y=point_on_south(min(max(x,20),98))-.23
    box('Vertical facade expansion joint',(x,y,SOUTH_ROOF/2),(.055,.055,SOUTH_ROOF-.35),dark,0,.005)
box('South parapet limestone coping',(64,-567.0,SOUTH_ROOF-.05),(78,.52,.20),limestone,0,.03)

# Main name band, converted to a mesh to avoid font dependencies in the asset.
cu=bpy.data.curves.new('Pao Hall sign lettering','FONT'); cu.body='YUE-KONG PAO HALL  •  VISUAL AND PERFORMING ARTS'; cu.size=.78; cu.extrude=.012; cu.bevel_depth=.003
txt=bpy.data.objects.new('Yue-Kong Pao Hall facade lettering',cu); col.objects.link(txt)
facade_angle=math.atan2(point_on_south(82)-point_on_south(42),40.0)
txt.location=(42,point_on_south(42)-1.10,10.05); txt.rotation_euler=(math.pi/2,0,facade_angle); txt.data.materials.append(signmat)
bpy.context.view_layer.objects.active=txt; txt.select_set(True); bpy.ops.object.convert(target='MESH'); txt=bpy.context.object; txt.name='Yue-Kong Pao Hall facade lettering'; txt.select_set(False)

# Low brick-and-stone canopy over the western lobby door.
door_y=point_on_south(24)-.95
box('West entry canopy',(24,door_y,4.0),(9.0,2.7,.38),roofmat,0,.08)
for x in (20.0,28.0):
    box('Entry canopy column',(x,door_y-.75,2.2),(.28,.28,3.6),limestone,0,.025)

# Warm lobby lighting and visible furnishings are restrained and wholly inside the shell.
for x in (22,27,32):
    box('Lobby pendant',(x,-555,2.75),(.20,.20,.08),lightmat,0,.02)
    box('Lobby pendant stem',(x,-555,2.98),(.035,.035,.42),frame)

# Material and coordinate metadata are embedded in the asset library for integration review.
col['asset_id']=ASSET_ID
col['coordinate_convention']='campus coordinates in metres; direct-link massing asset'
col['source_footprint']='Original stable massing ring; compared with Purdue GIS FID 72 in EPSG:3857'
col['height_status']='16 m source massing retained as estimated; ArcGIS Extrution=60 has unknown unit metadata'
col['interior_status']='Illustrative spaces based on Purdue-reported program; plan arrangement not sourced'
scene['asset_id']=ASSET_ID
scene['building_name']='Yue-Kong Pao Hall of Visual and Performing Arts'
scene['asset_evidence_folder']='audit/yue_kong_pao_hall'

# Remove only now-unused original source mesh; keep its library materials for portability.
for image in bpy.data.images:
    if image.source == 'FILE' and image.packed_file is None:
        try: image.pack()
        except Exception as e: print('PACK IMAGE WARNING',image.name,str(e))

# Keep simple massing assets in campus coordinates; this is not an instance-based detailed asset.
bpy.ops.wm.save_as_mainfile(filepath=ASSET_FILE, compress=True)

report={
 'asset_id':ASSET_ID,'asset_file':os.path.relpath(ASSET_FILE,ROOT).replace('\\','/'),
 'source_asset_sha256_before':'96660c74961004f3af62c79241f439ff556f1ec5cb8b4d6ad9c1b7317dcd7261',
 'source_shape_vertices':N,'source_bounds_xyz_m':old_bounds,'campus_xy_preserved':True,
 'model_estimated_envelope_height_m':18.87,
 'geometry_changes':['Replaced single solid extrusion by thin perimeter walls with a lower 11.5 m south/front wing and a higher 16 m set-back north performance wing, matching the roof step visible in the exterior photo.','Added 6 illustrative interior floor plates (upper plates restricted to the high north wing).','Built 10 ground-level glazing openings (one lobby entry and nine tall glazed bays) on the south/plaza facade with aluminum mullions and transoms.','Added stepped roof decks, a 2.7 m raised backstage/rehearsal penthouse, and screened roof equipment.','Added facade base stone, parapet coping, vertical expansion joints, and mesh-converted facade lettering.','Added schematic lobby, gallery, flexible studio, black-box rehearsal theater seating, dance studio mirrors, and music teaching furniture.'],
 'source_window_bays':south_windows,
 'source_footprint_xy_m':[[round(x,6),round(y,6)] for x,y in footprint],
 'footprint_warning':'The source mesh perimeter is a simplified massing outline, not a surveyed wall line. Its GIS candidate bounds are close but do not verify all wall offsets.',
 'height_warning':'GIS layer has NUM_LEVELS=6 and Extrution=60 but its field documentation does not expose units. Existing 16 m massing height retained; roof penthouse raises modeled silhouette to 18.87 m.',
 'interior_warning':'Interior program names are supported by Purdue facilities/archives pages, but detailed room positions and floor distribution are representative assumptions because no floor-plan source was found.',
 'reference_photo':'Purdue official PAO exterior image, retrieved 2026-10-25; used for south facade window/sign rhythm; not included as a material dependency.',
 'reference_ortho':'Esri World Imagery MapServer export (EPSG:3857), retrieval 2026-10-25; used for footprint context/orientation; source imagery acquisition date is not exposed in export.'
}
with open(os.path.join(AUDIT,'build_report.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('PAO_BUILD_COMPLETE',json.dumps({'objects':len(col.objects),'vertices':sum(len(o.data.vertices) for o in col.objects if o.type=='MESH'),'bounds':old_bounds,'asset':ASSET_FILE}))

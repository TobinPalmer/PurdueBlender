"""Build the GIS-footprint-derived north Mackey athletics wing into its standalone asset.

Safe target: modular/buildings/mackey_arena.blend only. No master/index edits.
"""
import bpy, json, math, bmesh
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'mackey_arena.blend'
SOURCE = ROOT / 'audit' / 'mackey_arena' / 'mackey_footprint_source.json'
TRACE = ROOT / 'audit' / 'mackey_arena' / 'mackey_roof_trace.json'

# Stadium architectural height is estimated from the official three-level use and
# the GIS extrusion attribute (47, likely feet; no field unit metadata is supplied).
WING_HEIGHT = 14.3
ANCHOR = (-209.59000396728516, 671.8374938964844)
LEVELS = 3
FLOOR_HEIGHT = WING_HEIGHT / LEVELS

with open(SOURCE, encoding='utf-8') as f:
    source = json.load(f)
with open(TRACE, encoding='utf-8') as f:
    trace = json.load(f)
feature = source['feature']
points = [tuple(p) for p in trace['north_sdac_footprint_local']]
perimeter_traces = trace['one_story_perimeter_additions']
if len(points) < 4 or not perimeter_traces:
    raise RuntimeError('Photo-registered Mackey roof trace is incomplete')

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections.get('Asset_mackey_arena')
if not asset:
    raise RuntimeError('Expected Asset_mackey_arena collection is missing')
# Idempotent regeneration of this subcomponent.
for obj in list(asset.objects):
    if obj.name.startswith(('MACK_SDAC_', 'MACK_PERIM_')):
        bpy.data.objects.remove(obj, do_unlink=True)

# Use the existing Mackey materials and add a matte roof membrane.
def mat(name, color, roughness=0.6, metallic=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return m
brick = bpy.data.materials.get('MACK_Purdue_Red_Brick') or mat('MACK_Purdue_Red_Brick', (0.31,0.09,0.04))
brickwork = mat('MACK_SDAC_Brickwork_Procedural', (0.38,0.13,0.075), 0.82)
# A restrained real-scale brick pattern and shallow mortar relief based on the HNTB facade photographs.
bnodes = brickwork.node_tree.nodes; bshader = bnodes.get('Principled BSDF')
btex = bnodes.new('ShaderNodeTexBrick'); btex.inputs['Color1'].default_value=(0.40,0.14,0.08,1); btex.inputs['Color2'].default_value=(0.27,0.075,0.045,1); btex.inputs['Mortar'].default_value=(0.19,0.16,0.14,1); btex.inputs['Scale'].default_value=1.0; btex.inputs['Mortar Size'].default_value=0.018; btex.inputs['Brick Width'].default_value=0.55; btex.inputs['Row Height'].default_value=0.24
# Facade meshes receive explicit metre-scaled planar UVs below. A single XYZ
# mapping gives vertical stripes on north/south-facing walls, so do not use it.
bcoord=bnodes.new('ShaderNodeTexCoord'); brickwork.node_tree.links.new(bcoord.outputs['UV'],btex.inputs['Vector']); brickwork.node_tree.links.new(btex.outputs['Color'],bshader.inputs['Base Color'])
bump=bnodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.16; bump.inputs['Distance'].default_value=0.025; brickwork.node_tree.links.new(btex.outputs['Fac'],bump.inputs['Height']); brickwork.node_tree.links.new(bump.outputs['Normal'],bshader.inputs['Normal'])
glass = mat('MACK_SDAC_Insulated_Glazing', (0.08,0.16,0.22), 0.2, 0.08)
glass.diffuse_color = (0.08,0.16,0.22,0.55)
glass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value = 0.55
glass.surface_render_method = 'DITHERED'
bronze = bpy.data.materials.get('MACK_Bronze_Mullion') or mat('MACK_Bronze_Mullion', (0.22,0.17,0.13), 0.35, 0.55)
stone = bpy.data.materials.get('MACK_Bedford_Limestone') or mat('MACK_Bedford_Limestone', (0.82,0.79,0.72))
roof_mat = mat('MACK_SDAC_Roof_Membrane', (0.12,0.13,0.14), 0.85)
concrete = bpy.data.materials.get('MACK_Radial_Buttress_Concrete') or mat('MACK_Radial_Buttress_Concrete', (0.58,0.57,0.55))
hardwood = bpy.data.materials.get('MACK_Keady_Hardwood_Maple') or mat('MACK_Keady_Hardwood_Maple', (0.32,0.2,0.12))
# Fine, restrained maple variation reads as a finished sports floor without
# inventing painted plank divisions or a particular court branding.
hn=hardwood.node_tree.nodes;hs=next(n for n in hn if n.type=='BSDF_PRINCIPLED')
noise=hn.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6.0;noise.inputs['Detail'].default_value=2.0;noise.inputs['Roughness'].default_value=0.68
coord=hn.new('ShaderNodeTexCoord');hardwood.node_tree.links.new(coord.outputs['Object'],noise.inputs['Vector'])
ramp=hn.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=0.20;ramp.color_ramp.elements[0].color=(0.27,0.14,0.065,1)
ramp.color_ramp.elements[1].position=0.82;ramp.color_ramp.elements[1].color=(0.45,0.285,0.14,1)
hardwood.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);hardwood.node_tree.links.new(ramp.outputs['Color'],hs.inputs['Base Color'])
white = bpy.data.materials.get('MACK_Court_White_Lines') or mat('MACK_Court_White_Lines', (0.8,0.8,0.8))
black = bpy.data.materials.get('MACK_Boilermaker_Black') or mat('MACK_Boilermaker_Black', (0.025,0.025,0.025))

# Build geometry in material batches so the new wing remains a light, editable asset.
boxes = {m: ([], []) for m in [brick, brickwork, bronze, stone, roof_mat, concrete, black, white, glass, hardwood]}
meshes = {m: ([], []) for m in [glass, hardwood]}
def add_box(material, center, length, depth, height, angle=0.0):
    verts, faces = boxes[material]
    base = len(verts)
    rot = Matrix.Rotation(angle, 4, 'Z')
    for z in (-height/2, height/2):
        for y in (-depth/2, depth/2):
            for x in (-length/2, length/2):
                p = rot @ Vector((x,y,z)) + Vector(center)
                verts.append(tuple(p))
    # local corner order: bottom (x-,y-),(x+,y-),(x-,y+),(x+,y+), then top
    faces.extend([(base+0,base+1,base+3,base+2),(base+4,base+6,base+7,base+5),
                  (base+0,base+2,base+6,base+4),(base+1,base+5,base+7,base+3),
                  (base+0,base+4,base+5,base+1),(base+2,base+3,base+7,base+6)])
def seg_box(material, a, b, z0, z1, depth=0.45, offset=0.0, width_override=None):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx,dy) if width_override is None else width_override
    if length < 0.03:
        return
    angle = math.atan2(dy,dx)
    # Clockwise outer boundary: left normal is outward.
    nx, ny = -dy/max(math.hypot(dx,dy),1e-9), dx/max(math.hypot(dx,dy),1e-9)
    cx, cy = (a[0]+b[0])/2 + nx*offset, (a[1]+b[1])/2 + ny*offset
    add_box(material, (cx,cy,(z0+z1)/2), length, depth, z1-z0, angle)
def add_window_quad(a, b, z0, z1, offset=0.18):
    verts, faces = meshes[glass]; base=len(verts)
    dx,dy=b[0]-a[0],b[1]-a[1]; ln=max(math.hypot(dx,dy),1e-9); nx,ny=-dy/ln,dx/ln
    aa=(a[0]+nx*offset,a[1]+ny*offset);bb=(b[0]+nx*offset,b[1]+ny*offset)
    verts.extend([(aa[0],aa[1],z0),(bb[0],bb[1],z0),(bb[0],bb[1],z1),(aa[0],aa[1],z1)])
    faces.append((base,base+1,base+2,base+3))
def seg_box_outside_south_lobby(material,a,b,z0,z1,depth=0.45,offset=0.0,skip=False):
    # Split south-end horizontal wall/belt bands around the documented curved
    # glass atrium rather than letting opaque boxes pass through its curtain wall.
    if not skip:
        seg_box(material,a,b,z0,z1,depth,offset);return
    t_at_x0=(46.0-a[0])/(b[0]-a[0]);t_at_x1=(59.0-a[0])/(b[0]-a[0])
    lo,hi=sorted((t_at_x0,t_at_x1))
    for t0,t1 in ((0.0,lo),(hi,1.0)):
        if t1-t0<0.01:continue
        p0=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0)
        p1=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)
        seg_box(material,p0,p1,z0,z1,depth,offset)
def add_polygon_prism(name, z0, z1, material):
    verts=[]
    for z in (z0,z1): verts.extend([(x,y,z) for x,y in points])
    n=len(points); faces=[]
    # Boundary sides plus ngon cap. Blender triangulates concave top ngons on export/render.
    faces.append(tuple(range(n-1,-1,-1)))
    faces.append(tuple(range(n,2*n)))
    faces.extend([(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
    bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(name,mesh);asset.objects.link(obj);obj.data.materials.append(material)
    return obj

def add_ring_surface(name, outer, inner, z0, z1, material):
    # Photo-traced annular one-storey roof/floor surface; each strip is a real quad.
    verts=[];faces=[];n=min(len(outer),len(inner))
    for z in (z0,z1):
        verts.extend([(p[0],p[1],z) for p in inner[:n]])
        verts.extend([(p[0],p[1],z) for p in outer[:n]])
    off=2*n
    for i in range(n-1):
        faces.append((i,n+i,n+i+1,i+1))
        faces.append((off+i,off+i+1,off+n+i+1,off+n+i))
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(name,mesh);asset.objects.link(obj);obj.data.materials.append(material)
    obj['component']='orthophoto-traced one-storey arena-perimeter addition'
    return obj


def build_perimeter_addition(label, sector):
    outer=[tuple(p) for p in sector['outer_local']];inner=[tuple(p) for p in sector['inner_local']]
    height=4.6;floor0=0.12;floor1=0.34;roof0=height-0.28
    add_ring_surface('MACK_PERIM_'+label+'_Floor',outer,inner,floor0,floor1,concrete)
    add_ring_surface('MACK_PERIM_'+label+'_Roof',outer,inner,roof0,height,roof_mat)
    for i in range(len(outer)-1):
        a,b=outer[i],outer[i+1];length=math.dist(a,b)
        if length<0.25:continue
        seg_box(brickwork,a,b,floor1,1.1,depth=0.48,offset=-0.04)
        seg_box(brickwork,a,b,3.25,roof0,depth=0.48,offset=-0.04)
        dx,dy=b[0]-a[0],b[1]-a[1];ln=max(length,1e-9);tx,ty=dx/ln,dy/ln
        for p in (a,b):
            q0=(p[0]-tx*0.18,p[1]-ty*0.18);q1=(p[0]+tx*0.18,p[1]+ty*0.18)
            seg_box(brickwork,q0,q1,floor1,roof0,depth=0.48,offset=-0.04)
        add_window_quad(a,b,1.1,3.25,offset=-0.20)
        seg_box(bronze,a,b,1.10,1.18,depth=0.12,offset=-0.26)
        seg_box(bronze,a,b,3.17,3.25,depth=0.12,offset=-0.26)
        seg_box(stone,a,b,3.82,4.02,depth=0.66,offset=-0.11)
    # End closures follow the traced inner/outer arc endpoints.
    for j in (0,-1):
        seg_box(brickwork,inner[j],outer[j],floor1,roof0,depth=0.42)
    return height

# Separate one-story additions follow the registered visible roof strips and DLZ's description.
for trace_name, sector in perimeter_traces.items():
    build_perimeter_addition(trace_name.replace('_','_').title().replace(' ','_'), sector)

# Structural slab, two occupied floors, and flat roof follow the photo-traced SDAC footprint.
add_polygon_prism('MACK_SDAC_Ground_Foundation', 0.08, 0.35, concrete)
for level in (1,2):
    add_polygon_prism(f'MACK_SDAC_Level_{level}_Floor_Slab', level*FLOOR_HEIGHT-0.22, level*FLOOR_HEIGHT+0.08, concrete)
add_polygon_prism('MACK_SDAC_Roof_Slab', WING_HEIGHT-0.4, WING_HEIGHT, roof_mat)

# Brick base/plinth and rhythmic stone sill/cornice bands around all three levels.
N=len(points)
for i,a in enumerate(points):
    b=points[(i+1)%N]; length=math.dist(a,b)
    if length<0.5: continue
    # Photograph shows a low light masonry base beneath the broad ground-floor glazing.
    seg_box_outside_south_lobby(stone,a,b,0.35,0.72,depth=0.55,offset=0.04,skip=(i==N-1))
    # A narrow horizontal belt establishes the three-level articulation.
    for z in (FLOOR_HEIGHT-0.18, 2*FLOOR_HEIGHT-0.18, WING_HEIGHT-0.3):
        seg_box_outside_south_lobby(stone,a,b,z,z+0.22,depth=0.72,offset=0.1,skip=(i==N-1 and z<9.4))
    # Three storeys of window bays, brick piers, and real openings to the interior.
    for level in range(LEVELS):
        lo=level*FLOOR_HEIGHT+0.35; hi=(level+1)*FLOOR_HEIGHT-0.24
        wz0=level*FLOOR_HEIGHT+1.35;wz1=level*FLOOR_HEIGHT+3.28
        seg_box_outside_south_lobby(stone if level==0 else brickwork,a,b,lo,wz0,depth=0.55,offset=0.04,skip=(i==N-1 and level<2))
        seg_box_outside_south_lobby(brickwork,a,b,wz1,hi,depth=0.55,offset=0.04,skip=(i==N-1 and level<2))
        bay_count=max(1,int(length//4.0))
        bay=length/bay_count
        # End/corner piers create continuous structural masonry rhythm.
        for k in range(bay_count+1):
            t=k/bay_count
            center=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
            half=0.24
            p0=(center[0]-(b[0]-a[0])/length*half,center[1]-(b[1]-a[1])/length*half)
            p1=(center[0]+(b[0]-a[0])/length*half,center[1]+(b[1]-a[1])/length*half)
            if not (level<2 and i==N-1 and 46.0 <= center[0] <= 59.0):
                seg_box(brickwork,p0,p1,lo,hi,depth=0.55,offset=0.04)
        for k in range(bay_count):
            t0=(k+0.16)/bay_count;t1=(k+0.84)/bay_count
            bay_center=(a[0]+(b[0]-a[0])*(k+0.5)/bay_count,
                        a[1]+(b[1]-a[1])*(k+0.5)/bay_count)
            # Reserve the photo-supported rounded, two-storey glazed lobby at
            # the south end; its faceted curtain wall is built below.
            if level<2 and i==N-1 and 46.0 <= bay_center[0] <= 59.0:
                continue
            if level==0:
                # The published facade photo shows a larger, nearly continuous
                # storefront strip at grade, with a low sill and deep brick lintel.
                wz0=level*FLOOR_HEIGHT+0.72;wz1=level*FLOOR_HEIGHT+3.35
                spans=[((k+0.10)/bay_count,(k+0.90)/bay_count)]
            else:
                # HNTB's oblique elevation shows upper openings grouped as
                # alternating singles and paired tall, narrow windows.
                wz0=level*FLOOR_HEIGHT+1.10;wz1=level*FLOOR_HEIGHT+3.55
                if k%3==1:
                    spans=[((k+0.17)/bay_count,(k+0.40)/bay_count),
                           ((k+0.60)/bay_count,(k+0.83)/bay_count)]
                else:
                    spans=[((k+0.29)/bay_count,(k+0.71)/bay_count)]
            # Close the brick reveals around the narrower upper windows. Without
            # these panels the grouped windows read as missing facade sections.
            cursor=(k/bay_count)
            for t0,t1 in spans:
                if t0-cursor>0.015:
                    q0=(a[0]+(b[0]-a[0])*cursor,a[1]+(b[1]-a[1])*cursor)
                    q1=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0)
                    seg_box(brickwork,q0,q1,lo,hi,depth=0.55,offset=0.04)
                cursor=t1
            if (k+1)/bay_count-cursor>0.015:
                q0=(a[0]+(b[0]-a[0])*cursor,a[1]+(b[1]-a[1])*cursor)
                q1=(a[0]+(b[0]-a[0])*(k+1)/bay_count,a[1]+(b[1]-a[1])*(k+1)/bay_count)
                seg_box(brickwork,q0,q1,lo,hi,depth=0.55,offset=0.04)
            for t0,t1 in spans:
                p0=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0)
                p1=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)
                # Actual glazing panels; no backing wall hides the interior.
                add_window_quad(p0,p1,wz0,wz1,offset=0.18)
                # Pale metal/stone heads and sills follow the photograph's
                # continuous light framing around the grouped openings.
                seg_box(stone,p0,p1,wz0,wz0+0.10,depth=0.14,offset=0.22)
                seg_box(stone,p0,p1,wz1-0.10,wz1,depth=0.14,offset=0.22)
                for q in (0.0,0.5,1.0):
                    p=(p0[0]+(p1[0]-p0[0])*q,p0[1]+(p1[1]-p0[1])*q)
                    # Single-box mullion is perpendicular to the façade.
                    dx,dy=b[0]-a[0],b[1]-a[1];theta=math.atan2(dy,dx)+math.pi/2
                    add_box(bronze,(p[0]-(-dy/length)*0.22,p[1]-(dx/length)*0.22,(wz0+wz1)/2),0.065,0.12,wz1-wz0,theta)

# Curved double-height entry lobby: the rounded glazed end and visible stair are
# shown in HNTB's published Mackey Athletics Complex photographs. The exact arc
# radius and interior stair route are interpretive because plans are unavailable.
atrium_center=(52.5,69.5);atrium_radius=6.5;atrium_steps=12
arc=[]
for j in range(atrium_steps+1):
    angle=math.pi+j*math.pi/atrium_steps
    arc.append((atrium_center[0]+atrium_radius*math.cos(angle),
                atrium_center[1]+atrium_radius*math.sin(angle)))
for a,b in zip(arc,arc[1:]):
    add_window_quad(a,b,0.55,9.25,offset=0.0)
    seg_box(bronze,a,b,0.48,0.60,depth=0.14)
    seg_box(bronze,a,b,4.66,4.79,depth=0.14)
    seg_box(bronze,a,b,9.17,9.30,depth=0.14)
for p in arc:
    add_box(bronze,(p[0],p[1],4.90),0.09,0.12,8.8)
# Double-door opening with a metal threshold and paired pulls at the south-facing
# center of the rounded lobby. Door width/height are illustrative, not measured.
add_window_quad((51.1,63.08),(53.9,63.08),0.30,2.75,offset=0.0)
seg_box(bronze,(51.1,63.08),(53.9,63.08),2.70,2.80,depth=0.10,offset=0.12)
for xx in (52.35,52.65):
    add_box(bronze,(xx,62.99,1.55),0.045,0.045,0.78)
add_box(stone,(52.5,63.04,0.22),2.9,0.22,0.12)

# Two compact flights and an intermediate landing make the stair legible through
# the lobby glass; dimensions communicate circulation, not a surveyed stair plan.
def stair_flight(start, direction, count=12, rise=0.29, run=0.42):
    sx,sy,sz=start;dx,dy=direction;theta=math.atan2(dy,dx)
    for k in range(count):
        cx=sx+dx*run*k;cy=sy+dy*run*k;cz=sz+rise*k
        add_box(stone,(cx,cy,cz),1.35,0.38,0.16,theta+math.pi/2)
    length=run*(count-1)
    for side in (-0.72,0.72):
        add_box(bronze,(sx+dx*length/2-dy*side,sy+dy*length/2+dx*side,
                        sz+rise*count+0.86),length+0.35,0.055,0.08,theta)
stair_flight((48.3,66.1,0.70),(0.72,0.48))
add_box(stone,(52.7,69.0,4.45),2.0,1.7,0.16,math.radians(34))
stair_flight((54.6,70.0,4.76),(-0.68,0.42),rise=0.29)

# Ground-level practice basketball court: Purdue's official project page documents an
# oversized practice facility with a full-size court and three breakout shooting areas.
# The primary court is positioned in the north wing as a source-backed interior use.
cx,cy=-164.8-ANCHOR[0],773.4-ANCHOR[1];cw,ch=15.24,28.65;cz=0.37
add_box(hardwood,(cx,cy,cz),cw,ch,0.025)
line=0.055
# Boundary and center lines
for yy in (cy-ch/2,cy+ch/2): add_box(white,(cx,yy,cz+0.02),cw,line,0.012)
for xx in (cx-cw/2,cx+cw/2): add_box(white,(xx,cy,cz+0.02),line,ch,0.012)
add_box(white,(cx,cy,cz+0.02),cw,line,0.012)
# Rectangular keys and free throw lines.
for sign in (-1,1):
    end=cy+sign*(ch/2-5.8)
    for xx in (cx-2.45,cx+2.45): add_box(white,(xx,(end+cy+sign*(ch/2-1.8))/2,cz+0.02),line,4.0,0.012)
    add_box(white,(cx,cy+sign*(ch/2-3.8),cz+0.02),4.9,line,0.012)
    # Backboards and dark support frames, 3.05 m above playing surface.
    gy=cy+sign*(ch/2-1.25)
    add_box(black,(cx,gy,3.35),1.85,0.12,1.05)
    add_box(glass,(cx,gy-sign*0.08,3.35),1.72,0.03,0.92)
    add_box(bronze,(cx,gy-sign*0.75,3.0),1.3,1.35,0.14)

# The official project description also documents three breakout shooting areas.
# Their exact room partitioning is not public; these open bays are an explicit
# program-level representation, set beside the full court rather than guessed walls.
for idx, yy in enumerate((90.3,101.6,112.9),1):
    bx,by=56.1,yy;bw,bh=4.2,5.6;z=0.39
    add_box(hardwood,(bx,by,z),bw,bh,0.025)
    for edge_y in (by-bh/2,by+bh/2):add_box(white,(bx,edge_y,z+0.02),bw,0.045,0.012)
    for edge_x in (bx-bw/2,bx+bw/2):add_box(white,(edge_x,by,z+0.02),0.045,bh,0.012)
    # Simple wall-mounted practice goal and target, facing west into each bay.
    add_box(black,(58.05,by,3.20),0.13,1.50,0.95,math.pi/2)
    add_box(glass,(57.94,by,3.20),0.045,1.38,0.82,math.pi/2)
    add_box(bronze,(57.38,by,2.83),0.10,0.72,0.08,math.pi/2)

# Rooftop equipment placement follows two dark rooftop units visible in the orthophoto.
for idx, (xx,yy) in enumerate(((47.5,105.3),(51.1,75.3))):
    add_box(concrete,(xx,yy,WING_HEIGHT+0.16),4.0,2.8,0.32)
    add_box(roof_mat,(xx,yy,WING_HEIGHT+0.82),3.6,2.4,1.0)
    for side in (-1,1):
        add_box(black,(xx+side*1.86,yy,WING_HEIGHT+0.82),0.08,1.85,0.54)

# Emit batched box geometry and the glazing mesh into the existing asset collection.
for material,(verts,faces) in boxes.items():
    if not verts: continue
    mesh=bpy.data.meshes.new('MACK_SDAC_'+material.name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    if material==brickwork:
        uv=mesh.uv_layers.new(name='MACK_Facade_MetreUV')
        mesh.uv_layers.active=uv;uv.active_render=True
        # Project every face on its own plane: XZ or YZ for elevations, XY for
        # horizontal caps. World-aligned coordinates preserve a real brick size
        # and level courses on all four facades despite batched geometry.
        for poly in mesh.polygons:
            nx,ny,nz=map(abs,poly.normal)
            for li in poly.loop_indices:
                co=mesh.vertices[mesh.loops[li].vertex_index].co
                if nz>0.5: u,v=co.x,co.y
                elif nx>=ny: u,v=co.y,co.z
                else: u,v=co.x,co.z
                uv.data[li].uv=(u,v)
    obj=bpy.data.objects.new('MACK_SDAC_'+material.name.replace('MACK_',''),mesh);asset.objects.link(obj);obj.data.materials.append(material)
    obj['component']='Student-Athlete Development Center wing';obj['evidence']='GIS FID 873; Purdue Athletics; DLZ project description'
for material,(verts,faces) in meshes.items():
    if not verts: continue
    mesh=bpy.data.meshes.new('MACK_SDAC_'+material.name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('MACK_SDAC_'+material.name.replace('MACK_',''),mesh);asset.objects.link(obj);obj.data.materials.append(material)
    obj['component']='Student-Athlete Development Center glazing/practice court'

# Parent the new local-coordinate components to the same asset root used by the original shell.
root = bpy.data.objects.get('AssetRoot_mackey_arena')
if root is None:
    raise RuntimeError('Expected Mackey asset root is missing')
for obj in asset.objects:
    if obj.name.startswith(('MACK_SDAC_', 'MACK_PERIM_')) and obj.parent is not root:
        world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = world

# Standalone asset bounds stay in the existing master-aligned campus coordinate frame.
for obj in asset.objects:
    if obj.name.startswith(('MACK_SDAC_', 'MACK_PERIM_')):
        obj['source_feature']='FID 873, Guy J. Mackey Arena composite footprint'
        obj['source_crs']='EPSG:4326 WGS84';obj['source_retrieved']='2026-10-24'
        if obj.name.startswith('MACK_PERIM_'):
            obj['height_status']='estimated: one storey, 4.6m overall; DLZ documents single-storey perimeter additions, roof height is not surveyed'
        else:
            obj['height_status']='estimated: 3 levels at 4.77m per level; GIS extrusion 47 has no published units'
        obj['plan_status']='north wing and perimeter roof traces follow separate visible roof seams in registered Indiana 2023 orthophoto; raw composite GIS ring is not treated as a single mass'

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('MACK_SDAC_BUILD_OK', 'vertices=',len(points),'height=',WING_HEIGHT,'asset_objects=',len(asset.objects))




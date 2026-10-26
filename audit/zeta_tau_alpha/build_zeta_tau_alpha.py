"""Build a detailed, local-coordinate Zeta Tau Alpha chapter-house library.

Sources and modeled uncertainty are recorded in source_record.json. Run with
Blender 5.2: blender --background --python build_zeta_tau_alpha.py
"""
import bpy, json, math, os, hashlib
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
EVIDENCE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(EVIDENCE, 'gis_fid773_raw.json')
OUT = os.path.join(ROOT, 'modular', 'buildings', 'zeta_tau_alpha.blend')
ASSET_ID = 'massing_zeta_tau_alpha_af8a443'
COLLECTION_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID

with open(SOURCE, 'r', encoding='utf-8') as f:
    feature = json.load(f)['feature']
raw_ring = feature['geometry']['rings'][0][:-1]
R = 6378137.0
origin_lat, origin_lon = 40.4274, -86.9137
origin_lat_rad = math.radians(origin_lat)
scale_x = 111412.84 * math.cos(origin_lat_rad)
scale_y = 111040.0
world_ring = []
for mx, my in raw_ring:
    lon = mx / R * 180.0 / math.pi
    lat = (2.0 * math.atan(math.exp(my / R)) - math.pi / 2.0) * 180.0 / math.pi
    world_ring.append(((lon - origin_lon) * scale_x, (lat - origin_lat) * scale_y))
area2 = sum(world_ring[i][0] * world_ring[(i + 1) % len(world_ring)][1] -
            world_ring[(i + 1) % len(world_ring)][0] * world_ring[i][1]
            for i in range(len(world_ring)))
signed_area = area2 / 2.0
cx = sum((world_ring[i][0] + world_ring[(i + 1) % len(world_ring)][0]) *
         (world_ring[i][0] * world_ring[(i + 1) % len(world_ring)][1] -
          world_ring[(i + 1) % len(world_ring)][0] * world_ring[i][1])
         for i in range(len(world_ring))) / (6.0 * signed_area)
cy = sum((world_ring[i][1] + world_ring[(i + 1) % len(world_ring)][1]) *
         (world_ring[i][0] * world_ring[(i + 1) % len(world_ring)][1] -
          world_ring[(i + 1) % len(world_ring)][0] * world_ring[i][1])
         for i in range(len(world_ring))) / (6.0 * signed_area)
ring = [(x - cx, y - cy) for x, y in world_ring]
if signed_area > 0:
    ring.reverse()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.collections, bpy.data.materials, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset)
exterior = bpy.data.collections.new('ZTA_Exterior')
interior = bpy.data.collections.new('ZTA_Schematic_Interior')
site = bpy.data.collections.new('ZTA_Entry_and_Landscape')
asset.children.link(exterior)
asset.children.link(interior)
asset.children.link(site)

def principled(name, color, rough=0.72, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    return m

brick = principled('ZTA | warm variegated red-brown brick', (0.34, 0.105, 0.052), 0.82)
trim = principled('ZTA | painted warm white trim', (0.88, 0.86, 0.78), 0.54)
stone = principled('ZTA | pale limestone and cast-stone base', (0.67, 0.63, 0.54), 0.84)
roof = principled('ZTA | charcoal slate', (0.29, 0.32, 0.34), 0.62)
glass = principled('ZTA | reflective blue-gray glazing', (0.095, 0.19, 0.23), 0.22, 0.12)
dark = principled('ZTA | dark bronze metal', (0.095, 0.075, 0.055), 0.34, 0.7)
door_mat = principled('ZTA | dark stained entry doors', (0.105, 0.055, 0.028), 0.42)
oak = principled('ZTA | interior oak', (0.34, 0.19, 0.085), 0.54)
cream = principled('ZTA | interior plaster', (0.82, 0.76, 0.63), 0.87)
carpet = principled('ZTA | interior carpet', (0.33, 0.25, 0.18), 0.92)
green = principled('ZTA | boxwood foliage', (0.075, 0.17, 0.075), 0.9)
concrete = principled('ZTA | entry walk and steps', (0.46, 0.45, 0.42), 0.9)
leaf = principled('ZTA | planting accents', (0.14, 0.25, 0.08), 0.92)

# Use the project's seamless PBR masonry maps; the mesh carries wall-specific UVs
# so each elevation has correctly oriented horizontal brick courses.
nodes = brick.node_tree.nodes
links = brick.node_tree.links
p = nodes.get('Principled BSDF')
for node in list(nodes):
    if node != p and node.type not in {'OUTPUT_MATERIAL'}:
        nodes.remove(node)
brick_dir=os.path.join(ROOT,'materials','textures','red_brick')
uvnode=nodes.new('ShaderNodeUVMap'); uvnode.uv_map='ZTA_Wall_UV'
def image_node(name, filename, noncolor=False):
    im=bpy.data.images.load(os.path.join(brick_dir,filename),check_existing=True)
    if noncolor: im.colorspace_settings.name='Non-Color'
    im.pack()
    n=nodes.new('ShaderNodeTexImage'); n.name=name; n.image=im; n.extension='REPEAT'
    links.new(uvnode.outputs['UV'],n.inputs['Vector'])
    return n
base_tex=image_node('Packed_Seamless_Brick_Color','diffuse.jpg')
rough_tex=image_node('Packed_Seamless_Brick_Roughness','rough.jpg',True)
normal_tex=image_node('Packed_Seamless_Brick_Normal','normal.jpg',True)
height_tex=image_node('Packed_Seamless_Brick_Height','height.jpg',True)
links.new(base_tex.outputs['Color'],p.inputs['Base Color'])
links.new(rough_tex.outputs['Color'],p.inputs['Roughness'])
nmap=nodes.new('ShaderNodeNormalMap'); links.new(normal_tex.outputs['Color'],nmap.inputs['Color'])
bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.12; bump.inputs['Distance'].default_value=0.025
links.new(height_tex.outputs['Color'],bump.inputs['Height']); links.new(nmap.outputs['Normal'],bump.inputs['Normal'])
links.new(bump.outputs['Normal'],p.inputs['Normal'])

def link_obj(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

def mesh_obj(name, verts, faces, mat, col=exterior):
    mesh = bpy.data.meshes.new(name + '_Mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.validate(verbose=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return obj

def box(name, loc, dims, mat, col=exterior, rot=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('soft stone or joinery edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.affect = 'EDGES'
        obj.modifiers.new('weighted architectural normals', 'WEIGHTED_NORMAL')
    return link_obj(obj, col)

def cylinder(name, loc, radius, depth, mat, col=exterior, vertices=20, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        end_fill_type='NGON', location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = poly.loop_total == 4
    return link_obj(obj, col)

def poly_slab(name, points, z0, z1, mat, col=exterior):
    n = len(points)
    verts = [(x,y,z0) for x,y in points] + [(x,y,z1) for x,y in points]
    # Polygon is concave, so triangulate the caps rather than relying on an n-gon fan.
    v2 = [Vector((x,y,0)) for x,y in points]
    tris = tessellate_polygon([v2])
    faces = []
    for tri in tris:
        ids = list(tri)
        faces.append(tuple(ids))
        faces.append(tuple(n+i for i in reversed(ids)))
    for i in range(n):
        j = (i+1) % n
        faces.append((i,j,n+j,n+i))
    return mesh_obj(name, verts, faces, mat, col)

minx=min(x for x,y in ring); maxx=max(x for x,y in ring)
miny=min(y for x,y in ring); maxy=max(y for x,y in ring)
W=maxx-minx; D=maxy-miny
wall_top=8.18

# Monolithic 14-segment shell follows the published Purdue footprint.
verts=[(x,y,z) for z in (0.15, wall_top) for x,y in ring]
faces=[]
for i in range(len(ring)):
    j=(i+1)%len(ring)
    faces.append((i,j,j+len(ring),i+len(ring)))
for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in ring]]):
    ids=list(tri)
    faces.append(tuple(ids))
    faces.append(tuple(len(ring)+i for i in reversed(ids)))
shell=mesh_obj('ZTA_Continuous_Red_Brick_Exterior_Shell',verts,faces,brick)
shell['source_feature']='Purdue ArcGIS BuildingShapesZip4 FeatureServer/0 FID 773'
shell['representation']='building shell; public GIS outline retained in plan'
uv=shell.data.uv_layers.new(name='ZTA_Wall_UV')
for poly in shell.data.polygons[:len(ring)]:
    edge_index=poly.index; a=ring[edge_index]; b=ring[(edge_index+1)%len(ring)]
    edge_len=math.dist(a,b)
    for loop_index in poly.loop_indices:
        vi=shell.data.loops[loop_index].vertex_index
        t=0.0 if vi in (edge_index,edge_index+len(ring)) else edge_len
        z=0.0 if vi<len(ring) else wall_top-0.15
        uv.data[loop_index].uv=(t*0.20,z*0.5)

# Stone base and broad white stringcourses around the perimeter.
for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    if length < 0.2: continue
    angle=math.atan2(dy,dx)
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    outward=(-dy/length,dx/length) # ring normalized clockwise
    for name,z,height,depth,material,offset in [('Limestone_Base',0.38,0.42,0.18,stone,0.04),
                                                ('Belt_Course',3.28,0.10,0.11,trim,0.02),
                                                ('Eave_Cornice',wall_top-0.18,0.22,0.2,trim,0.06)]:
        loc=(mid[0]+outward[0]*offset,mid[1]+outward[1]*offset,z)
        box(f'ZTA_{name}_{i:02d}_{z:.2f}',loc,(length,depth,height),material,rot=angle,bevel=0.025)

# Main front is the long, level north face visible in the 2022 ZTA chapter-house photograph.
front_edges=[]
for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    if abs(a[1]-maxy)<0.50 and abs(b[1]-maxy)<0.50 and abs(a[1]-b[1])<0.50:
        front_edges.append((i,a,b,math.hypot(b[0]-a[0],b[1]-a[1])))
front_edge=max(front_edges,key=lambda item:item[3])
fi,fa,fb,front_len=front_edge
front_y=maxy
front_x=(minx+maxx)/2
front_min=min(fa[0],fb[0]); front_max=max(fa[0],fb[0])
front_angle=math.atan2(fb[1]-fa[1],fb[0]-fa[0])

def wall_window(name, x, y, angle, w, h, z, outward=0.10):
    # Trim surround, recessed glass, sill, central mullion, and sash rails.
    c,s=math.cos(angle),math.sin(angle)
    nx,ny=-s,c
    x0=x+nx*outward; y0=y+ny*outward
    box(name+'_Surround',(x0,y0,z),(w+0.30,0.20,h+0.26),trim,rot=angle,bevel=0.035)
    box(name+'_Glazing',(x0+nx*0.115,y0+ny*0.115,z),(w,0.045,h),glass,rot=angle)
    box(name+'_Sill',(x0+nx*0.12,y0+ny*0.12,z-h/2-0.13),(w+0.38,0.30,0.12),stone,rot=angle,bevel=0.025)
    box(name+'_Mullion',(x0+nx*0.15,y0+ny*0.15,z),(0.075,0.06,h),trim,rot=angle)
    for dz in (-h*0.22,h*0.22):
        box(name+f'_Rail_{dz:.2f}',(x0+nx*0.15,y0+ny*0.15,z+dz),(w,0.06,0.065),trim,rot=angle)
    # Traditional vertical shutters, kept narrow so they don't mask the glazing.
    for sign in (-1,1):
        box(name+f'_Shutter_{sign}',(x0+c*sign*(w/2+0.24),y0+s*sign*(w/2+0.24),z),
            (0.28,0.12,h*0.92),trim,rot=angle,bevel=0.02)

# Windows are repeated across every sufficiently long exterior wall, three floors.
for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    if length < 4.3: continue
    angle=math.atan2(dy,dx)
    count=max(1,int(length//4.4))
    for bay in range(count):
        t=(bay+0.5)/count
        x=a[0]+dx*t; y=a[1]+dy*t
        # Keep the principal entry bay clear at grade; upper floors retain windows.
        is_front=(abs(a[1]-maxy)<0.50 and abs(b[1]-maxy)<0.50 and abs(a[1]-b[1])<0.50)
        for floor,z in enumerate((1.78,5.28)):
            if is_front and abs(x-front_x)<5.5 and floor==0: continue
            if is_front and abs(x-front_x)<4.8 and floor==1: continue
            wall_window(f'ZTA_Window_E{i:02d}_B{bay:02d}_F{floor+1}',x,y,angle,1.34,1.70,z)

# Central white columned portico, matching the chapter photograph; door set and transom.
portico_half=5.3
porch_depth=3.2
portico_y=front_y+porch_depth+0.42
box('ZTA_Portico_Entry_Platform',(front_x,front_y+0.05,0.28),(10.9,1.2,0.38),stone,bevel=0.08)
for i in range(4):
    box(f'ZTA_Portico_Step_{i+1}',(front_x,front_y-0.68-i*0.62,0.13+i*0.10),
        (8.0+i*1.25,0.66,0.22),concrete,bevel=0.035)
for ix,x in enumerate((front_x-4.45,front_x-1.48,front_x+1.48,front_x+4.45)):
    cylinder(f'ZTA_Portico_Column_Base_{ix}',(x,portico_y,0.52),0.57,0.42,trim)
    cylinder(f'ZTA_Portico_Column_{ix}',(x,portico_y,4.05),0.38,6.75,trim,vertices=24)
    cylinder(f'ZTA_Portico_Capital_{ix}',(x,portico_y,7.48),0.58,0.36,trim)
    cylinder(f'ZTA_Portico_Abacus_{ix}',(x,portico_y,7.70),0.68,0.14,trim)
box('ZTA_Portico_Entablature',(front_x,portico_y,7.93),(10.7,0.80,0.42),trim,bevel=0.03)
# Classical triangular pediment facing out over the columns.
mesh_obj('ZTA_Portico_Triangular_Pediment',
         [(front_x-portico_half,portico_y-0.42,8.13),(front_x+portico_half,portico_y-0.42,8.13),
          (front_x,portico_y-0.42,10.62),(front_x-portico_half,portico_y+0.30,8.13),
          (front_x+portico_half,portico_y+0.30,8.13),(front_x,portico_y+0.30,10.62)],
         [(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],trim)
box('ZTA_Pediment_Cornice_Base',(front_x,portico_y-0.06,8.22),(10.9,1.05,0.18),trim,bevel=0.025)
# Plaque and raised three-letter chapter mark. The positive-Y pediment face is
# the outward-facing side (the review camera is also on the +Y side).
box('ZTA_Chapter_Name_Plaque',(front_x,portico_y+0.36,9.18),(3.1,0.10,0.68),stone,bevel=0.04)
txt=bpy.data.curves.new('ZTA_Greek_Letters_Curve','FONT')
txt.body='ZTA'; txt.size=0.46; txt.extrude=0.012; txt.align_x='CENTER'; txt.align_y='CENTER'
obj=bpy.data.objects.new('ZTA_Pediment_Letters',txt); exterior.objects.link(obj)
# Orient local X toward screen-right for the +Y-facing review view, local Y up,
# and the text extrusion normal outward toward +Y.
obj.location=(front_x,portico_y+0.42,9.18)
obj.rotation_euler=Matrix(((-1,0,0),(0,0,1),(0,1,0))).to_euler()
txt.materials.append(door_mat)
# Paired entry leaves, transom and side lights.
box('ZTA_Entry_Double_Door',(front_x,front_y+0.13,1.64),(2.35,0.12,3.10),door_mat,bevel=0.04)
box('ZTA_Entry_Door_Leaf_Seam',(front_x,front_y+0.06,1.65),(0.055,0.055,3.0),dark)
for sign in (-1,1):
    cylinder(f'ZTA_Entry_Door_Handle_{sign}',(front_x+sign*0.22,front_y-0.01,1.55),0.055,0.04,dark,rot=(math.pi/2,0,0),vertices=12)
box('ZTA_Entry_Transom',(front_x,front_y+0.10,3.42),(2.72,0.10,0.42),glass)
for sign in (-1,1):
    box(f'ZTA_Entry_Sidelight_{sign}',(front_x+sign*1.55,front_y+0.11,1.80),(0.48,0.09,2.72),glass)

# Low-pitched hipped slate roof over main block, with a separate attached south wing.
eave=wall_top+0.08
main_x0=minx-0.45; main_x1=maxx+0.45
main_y0=miny+12.6; main_y1=maxy+0.35
mid_x=(main_x0+main_x1)/2; mid_y=(main_y0+main_y1)/2
ridge_z=eave+3.50
ridge_half=max(1.8,(main_x1-main_x0-(main_y1-main_y0))*0.42)
E=(mid_x-ridge_half,mid_y,ridge_z); F=(mid_x+ridge_half,mid_y,ridge_z)
A=(main_x0,main_y0,eave); B=(main_x1,main_y0,eave); C=(main_x1,main_y1,eave); D=(main_x0,main_y1,eave)
roof_obj=mesh_obj('ZTA_Main_Hipped_Slate_Roof',[A,B,C,D,E,F],[(0,1,5,4),(3,2,5,4),(0,3,4),(1,2,5)],roof)
roof_obj['roof_form']='hipped slate roof; ridge and dormer elevations estimated from street and chapter images'
# Thin ridge cap.
box('ZTA_Main_Ridge_Cap',(mid_x,mid_y,ridge_z+0.05),(2*ridge_half+0.9,0.20,0.20),dark,rot=0.0,bevel=0.045)
# Eaves and fascia along main roof perimeter.
for i,(a,b) in enumerate(((A,B),(B,C),(C,D),(D,A))):
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    angle=math.atan2(b[1]-a[1],b[0]-a[0]); length=math.dist(a[:2],b[:2])
    box(f'ZTA_Roof_Fascia_{i}',(mid[0],mid[1],eave-0.06),(length,0.24,0.32),trim,rot=angle,bevel=0.025)

# Smaller hipped wing roof at the southern extension.
wing_x0=-0.78-0.35; wing_x1=9.98+0.35
wing_y0=miny-0.35; wing_y1=main_y0+0.1
weave=wall_top-0.10; wridge=weave+3.15; wmid_x=(wing_x0+wing_x1)/2; wmid_y=(wing_y0+wing_y1)/2
whalf=max(0.7,(wing_y1-wing_y0-(wing_x1-wing_x0))*0.40)
WE=(wmid_x,wmid_y-whalf,wridge); WF=(wmid_x,wmid_y+whalf,wridge)
WA=(wing_x0,wing_y0,weave); WB=(wing_x1,wing_y0,weave); WC=(wing_x1,wing_y1,weave); WD=(wing_x0,wing_y1,weave)
mesh_obj('ZTA_South_Wing_Hipped_Slate_Roof',[WA,WB,WC,WD,WE,WF],[(0,1,5,4),(3,2,5,4),(0,3,4),(1,2,5)],roof)
box('ZTA_Wing_Ridge_Cap',(wmid_x,wmid_y,wridge+0.05),(0.20,2*whalf+0.8,0.18),dark,bevel=0.04)

# Five front dormers with gabled white cheeks, slate caps, and divided sash windows.
for d,x in enumerate((-9.5,-5.0,0.0,5.0,9.5)):
    y=main_y1-1.9; z=wall_top+0.90
    box(f'ZTA_Dormer_{d}_Body',(x,y,z),(2.55,1.65,2.25),brick,bevel=0.03)
    box(f'ZTA_Dormer_{d}_Window_Trim',(x,y+0.84,z),(1.88,0.10,1.55),trim)
    box(f'ZTA_Dormer_{d}_Glazing',(x,y+0.90,z),(1.52,0.05,1.22),glass)
    box(f'ZTA_Dormer_{d}_Mullion',(x,y+0.95,z),(0.08,0.05,1.22),trim)
    mesh_obj(f'ZTA_Dormer_{d}_Gable',[(x-1.28,y-0.84,z+0.98),(x+1.28,y-0.84,z+0.98),(x,y-0.84,z+2.10),
                                      (x-1.28,y+0.82,z+0.98),(x+1.28,y+0.82,z+0.98),(x,y+0.82,z+2.10)],
             [(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],trim)
    # small dormer roof cap
    mesh_obj(f'ZTA_Dormer_{d}_Slate_Cap',[(x-1.48,y-1.02,z+1.02),(x+1.48,y-1.02,z+1.02),(x,y-0.02,z+2.25),
                                          (x-1.48,y+1.02,z+1.02),(x+1.48,y+1.02,z+1.02),(x,y+0.02,z+2.25)],
             [(0,1,2),(3,5,4),(0,3,5,2),(1,4,5,2)],roof)

# A secondary west-facing entrance and restrained side stoops reflect the street approach.
west_edge=max((i,a,b,math.hypot(b[0]-a[0],b[1]-a[1])) for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])) if abs(a[0]-minx)<0.5 and abs(b[0]-minx)<0.5 and abs(a[0]-b[0])<0.5)
wi,wa,wb,wlen=west_edge
west_angle=math.atan2(wb[1]-wa[1],wb[0]-wa[0])
west_y=(wa[1]+wb[1])/2
west_x=minx
box('ZTA_West_Service_Door',(west_x-0.08,west_y,1.32),(0.12,1.15,2.65),door_mat,rot=west_angle)
box('ZTA_West_Service_Landing',(west_x-0.55,west_y,0.18),(1.4,1.85,0.32),stone,rot=west_angle,bevel=0.04)

# Schematic, deliberately labeled interior: three floor plates, corridors, stair and common spaces.
poly_slab('ZTA_Interior_Ground_Floor_Plate',ring,0.34,0.48,oak,interior)
poly_slab('ZTA_Interior_Level_2_Plate',ring,3.50,3.64,oak,interior)
poly_slab('ZTA_Interior_Level_3_Plate',ring,6.78,6.92,oak,interior)
for level,z in enumerate((0.50,3.65,6.93),1):
    box(f'ZTA_Interior_Main_Corridor_Level_{level}',(front_x,2.4,z+0.04),(2.2,19.0,0.10),carpet,interior)
    # Kitchen / dining tables on the eastern side and lounge group on west.
    for t in range(3):
        box(f'ZTA_Interior_Dining_Table_L{level}_{t}',(5.6,-4.2+t*4.4,z+0.55),(2.0,0.95,0.12),oak,interior,bevel=0.05)
        for sx in (-0.65,0.65):
            for sy in (-0.4,0.4):
                box(f'ZTA_Interior_Dining_Chair_L{level}_{t}_{sx}_{sy}',(5.6+sx,-4.2+t*4.4+sy,z+0.28),(0.48,0.48,0.52),door_mat,interior,bevel=0.04)
    for t in range(3):
        box(f'ZTA_Interior_Lounge_Sofa_L{level}_{t}',(-7.2,-4.0+t*4.8,z+0.42),(2.2,0.85,0.72),cream,interior,bevel=0.09)
        box(f'ZTA_Interior_Lounge_Table_L{level}_{t}',(-7.2,-2.8+t*4.8,z+0.30),(1.0,0.75,0.10),oak,interior,bevel=0.04)
    # Twin-sleeping room layouts on the upper levels; ground level remains common-space forward.
    if level>1:
        for room in range(4):
            x=-9.0+room*5.3; y=10.0
            box(f'ZTA_Interior_Bed_L{level}_{room}',(x,y,z+0.32),(1.35,2.05,0.40),cream,interior,bevel=0.06)
            box(f'ZTA_Interior_Desk_L{level}_{room}',(x+1.15,y-1.35,z+0.50),(1.15,0.58,0.10),oak,interior,bevel=0.03)
    # Lift/core and schematic stairs toward the south wing.
    box(f'ZTA_Interior_Stair_Core_L{level}',(2.0,-9.0,z+0.42),(2.0,4.0,0.20),stone,interior)
    for n in range(8):
        box(f'ZTA_Interior_Stair_Tread_L{level}_{n}',(2.0,-10.3+n*0.38,z+0.15+n*0.16),(1.5,0.42,0.16),oak,interior)
interior['representation']='schematic furnishings and room plan; not based on measured floorplans'

# Site-level entry walk and clipped low planting, without shifting the GIS building outline.
box('ZTA_Entry_Walk_South',(front_x,front_y-5.5,0.04),(2.6,8.7,0.08),concrete,site)
for i,x in enumerate((front_x-11.7,front_x-9.7,front_x+9.7,front_x+11.7)):
    box(f'ZTA_Front_Boxwood_{i}',(x,front_y-1.0,0.62),(1.55,0.82,1.12),green,site,bevel=0.20)
for i,x in enumerate((front_x-7.4,front_x+7.4)):
    cylinder(f'ZTA_Foundation_Shrub_{i}',(x,front_y-0.8,0.58),0.58,1.0,leaf,site,vertices=12)

# Asset metadata enables the coordinator to register a master placement marker without modifying it here.
asset['stable_building_id']=ASSET_ID
asset['placement_origin_xy_m']=(float(cx),float(cy))
asset['coordinate_frame']='local; source outline was in campus meters and translated by placement_origin_xy_m'
asset['gis_source_fid']=773
asset['known_height_status']='estimated; complete asset bounding-box maximum Z is measured from this model; GIS Extrution field is 12 m but is not established as measured height'
for obj in list(asset.all_objects):
    obj['building_id']=ASSET_ID

# Studio render camera looking at the documented front elevation, saved for visual review.
def look_at(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('ZTA_Review_Camera')
cam=bpy.data.objects.new('ZTA_Review_Camera',cam_data); scene.collection.objects.link(cam)
cam.location=(front_x+30,front_y+52,26); look_at(cam,(front_x,0,6.5)); cam_data.lens=44; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.34,0.38,0.43,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.65
def area_light(name,loc,power,size,color):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; data.color=color
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc; look_at(obj,(front_x,0,5.5)); return obj
area_light('ZTA_Review_Key_Softbox',(front_x+12,front_y+36,33),6800,22,(1.0,0.82,0.68))
area_light('ZTA_Review_Fill',(front_x-24,front_y+15,19),5200,18,(0.72,0.82,1.0))
scene.render.image_settings.file_format='PNG'
scene.render.filepath=os.path.join(EVIDENCE,'candidate_front_review_r2.png')
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.resolution_percentage=80

scene['asset_id']=ASSET_ID
scene['source_feature']='Purdue ArcGIS FeatureServer/0, FID 773, SOZTA'
scene['source_outline_area_m2']=abs(signed_area)
scene['source_outline_origin_xy_m']=(float(cx),float(cy))
scene['building_height_m']='estimated; see build report for measured asset bounding-box maximum Z; GIS Extrution field lists 12m but is not a measured survey'
scene.render.image_settings.color_mode='RGBA'
bpy.ops.wm.save_as_mainfile(filepath=OUT)
bpy.ops.render.render(write_still=True)

all_objects=list(asset.all_objects)
bpy.context.view_layer.update()
asset_max_z=max((obj.matrix_world @ Vector(corner)).z
                for obj in all_objects for corner in obj.bound_box)
asset_max_z=round(asset_max_z,2)
report={
  'asset_id':ASSET_ID,'candidate_file':os.path.relpath(OUT,ROOT).replace('\\','/'),
  'source_feature_id':773,'source_address':feature['attributes']['ADDRESS'],
  'source_crs':'EPSG:3857 (verified by ArcGIS layer metadata; WKID 102100/latest WKID 3857)',
  'transform':'EPSG:3857 inverse to lon/lat, then project local approximation: X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0',
  'retrieved_utc':'2026-10-26','placement_origin_xy_m':[cx,cy],
  'outline_vertex_count':len(raw_ring),'outline_area_m2':abs(signed_area),
  'outline_local_xy_m':[[round(x,6),round(y,6)] for x,y in ring],
  'estimated_height_m':asset_max_z,'measured_asset_bbox_max_z_m':asset_max_z,
  'height_interpretation':'11.91 m is the measured maximum Z of this model, treated as an estimate of building peak because no surveyed elevation was found; the GIS Extrution field is not documented as measured height.',
  'gis_extrusion_attribute_m':12,
  'object_count':len(all_objects),'mesh_count':sum(o.type=='MESH' for o in all_objects),
  'material_count':len([m for m in bpy.data.materials if m.name.startswith('ZTA |')]),
  'collections':{c.name:len(c.all_objects) for c in [asset,exterior,interior,site]},
  'geometry_notes':['Footprint follows the source GIS ring after an explicitly stated Web Mercator inverse and campus-local conversion.',
                    'Shell uses a continuous outline; windows are layered facade details rather than cut-through openings.',
                    'Front portico, three-level wall bands, roof form and dormers are interpreted from the 2022 chapter photo and 2026 Street View.',
                    'Interior furniture and partitions are explicitly schematic; no measured floor plan was available.',
                    'Only the building is modeled; surrounding planting is restrained and not surveyed.'],
  'source_urls':['https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/773?f=pjson',
                 'https://zetataualpha.org/news/alpha-theta-celebrates-101-years-at-purdue',
                 'https://zetataualpha.org/uploads/card-images/AlphaThetaWeb2.jpg',
                 'https://www.google.com/maps/place/118+Waldron+St,+West+Lafayette,+IN+47906/@40.4255967,-86.91789,3a,75y,65.05h,90t/data=!3m5!1e1!3m3!1s8sVKIehKbcyb50bjkmpU1Q!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3D8sVKIehKbcyb50bjkmpU1Q%26yaw%3D65.04872'],
  'file_sha256':None
}
with open(OUT,'rb') as f: report['file_sha256']=hashlib.sha256(f.read()).hexdigest()
with open(os.path.join(EVIDENCE,'build_report_r2.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('ZTA_BUILD_REPORT',json.dumps({k:report[k] for k in ('candidate_file','file_sha256','object_count','mesh_count','material_count','placement_origin_xy_m','outline_area_m2')},indent=2))

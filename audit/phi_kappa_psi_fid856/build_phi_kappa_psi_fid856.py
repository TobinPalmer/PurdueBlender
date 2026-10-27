"""Build a source-guided local-coordinate library for Phi Kappa Psi, Indiana Delta.

The surveyed-looking wall ring is the Purdue GIS FID 856 polygon. Facade proportions,
materials, portico and the visible rear/entry features are reconstructed from the
project-contractor photographs in sources/contractor_photos; interiors are explicitly
schematic because no georeferenced plans were available.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "phi_kappa_psi_fid856"
SOURCE = AUDIT / "sources" / "purdue_gis_fid856_2026-10-26.json"
OUT = ROOT / "modular" / "buildings" / "phi_kappa_psi_fid856.blend"
RENDER = AUDIT / "renders"
RENDER.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.collections,):
    pass
scene = bpy.context.scene
for c in list(bpy.data.collections):
    if c != scene.collection:
        bpy.data.collections.remove(c)
asset = bpy.data.collections.new("Asset_phi_kappa_psi_fid856")
scene.collection.children.link(asset)

def mat(name, color, roughness=0.75, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m

brick = mat("Warm red-brown running-bond brick", (0.34, 0.105, 0.064), 0.88)
nodes = brick.node_tree.nodes
links = brick.node_tree.links
tex = nodes.new("ShaderNodeTexBrick")
tex.inputs["Color1"].default_value = (0.39, 0.13, 0.078, 1)
tex.inputs["Color2"].default_value = (0.22, 0.065, 0.045, 1)
tex.inputs["Mortar"].default_value = (0.55, 0.48, 0.39, 1)
tex.inputs["Scale"].default_value = 1.0
tex.inputs["Mortar Size"].default_value = 0.014
tex.inputs["Mortar Smooth"].default_value = 0.02
tex.inputs["Brick Width"].default_value = 0.5
tex.inputs["Row Height"].default_value = 0.25
tc = nodes.new("ShaderNodeTexCoord")
links.new(tc.outputs["UV"], tex.inputs["Vector"])
bsdf = nodes.get("Principled BSDF")
links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.13
bump.inputs["Distance"].default_value = 0.035
links.new(tex.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
stone = mat("Pale limestone architectural trim", (0.76, 0.72, 0.62), 0.68)
white = mat("Painted white portico and balcony", (0.82, 0.81, 0.76), 0.72)
roofmat = mat("Charcoal gray shingle roof", (0.105, 0.12, 0.13), 0.9)
roof_nodes=roofmat.node_tree.nodes; roof_links=roofmat.node_tree.links
roof_bsdf=roof_nodes.get("Principled BSDF")
roof_tc=roof_nodes.new("ShaderNodeTexCoord")
roof_noise=roof_nodes.new("ShaderNodeTexNoise"); roof_noise.inputs["Scale"].default_value=42
roof_ramp=roof_nodes.new("ShaderNodeValToRGB")
roof_ramp.color_ramp.elements[0].position=0.16
roof_ramp.color_ramp.elements[0].color=(0.055,0.065,0.072,1)
roof_ramp.color_ramp.elements[1].position=0.82
roof_ramp.color_ramp.elements[1].color=(0.16,0.175,0.18,1)
roof_links.new(roof_tc.outputs["Generated"],roof_noise.inputs["Vector"])
roof_links.new(roof_noise.outputs["Fac"],roof_ramp.inputs["Fac"])
roof_links.new(roof_ramp.outputs["Color"],roof_bsdf.inputs["Base Color"])
roof_bump=roof_nodes.new("ShaderNodeBump"); roof_bump.inputs["Strength"].default_value=0.09; roof_bump.inputs["Distance"].default_value=0.025
roof_links.new(roof_noise.outputs["Fac"],roof_bump.inputs["Height"]); roof_links.new(roof_bump.outputs["Normal"],roof_bsdf.inputs["Normal"])
glass = mat("Dark blue-gray glazing", (0.035, 0.09, 0.13), 0.2, 0.25)
glass.node_tree.nodes.get("Principled BSDF").inputs["Metallic"].default_value = 0.1
dark = mat("Dark bronze metal", (0.075, 0.065, 0.052), 0.4, 0.45)
wood = mat("Warm interior oak", (0.31, 0.19, 0.095), 0.68)
interior = mat("Warm interior plaster", (0.68, 0.64, 0.56), 0.86)
concrete = mat("Foundation concrete", (0.46, 0.45, 0.42), 0.92)

def link_obj(obj, name, material):
    obj.name = name
    asset.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

def cube(name, center, dims, material, angle=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.dimensions = dims
    o.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Move the just-created object out of the scene root and into the asset collection.
    for c in list(o.users_collection):
        c.objects.unlink(o)
    asset.objects.link(o)
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft masonry arris", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod = o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def mesh_obj(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    asset.objects.link(ob)
    return ob

def beam_between(name, a, b, thickness, material, depth=0.28):
    a, b = Vector(a), Vector(b)
    mid = (a + b) * 0.5
    d = b - a
    return cube(name, mid, (d.length, depth, thickness), material, math.atan2(d.y, d.x), 0.025)

def facade_slope_beam(name, a, b, material, depth=0.34, thickness=0.22, outward_vec=None):
    """Rectangular molding following a sloped line in the vertical facade plane."""
    a,b=Vector(a),Vector(b); direction=(b-a).normalized()
    raw_out=Vector(outward_vec if outward_vec is not None else (normal.x,normal.y,0))
    if len(raw_out)==2: raw_out=Vector((raw_out.x,raw_out.y,0))
    outward=raw_out.normalized()
    vertical_axis=direction.cross(outward).normalized()
    basis=Matrix((direction,outward,vertical_axis)).transposed()
    ob=cube(name,(a+b)*0.5,((b-a).length,depth,thickness),material,0.0,0.02)
    ob.rotation_euler=basis.to_euler()
    return ob

def uv_to_xy(u, v, basis_u, basis_v):
    return (u*basis_u[0] + v*basis_v[0], u*basis_u[1] + v*basis_v[1])

# Native Purdue GIS FID856 wall polygon; inverse Web Mercator then repo's local
# east/north approximation. Geometry is centered on the polygon centroid.
gis = json.loads(SOURCE.read_text(encoding="utf-8"))
feature = next(f for f in gis["features"] if f["attributes"]["FID"] == 856)
ring = feature["geometry"]["rings"][0][:-1]
poly = []
for mx, my in ring:
    lon = math.degrees(mx / 6378137.0)
    lat = math.degrees(2 * math.atan(math.exp(my / 6378137.0)) - math.pi / 2)
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    poly.append((x, y))
area2 = sum(poly[i][0]*poly[(i+1)%len(poly)][1] - poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
cx = sum((poly[i][0]+poly[(i+1)%len(poly)][0])*(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1]) for i in range(len(poly))) / (3*area2)
cy = sum((poly[i][1]+poly[(i+1)%len(poly)][1])*(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1]) for i in range(len(poly))) / (3*area2)
poly = [(x-cx, y-cy) for x,y in poly]

# Principal axis follows the 33.9 m GIS edge. These axes only help place facade
# features; the actual footprint retains its GIS orientation and vertices.
edge = (poly[1][0]-poly[0][0], poly[1][1]-poly[0][1])
elen = math.hypot(*edge)
U = (edge[0]/elen, edge[1]/elen)
V = (U[1], -U[0])
uv = [(x*U[0]+y*U[1], x*V[0]+y*V[1]) for x,y in poly]
zbase, walltop, ridge_z = 0.45, 13.15, 16.1

# Structural base and walls from source ring.
n = len(poly)
verts = [(x,y,zbase) for x,y in poly] + [(x,y,walltop) for x,y in poly]
faces = [tuple(range(n-1,-1,-1)), tuple(range(n,2*n))]
faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
shell = mesh_obj("FID856 verified structural wall ring | GIS footprint", verts, faces, brick)
uv_layer = shell.data.uv_layers.new(name="Facade brick courses in meters")
for i in range(n):
    face = shell.data.polygons[i+2]
    length = math.dist(poly[i], poly[(i+1)%n])
    coords = ((0,0),(length,0),(length,walltop-zbase),(0,walltop-zbase))
    for loop_index, uv_coord in zip(face.loop_indices, coords):
        uv_layer.data[loop_index].uv = uv_coord
cube("Basement plinth coping", (0,0,zbase+0.08), (1,1,0.16), concrete) # replaced below by polygon base
# Remove the placeholder box; build a simple ring-shaped foundation directly.
bpy.data.objects.remove(bpy.data.objects["Basement plinth coping"], do_unlink=True)
# GIS ring walls are the footprint reference; a low foundation cap follows each edge.
signed = 1 if area2 > 0 else -1
for i,a in enumerate(poly):
    b=poly[(i+1)%n]; d=Vector((b[0]-a[0],b[1]-a[1])); length=d.length
    angle=math.atan2(d.y,d.x)
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2,zbase+0.03)
    cube(f"Limestone water table {i+1:02d}",mid,(length+0.04,0.38,0.34),stone,angle,0.025)

# Main roof mass: low pitched hipped roof over the original wall ring's principal
# long rectangle. The roof length/width are image-calibrated estimates; GIS Extrution
# gives a 53 ft height attribute but its two-level field conflicts with photos.
us=[p[0] for p in uv]; vs=[p[1] for p in uv]
u0,u1=min(us),max(us); v0,v1=min(vs),max(vs)
v_mid=(v0+v1)/2
def xyuv(u,v): return uv_to_xy(u,v,U,V)
def point(u,v,z): return (*xyuv(u,v),z)
ridge0, ridge1 = point(u0+0.8,v_mid,ridge_z), point(u1-0.8,v_mid,ridge_z)
corners=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
roofverts=[point(u,v,walltop) for u,v in corners]+[ridge0,ridge1]
roof_faces=[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]
roof=mesh_obj("Main charcoal hip roof",roofverts,roof_faces,roofmat)
roof_solid=roof.modifiers.new("Roof thickness", "SOLIDIFY"); roof_solid.thickness=0.22
roof_bevel=roof.modifiers.new("Roof edge normals", "BEVEL"); roof_bevel.width=0.04; roof_bevel.segments=2
# Narrow dark ridge cap segmented along the long roof axis.
beam_between("Main roof ridge cap",(ridge0[0],ridge0[1],ridge_z+0.06),(ridge1[0],ridge1[1],ridge_z+0.06),0.16,roofmat,0.20)

# Main entrance facade uses the southeast long wall (edge 6 in the ring), verified
# against the aerial access path and contractor's portico elevation. The image shows
# a broad centered classical porch, balcony, triangular pediment, and brick wings.
front_idx=6
a,b=poly[front_idx],poly[(front_idx+1)%n]
front_t=Vector((b[0]-a[0],b[1]-a[1])); front_len=front_t.length; front_t.normalize()
front_angle=math.atan2(front_t.y,front_t.x)
# Exterior normal points outward based on source ring winding.
normal=Vector((front_t.y,-front_t.x)) * signed
def frontpos(s, offset, z):
    q=Vector(a)+front_t*s+normal*offset
    return (q.x,q.y,z)
port_w,port_d=11.8,3.15
port_c=front_len/2
port_start=port_c-port_w/2
port_end=port_c+port_w/2
# Four broad square painted columns, matching project photos.
col_positions=[port_start+0.25,port_start+port_w/3,port_start+2*port_w/3,port_end-0.25]
for i,s in enumerate(col_positions):
    p=frontpos(s,0.04,zbase+4.05)
    cube(f"Portico column {i+1} shaft",p,(0.62,0.62,7.2),white,front_angle,0.045)
    cube(f"Portico column {i+1} plinth",frontpos(s,0.04,zbase+0.42),(0.92,0.94,0.55),stone,front_angle,0.04)
    cube(f"Portico column {i+1} capital",frontpos(s,0.04,zbase+7.72),(0.95,0.92,0.48),white,front_angle,0.04)
# Entablature and balcony floor across the column line.
cube("Portico entablature",frontpos(port_c,0.02,zbase+8.15),(port_w+0.8,0.95,0.52),white,front_angle,0.035)
cube("Second-floor balcony slab",frontpos(port_c,1.08,zbase+8.58),(port_w+1.1,2.7,0.28),stone,front_angle,0.04)
for s in [port_start-0.4+i*0.46 for i in range(int((port_w+0.8)/0.46)+1)]:
    if port_start-0.4 <= s <= port_end+0.4:
        cube("Balcony baluster",frontpos(s,2.27,zbase+9.02),(0.10,0.10,0.65),white,front_angle,0.018)
beam_between("Balcony handrail",frontpos(port_start-0.48,2.27,zbase+9.36),frontpos(port_end+0.48,2.27,zbase+9.36),0.13,white,0.16)
# Tall entry opening with double leaf doors and stone surround.
door_c=front_c=front_c=front_len/2
cube("Entry double door dark recess",frontpos(door_c,0.12,zbase+1.8),(2.5,0.18,3.45),dark,front_angle,0.025)
for side in (-1,1):
    cube("Entry door leaf",frontpos(door_c+side*0.57,0.24,zbase+1.78),(1.04,0.12,3.1),wood,front_angle,0.025)
    cube("Entry door glazed panel",frontpos(door_c+side*0.57,0.32,zbase+2.38),(0.76,0.06,1.55),glass,front_angle,0.018)
    cube("Entry door handle",frontpos(door_c+side*0.12,0.39,zbase+1.55),(0.06,0.045,0.18),dark,front_angle,0.01)
for s in (door_c-1.45,door_c+1.45):
    cube("Limestone entry jamb",frontpos(s,0.16,zbase+1.84),(0.2,0.22,3.7),stone,front_angle,0.025)
cube("Limestone entry lintel",frontpos(door_c,0.16,zbase+3.75),(3.1,0.22,0.24),stone,front_angle,0.025)
# Main facade pediment with raised triangular molding and pale inset.
ped_half=6.65
ped_base=12.82
ped_offset=port_d+0.36
tri_left=frontpos(port_c-ped_half,ped_offset,ped_base)
tri_peak=frontpos(port_c,ped_offset,16.0)
tri_right=frontpos(port_c+ped_half,ped_offset,ped_base)
mesh_obj("White classical pediment tympanum",[tri_left,tri_right,tri_peak],[(0,1,2)],white)
beam_between("Pediment lower cornice",frontpos(port_c-ped_half-0.25,ped_offset+0.18,ped_base),frontpos(port_c+ped_half+0.25,ped_offset+0.18,ped_base),0.24,white,0.34)
facade_slope_beam("Pediment left rake",frontpos(port_c-ped_half,ped_offset+0.18,ped_base),frontpos(port_c,ped_offset+0.18,16.0),white)
facade_slope_beam("Pediment right rake",frontpos(port_c,ped_offset+0.18,16.0),frontpos(port_c+ped_half,ped_offset+0.18,ped_base),white)
# Greek letters in the gable are a documented identifying feature in the project photo.
font=bpy.data.curves.new("Phi Kappa Psi Greek letters",type='FONT'); font.body="ΦΚΨ"; font.size=1.18; font.extrude=0.012
letter=bpy.data.objects.new("ΦΚΨ pediment emblem",font); asset.objects.link(letter)
letter.location=frontpos(port_c,ped_offset+0.24,14.25)
letter.rotation_euler=Matrix((Vector((-front_t.x,-front_t.y,0)),Vector((0,0,1)),Vector((normal.x,normal.y,0)))).transposed().to_euler()
letter.data.materials.append(dark)

# Main central projection between balcony and pediment, with three tall double-hung
# windows visible in the contractor's front elevation.
cube("Light painted central facade above balcony",frontpos(port_c,0.14,10.75),(port_w-0.25,0.26,3.68),white,front_angle,0.035)
for i,s in enumerate([port_c-3.2,port_c,port_c+3.2]):
    # These are located on the same exterior plane as the wall and framed in pale trim.
    add_center = frontpos(s,0.14,10.95)
    ang=front_angle
    cube(f"Upper portico window {i+1} frame",add_center,(1.52,0.18,2.75),stone,ang,0.02)
    cube(f"Upper portico window {i+1} glass",frontpos(s,0.25,10.95),(1.20,0.08,2.36),glass,ang,0.015)
    cube(f"Upper window {i+1} vertical muntin",frontpos(s,0.31,10.95),(0.06,0.04,2.25),white,ang,0.01)
    cube(f"Upper window {i+1} cross muntin",frontpos(s,0.32,10.95),(1.1,0.04,0.07),white,ang,0.01)

# Contractor rear elevation shows a broad light-painted central bay that projects
# and carries its own centered cross-gable. Its exact depth and roof dimensions are
# photo-calibrated estimates; the GIS structural wall ring remains unchanged.
rear_idx=0
ra,rb=poly[rear_idx],poly[(rear_idx+1)%n]
rear_t=Vector((rb[0]-ra[0],rb[1]-ra[1])).normalized()
rear_len=Vector((rb[0]-ra[0],rb[1]-ra[1])).length
rear_out=Vector((rear_t.y,-rear_t.x))*signed
rear_center=Vector(ra)+rear_t*(rear_len/2)
rear_bay_center=rear_center+rear_out*0.27
rear_angle=math.atan2(rear_t.y,rear_t.x)
cube("Rear elevation pale central bay",(rear_bay_center.x,rear_bay_center.y,9.65),(8.7,0.68,6.25),white,rear_angle,0.04)
def rearpos(s,offset,z):
    q=rear_center+rear_t*s+rear_out*offset
    return (q.x,q.y,z)
rear_surface=0.64
for row,z in enumerate((7.35,9.7,12.0)):
    for col,du in enumerate((-2.15,2.15)):
        cube(f"Rear central bay row {row+1} window {col+1} frame",rearpos(du,rear_surface+0.05,z),(1.50,0.16,1.78),stone,rear_angle,0.02)
        cube(f"Rear central bay row {row+1} window {col+1} glazing",rearpos(du,rear_surface+0.16,z),(1.24,0.08,1.48),glass,rear_angle,0.015)
        cube(f"Rear central bay row {row+1} window {col+1} vertical muntin",rearpos(du,rear_surface+0.22,z),(0.06,0.04,1.42),white,rear_angle,0.008)
        cube(f"Rear central bay row {row+1} window {col+1} cross muntin",rearpos(du,rear_surface+0.23,z),(1.15,0.04,0.06),white,rear_angle,0.008)
# Broad, projecting gabled roof feature visible over the rear bay in photo 3.
rear_gable_half=5.8; rear_base=12.78; rear_peak=17.15; rear_projection=1.65
g_l=rearpos(-rear_gable_half,rear_projection,rear_base)
g_r=rearpos(rear_gable_half,rear_projection,rear_base)
g_peak=rearpos(0,rear_projection,rear_peak)
mesh_obj("Rear central bay white gable face",[g_l,g_r,g_peak],[(0,1,2)],white)
facade_slope_beam("Rear bay gable left rake",g_l,g_peak,white,outward_vec=rear_out)
facade_slope_beam("Rear bay gable right rake",g_peak,g_r,white,outward_vec=rear_out)
beam_between("Rear bay gable base cornice",rearpos(-rear_gable_half,rear_projection+0.15,rear_base),rearpos(rear_gable_half,rear_projection+0.15,rear_base),0.24,white,0.34)
# Recessed dark shingle triangle inside the raised white gable molding.
in_l=rearpos(-4.82,rear_projection+0.10,13.18)
in_r=rearpos(4.82,rear_projection+0.10,13.18)
in_peak=rearpos(0,rear_projection+0.10,16.55)
mesh_obj("Rear gable dark shingle infill",[in_l,in_r,in_peak],[(0,1,2)],roofmat)
# Raised pale roof-stack/chimney feature documented in the rear roof photograph.
chimney_c=rear_center+rear_out*2.1
cube("Tall central rear roof stack",(chimney_c.x,chimney_c.y,17.1),(1.45,1.25,1.8),white,rear_angle,0.04)
cube("Central roof stack cap",(chimney_c.x,chimney_c.y,18.05),(1.82,1.62,0.2),stone,rear_angle,0.035)
# Two ground-level windows remain under the bay's broad projecting lower edge.
for j,du in enumerate((-2.0,2.0)):
    cube(f"Rear lower opening {j+1} frame",rearpos(du,0.18,4.15),(1.45,0.18,2.0),stone,rear_angle,0.02)
    cube(f"Rear lower opening {j+1} glazing",rearpos(du,0.30,4.15),(1.20,0.08,1.7),glass,rear_angle,0.015)

# Repeated source-style double-hung windows, placed only on walls with enough length.
def make_window(center, tangent, normal_vec, width=1.38, height=1.92, zmid=0, prefix="Window"):
    angle=math.atan2(tangent.y,tangent.x)
    c=Vector(center)+normal_vec*0.12
    pos=(c.x,c.y,zmid)
    cube(prefix+" pale stone surround",pos,(width+0.26,0.18,height+0.28),stone,angle,0.02)
    c2=c+normal_vec*0.12
    cube(prefix+" glazing",(c2.x,c2.y,zmid),(width,0.09,height),glass,angle,0.012)
    for side in (-1,1):
        q=c2+tangent*(side*width/2)
        cube(prefix+" sash stile",(q.x,q.y,zmid),(0.06,0.06,height-0.08),white,angle,0.008)
    cube(prefix+" sash rail",(c2.x,c2.y,zmid),(width-0.08,0.06,0.07),white,angle,0.008)
    cube(prefix+" horizontal meeting rail",(c2.x,c2.y,zmid),(width-0.08,0.06,0.055),white,angle,0.008)
    cube(prefix+" sill",(c.x,c.y,zmid-height/2-0.15),(width+0.42,0.28,0.14),stone,angle,0.02)

floor_z=[2.15,5.28,8.38,11.45]
for ei,aa in enumerate(poly):
    bb=poly[(ei+1)%n]
    d=Vector((bb[0]-aa[0],bb[1]-aa[1])); L=d.length
    if L<6.0: continue
    tangent=d.normalized()
    outward=Vector((tangent.y,-tangent.x))*signed
    # Main front edge uses windows outside the central portico opening.
    if ei==front_idx:
        left_range=(0.7,port_start-1.0); right_range=(port_end+1.0,L-0.7)
        for lo,hi in (left_range,right_range):
            nwin=max(1,int((hi-lo)//3.25))
            for k in range(nwin):
                s=lo+(k+0.5)*(hi-lo)/nwin
                pos=Vector(aa)+tangent*s
                for fz in floor_z[:3]:
                    make_window(pos,tangent,outward,1.35,1.82,fz,f"Front double-hung {ei}-{k}-{fz}")
        # Door-adjacent sidelights flank the entry and are mostly sheltered.
        continue
    count=max(2,int(L//3.55))
    for k in range(count):
        s=L*(k+0.5)/count
        pos=Vector(aa)+tangent*s
        for fz in floor_z:
            if ei==rear_idx and abs(s-L/2)<5.0 and 6.1<fz<13.0:
                continue # windows on those courses are part of the projecting rear bay
            make_window(pos,tangent,outward,1.32,1.8,fz,f"Facade double-hung {ei}-{k}-{fz}")

# Lower rear windows and door awnings follow the documented rear photograph.
# Back service door on the short west end with a modest dark metal canopy.
short_edge=max(range(n),key=lambda i: math.hypot(poly[(i+1)%n][0]-poly[i][0],poly[(i+1)%n][1]-poly[i][1])*-1)
for ei,aa in enumerate(poly):
    bb=poly[(ei+1)%n]; d=Vector((bb[0]-aa[0],bb[1]-aa[1])); L=d.length
    if 4.0<L<8.0:
        tangent=d.normalized(); outward=Vector((tangent.y,-tangent.x))*signed
        pos=Vector(aa)+tangent*L*0.5; c=pos+outward*0.16
        cube("Side service door",(c.x,c.y,zbase+1.55),(1.15,0.15,2.75),wood,math.atan2(tangent.y,tangent.x),0.025)

# Continuous low roof fascia and white corner quoins keep the trim legible at distance.
for i,aa in enumerate(poly):
    bb=poly[(i+1)%n]; d=Vector((bb[0]-aa[0],bb[1]-aa[1])); L=d.length
    if L>6:
        cube(f"Upper cornice {i+1}",((aa[0]+bb[0])/2,(aa[1]+bb[1])/2,walltop-0.08),(L+0.1,0.28,0.20),stone,math.atan2(d.y,d.x),0.02)

# Chimneys, small roof vents, and front entry steps.
for u in (u0+2.8,u1-2.8):
    x,y=xyuv(u,v_mid+0.7)
    chimney_brick=mat("Solid red brick chimney",(0.31,0.095,0.058),0.88)
    cube("Brick roof chimney",(x,y,walltop+1.5),(0.95,0.9,2.4),chimney_brick,math.atan2(U[1],U[0]),0.035)
    cube("Chimney limestone cap",(x,y,walltop+2.75),(1.18,1.1,0.2),stone,math.atan2(U[1],U[0]),0.035)
for i in range(5):
    z=zbase-0.12-i*0.19
    p=frontpos(port_c,0.8+i*0.36,z)
    cube(f"Entry approach step {i+1}",p,(4.6,0.68,0.18),stone,front_angle,0.025)

# Schematic but recognizable interior based on project photos 5-6. The render proves
# spatial relationships; it is not an architectural floor-plan claim.
interior_collection=bpy.data.collections.new("Interior_Schematic")
asset.children.link(interior_collection)
def interiorize(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    interior_collection.objects.link(obj)
    return obj
def box_uv(name,u,v,z,width,depth,height,material,angle=None,bevel=0.025):
    x,y=xyuv(u,v)
    return interiorize(cube(name,(x,y,z),(width,depth,height),material,angle if angle is not None else math.atan2(U[1],U[0]),bevel))
u_angle=math.atan2(U[1],U[0]); v_angle=u_angle+math.pi/2

# Segmented upper-floor slabs leave an open stairwell through the center.
for floor_index,lev in enumerate((3.65,6.78,9.92),1):
    for name,u,v,w,d in (
        ("west wing",-9.4,-2.2,13.0,11.2),
        ("east wing",9.4,-2.2,13.0,11.2),
        ("front stairwell bridge",0.0,2.2,5.8,2.4),
        ("rear stairwell bridge",0.0,-7.15,5.8,2.1)):
        box_uv(f"Schematic floor {floor_index} {name}",u,v,lev,w,d,0.15,wood,bevel=0.01)

# Ground-floor lounge enclosure: the large opening and arched casing lead to the stair,
# matching the lobby photograph. All positions are intentionally schematic.
room_u0,room_u1=-10.5,4.1
room_v0,room_v1=-5.65,2.35
room_h=3.45; room_z=0.52+room_h/2
box_uv("Lounge carpet and oak perimeter",(room_u0+room_u1)/2,(room_v0+room_v1)/2,0.53,room_u1-room_u0,room_v1-room_v0,0.12,wood,bevel=0.015)
carpet=mat("Muted charcoal lounge carpet",(0.22,0.22,0.20),0.96)
box_uv("Wall-to-wall lounge carpet",(room_u0+room_u1)/2,(room_v0+room_v1)/2,0.61,room_u1-room_u0-0.42,room_v1-room_v0-0.42,0.035,carpet,bevel=0.01)
# Side walls.
box_uv("Lounge west partition wall",room_u0+0.1,(room_v0+room_v1)/2,room_z,room_v1-room_v0,0.22,room_h,interior,angle=v_angle)
box_uv("Lounge east partition wall",room_u1-0.1,(room_v0+room_v1)/2,room_z,room_v1-room_v0,0.22,room_h,interior,angle=v_angle)
# Far wall split for a 4.6 m arched opening to the stair hall.
arch_c=-1.5; arch_half=2.3
box_uv("Lounge rear wall left pier",(room_u0+arch_c-arch_half)/2,room_v0,room_z,arch_c-arch_half-room_u0,0.20,room_h,interior)
box_uv("Lounge rear wall right pier",(arch_c+arch_half+room_u1)/2,room_v0,room_z,room_u1-arch_c-arch_half,0.20,room_h,interior)
box_uv("Lounge rear wall arch spandrel",arch_c,room_v0,3.18,arch_half*2,0.20,0.54,interior)
# Shallow circular arch surround: polyline curve in the rear-wall plane.
arc_data=bpy.data.curves.new("Lounge stair arch casing curve",type='CURVE'); arc_data.dimensions='3D'; arc_data.bevel_depth=0.105; arc_data.bevel_resolution=3
spl=arc_data.splines.new('POLY'); count=17; spl.points.add(count-1)
for j in range(count):
    theta=math.pi-j*math.pi/(count-1)
    u=arch_c+arch_half*math.cos(theta); z=2.32+1.05*math.sin(theta)
    x,y=xyuv(u,room_v0+0.13); spl.points[j].co=(x,y,z,1)
arch_obj=bpy.data.objects.new("Wide arched stair-hall opening casing",arc_data); interior_collection.objects.link(arch_obj); arc_data.materials.append(wood)
# Front lounge edge is open to the main entry hall; a short return on both sides frames it.
box_uv("Lounge front left return",-9.45,room_v1,room_z,2.1,0.20,room_h,interior)
box_uv("Lounge front right return",3.05,room_v1,room_z,2.1,0.20,room_h,interior)
# Dark wood dado/baseboard and crown molding emphasize the room edges.
for u in (room_u0+0.28,room_u1-0.28):
    box_uv("Lounge wall dark oak baseboard",u,(room_v0+room_v1)/2,0.78,room_v1-room_v0-0.35,0.10,0.24,wood,angle=v_angle)
    box_uv("Lounge wall dark oak crown",u,(room_v0+room_v1)/2,3.29,room_v1-room_v0-0.35,0.14,0.22,wood,angle=v_angle)
for v in (room_v0+0.24,room_v1-0.24):
    box_uv("Lounge wall dark oak baseboard",(room_u0+room_u1)/2,v,0.78,room_u1-room_u0-0.4,0.12,0.24,wood)
    box_uv("Lounge wall dark oak crown",(room_u0+room_u1)/2,v,3.29,room_u1-room_u0-0.4,0.16,0.22,wood)
# Tall divided windows on the lounge's left wall, as in the room photograph.
for idx,v in enumerate((-3.25,0.25),1):
    box_uv(f"Lounge window {idx} frame",room_u0+0.17,v,2.08,1.58,0.16,2.44,stone,angle=v_angle)
    box_uv(f"Lounge window {idx} glazing",room_u0+0.28,v,2.08,1.25,0.08,2.15,glass,angle=v_angle)
    box_uv(f"Lounge window {idx} center mullion",room_u0+0.35,v,2.08,0.06,0.045,2.1,white,angle=v_angle)
    box_uv(f"Lounge window {idx} meeting rail",room_u0+0.35,v,2.08,1.18,0.045,0.07,white,angle=v_angle)

# Built-in trophy and book shelves on the right wall. Each bookcase has a solid back,
# side stiles, multiple shelves, a broad crown and a stone-like lower plinth.
for bay,v in enumerate((-3.55,-0.75,1.05),1):
    box_uv(f"Bookcase {bay} dark recessed back",3.88,v,2.0,2.45,0.16,2.9,wood,angle=v_angle)
    for side in (-1,1):
        box_uv(f"Bookcase {bay} side stile",3.63,v+side*1.22,2.0,0.18,0.40,3.0,wood,angle=v_angle)
    for level in range(6):
        box_uv(f"Bookcase {bay} shelf {level+1}",3.58,v,0.70+level*0.50,2.48,0.52,0.09,wood,angle=v_angle)
    box_uv(f"Bookcase {bay} crown",3.55,v,3.60,2.65,0.72,0.18,wood,angle=v_angle)
    box_uv(f"Bookcase {bay} plinth",3.55,v,0.78,2.65,0.72,0.22,wood,angle=v_angle)
# Shelf contents: understated alternating books and small trophies.
for bay,v in enumerate((-3.55,-0.75,1.05),1):
    for level in range(5):
        for k in range(4):
            h=0.19+0.055*((k+level)%4)
            box_uv(f"Schematic book {bay}-{level}-{k}",3.47,v-0.78+k*0.42,0.84+level*0.50+h/2,0.15,0.24,h,stone if (k+level)%3==0 else dark,angle=v_angle,bevel=0.008)

# Stairs: 15 timber treads rise through the arch toward a landing; guard posts, balusters,
# and a continuous wood handrail make the photo's stair composition recognizable.
stair_u=arch_c; stair_start_v=-3.20; stair_end_v=-8.20; step_count=18
for i in range(step_count):
    t=i/(step_count-1); v=stair_start_v+t*(stair_end_v-stair_start_v); z=0.66+t*3.18
    box_uv(f"Main stair tread {i+1:02d}",stair_u,v,z,2.7,0.52,0.16,wood,bevel=0.025)
    box_uv(f"Main stair riser {i+1:02d}",stair_u,v-0.24,z-0.10,2.7,0.08,0.23,dark,bevel=0.008)
for side in (-1,1):
    rail_u=stair_u+side*1.52
    for i in range(step_count):
        t=i/(step_count-1); v=stair_start_v+t*(stair_end_v-stair_start_v); z=0.90+t*3.18
        box_uv(f"Main stair guard baluster {side}-{i+1}",rail_u,v,z-0.42,0.085,0.085,0.84,wood,bevel=0.012)
    p0=Vector(xyuv(rail_u,stair_start_v)); p1=Vector(xyuv(rail_u,stair_end_v))
    beam=facade_slope_beam("Main stair continuous handrail",(p0.x,p0.y,1.32),(p1.x,p1.y,4.50),wood,depth=0.12,thickness=0.11,outward_vec=(U[0],U[1],0))
    interiorize(beam)
box_uv("Stair upper landing",stair_u,-8.25,3.88,3.5,1.6,0.20,wood,bevel=0.02)
box_uv("Landing guardrail",stair_u+1.83,-8.25,4.38,0.12,1.5,0.12,wood,bevel=0.02)

# Ground-floor common lounge furniture modeled in recognizable layers, not single blocks.
def sofa(prefix,u,v,angle=0.0):
    box_uv(prefix+" lower frame",u,v,0.93,3.55,1.10,0.38,wood,angle)
    box_uv(prefix+" seat cushion",u,v-0.04,1.20,3.16,0.95,0.30,interior,angle)
    box_uv(prefix+" back frame",u,v+0.41,1.72,3.40,0.34,1.05,wood,angle)
    for k in range(3):
        box_uv(prefix+f" back cushion {k+1}",u-1.02+k*1.02,v+0.20,1.78,0.94,0.18,0.72,stone,angle)
        box_uv(prefix+f" seat cushion seam {k+1}",u-1.02+k*1.02,v-0.12,1.37,0.96,0.85,0.06,stone,angle)
    for side in (-1,1):
        box_uv(prefix+" arm",u+side*1.73,v,1.34,0.38,1.2,0.95,wood,angle)
        for leg_v in (-0.36,0.36): box_uv(prefix+" foot",u+side*1.45,v+leg_v,0.72,0.11,0.11,0.32,dark,angle,0.01)
sofa("Leather lounge sofa",-7.1,0.25,0)
sofa("Lounge settee",-6.0,-3.1,math.pi/2)
# Coffee table with turned-looking legs and book/flower detail.
box_uv("Coffee table apron",-2.5,-0.75,0.91,1.58,0.88,0.30,wood)
box_uv("Coffee table top",-2.5,-0.75,1.12,1.82,1.12,0.14,stone)
for du in (-0.68,0.68):
    for dv in (-0.34,0.34): box_uv("Coffee table leg",-2.5+du,-0.75+dv,0.78,0.13,0.13,0.62,wood)
box_uv("Coffee table album",-2.45,-0.72,1.23,0.55,0.36,0.07,dark)
box_uv("Decorative lounge tray",-2.50,-0.72,1.29,0.32,0.18,0.04,stone,bevel=0.01)
# Armchair at the coffee table, layered cushions and wood rails.
box_uv("Lounge armchair seat frame",0.45,-0.2,0.88,1.25,1.24,0.34,wood)
box_uv("Lounge armchair seat cushion",0.45,-0.2,1.10,1.05,1.04,0.20,stone)
box_uv("Lounge armchair back frame",0.45,0.28,1.58,1.24,0.22,1.05,wood)
box_uv("Lounge armchair back cushion",0.45,0.15,1.62,1.02,0.12,0.80,interior)
for side in (-1,1): box_uv("Lounge chair arm",0.45+side*0.64,-0.2,1.26,0.13,1.25,0.58,wood)
for du in (-0.48,0.48):
    for dv in (-0.47,0.47): box_uv("Lounge chair leg",0.45+du,-0.2+dv,0.69,0.10,0.10,0.36,dark,bevel=0.01)
# Side table and lamp; lamp shade is a tapered cylinder with a warm brass stem.
box_uv("Lounge side table top",-9.1,-0.3,1.08,1.0,0.9,0.14,wood)
box_uv("Lounge side table stem",-9.1,-0.3,0.82,0.18,0.18,0.46,dark)
box_uv("Lounge lamp stem",-9.1,-0.3,1.78,0.07,0.07,1.26,stone)
lamp_shade_data=bpy.data.curves.new("Lounge lamp shade profile",'CURVE')
# Use a simple tapered lampshade mesh of two rings.
def cone_uv(name,u,v,z,r0,r1,height,material):
    x,y=xyuv(u,v); bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=r0,radius2=r1,depth=height,location=(x,y,z))
    ob=bpy.context.object
    for c in list(ob.users_collection): c.objects.unlink(ob)
    interior_collection.objects.link(ob); ob.name=name; ob.data.materials.append(material); return ob
cone_uv("Lounge lamp shade",-9.1,-0.3,2.55,0.58,0.30,0.72,stone)
# Dining table and six chairs under the built-in shelves, like the project lounge view.
box_uv("Lounge dining table apron",1.35,-3.15,1.24,2.35,1.35,0.22,wood)
box_uv("Lounge dining table top",1.35,-3.15,1.43,2.55,1.55,0.13,stone)
for du in (-1.0,1.0):
    for dv in (-0.5,0.5): box_uv("Dining table leg",1.35+du,-3.15+dv,0.82,0.12,0.12,1.08,wood)
for i,(du,dv) in enumerate(((-1.6,0),(-0.55,-1.10),(0.55,-1.10),(1.6,0),(-0.55,1.10),(0.55,1.10))):
    box_uv(f"Dining chair {i+1} seat",1.35+du,-3.15+dv,0.96,0.72,0.68,0.16,wood)
    box_uv(f"Dining chair {i+1} upholstered pad",1.35+du,-3.15+dv,1.08,0.57,0.54,0.11,stone)
    box_uv(f"Dining chair {i+1} back",1.35+du,-3.15+dv+0.34,1.55,0.72,0.16,0.91,wood)
    for dx in (-0.27,0.27): box_uv(f"Dining chair {i+1} front leg",1.35+du+dx,-3.15+dv-0.25,0.70,0.07,0.07,0.55,wood,bevel=0.008)
# Wall artwork, thermostat, and a low-pile floor lamp, kept as small readable silhouettes.
box_uv("Framed lounge landscape",-10.28,1.15,2.22,0.16,1.0,1.22,wood,angle=v_angle)
box_uv("Landscape print mat",-10.17,1.15,2.22,0.06,0.78,1.0,stone,angle=v_angle)
box_uv("Lounge wall thermostat",-10.27,-0.85,2.45,0.12,0.28,0.25,stone,angle=v_angle)

# Schematic upper-floor corridor, room partitions and sparse bedroom/desk furniture.
# These elements make the plates inhabitable in massing terms without asserting a plan.
for floor_index,lev in enumerate((3.65,6.78,9.92),1):
    base=lev+0.18; mid=base+1.35; h=2.7
    # Corridor boundaries are broken at room-door positions.
    for vwall in (-5.9,2.15):
        door_centers=(-12.0,-6.0,6.0,12.0)
        edges=[-15.5,*door_centers,15.5]
        for seg in range(len(edges)-1):
            lo,hi=edges[seg],edges[seg+1]
            if seg%2==0:
                box_uv(f"Schematic floor {floor_index} room partition",(lo+hi)/2,vwall,mid,hi-lo,0.14,h,interior)
    # Room dividers terminate at the corridor, leaving a continuous circulation band.
    for udiv in (-12.0,-6.0,0.0,6.0,12.0):
        for v0p,v1p in ((-5.9,-3.15),(-0.95,2.15)):
            box_uv(f"Schematic floor {floor_index} cross partition",udiv,(v0p+v1p)/2,mid,0.14,v1p-v0p,h,interior,angle=v_angle)
        # Simple framed door panels at the corridor edge.
        for vdoor in (-3.15,-0.95):
            box_uv(f"Schematic floor {floor_index} room door",udiv+0.72,vdoor,base+1.02,0.9,0.10,2.04,wood,angle=v_angle)
    # Beds and desks appear only as schematic planning cues, not furnished floorplans.
    for room_i,u in enumerate((-9.0,-3.0,3.0,9.0),1):
        vbed=-4.6 if room_i%2 else 0.7
        box_uv(f"Schematic floor {floor_index} bed {room_i} frame",u,vbed,base+0.30,1.35,2.10,0.32,wood)
        box_uv(f"Schematic floor {floor_index} bed {room_i} mattress",u,vbed,base+0.53,1.26,1.98,0.16,stone)
        box_uv(f"Schematic floor {floor_index} bed {room_i} pillow",u,vbed+0.70,base+0.66,0.70,0.38,0.17,interior)
        udesk=u+1.55 if u<7 else u-1.55
        box_uv(f"Schematic floor {floor_index} study desk {room_i}",udesk,vbed,base+0.77,1.25,0.7,0.12,wood)

# Information metadata embedded in the Blender file for downstream integration.
scene.name="Building_phi_kappa_psi_fid856"
scene["stable_id_proposal"]="phi_kappa_psi_fid856"
scene["source_gis_fid"]="856"
scene["asset_collection"]="Asset_phi_kappa_psi_fid856"
scene["coordinate_frame"]="local east-north meters centered on Purdue GIS FID856 polygon centroid"
scene["interior_status"]="schematic room partitions, continuous stair/landing, and lounge composition based on contractor photos; no georegistered floorplan source found"

# Render studio setup: front facade, 3/4 aerial, and rear. Camera is saved in the file.
world=bpy.data.worlds.new("Soft overcast studio") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.52,0.58,0.66,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.72
def aim(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def set_camera(name, loc, target, lens=55):
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam)
    cam.location=loc; data.lens=lens; aim(cam,target); return cam
lamp_data=bpy.data.lights.new("Large softbox",'AREA'); lamp=bpy.data.objects.new("Large softbox",lamp_data); scene.collection.objects.link(lamp)
lamp.location=(25,-28,38); lamp_data.energy=6500; lamp_data.shape='DISK'; lamp_data.size=24; aim(lamp,(0,0,6))
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1280; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(RENDER/"phi_kappa_psi_front.png")
# World-space front normal and center guide the source-view render.
front_center_2d=Vector(a)+front_t*port_c+normal*1.0
front_center=Vector((front_center_2d.x,front_center_2d.y,0))
front_cam_loc=Vector((front_center.x+normal.x*54,front_center.y+normal.y*54,8.6))
cam=set_camera("Camera_front_facade",front_cam_loc,(0,0,7.3),48); scene.camera=cam

def render_view(filename, location, target, lens=50):
    cam.location=location; cam.data.lens=lens; aim(cam,target); scene.render.filepath=str(RENDER/filename); bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
interior_visibility={o:o.hide_render for o in interior_collection.all_objects}
for o in interior_visibility: o.hide_render=True
render_view("phi_kappa_psi_front.png",front_cam_loc,(0,0,7.3),48)
render_view("phi_kappa_psi_aerial.png",(34,-40,35),(0,0,6),44)
render_view("phi_kappa_psi_rear.png",(front_center.x-normal.x*48,front_center.y-normal.y*48,18),(0,0,7.2),50)
for o,value in interior_visibility.items(): o.hide_render=value
interior_light_data=bpy.data.lights.new("Warm lounge fill",'AREA'); interior_light=bpy.data.objects.new("Warm lounge fill",interior_light_data); scene.collection.objects.link(interior_light)
interior_light.location=(*xyuv(-3.5,-1.5),3.15); interior_light_data.energy=680; interior_light_data.shape='DISK'; interior_light_data.size=5.0; interior_light_data.color=(1.0,0.93,0.84)
aim(interior_light,(*xyuv(-2.0,-4.5),0.6))
interior_cam=set_camera("Camera_schematic_lounge_cutaway",(*xyuv(-12.0,4.8),10.0),(*xyuv(-2.3,-1.0),1.1),38)
exterior_visibility={o:o.hide_render for o in asset.objects}
for o in exterior_visibility: o.hide_render=True
cutaway_excluded=[o for o in interior_collection.all_objects if o.name.startswith("Schematic floor ")]
slab_visibility={o:o.hide_render for o in cutaway_excluded}
for o in cutaway_excluded: o.hide_render=True # upper-floor furnishings/partitions are omitted in this ground-room cutaway
scene.camera=interior_cam
render_view("phi_kappa_psi_lounge_cutaway.png",(*xyuv(-12.0,4.8),10.0),(*xyuv(-2.3,-1.0),1.1),38)
for o,value in slab_visibility.items(): o.hide_render=value
# A second, lower interior view makes the lounge-to-stair composition from photos
# 5-6 easy to inspect alongside the explanatory elevated cutaway.
eye_cam=set_camera("Camera_schematic_lounge_eye",(*xyuv(-4.6,6.8),1.72),(*xyuv(-1.5,-5.2),2.15),44)
eye_exclusions={o:o.hide_render for o in cutaway_excluded}
for o in eye_exclusions: o.hide_render=True
scene.camera=eye_cam
render_view("phi_kappa_psi_lounge_eye.png",(*xyuv(-4.6,6.8),1.72),(*xyuv(-1.5,-5.2),2.15),44)
for o,value in eye_exclusions.items(): o.hide_render=value
eye_cam.hide_render=True
for o,value in exterior_visibility.items(): o.hide_render=value
interior_cam.hide_render=True
cam.location=front_cam_loc; cam.data.lens=48; aim(cam,(0,0,7.3)); scene.camera=cam
scene.render.filepath=str(RENDER/"phi_kappa_psi_front.png")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print(json.dumps({"asset":str(OUT),"object_count":len(asset.all_objects),"gis_centroid_local_source_xy_m":[cx,cy],"wall_height_m":walltop-zbase,"roof_ridge_z_m":ridge_z,"footprint_area_m2":abs(area2)/2.0,"render_dir":str(RENDER)}))


"""Rebuild South Hall from Purdue GIS FID 528 with a source-labeled interior."""
import bpy, json, math, os
from mathutils import Vector

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
BASE=os.path.join(ROOT,"audit","south_hall_refine","south_hall_before_r1.blend")
ASSET=os.path.join(ROOT,"modular","buildings","south_hall.blend")
FOOTPRINT=os.path.join(ROOT,"audit","south_hall_refine","gis_footprint_r1.json")
LAYOUT=os.path.join(ROOT,"audit","south_hall_refine","schematic_lab_centers_r1.json")
PARTITION=os.path.join(ROOT,"audit","south_hall_refine","gis_partition_r1.json")
PUBLIC_GEOMETRY=os.path.join(ROOT,"audit","south_hall_refine","public_geometry_r2.json")
assert os.path.exists(BASE) and os.path.exists(FOOTPRINT) and os.path.exists(LAYOUT) and os.path.exists(PARTITION) and os.path.exists(PUBLIC_GEOMETRY)
bpy.ops.wm.open_mainfile(filepath=BASE)
scene=bpy.context.scene
asset=bpy.data.collections["Asset_south_hall"]
ext=bpy.data.collections.get("12_South_Hall_Exterior") or bpy.data.collections.new("12_South_Hall_Exterior")
interior=bpy.data.collections.get("13_South_Hall_Interiors") or bpy.data.collections.new("13_South_Hall_Interiors")
if ext.name not in [c.name for c in scene.collection.children]: scene.collection.children.link(ext)
if interior.name not in [c.name for c in scene.collection.children]: scene.collection.children.link(interior)
root=bpy.data.objects.get("AssetRoot_south_hall")
if root is None:
    root=bpy.data.objects.new("AssetRoot_south_hall",None); asset.objects.link(root)
assert tuple(round(v,5) for v in root.matrix_world.translation)==(0.0,0.0,0.0), "Keep local asset root identity"

fd=json.load(open(FOOTPRINT,encoding="utf-8")); ld=json.load(open(LAYOUT,encoding="utf-8")); pd=json.load(open(PARTITION,encoding="utf-8")); pg=json.load(open(PUBLIC_GEOMETRY,encoding="utf-8"))
ring=[tuple(map(float,p)) for p in fd["local_outline_xy_m"][:-1]]
assert len(ring)>20 and fd["source_feature_id"]==528
signed=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
if signed<0: ring.reverse()
area=abs(signed)/2
residential_ring=[tuple(map(float,p)) for p in pd["residential_outline_xy_local_m"]]
connector_ring=[tuple(map(float,p)) for p in pd["connector_outline_xy_local_m"]]
def ensure_ccw(r):
    s=sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r)))
    return list(reversed(r)) if s<0 else r
residential_ring=ensure_ccw(residential_ring); connector_ring=ensure_ccw(connector_ring)
assert abs(area-fd["outline_metrics"]["simplified_area_m2"])<0.1
minx=min(p[0] for p in ring); maxx=max(p[0] for p in ring); miny=min(p[1] for p in ring); maxy=max(p[1] for p in ring)

# Preserve the stable collection/root, but replace the old unsupported rectangular shell,
# 40 m skybridge, and invented object layout with measured footprint and explicitly schematic rooms.
for ob in list(asset.all_objects):
    if ob==root: continue
    bpy.data.objects.remove(ob,do_unlink=True)
for c in (ext,interior):
    for ob in list(c.objects):
        if ob.name not in bpy.data.objects: continue
        if ob==root: continue

def mat(name, color, rough=.75, metallic=0.0, transmission=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    nodes=m.node_tree.nodes; links=m.node_tree.links
    p=next(n for n in nodes if n.type=="BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    if "Metallic" in p.inputs: p.inputs["Metallic"].default_value=metallic
    if "Transmission Weight" in p.inputs: p.inputs["Transmission Weight"].default_value=transmission
    elif "Transmission" in p.inputs: p.inputs["Transmission"].default_value=transmission
    return m

brick=mat("SouthHall_R1_Warm_Red_Brick_PBR",(.27,.055,.022),.84)
stone=mat("SouthHall_R1_Light_Precast_Concrete",(.62,.59,.53),.74)
glass=mat("SouthHall_R1_Tinted_Curtain_Glass",(.075,.16,.19),.14,.18,.42)
frame=mat("SouthHall_R1_Charcoal_Aluminum",(.055,.07,.082),.3,.68)
roof=mat("SouthHall_R1_Roof_Membrane",(.025,.032,.039),.86)
terrazzo=mat("SouthHall_R1_Terrazzo",(.57,.55,.50),.35)
wood=mat("SouthHall_R1_Oak",(.37,.20,.085),.54)
carpet=mat("SouthHall_R1_Carpet",(.16,.20,.22),.92)
screen=mat("SouthHall_R1_Display",(.016,.023,.028),.22)
white=mat("SouthHall_R1_Interior_Paint",(.77,.75,.70),.87)
navy=mat("SouthHall_R1_Navy_Bedding",(.045,.09,.19),.95)
gold=mat("SouthHall_R1_Gold_Acoustic_Fabric",(.48,.29,.075),.91)
green=mat("SouthHall_R1_Billiard_Felt",(.035,.24,.105),.96)
corridor_mat=mat("SouthHall_R2_Schematic_Public_Circulation",(.075,.095,.115),.94)
public_zone_mat=mat("SouthHall_R2_Schematic_Public_Area_Carpet",(.22,.17,.105),.96)

# Procedural modular masonry, UV mapped in metres (bricks remain correctly oriented on each wall).
nodes=brick.node_tree.nodes; links=brick.node_tree.links
p=next(n for n in nodes if n.type=="BSDF_PRINCIPLED")
texcoord=nodes.new("ShaderNodeUVMap"); texcoord.uv_map="UVMap"
bt=nodes.new("ShaderNodeTexBrick"); bt.inputs["Scale"].default_value=1.0
bt.inputs["Color1"].default_value=(.31,.065,.027,1); bt.inputs["Color2"].default_value=(.18,.034,.014,1)
bt.inputs["Mortar"].default_value=(.16,.13,.11,1); bt.inputs["Mortar Size"].default_value=.009
bt.inputs["Mortar Smooth"].default_value=.025; bt.inputs["Brick Width"].default_value=.46
bt.inputs["Row Height"].default_value=.075; bt.inputs["Brick Width"].default_value=.24
links.new(texcoord.outputs["UV"],bt.inputs["Vector"]); links.new(bt.outputs["Color"],p.inputs["Base Color"])
bump=nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.16; bump.inputs["Distance"].default_value=.012
links.new(bt.outputs["Fac"],bump.inputs["Height"]); links.new(bump.outputs["Normal"],p.inputs["Normal"])

# Restrained, low-confidence membrane finish; no public roof imagery was found.
roof_p=next(n for n in roof.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
roof_nodes=roof.node_tree.nodes; roof_links=roof.node_tree.links
roof_noise=roof_nodes.new("ShaderNodeTexNoise"); roof_noise.inputs["Scale"].default_value=7.0
roof_noise.inputs["Detail"].default_value=2.0; roof_noise.inputs["Roughness"].default_value=.68
roof_ramp=roof_nodes.new("ShaderNodeValToRGB")
roof_ramp.color_ramp.elements[0].position=.2; roof_ramp.color_ramp.elements[0].color=(.003,.005,.007,1)
roof_ramp.color_ramp.elements[1].position=.8; roof_ramp.color_ramp.elements[1].color=(.012,.018,.022,1)
roof_links.new(roof_noise.outputs["Fac"],roof_ramp.inputs["Fac"])
roof_links.new(roof_ramp.outputs["Color"],roof_p.inputs["Base Color"])
roof_bump=roof_nodes.new("ShaderNodeBump"); roof_bump.inputs["Strength"].default_value=.035; roof_bump.inputs["Distance"].default_value=.004
roof_links.new(roof_noise.outputs["Fac"],roof_bump.inputs["Height"]); roof_links.new(roof_bump.outputs["Normal"],roof_p.inputs["Normal"])

def make_mesh(name, verts, faces, materials, mat_ids=None, uv_faces=None, collection=ext):
    me=bpy.data.meshes.new(name+"_Mesh"); me.from_pydata(verts,[],faces); me.materials.clear()
    for m in materials: me.materials.append(m)
    me.update()
    if mat_ids:
        for poly,mi in zip(me.polygons,mat_ids): poly.material_index=mi
    if uv_faces:
        uv=me.uv_layers.new(name="UVMap")
        for poly,coords in zip(me.polygons,uv_faces):
            for li,co in zip(poly.loop_indices,coords): uv.data[li].uv=co
    ob=bpy.data.objects.new(name,me); ob.parent=root; ob.matrix_parent_inverse=__import__('mathutils').Matrix.Identity(4); ob.location=(0,0,0)
    collection.objects.link(ob)
    if ob.name not in asset.objects: asset.objects.link(ob)
    return ob

def flat_triangle_mesh(name, triangles, z, material, collection=interior):
    verts=[]; faces=[]
    for tri in triangles:
        base=len(verts); verts.extend([(float(x),float(y),z) for x,y in tri]); faces.append([base,base+1,base+2])
    assert faces, "Expected clipped public-floor triangles"
    return make_mesh(name,verts,faces,[material],[0]*len(faces),None,collection)

def prism(name, r, z0, z1, side, cap, collection=ext, uvbrick=False):
    n=len(r); verts=[(x,y,z0) for x,y in r]+[(x,y,z1) for x,y in r]
    faces=[]; matids=[]; uvs=[]
    faces.append(list(reversed(range(n)))); matids.append(1); uvs.append([(r[i][0],r[i][1]) for i in reversed(range(n))])
    faces.append(list(range(n,2*n))); matids.append(1); uvs.append([(x,y) for x,y in r])
    lens=[]; total=0.0
    for i in range(n):
        a=Vector(r[i]); b=Vector(r[(i+1)%n]); leng=(b-a).length; lens.append((total,total+leng)); total+=leng
    for i in range(n):
        j=(i+1)%n; u0,u1=lens[i]
        faces.append([i,j,n+j,n+i]); matids.append(0)
        uvs.append([(u0,z0),(u1,z0),(u1,z1),(u0,z1)])
    return make_mesh(name,verts,faces,[side,cap],matids,uvs,collection)

def plate(name,z,thickness,material,outline=ring):
    return prism(name,outline,z,z+thickness,material,material,interior)

class Assembler:
    def __init__(self): self.v=[]; self.f=[]; self.mi=[]
    def box(self,c,axes,dims,mat_id):
        c=Vector(c); axes=[Vector(a).normalized() for a in axes]; h=[dims[i]*.5 for i in range(3)]; base=len(self.v)
        for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            self.v.append(tuple(c+axes[0]*h[0]*sx+axes[1]*h[1]*sy+axes[2]*h[2]*sz))
        for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            self.f.append([base+i for i in face]); self.mi.append(mat_id)
    def finish(self,name,mats,collection=ext):
        return make_mesh(name,self.v,self.f,mats,self.mi,None,collection)

up=Vector((0,0,1))
# Low-contrast, 6 m sheet seams clipped to the GIS polygon.
seam_mat=mat("SouthHall_R1_Roof_Seam_Charcoal",(.012,.016,.019),.9)
def roof_intersections(axis,value):
    hits=[]
    for i,p0 in enumerate(ring):
        p1=ring[(i+1)%len(ring)]
        c0=p0[axis]; c1=p1[axis]
        if (c0<=value<c1) or (c1<=value<c0):
            t=(value-c0)/(c1-c0)
            other=1-axis
            hits.append(p0[other]+t*(p1[other]-p0[other]))
    return sorted(hits)
roofseams=Assembler(); seam_z=25.706
roof_minx=min(x for x,y in residential_ring); roof_maxx=max(x for x,y in residential_ring)
roof_miny=min(y for x,y in residential_ring); roof_maxy=max(y for x,y in residential_ring)
for y in [math.ceil(roof_miny/6.0)*6.0+i*6.0 for i in range(int((roof_maxy-roof_miny)/6.0)+1)]:
    xs=roof_intersections(1,y)
    for i in range(0,len(xs)-1,2):
        if xs[i+1]-xs[i]>.5:
            roofseams.box(((xs[i]+xs[i+1])*.5,y,seam_z),(Vector((1,0,0)),Vector((0,1,0)),up),(xs[i+1]-xs[i],.065,.016),0)
for x in [math.ceil(roof_minx/6.0)*6.0+i*6.0 for i in range(int((roof_maxx-roof_minx)/6.0)+1)]:
    ys=roof_intersections(0,x)
    for i in range(0,len(ys)-1,2):
        if ys[i+1]-ys[i]>.5:
            roofseams.box((x,(ys[i]+ys[i+1])*.5,seam_z),(Vector((1,0,0)),Vector((0,1,0)),up),(.065,ys[i+1]-ys[i],.016),0)
roofseams.finish("SouthHall_Roof_Membrane_Seams_LowConfidence_6m",[seam_mat],ext)
glassbase=prism("SouthHall_GIS_GroundFloor_Glass_Podium",ring,0,4.2672,glass,roof,ext)
upper=prism("SouthHall_GIS_Residential_Brick_Envelope",residential_ring,4.2672,25.6032,brick,roof,ext,True)
# Level bands interpreted from the GIS floor elevation deltas (10 ft typical); absolute elevations
# are not a verified vertical datum. Eight storeys = ground/main floor plus seven residential floors.
levels=[0,4.2672,7.3152,10.3632,13.4112,16.4592,19.5072,22.5552,25.6032]
plate("SouthHall_Level01_Terrazzo_Slab",.06,.16,terrazzo,ring)
for idx,z in enumerate(levels[1:-1],2):
    plate(f"SouthHall_Level{idx:02d}_Carpeted_Slab_Schematic",z,.15,carpet,residential_ring)
plate("SouthHall_Roof_Slab",25.45,.25,roof,residential_ring)
# Low parapet follows the measured plan perimeter. Its height is inferred, not surveyed.
prism("SouthHall_Roof_Parapet_Estimated",residential_ring,25.6,26.3,brick,roof,ext)
# Fine 6 m membrane-sheet seams; this restrained panel rhythm is illustrative because
# public roof imagery/detail drawings were unavailable.

# Facade glazing: repeated recessed-height dorm windows and floor-to-floor study-lounge glass bays.
win=Assembler(); facade=Assembler()
area2=sum(residential_ring[i][0]*residential_ring[(i+1)%len(residential_ring)][1]-residential_ring[(i+1)%len(residential_ring)][0]*residential_ring[i][1] for i in range(len(residential_ring)))/2
maxx=max(p[0] for p in residential_ring)
# The official 2026 construction photo shows a full-height glazed corner bay. The
# image cannot be georegistered to a specific facade, so this corner assignment is labeled estimated.
atrium_target=Vector((48.21523,-53.77678,0))
atrium_corner_i=min(range(len(residential_ring)),key=lambda i:(Vector((residential_ring[i][0],residential_ring[i][1],0))-atrium_target).length)
atrium_prev_i=(atrium_corner_i-1)%len(residential_ring)
atrium_ranges={}
for edge_i,from_corner in ((atrium_prev_i,False),(atrium_corner_i,True)):
    ea=Vector(residential_ring[edge_i]); eb=Vector(residential_ring[(edge_i+1)%len(residential_ring)])
    el=(eb-ea).length
    if el>6:
        atrium_ranges[edge_i]=(0.0,6.0) if from_corner else (el-6.0,el)
east_edges=[]
for i,a0 in enumerate(residential_ring):
    b0=residential_ring[(i+1)%len(residential_ring)]; a=Vector((a0[0],a0[1],0)); b=Vector((b0[0],b0[1],0)); d=b-a; L=d.length
    if L<5.5: continue
    t=d.normalized(); outward=Vector((t.y,-t.x,0)) if area2>0 else Vector((-t.y,t.x,0))
    mid=(a+b)*.5
    if mid.x>maxx-1.0 and L>7: east_edges.append((i,a,b,t,outward,L,mid))
    margin=1.65; spacing=3.25; count=max(1,int((L-2*margin)//spacing)+1)
    if count*spacing>L-1.4: count=max(1,int((L-1.4)/spacing))
    for q in range(count):
        along=(L-(count-1)*spacing)*.5+q*spacing
        if i in atrium_ranges and atrium_ranges[i][0]-.3<=along<=atrium_ranges[i][1]+.3:
            continue
        center=a+t*along+outward*.10
        entrance_segment=any(i==ee[0] for ee in east_edges)
        if entrance_segment and abs(along-L*.5)<4.2: continue
        for fl in levels[1:-1]:
            c=center+up*(fl+1.65)
            # Slightly vary the punched-window module: source imagery shows broad
            # room/lounge bays mixed with narrower bedroom openings on the repeated grid.
            ww=1.48 if q%3==0 else 1.18
            wh=1.92 if q%3==0 else 1.78
            win.box(c,(t,outward,up),(ww,.12,wh),0)
            # Dark perimeter frame and center mullion around each glass opening.
            win.box(c+t*(ww*.5+.045),(t,outward,up),(.09,.16,wh+.18),1)
            win.box(c-t*(ww*.5+.045),(t,outward,up),(.09,.16,wh+.18),1)
            win.box(c+up*(wh*.5+.045),(t,outward,up),(ww+.18,.16,.09),1)
            win.box(c-up*(wh*.5+.045),(t,outward,up),(ww+.18,.16,.09),1)
            win.box(c,(t,outward,up),(.055,.17,wh-.08),1)
        # Ground-floor storefront mullions and transoms.
        nbar=max(2,int(L//4.2))
        for qbar in range(nbar+1):
            pos=(L*qbar/nbar)
            cc=a+t*pos+outward*.12+up*2.12
            facade.box(cc,(t,outward,up),(.09,.17,4.1),0)
        for z in (0.35,2.05,4.08):
            cc=mid+outward*.12+up*z
            facade.box(cc,(t,outward,up),(L,.17,.075),0)

win.finish("SouthHall_Repetitive_Residential_Windows",[glass,frame],ext)
facade.finish("SouthHall_GroundFloor_Curtainwall_Mullions",[frame],ext)
# Two adjoining curtain-wall segments form the high glass atrium/study bay visible in
# Purdue's 2026 construction photo. Exact location and dimension are interpretive.
atrium=Assembler(); zlo=4.2672; zhi=25.6032; zc=(zlo+zhi)*.5; zh=zhi-zlo
for edge_i,(s0,s1) in atrium_ranges.items():
    a=Vector((residential_ring[edge_i][0],residential_ring[edge_i][1],0))
    b=Vector((residential_ring[(edge_i+1)%len(residential_ring)][0],residential_ring[(edge_i+1)%len(residential_ring)][1],0))
    d=b-a; L=d.length; t=d.normalized(); outward=Vector((t.y,-t.x,0)) if area2>0 else Vector((-t.y,t.x,0))
    width=s1-s0; mid=a+t*((s0+s1)*.5)+outward*.20
    atrium.box(mid+up*zc,(t,outward,up),(width,.10,zh),0)
    # Strong but slender perimeter and vertical mullions, plus level-aligned transoms.
    for offset in [0.18,width*.5,width-0.18]:
        atrium.box(a+t*(s0+offset)+outward*.27+up*zc,(t,outward,up),(.10,.16,zh),1)
    for fl in levels[1:]:
        atrium.box(a+t*((s0+s1)*.5)+outward*.27+up*fl,(t,outward,up),(width,.16,.11),1)
atrium_obj=atrium.finish("SouthHall_FullHeight_Glazed_Atrium_Bay_Estimated",[glass,frame],ext)
atrium_obj["source_reference"]="Purdue University Residences 2026 South Hall construction photo; captured at audit/south_hall_refine/purdue_southhall_exterior_construction_2026.jpg"
atrium_obj["position_status"]="approximate facade match; reference image is not georegistered"
# The north dining/link arm is part of the official GIS base footprint, but the
# 2023 plan differentiates it from the blue residential tower; keep it one-storey.
link_frames=Assembler()
for i,a0 in enumerate(connector_ring):
    b0=connector_ring[(i+1)%len(connector_ring)]
    a=Vector((a0[0],a0[1],0)); b=Vector((b0[0],b0[1],0)); d=b-a; L=d.length
    if L<.8: continue
    t=d.normalized(); outward=Vector((t.y,-t.x,0)) if area2>0 else Vector((-t.y,t.x,0))
    nbar=max(1,int(L//2.5))
    for qbar in range(nbar+1):
        cc=a+t*(L*qbar/nbar)+outward*.12+up*2.12
        link_frames.box(cc,(t,outward,up),(.07,.16,4.1),0)
    for z in (.35,2.05,4.08):
        link_frames.box((a+b)*.5+outward*.12+up*z,(t,outward,up),(L,.16,.07),0)
link_frames.finish("SouthHall_Estimated_OneStorey_North_DiningLink_Mullions",[frame],ext)

# East/MacArthur-facing entry portal, positioned on the east GIS edge. Doors and canopy dimensions
# are interpretive; Purdue confirms the entry faces MacArthur, but does not publish elevations.
if east_edges:
    ei,a,b,t,n,L,mid=max(east_edges,key=lambda x:x[5])
    entry=mid+n*.10
    portal=Assembler()
    depth=2.8; width=5.6; h=3.8
    back=entry+n*.12; front=entry+n*depth
    # A light, three-sided vestibule: glass is modeled as panels rather than one opaque block.
    for off in (-width*.5,width*.5):
        portal.box(back+n*(depth*.5)+t*off+up*(h*.5),(n,t,up),(depth,.09,h),0)
    for off in (-1.52,1.52): portal.box(front+t*off+up*(h*.5),(t,n,up),(1.48,.09,h),0)
    for off in (-1.0,0.0,1.0): portal.box(front+t*off+up*1.35,(t,n,up),(.065,.14,2.7),1)
    # Explicit double-leaf glass doors within the vestibule's front glazing.
    for off in (-.39,.39):
        portal.box(front+t*off+up*1.34,(t,n,up),(.72,.045,2.62),0)
        portal.box(front+t*(off-.37)+up*1.34,(t,n,up),(.045,.12,2.74),1)
        portal.box(front+t*(off+.37)+up*1.34,(t,n,up),(.045,.12,2.74),1)
    portal.box(front+up*2.72,(t,n,up),(1.62,.14,.08),1)
    # Minimal vertical pulls and a low threshold make the entry legible at eye level.
    for off in (-.12,.12): portal.box(front+n*.08+t*off+up*1.35,(t,n,up),(.035,.075,.52),1)
    portal.box(front+n*.06+up*.10,(t,n,up),(1.65,.35,.13),2)
    portal.box(entry+n*1.4+up*.12,(t,n,up),(5.6,2.8,.24),2)
    # Restrained, supported canopy; exact dimensions remain interpretive.
    portal.box(entry+n*1.42+up*4.0,(t,n,up),(6.5,2.7,.25),1)
    for off in (-2.85,2.85):
        portal.box(entry+n*2.65+t*off+up*1.92,(t,n,up),(.14,.14,3.85),1)
    portal.finish("SouthHall_MacArthur_Glass_Entry_Vestibule_and_Canopy",[glass,frame,stone],ext)

# The tan one-storey north dining/link component is represented by the corresponding
# GIS polygon partition at grade. Its boundary is approximate; no separate off-site tunnel
# is added because the plan-to-GIS endpoint cannot yet be registered precisely.

# The interiors are representative amenity modules only. Purdue confirms nine learning labs,
# game room, lounges, Sushi Boss, and varied residential rooms; no room-by-room plan is published.
lab_centers=[Vector((x,y,0)) for x,y in ld["centers_xy_local_m"]]
inside=Assembler(); interior_boxes=Assembler(); finish_mats=[glass,frame,wood,screen,white,navy,gold,green,stone,terrazzo]
for i,c2 in enumerate(lab_centers,1):
    x,y=c2.x,c2.y; z=0.12
    # Three low glass partitions suggest collaborative lab rooms while preserving an open sightline.
    inside.box((x,y-2.35,1.35),(Vector((1,0,0)),Vector((0,1,0)),up),(5.2,.07,2.5),0)
    inside.box((x-2.55,y,1.35),(Vector((0,1,0)),Vector((1,0,0)),up),(4.7,.07,2.5),0)
    inside.box((x+2.55,y,1.35),(Vector((0,1,0)),Vector((-1,0,0)),up),(4.7,.07,2.5),0)
    interior_boxes.box((x,y,0.95),(Vector((1,0,0)),Vector((0,1,0)),up),(2.25,1.05,.12),2)
    interior_boxes.box((x,y,1.43),(Vector((1,0,0)),Vector((0,1,0)),up),(1.45,.12,.78),3)
    interior_boxes.box((x,y+1.88,1.65),(Vector((1,0,0)),Vector((0,1,0)),up),(2.1,.08,1.15),4)
    for sx in (-1,1):
        for sy in (-1,1): interior_boxes.box((x+sx*1.35,y+sy*.75,.46),(Vector((1,0,0)),Vector((0,1,0)),up),(.48,.48,.88),1)
inside.finish("SouthHall_Schematic_DataMine_Lab_Glass_Partitions_01_09",finish_mats,interior)
interior_boxes.finish("SouthHall_Schematic_DataMine_Labs_Furniture_01_09",finish_mats,interior)

# Main-floor recreation/lounge/dining details at illustrative safe interior locations.
common=Assembler()
# Lobby/reception and seating (approximate location, source-backed program)
common.box((10,-41,.68),(Vector((1,0,0)),Vector((0,1,0)),up),(5.8,1.05,1.25),2)
common.box((10,-40.4,1.34),(Vector((1,0,0)),Vector((0,1,0)),up),(6.0,1.1,.12),8)
for x in (6.8,9.5,12.2):
    common.box((x,-33.5,.48),(Vector((1,0,0)),Vector((0,1,0)),up),(2.3,.85,.82),6)
    common.box((x,-34.0,.91),(Vector((1,0,0)),Vector((0,1,0)),up),(2.2,.12,.12),6)
# Sushi Boss counter, refrigerated case and menu panel (program confirmed; exact fitout schematic).
common.box((22,-46,.62),(Vector((1,0,0)),Vector((0,1,0)),up),(7.2,1.1,1.15),2)
common.box((22,-45.35,1.22),(Vector((1,0,0)),Vector((0,1,0)),up),(7.3,1.15,.12),8)
common.box((22,-45.0,2.25),(Vector((1,0,0)),Vector((0,1,0)),up),(6.7,.12,.95),3)
# Game room: pool table + ping-pong, with one billiard-felt plane.
common.box((-52,-39,.46),(Vector((1,0,0)),Vector((0,1,0)),up),(3.1,1.65,.85),2)
common.box((-52,-39,.91),(Vector((1,0,0)),Vector((0,1,0)),up),(2.8,1.4,.08),7)
common.box((-44,-39,.43),(Vector((1,0,0)),Vector((0,1,0)),up),(3.0,1.55,.82),2)
common.box((-44,-39,.87),(Vector((1,0,0)),Vector((0,1,0)),up),(3.0,1.55,.06),8)
common.box((-30,-48,.40),(Vector((1,0,0)),Vector((0,1,0)),up),(5.0,2.2,.72),2)
common.box((-30,-48,.78),(Vector((1,0,0)),Vector((0,1,0)),up),(5.2,2.3,.08),6)
common.finish("SouthHall_Schematic_Lobby_Dining_Game_Amenities",finish_mats,interior)

# Schematic lobby/dining/game zones and their connecting public route are triangulated
# from exact intersections with the full GIS polygon; no patch or path extends outside it.
zone_triangles=[tri for zone in pg["zones"] for tri in zone["triangles_xy"]]
zone_obj=flat_triangle_mesh("SouthHall_Schematic_Public_Areas_Clipped_to_GIS_Outline",zone_triangles,.2375,public_zone_mat,interior)
zone_obj["layout_status"]="schematic lobby/dining/game area patches clipped inside GIS envelope; no floor plan available"
zone_obj["preclip_overhang_area_m2"]=pg["total_zone_overhang_area_m2"]
zone_obj["postclip_overhang_area_m2"]=pg["residual_overhang_after_clip_m2"]
route_triangles=[tri for route in pg["routes"] for tri in route["triangles_xy"]]
circulation_obj=flat_triangle_mesh("SouthHall_Schematic_Connected_Public_Circulation",route_triangles,.26,corridor_mat,interior)
circulation_obj["layout_status"]="schematic circulation linking entry, lobby, dining, and lounge/game amenities; clipped inside GIS envelope; no floor plan available"
circulation_obj["preclip_overhang_area_m2"]=pg["total_route_overhang_area_m2"]
circulation_obj["postclip_overhang_area_m2"]=pg["residual_overhang_after_clip_m2"]

# One representative double-occupancy room uses the published 11 ft 6 in x 16 ft 11 in plan
# dimensions; exact room assignment and internal layout remain schematic.
room=Assembler(); rx,ry=-13,-31; z0=4.42; rw=3.505; rd=5.156; wh=2.75; wt=.12
room.box((rx,ry-rd/2,z0+wh/2),(Vector((1,0,0)),Vector((0,1,0)),up),(rw,wt,wh),0)
room.box((rx-rw/2,ry,z0+wh/2),(Vector((0,1,0)),Vector((1,0,0)),up),(rd,wt,wh),0)
room.box((rx+rw/2,ry,z0+wh/2),(Vector((0,1,0)),Vector((-1,0,0)),up),(rd,wt,wh),0)
room.box((rx,ry+rd/2,z0+wh/2),(Vector((1,0,0)),Vector((0,1,0)),up),(rw,wt,wh),0)
for bx in (rx-.78,rx+.78):
    room.box((bx,ry-.65,z0+.52),(Vector((1,0,0)),Vector((0,1,0)),up),(1.0,2.05,.38),2)
    room.box((bx,ry-.65,z0+.77),(Vector((1,0,0)),Vector((0,1,0)),up),(1.0,2.0,.16),5)
room.box((rx+.72,ry+1.15,z0+.42),(Vector((1,0,0)),Vector((0,1,0)),up),(1.0,.55,.82),2)
room.box((rx+.72,ry+1.15,z0+1.05),(Vector((1,0,0)),Vector((0,1,0)),up),(.92,.48,.44),2)
room.box((rx+.75,ry-1.45,z0+.72),(Vector((1,0,0)),Vector((0,1,0)),up),(1.3,.5,.12),2)
room.finish("SouthHall_Schematic_Representative_Double_Room_Walls_Furnishings",finish_mats,interior)

# Collection organization, descriptive custom properties for reviewers.
for ob in ext.objects:
    ob["source_building_id"]="south_hall"
    ob["footprint_source_fid"]=528
for ob in interior.objects:
    ob["source_building_id"]="south_hall"
    ob["layout_status"]="schematic; no room-by-room floor plan is publicly available"
asset["gis_source_feature_id"]=528
asset["interior_layout_status"]="representative amenities; locations schematic"
asset["height_status"]="main residential polygon: eight storeys; roof 25.603 m above local floor datum estimated from relative GIS floor values interpreted as feet; north dining/link polygon: one storey at 4.267 m"
asset["roof_status"]="flat membrane roof appearance is a low-confidence material choice; roof imagery unavailable"
asset["residential_connector_split_status"]="north dining/link component modeled one storey; y=5 m split is a morphology-based estimate from 2023 site plan, not georeferenced"
asset["residential_upper_shell_area_m2"]=pd["residential_area_m2"]
asset["estimated_low_dining_link_area_m2"]=pd["connector_area_m2"]
asset["atrium_bay_status"]="approximate two-facade full-height glazed bay based on Purdue 2026 construction photo; position not georegistered"
asset["ground_floor_circulation_status"]="schematic connected public circulation spine linking entry, lobby, dining, and game/lounge"

# Set meaningful viewport colors and a neutral transparent workbench preview.
scene.render.resolution_x=1280; scene.render.resolution_y=900; scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("SOUTH_HALL_R2_SAVED",ASSET)
print("FOOTPRINT",len(ring),"verts","area_m2",area,"bounds",minx,maxx,miny,maxy)
print("LEVELS",levels,"exterior",len(ext.all_objects),"interior",len(interior.all_objects),"asset",len(asset.all_objects))

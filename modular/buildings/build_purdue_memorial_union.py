"""Repeatable source-informed facade refinement for the PMU modular asset.

Run with Blender 5.x in background. This script edits only the individual PMU
library and creates only PMU-owned geometry. See audit/purdue_memorial_union_refine.
"""
import bpy, math, json, hashlib, os
from mathutils import Vector

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET = os.path.join(ROOT, "modular", "buildings", "purdue_memorial_union.blend")
EVIDENCE = os.path.join(ROOT, "audit", "purdue_memorial_union_refine")
COLLECTION = "Asset_purdue_memorial_union"
PREFIX = "PMU_R1_"

bpy.ops.wm.open_mainfile(filepath=ASSET)
col = bpy.data.collections[COLLECTION]
stone = bpy.data.materials["PMU_Bedford_Limestone"]
# Use the non-emissive leaded glazing material for exterior window surfaces;
# the legacy lancet material is emissive and rendered as an opaque peach panel.
glass = bpy.data.materials.get("PMU_Lead_Gothic_Glass", bpy.data.materials["PMU_Stained_Glass_Lancet"])
lead = bpy.data.materials.get("PMU_Lead_Gothic_Glass", glass)
brick = bpy.data.materials.get("PMU_Red_Brick_Gothic", stone)
slate = bpy.data.materials.get("PMU_Slate_Roof")

# Dedicated charcoal slate for the R3 roof assembly. This improves tonal
# separation and makes the source-documented eaves/ridges legible under neutral
# review lighting without changing legacy PMU material assignments.
roof_slate = bpy.data.materials.get("PMU_R3_Slate") or bpy.data.materials.new("PMU_R3_Slate")
roof_slate.diffuse_color=(.055,.075,.095,1); roof_slate.use_nodes=True
nt=roof_slate.node_tree; nt.nodes.clear()
out=nt.nodes.new("ShaderNodeOutputMaterial"); out.location=(520,40)
bs=nt.nodes.new("ShaderNodeBsdfPrincipled"); bs.location=(260,40)
bs.inputs["Base Color"].default_value=(.055,.075,.095,1); bs.inputs["Roughness"].default_value=.78
bs.inputs["Metallic"].default_value=.12
coord=nt.nodes.new("ShaderNodeTexCoord"); coord.location=(-700,60)
tiles=nt.nodes.new("ShaderNodeTexBrick"); tiles.location=(-430,100)
tiles.inputs["Scale"].default_value=1.0; tiles.inputs["Mortar Size"].default_value=.018
tiles.inputs["Mortar Smooth"].default_value=.01; tiles.inputs["Brick Width"].default_value=.58; tiles.inputs["Row Height"].default_value=.29
tiles.inputs["Color1"].default_value=(.07,.09,.115,1); tiles.inputs["Color2"].default_value=(.045,.062,.082,1); tiles.inputs["Mortar"].default_value=(.018,.026,.038,1)
bump=nt.nodes.new("ShaderNodeBump"); bump.location=(20,-120); bump.inputs["Strength"].default_value=.32; bump.inputs["Distance"].default_value=.022
nt.links.new(coord.outputs["Object"],tiles.inputs["Vector"]); nt.links.new(tiles.outputs["Color"],bs.inputs["Base Color"]); nt.links.new(tiles.outputs["Fac"],bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"]); nt.links.new(bs.outputs["BSDF"],out.inputs["Surface"])
roof_trim=bpy.data.materials.get("PMU_R3_Roof_Trim") or bpy.data.materials.new("PMU_R3_Roof_Trim")
roof_trim.diffuse_color=(.12,.14,.16,1); roof_trim.use_nodes=True
trim_bs=next((n for n in roof_trim.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
if trim_bs:
    trim_bs.inputs["Base Color"].default_value=(.12,.14,.16,1); trim_bs.inputs["Metallic"].default_value=.38; trim_bs.inputs["Roughness"].default_value=.62

# Idempotent cleanup for reruns. Legacy supports that obstruct the researched
# arches are intentionally replaced; no walls, foundations, or roof footprint
# objects are moved or scaled.
for obj in list(col.objects):
    if obj.name.startswith(PREFIX) or obj.name.startswith("PMU_R2_Roof_") or obj.name.startswith("PMU_R3_Roof_") or obj.name.startswith("PMU_R3_Dormer_") or obj.name.startswith("PMU_R4_"):
        bpy.data.objects.remove(obj, do_unlink=True)
for name in ["PMU_Tower_Portal_Lintel"] + [f"PMU_Gothic_Win_Lintel_{i}" for i in range(6)] + [f"PMU_Gothic_Win_Hood_{i}" for i in range(6)]:
    obj = bpy.data.objects.get(name)
    if obj and obj.name in col.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

def mesh_obj(name, verts, faces, mat):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces); mesh.materials.append(mat); mesh.update()
    obj = bpy.data.objects.new(name, mesh); col.objects.link(obj)
    return obj

def box(name, x0, x1, y0, y1, z0, z1, mat):
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
       (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return mesh_obj(name,v,f,mat)

def arch_wedge(name, cx, spring, rin, rout, a0, a1, yfront, yback, mat):
    # Wedge of a semicircular archivolt in the XZ plane, extruded in depth.
    # Angles are measured from the right spring point toward the crown.
    n=5
    angles=[a0+(a1-a0)*i/n for i in range(n+1)]
    v=[]
    for y in (yfront,yback):
        for r in (rin,rout):
            for a in angles:
                v.append((cx+r*math.cos(a),y,spring+r*math.sin(a)))
    N=n+1
    # front inner/outer surfaces, back surfaces, plus annular faces and ends
    faces=[]
    for i in range(n):
        faces.append((i,i+1,2*N+i+1,2*N+i))
        faces.append((N+i,3*N+i,3*N+i+1,N+i+1))
        faces.append((i, N+i, N+i+1, i+1))
        faces.append((2*N+i,2*N+i+1,3*N+i+1,3*N+i))
    faces += [(0,2*N,3*N,N),(n,N+n,3*N+n,2*N+n)]
    return mesh_obj(name,v,faces,mat)

def arch_ring(tag, cx, spring, rin, rout, yfront, yback, count, mat):
    # Individual voussoirs create readable limestone joints, not a smooth tube.
    step=math.pi/count; gap=math.radians(1.0)
    for i in range(count):
        arch_wedge(f"{PREFIX}{tag}_Voussoir_{i+1:02}",cx,spring,rin,rout,
                   i*step+gap/2,(i+1)*step-gap/2,yfront,yback,mat)

def arch_glass(name, cx, spring, radius, yfront, yback, mat, divisions=32):
    angles=[math.pi*i/divisions for i in range(divisions+1)]
    v=[]
    for y in (yfront,yback):
        v.extend([(cx+radius*math.cos(a),y,spring+radius*math.sin(a)) for a in angles])
        v.append((cx,y,spring))
    n=divisions+1; center0=n; center1=2*n+1
    faces=[]
    for i in range(divisions):
        faces.append((center0,i,i+1)); faces.append((center1,n+i+1,n+i))
        faces.append((i,n+i,n+i+1,i+1))
    faces.extend([(center0,center1,center1+1 if False else n,0)]) if False else None
    # Close the extruded half-disc on its two spring edges.
    faces += [(0,center0,center1,n+1),(divisions,2*n,center1,center0)]
    return mesh_obj(name,v,faces,mat)

def curve_bar(name, pts, bevel, mat):
    c=bpy.data.curves.new(name+"Curve","CURVE"); c.dimensions='3D'; c.resolution_u=1
    c.bevel_depth=bevel; c.bevel_resolution=1
    sp=c.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); col.objects.link(o); o.data.materials.append(mat); return o

# Six south-wing openings: retain historic window positions and jambs; replace
# the plain caps with a repeated round-arched head and separated limestone blocks.
centers=[-17,-11,-5,0,20,26,32]
for i,cx in enumerate(centers):
    spring=11.35; r=1.55
    # Add true-looking face glazing because the legacy wall is a solid block,
    # so its historical glass insert sits behind the wall surface.
    box(f"{PREFIX}Wing_Window_Glass_{i+1:02}",cx-1.1,cx+1.1,-45.72,-45.68,6.62,11.36,glass)
    arch_glass(f"{PREFIX}Wing_Arch_Glass_{i+1:02}",cx,spring,r,-45.72,-45.68,glass)
    arch_ring(f"Wing_{i+1:02}_Arch",cx,spring,r,1.86,-45.86,-44.00,9,stone)
    if cx==0: # one fourth historic south-west bay visible in the 1924 archive photo
        box(f"{PREFIX}Wing_JambL_07",cx-1.6,cx-1.1,-45.84,-44.0,6.6,11.35,stone)
        box(f"{PREFIX}Wing_JambR_07",cx+1.1,cx+1.6,-45.84,-44.0,6.6,11.35,stone)
        box(f"{PREFIX}Wing_Sill_07",cx-1.6,cx+1.6,-45.84,-44.0,6.0,6.6,stone)
        box(f"{PREFIX}Wing_Mullion_07",cx-.075,cx+.075,-45.82,-45.76,6.4,11.55,stone)
    # Fine dark lead ribs continue the existing mullion into the curved head.
    curve_bar(f"{PREFIX}Wing_Arch_Lead_{i+1:02}",
        [(cx,-45.80,spring),(cx,-45.80,spring+r*.48),(cx,-45.80,spring+r*.82)],.045,lead)
    # Spring imposts visually connect vertical jambs to the arch.
    for side in (-1,1):
        box(f"{PREFIX}Wing_Impost_{i+1:02}_{'L' if side<0 else 'R'}",
            cx+side*1.52-.22,cx+side*1.52+.22,-45.91,-43.97,11.18,11.58,stone)

# Main south entry: a deep limestone portal, glazed transom and three-leaf door.
# The lower arch proportion follows the official 2024 photograph; no wall or
# shell dimensions are changed. Center is the existing tower axis x=10.25.
cx=10.25; spring=4.0; rin=3.25; rout=3.85
arch_glass(f"{PREFIX}Entry_Arched_Transom",cx,spring,rin,-46.22,-46.18,glass,40)
arch_ring("Entry_Archivolt",cx,spring,rin,rout,-46.24,-44.58,13,stone)
# Multi-leaf entry doors and glazing: modeled as a readable, recessed entrance.
door_y0,door_y1=-46.22,-46.18
for i,(x0,x1) in enumerate([(7.15,9.18),(9.22,11.27),(11.31,13.35)]):
    box(f"{PREFIX}Entry_DoorLeaf_{i+1}",x0,x1,door_y0,door_y1,.55,4.0,stone)
    box(f"{PREFIX}Entry_Door_Glass_{i+1}",x0+.18,x1-.18,door_y0-.015,door_y0+.005,2.45,3.82,glass)
    box(f"{PREFIX}Entry_Door_Kick_{i+1}",x0+.14,x1-.14,door_y0-.025,door_y0+.01,.72,2.28,brick)
    box(f"{PREFIX}Entry_Door_Mullion_{i+1}",x0+.98,x0+1.04,door_y0-.08,door_y0-.04,2.45,3.82,stone)
# Arch fanlight lead pattern and central keystone.
for side in (-1,1):
    curve_bar(f"{PREFIX}Entry_Fanlight_Rib_{'L' if side<0 else 'R'}",
      [(cx,-46.34,spring),(cx+side*1.0,-46.34,spring+.55),(cx+side*2.0,-46.34,spring+1.05),(cx+side*2.9,-46.34,spring+1.48)],.055,lead)
box(f"{PREFIX}Entry_Keystone",cx-.24,cx+.24,-46.33,-45.93,6.65,7.25,stone)
# Vertical portal piers and shallow rectangular relief fields match the
# source-visible limestone surrounds without inventing figurative carving.
for side,label in [(-1,"L"),(1,"R")]:
    x=cx+side*4.35
    box(f"{PREFIX}Entry_Portal_Pier_{label}",x-.58,x+.58,-46.18,-44.58,0.35,8.0,stone)
    box(f"{PREFIX}Entry_Relief_Recess_{label}",x-.36,x+.36,-46.22,-46.17,1.2,6.8,brick)
    box(f"{PREFIX}Entry_Relief_Field_{label}",x-.28,x+.28,-46.27,-46.21,1.45,6.55,stone)

# Tall tower window: arched limestone crown above existing multi-storey glazing.
# The visible upper arch and deep surround match the source image; dimensions
# above the existing glazing are photo-derived estimates rather than survey data.
box(f"{PREFIX}Tower_Mid_Window_Glass",6.85,13.65,-46.19,-46.16,10.72,13.8,glass)
box(f"{PREFIX}Tower_Upper_Window_Glass",6.85,13.65,-46.19,-46.16,14.42,17.82,glass)
arch_glass(f"{PREFIX}Tower_Upper_Arch_Glass",10.25,17.82,4.45,-46.19,-46.16,glass,40)
arch_ring("Tower_Upper_Archivolt",10.25,17.82,4.45,5.0,-46.23,-44.35,15,stone)
# Multi-light bars articulate the lower rectangular tier and upper arched tier
# separately, as visible in the 2024 elevation photo.
for j,x in enumerate((7.45,8.82,10.25,11.68,13.05)):
    box(f"{PREFIX}Tower_Mid_Window_Mullion_{j+1}",x-.055,x+.055,-46.28,-46.23,10.78,13.76,stone)
    dx=x-10.25; arch_top=17.82+math.sqrt(max(0,4.45**2-dx**2))
    box(f"{PREFIX}Tower_Upper_Window_Mullion_{j+1}",x-.055,x+.055,-46.28,-46.23,14.48,arch_top,stone)
for tier,zs in (("Mid",(11.7,12.65)),("Upper",(15.55,16.65))):
    for j,z in enumerate(zs):
        box(f"{PREFIX}Tower_{tier}_Window_Transom_{j+1}",6.92,13.58,-46.28,-46.23,z,z+.12,stone)
for j,dx in enumerate((-2.7,0,2.7)):
    top=17.82+math.sqrt(max(0,4.45**2-dx**2))
    box(f"{PREFIX}Tower_Upper_Arch_Mullion_{j+1}",10.25+dx-.055,10.25+dx+.055,-46.28,-46.23,17.82,top,stone)

# Stone courses and restrained vertical brick pilasters break up the flat tower
# face, echoing the visible masonry banding without implying a precise survey.
for z in (8.35,9.0,18.55,19.15,21.9):
    box(f"{PREFIX}Tower_Stone_Band_{int(z*100)}",2.55,17.95,-46.22,-44.62,z,z+.22,stone)
for x,label in ((3.15,"L"),(17.35,"R")):
    box(f"{PREFIX}Tower_Brick_Pilaster_{label}",x-.22,x+.22,-46.12,-44.58,8.0,24.9,brick)

# Photo-supported tower relief groups: the 2024 Purdue south-elevation photo
# shows paired standing figures in shallow limestone panels to either side of
# the middle tower glazing.  These are intentionally broad, low-relief forms;
# facial and garment details are not inferred beyond what the photograph shows.
relief_mat=bpy.data.materials.get("PMU_R4_Relief_Limestone") or bpy.data.materials.new("PMU_R4_Relief_Limestone")
relief_mat.diffuse_color=(.62,.52,.38,1);relief_mat.use_nodes=True
relief_bs=next((n for n in relief_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
if relief_bs: relief_bs.inputs["Base Color"].default_value=(.62,.52,.38,1);relief_bs.inputs["Roughness"].default_value=.83
for side,xc in (("L",5.18),("R",15.32)):
    box(f"PMU_R4_Tower_Relief_Back_{side}",xc-1.05,xc+1.05,-46.26,-46.18,10.25,15.25,stone)
    for j,dx in enumerate((-.42,.42),1):
        x=xc+dx
        # Shallow paired figures rise from a shared plinth, matching the
        # source-visible grouped vertical silhouettes without freestanding art.
        mesh_obj(f"PMU_R4_Tower_Relief_Robe_{side}_{j}",
          [(x-.28,-46.42,10.65),(x-.36,-46.42,12.05),(x-.30,-46.42,13.15),(x,-46.42,13.48),(x+.30,-46.42,13.15),(x+.36,-46.42,12.05),(x+.28,-46.42,10.65)],
          [(0,1,2,3,4,5,6)],relief_mat)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=(x,-46.37,13.72))
        head=bpy.context.object; head.name=f"PMU_R4_Tower_Relief_Head_{side}_{j}"
        head.scale=(.20,.14,.29); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(head.users_collection): c.objects.unlink(head)
        col.objects.link(head); head.data.materials.append(relief_mat)
        head["source_record"]="Purdue Stories 2024 south facade photograph; paired tower relief figures visible"
        head["model_status"]="shallow relief silhouette; fine sculptural details intentionally unmodeled"
        # Arms read as shallow shoulder-to-body forms in the frontal elevation.
        for arm,sign in (("L",-1),("R",1)):
            box(f"PMU_R4_Tower_Relief_Arm_{side}_{j}_{arm}",
                x+sign*.20-.10,x+sign*.20+.10,-46.43,-46.25,11.45,12.72,relief_mat)
    box(f"PMU_R4_Tower_Relief_Plith_{side}",xc-.92,xc+.92,-46.39,-46.24,10.22,10.55,stone)

# Roofs: keep each wing as an independent, watertight low-pitch gable. The
# source photos show slate gables and a tall tower; eaves follow existing wall
# tops. Ridge/eave heights and roof intersections are photo-derived estimates.
# The former south roof ran 56.5 m into the court and merged with the side roofs;
# its depth is corrected to the actual 16 m south-wing wall depth.
roof_names={"PMU_Roof_North_Wing","PMU_Roof_East_Wing","PMU_Roof_West_Wing",
            "PMU_Roof_South_Wing","PMU_EastWing_Roof_Slab"}
roof_objects=[o for o in col.objects if o.type=='MESH' and o.name in roof_names]
for o in roof_objects: bpy.data.objects.remove(o,do_unlink=True)

def gable_x(name,x0,xr,x1,y0,y1,eave,ridge,thickness=.22):
    # Gable cross-section in XZ, extruded along the wing length (Y).
    prof=[(x0,eave),(xr,ridge),(x1,eave),(x1,eave-thickness),(xr,ridge-thickness),(x0,eave-thickness)]
    v=[(x,y,z) for y in (y0,y1) for x,z in prof]
    f=[(0,1,7,6),(1,2,8,7),(5,4,10,11),(4,3,9,10),
       (0,5,4,3,2,1),(6,7,8,9,10,11),(0,6,11,5),(2,8,9,3)]
    return mesh_obj(name,v,f,roof_slate)

def gable_y(name,x0,x1,y0,yr,y1,eave,ridge,thickness=.22):
    # South/north cross-gables extruded across the front wing (X).
    prof=[(y0,eave),(yr,ridge),(y1,eave),(y1,eave-thickness),(yr,ridge-thickness),(y0,eave-thickness)]
    v=[(x,y,z) for x in (x0,x1) for y,z in prof]
    f=[(0,1,7,6),(1,2,8,7),(5,4,10,11),(4,3,9,10),
       (0,5,4,3,2,1),(6,7,8,9,10,11),(0,6,11,5),(2,8,9,3)]
    return mesh_obj(name,v,f,roof_slate)

# Side-wing roofs cover the documented full side elevations. Junctions with
# the north cross-wing are articulated with separate valley flashing below;
# this preserves the roofed wall lengths rather than leaving exposed masonry.
gable_x("PMU_R4_Roof_West_Wing",-40.75,-25.5,-10.25,-28.85,57.15,18.25,20.1)
gable_x("PMU_R4_Roof_East_Wing",29.25,45.0,60.75,-28.85,57.15,18.25,20.1)
gable_y("PMU_R4_Roof_North_Wing",-20.75,40.25,26.65,44.15,61.65,18.25,19.95)
gable_y("PMU_R4_Roof_South_West",-20.75,2.25,-44.85,-36.85,-28.85,18.25,19.85)
gable_y("PMU_R4_Roof_South_East",18.25,40.25,-44.85,-36.85,-28.85,18.25,19.85)

# Three south-west roof dormers are directly visible in Purdue's 1924 archive
# photograph. Their sizes are photo-derived; they are intentionally limited to
# the documented wing and do not add unsupported sculptures or openings.
def triangular_gable(name,cx,yfront,yback,half,zbase,zpeak,mat):
    v=[(cx-half,yfront,zbase),(cx,yfront,zpeak),(cx+half,yfront,zbase),
       (cx-half,yback,zbase),(cx,yback,zpeak),(cx+half,yback,zbase)]
    f=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
    return mesh_obj(name,v,f,mat)
for i,cx in enumerate((-17,-10,-3),1):
    box(f"PMU_R3_Dormer_{i}_Body",cx-1.25,cx+1.25,-42.82,-40.15,18.72,19.72,brick)
    triangular_gable(f"PMU_R3_Dormer_{i}_Gable",cx,-42.84,-40.15,1.25,19.70,20.45,brick)
    gable_x(f"PMU_R3_Roof_Dormer_{i}",cx-1.42,cx,cx+1.42,-42.98,-40.05,19.72,20.45,.14)
    # Small divided window with limestone head, jambs and sill, matching the
    # measured visual proportions of the archival dormer bays.
    box(f"PMU_R3_Dormer_{i}_Glass",cx-.82,cx+.82,-42.91,-42.87,18.91,19.55,glass)
    for side,label in ((-1,"L"),(1,"R")):
        box(f"PMU_R3_Dormer_{i}_Jamb_{label}",cx+side*.98-.12,cx+side*.98+.12,-42.96,-42.86,18.86,19.62,stone)
    box(f"PMU_R3_Dormer_{i}_Sill",cx-1.08,cx+1.08,-42.96,-42.84,18.78,18.91,stone)
    box(f"PMU_R3_Dormer_{i}_Head",cx-1.08,cx+1.08,-42.96,-42.84,19.56,19.70,stone)
    box(f"PMU_R3_Dormer_{i}_Mullion",cx-.045,cx+.045,-42.97,-42.90,18.92,19.55,stone)
    box(f"PMU_R3_Dormer_{i}_Transom",cx-.82,cx+.82,-42.97,-42.90,19.22,19.30,stone)
    curve_bar(f"PMU_R3_Dormer_{i}_Gable_Trim",[(cx-1.3,-42.96,19.7),(cx,-42.96,20.47),(cx+1.3,-42.96,19.7)],.045,stone)

# Slim slate ridge caps and clean eave fascia help the distinct roof planes read
# as separate wings. They follow roof edges; no foundation/wall geometry moves.
def fascia(name,xa,xb,ya,yb,z0,z1): return box(name,xa,xb,ya,yb,z0,z1,roof_trim)
for side,x0,xr,x1 in (("West",-40.75,-25.5,-10.25),("East",29.25,45.0,60.75)):
    fascia(f"PMU_R4_Roof_{side}_Ridge_Cap",xr-.16,xr+.16,-28.85,57.15,20.02,20.2)
    for label,x in (("Outer",x0),("Inner",x1)):
        fascia(f"PMU_R4_Roof_{side}_{label}_Eave",x-.1,x+.1,-28.85,57.15,18.0,18.27)
fascia("PMU_R4_Roof_North_Ridge_Cap",-20.75,40.25,43.98,44.32,19.87,20.05)
for label,y in (("Front",26.65),("Back",61.65)):
    fascia(f"PMU_R4_Roof_North_{label}_Eave",-20.75,40.25,y-.1,y+.1,18.0,18.27)
for side,x0,x1 in (("West",-20.75,2.25),("East",18.25,40.25)):
    fascia(f"PMU_R4_Roof_South_{side}_Ridge_Cap",x0,x1,-37.02,-36.68,19.77,19.95)
    for label,y in (("Front",-44.85),("Back",-28.85)):
        fascia(f"PMU_R4_Roof_South_{side}_{label}_Eave",x0,x1,y-.1,y+.1,18.0,18.27)

# Narrow flashing marks the approximate valleys where the north cross-gable
# meets the inner side-wing slopes. The linework clarifies the crossing without
# adding a large canopy plane; exact roof junction elevations remain estimated.
for side,x in (("West",-20.75),("East",40.25)):
    curve_bar(f"PMU_R4_Roof_{side}_Valley_Flashing",[(x,26.8,18.35),(x,34.0,19.08),(x,44.15,19.95)],.065,roof_trim)

# Metadata embedded on new objects for provenance and reviewer discoverability.
for o in [x for x in col.objects if x.name.startswith(PREFIX) or x.name.startswith("PMU_R4_") or x.name.startswith("PMU_R3_Dormer_")]:
    o["source_record"]="Purdue Archives 1924 facade photo; Purdue Stories 2024 south facade photo"
    o["model_status"]="source-informed visual reconstruction; dimensions and roof elevations approximate"

# Preserve asset scene/collection/root transforms. Save the modular asset itself.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

new=[o for o in col.all_objects if o.name.startswith(PREFIX)]
print(json.dumps({"asset":ASSET,"sha256":sha256(ASSET),"object_count":len(col.all_objects),
 "new_refinement_objects":len(new),"mesh_count":sum(o.type=='MESH' for o in col.all_objects),
 "legacy_roof_objects_removed_this_run":len(roof_objects),
 "original_baseline_roof_objects_replaced":5,
 "new_roof_objects":sum(o.name.startswith("PMU_R4_Roof_") for o in col.all_objects),
 "bounds_local":{"structural preserved":True},
 "new_objects_materialized":sum(bool(o.data.materials) for o in new)},indent=2))

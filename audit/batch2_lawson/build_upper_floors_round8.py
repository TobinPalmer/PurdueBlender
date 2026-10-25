"""Add source-registered Lawson L2/L3 plan partitions as explicitly schematic 3D geometry.

Horizontal locations come from Purdue's official north-up, 1:16 floor-plan PDFs. The
PDF raster registration is tied to the R7 three-point GIS/L1 registration. Story Z,
wall thickness, and wall height are display estimates because no vertical section was
found. Stair treads are intentionally not extrapolated between floors.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
AUD = ROOT / "audit/batch2_lawson"
ASSET = ROOT / "modular/buildings/lawson_hall.blend"
MARKER = (-282.5, 44.0)

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections["Asset_lawson_hall"]
root = bpy.data.objects["AssetRoot_lawson_hall"]
previous_r8_roof = bpy.data.objects.get("LWSN_R8_Roof_Surface_With_L3_Terrace_Notch")
previous_roof_material = previous_r8_roof.data.materials[0] if previous_r8_roof and previous_r8_roof.data.materials else None
for ob in list(asset.all_objects):
    if ob.name.startswith("LWSN_R8_"):
        bpy.data.objects.remove(ob, do_unlink=True)
for col in list(bpy.data.collections):
    if col.name.startswith("LWSN_R8_") and col.name != "Asset_lawson_hall":
        bpy.data.collections.remove(col)

col = bpy.data.collections.new("LWSN_R8_Official_Upper_Floor_Plan_Geometry")
asset.children.link(col)

# The three R7 image controls are on the 918x1188 L1 raster. R8 uses 1020x1320
# raster pages at the same aspect and 10/9 pixel dimensions. The plans' outer
# geometry overlays the 54-vertex GIS footprint within raster line-width limits.
SX0, SY0 = 0.092105, 0.0923377778
SX, SY = SX0 * 0.9, SY0 * 0.9
X0 = -13.209 - SX0 * 323
Y0 = 40.611 + SY0 * 86
def px_to_xy(x, y):
    return (X0 + SX * x, Y0 - SY * y)

gis = json.loads((ROOT / "modular/buildings/target_buildings_gis.json").read_text(encoding="utf8"))["LWSN"]["world_polygon"]
ring = [(float(x-MARKER[0]), float(y-MARKER[1])) for x,y in gis]
if len(ring)>1 and ring[0]==ring[-1]: ring=ring[:-1]

def point_in_poly(p, poly):
    x,y=p; inside=False
    for i,(x1,y1) in enumerate(poly):
        x2,y2=poly[(i+1)%len(poly)]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:
            inside=not inside
    return inside

def segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    if dx*dx+dy*dy==0: return math.hypot(p[0]-a[0],p[1]-a[1])
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))

def near_envelope(p):
    return min(segment_distance(p,ring[i],ring[(i+1)%len(ring)]) for i in range(len(ring))) < 0.42

mat = bpy.data.materials.get("LWSN_R8_Plan_Interior_Walls") or bpy.data.materials.new("LWSN_R8_Plan_Interior_Walls")
mat.diffuse_color=(0.67,0.65,0.59,1)
mat.use_nodes=True
bsdf=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value=(0.56,0.54,0.49,1)
bsdf.inputs["Roughness"].default_value=0.88
floor_mat=bpy.data.materials.get("LWSN_R8_Upper_Floor_Slab") or bpy.data.materials.new("LWSN_R8_Upper_Floor_Slab")
floor_mat.diffuse_color=(0.42,0.46,0.49,1); floor_mat.use_nodes=True
next(n for n in floor_mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Base Color"].default_value=(0.38,0.42,0.44,1)

def add_object_mesh(name, verts, faces, material, props):
    me=bpy.data.meshes.new(name+"_mesh"); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob.parent=root; ob.matrix_parent_inverse= root.matrix_world.inverted()
    for k,v in props.items(): ob[k]=v
    return ob

def add_slab(floor,z):
    # Floor outline follows the complete official GIS ring, including the R7 vestibule.
    thickness=0.16
    n=len(ring); verts=[(x,y,z) for x,y in ring]+[(x,y,z-thickness) for x,y in ring]
    faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=add_object_mesh(f"LWSN_R8_Floor_{floor}_GIS_Outline_Slab",verts,faces,floor_mat,{
        "source":"Purdue CS Lawson floor plan L%d + BuildingShapesZip4 FID 59"%floor,
        "plan_registration":"R7 north-up GIS/L1 affine fit reused; source page outline visually overlays the GIS ring",
        "vertical_status":"schematic display elevation; not measured",
        "slab_thickness_status":"illustrative 0.16 m; not source-measured"})
    return ob

def add_partition_mesh(floor,z):
    data=json.loads((AUD/f"floor{floor}_walltrace_round8.json").read_text(encoding="utf8"))
    # Stair runs and riser marks are not wall linework. The plan's main stair zones are
    # preserved in the source overlays; their vertical continuity is not guessed here.
    stair_boxes={
        2:[(605,687,88,173),(325,402,800,938),(520,600,775,875)],
        3:[(625,705,84,173),(325,402,798,940)]
    }[floor]
    filtered=[]
    for x1,y1,x2,y2 in data["segments_px"]:
        length=math.hypot(x2-x1,y2-y1)*min(SX,SY)
        if length<1.3: continue
        mx,my=(x1+x2)/2,(y1+y2)/2
        if any(a<=mx<=b and c<=my<=d for a,b,c,d in stair_boxes): continue
        p1=px_to_xy(x1,y1); p2=px_to_xy(x2,y2); mid=((p1[0]+p2[0])/2,(p1[1]+p2[1])/2)
        # Reject any segment whose endpoints or center approach the GIS boundary.
        # This avoids fragmenting the verified structural shell with auto-traced
        # raster strokes from window frames, ticks, and exterior linework.
        if (not point_in_poly(p1,ring) or not point_in_poly(p2,ring) or
                not point_in_poly(mid,ring) or near_envelope(p1) or
                near_envelope(p2) or near_envelope(mid)):
            continue
        filtered.append((p1,p2,length))
    # Collapse all plan-derived partition cuboids into a single mesh per floor to keep
    # the modular export efficient. Width and height are visual approximations.
    thickness=0.12; height=2.55
    verts=[];faces=[]
    for (x1,y1),(x2,y2),length in filtered:
        dx,dy=x2-x1,y2-y1; ll=math.hypot(dx,dy)
        if ll<1e-6: continue
        nx,ny=-dy/ll*thickness/2,dx/ll*thickness/2
        base=len(verts)
        verts.extend([(x1+nx,y1+ny,z),(x2+nx,y2+ny,z),(x2-nx,y2-ny,z),(x1-nx,y1-ny,z),
                      (x1+nx,y1+ny,z+height),(x2+nx,y2+ny,z+height),(x2-nx,y2-ny,z+height),(x1-nx,y1-ny,z+height)])
        faces.extend([(base,base+1,base+2,base+3),(base+4,base+7,base+6,base+5),
                      (base,base+4,base+5,base+1),(base+1,base+5,base+6,base+2),
                      (base+2,base+6,base+7,base+3),(base+3,base+7,base+4,base)])
    ob=add_object_mesh(f"LWSN_R8_Floor_{floor}_Plan_Derived_Partitions",verts,faces,mat,{
        "source_pdf":f"https://www.cs.purdue.edu/resources/docs/lawson_{floor}.PDF",
        "source_pdf_file":f"audit/batch2_lawson/lawson_{floor}.pdf",
        "horizontal_method":"long orthogonal low-chroma partition strokes traced from the official raster plan; filtered against GIS FID 59 envelope",
        "horizontal_uncertainty_m":"approximately 0.3 m raster edge-pick and pixel line-width uncertainty inherited from R7 registration",
        "vertical_status":"schematic display story elevation and 2.55 m partition height; no measured section found",
        "partition_thickness_status":"illustrative 0.12 m; not measured",
        "stair_status":"stair zones excluded from automated wall traces; no unsupported flights added",
        "retained_source_segments":len(filtered)})
    return ob,len(filtered)

def add_roof_terrace_notch():
    """Rebuild the schematic flat roof with the plan-verified third-floor terrace open."""
    old=bpy.data.objects.get("LWSN_Roof_Surface")
    roof_material=(old.data.materials[0] if old and old.data.materials else previous_roof_material) or floor_mat
    # The official L3 plan labels Tolonga Terrace. Trace its interior edge at the
    # registered raster points (622,960)->(570,1085), then follow the matching GIS
    # outer vertices. Remove GIS vestibule-chain vertices 42..51 from the roof edge;
    # those points belong to the outside of the L3 open terrace. This makes a notch
    # connected to the building perimeter rather than a floating roof hole.
    roof_ring=ring[:42]
    roof_ring += [px_to_xy(622,960),px_to_xy(570,1085),ring[52]]
    z=13.8  # inherited model datum; roof elevation remains unverified
    n=len(roof_ring); thickness=.14
    verts=[(x,y,z) for x,y in roof_ring]+[(x,y,z-thickness) for x,y in roof_ring]
    faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new("LWSN_R8_Roof_Terrace_Notch_mesh")
    me.from_pydata(verts,[],faces);me.materials.append(roof_material);me.update()
    roof=bpy.data.objects.new("LWSN_R8_Roof_Surface_With_L3_Terrace_Notch",me)
    col.objects.link(roof);roof.parent=root;roof.matrix_parent_inverse=root.matrix_world.inverted()
    roof["source_pdf"]="https://www.cs.purdue.edu/resources/docs/lawson_3.PDF"
    roof["source_feature"]="Tolonga Terrace is labeled on the official LWSN third-floor plan; the official CS building-hours page also lists the 3rd Floor Terrace/Balcony."
    roof["horizontal_method"]="GIS FID 59 perimeter with the terrace inner edge traced from the registered L3 PDF raster; the roof deck is not rendered across the terrace zone."
    roof["vertical_status"]="Not measured; this retains the previous 13.8 m roof datum."
    roof["terrace_edge_uncertainty"]="Approx. 0.3 m plan raster edge-pick/registration uncertainty; interior terrace boundary traced visually from PDF."
    if old: bpy.data.objects.remove(old,do_unlink=True)
    return roof.name

# L2 is registered to existing L2 landings at approximately 4.0 m. The L3 value
# repeats the visible R3 flight rise only as a display assumption, not as a measured
# elevation. The GIS NUM_LEVELS field does not establish story elevations.
levels={2:4.0,3:7.2}
summary={}
for floor,z in levels.items():
    slab=add_slab(floor,z)
    wall,n=add_partition_mesh(floor,z+0.16)
    summary[str(floor)]={"z_slab_top_m":z,"z_status":"schematic; L2 aligned to existing R3 landing datum; L3 repeats R3 stair rise as visual assumption","partition_segments":n,"slab":slab.name,"walls":wall.name}
summary["roof_terrace_opening"]=add_roof_terrace_notch()

# Preserve collection-root identity and make all new parts explicit children.
for ob in col.objects:
    ob.parent=root
    ob.matrix_parent_inverse=root.matrix_world.inverted()

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({"saved":str(ASSET),"upper_floor_geometry":summary,"objects_added":len(col.objects)},indent=2))

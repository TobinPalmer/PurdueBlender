"""Build the Life Science Ranges greenhouse complex from official GIS and imagery evidence.

Run with Blender 5.2: blender -b --python this_script.py
The exported asset remains in campus-local coordinates and uses the existing collection name.
"""
from __future__ import annotations
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

BUILDING_ID = "massing_life_science_ranges_greenhouse_and_service_building_c96231f"
ASSET_COLLECTION = "Asset_" + BUILDING_ID
ASSET_SCENE = "Building_" + BUILDING_ID
ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = Path(__file__).resolve().parent / (BUILDING_ID + ".blend")
EVIDENCE = ROOT / "audit" / "life_science_ranges_greenhouse_and_service_building_c96231f"
GIS_PATH = EVIDENCE / "sources" / "purdue_gis_fid915.geojson"
IMAGE_BBOX = (-86.9200, 40.4215, -86.9165, 40.4238)  # west, south, east, north, EPSG:4326
IMAGE_SIZE = (1800, 1200)
GEO_ORIGIN = (40.4274, -86.9137)

# Roof footprints interpreted from the orthorectified ArcGIS World Imagery crop.
# Pixels are in the saved image extent above; ranges align with the official FID 915 polygon.
# The final room count follows the 2022 Purdue site exhibit (Ranges 1,3,5,7-14).
RANGE_ROWS = [
    {"label":"Range 01", "pixels":(656,400,860,457), "room_count":1, "gables":2},
    {"label":"Ranges 03-04", "pixels":(314,466,858,526), "room_count":2, "gables":2},
    {"label":"Ranges 05-06", "pixels":(314,530,858,607), "room_count":2, "gables":3},
    {"label":"Ranges 07-08", "pixels":(353,621,858,672), "room_count":2, "gables":2},
    {"label":"Ranges 09-10", "pixels":(414,693,858,745), "room_count":2, "gables":2},
    {"label":"Ranges 11-12", "pixels":(414,762,858,813), "room_count":2, "gables":2},
    {"label":"Ranges 13-14", "pixels":(388,852,761,969), "room_count":2, "gables":4},
]
SERVICE_PIXELS = (286,468,357,810)

# Empty startup and stable scene/collection names for the project library loader.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = ASSET_SCENE
scene.render.engine = "CYCLES"
asset = bpy.data.collections.new(ASSET_COLLECTION)
scene.collection.children.link(asset)
scene.world = bpy.data.worlds.new("Lilly Greenhouse Preview World")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.28,0.34,0.40,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.75

# Convert the official feature to the documented project meter system. Center of its projected
# GIS bounds is the proposed Placement_<id> origin; the master coordinator will apply it.
feature = json.loads(GIS_PATH.read_text(encoding="utf-8"))["features"][0]
rings_geo = feature["geometry"]["coordinates"]
gis_props = feature["properties"]
# The service exposes this field literally as ``Extrution=12`` (integer), but
# provides no field description, vertical units, or definition. Preserve the
# source value as metadata without treating it as a measured height.
asset["official_gis_feature_id"] = int(gis_props["FID"])
asset["official_gis_building_abbr"] = str(gis_props["BLDG_ABBR"])
asset["official_gis_extrution_value"] = int(gis_props["Extrution"])
asset["official_gis_extrution_interpretation"] = "Raw integer attribute only; units and semantics are undocumented, so it is not used as a measured vertical height."
asset["height_status"] = "Estimated visual reconstruction; no dimensioned as-built section/elevation located."
asset["estimated_greenhouse_eave_height_m"] = 3.65
asset["estimated_greenhouse_ridge_height_m"] = 5.95
asset["estimated_service_wing_height_m"] = 6.8
def ll_to_world(lon,lat):
    x=(lon-GEO_ORIGIN[1])*111412.84*math.cos(math.radians(GEO_ORIGIN[0]))
    y=(lat-GEO_ORIGIN[0])*111040.0
    return (x,y)
all_world=[ll_to_world(p[0],p[1]) for ring in rings_geo for p in ring]
origin=( (min(p[0] for p in all_world)+max(p[0] for p in all_world))/2,
         (min(p[1] for p in all_world)+max(p[1] for p in all_world))/2 )

def pixel_to_local(px,py):
    west,south,east,north=IMAGE_BBOX
    lon=west+(px/IMAGE_SIZE[0])*(east-west)
    lat=north-(py/IMAGE_SIZE[1])*(north-south)
    x,y=ll_to_world(lon,lat)
    return (x-origin[0],y-origin[1])

# Materials: all procedural and packed in the Blend, no external dependencies.
def make_material(name, color, roughness=0.45, metallic=0.0, transmission=0.0, alpha=1.0, emission=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,alpha); m.use_nodes=True
    n=m.node_tree.nodes; p=n.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=roughness
    p.inputs["Metallic"].default_value=metallic
    if "Transmission Weight" in p.inputs: p.inputs["Transmission Weight"].default_value=transmission
    if "Alpha" in p.inputs: p.inputs["Alpha"].default_value=alpha
    if emission:
        if "Emission Color" in p.inputs: p.inputs["Emission Color"].default_value=(*emission,1)
        if "Emission Strength" in p.inputs: p.inputs["Emission Strength"].default_value=0.22
    if alpha < 0.999:
        try: m.surface_render_method="BLENDED"
        except Exception:
            try: m.surface_render_method="DITHERED"
            except Exception: pass
    return m

mat_glass=make_material("Horticultural low-iron glass",(0.57,0.76,0.78),0.13,0.12,0.55,0.34)
mat_glass_roof=make_material("Pale greenhouse roof glazing",(0.67,0.79,0.76),0.19,0.08,0.40,0.43)
mat_aluminum=make_material("Anodized aluminum framing",(0.56,0.64,0.66),0.28,0.32)
mat_steel=make_material("Dark galvanized greenhouse steel",(0.19,0.23,0.24),0.3,0.72)
mat_concrete=make_material("Warm gray concrete plinth",(0.43,0.43,0.40),0.83)
mat_concrete.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=0.88
mat_brick=make_material("Service building red-brown brick",(0.33,0.12,0.075),0.84)
# Subtle procedural brick relief provides scale and mortar definition.
nt=mat_brick.node_tree; nodes=nt.nodes; links=nt.links; bs=nodes.get("Principled BSDF")
tex=nodes.new("ShaderNodeTexBrick"); tex.inputs["Color1"].default_value=(0.38,0.16,0.10,1); tex.inputs["Color2"].default_value=(0.24,0.075,0.045,1)
tex.inputs["Mortar"].default_value=(0.30,0.29,0.26,1); tex.inputs["Scale"].default_value=4.0; tex.inputs["Mortar Size"].default_value=0.025; tex.inputs["Brick Width"].default_value=0.6; tex.inputs["Row Height"].default_value=0.28
coord=nodes.new("ShaderNodeTexCoord"); links.new(coord.outputs["Generated"],tex.inputs["Vector"]); links.new(tex.outputs["Color"],bs.inputs["Base Color"])
bump=nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=0.16; bump.inputs["Distance"].default_value=0.018; links.new(tex.outputs["Color"],bump.inputs["Height"]); links.new(bump.outputs["Normal"],bs.inputs["Normal"])
mat_roof=make_material("Service wing standing-seam roof",(0.31,0.34,0.34),0.36,0.62)
mat_bench=make_material("Galvanized growing bench",(0.40,0.46,0.43),0.43,0.62)
mat_tray=make_material("Green propagation trays",(0.12,0.25,0.12),0.52)
mat_soil=make_material("Growing media",(0.15,0.10,0.055),0.95)
mat_pot=make_material("Nursery pot dark polymer",(0.08,0.09,0.08),0.75)
mat_leaf1=make_material("Plant foliage deep green",(0.055,0.24,0.10),0.73)
mat_leaf2=make_material("Plant foliage fresh green",(0.14,0.36,0.12),0.72)
mat_leaf3=make_material("Plant foliage olive",(0.30,0.39,0.12),0.74)
mat_stem=make_material("Greenhouse plant stems",(0.12,0.22,0.08),0.76)
mat_led=make_material("Full spectrum grow-light diffuser",(0.82,0.94,0.86),0.28,0.15,0,1,(0.72,0.91,0.72))
mat_conveyor=make_material("Phenotyping conveyor belt",(0.11,0.13,0.13),0.5,0.55)
mat_sign=make_material("Greenhouse wayfinding letters",(0.91,0.82,0.57),0.42,0.4)

# Mesh batching primitives keep the linked building library manageable.
class Builder:
    def __init__(self,name,material): self.name=name; self.material=material; self.v=[]; self.f=[]
    def box(self,center,dims):
        x,y,z=center; dx,dy,dz=[d/2 for d in dims]; i=len(self.v)
        self.v.extend([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),
                       (x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)])
        self.f.extend([(i+a,i+b,i+c,i+d) for a,b,c,d in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    def rod(self,a,b,w,depth=None):
        a=Vector(a); b=Vector(b); axis=b-a
        if axis.length<1e-6: return
        axis.normalize(); depth=depth or w
        ref=Vector((0,0,1)) if abs(axis.z)<0.94 else Vector((0,1,0))
        side=axis.cross(ref).normalized(); up=axis.cross(side).normalized()
        s=side*(w/2); u=up*(depth/2); i=len(self.v)
        for p in (a-s-u,a+s-u,a+s+u,a-s+u,b-s-u,b+s-u,b+s+u,b-s+u): self.v.append(tuple(p))
        self.f.extend([(i+a,i+b,i+c,i+d) for a,b,c,d in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    def quad(self,pts):
        i=len(self.v); self.v.extend([tuple(p) for p in pts]); self.f.append(tuple(range(i,i+len(pts))))
    def triangle(self,pts): self.quad(pts)
    def mesh(self,collection=asset):
        if not self.f: return None
        me=bpy.data.meshes.new(self.name+"Mesh"); me.from_pydata(self.v,[],self.f); me.materials.append(self.material); me.update()
        ob=bpy.data.objects.new(self.name,me); collection.objects.link(ob)
        return ob

# Exact source outline curb/threshold from the official two-ring polygon. This preserves the
# GIS structural envelope and its internal void; row-by-row glazed volumes are drawn from imagery.
def make_ring_thresholds():
    b=Builder("GIS 915 perimeter concrete curb",mat_concrete)
    for ring in rings_geo:
        pts=[(*((ll_to_world(p[0],p[1])[0]-origin[0],ll_to_world(p[0],p[1])[1]-origin[1])),0.22) for p in ring]
        for a,c in zip(pts,pts[1:]+pts[:1]): b.rod(a,c,0.22,0.35)
    b.mesh()

make_ring_thresholds()

# Build large glass range row modules as transparent glass shells with visible mullions,
# aluminum posts, gutters and ridge/vent rails.
row_meta=[]
all_benches=Builder("Research benches and interior tables",mat_bench)
all_trays=Builder("Greenhouse propagation trays",mat_tray)
all_soil=Builder("Plant media and pots",mat_soil)
all_pots=Builder("Pots",mat_pot)
all_plants=[Builder("Foliage variant 1",mat_leaf1),Builder("Foliage variant 2",mat_leaf2),Builder("Foliage variant 3",mat_leaf3)]
all_stems=Builder("Plant stems",mat_stem)
all_lights=Builder("Full-spectrum LED strips",mat_led)
all_conveyors=Builder("Phenotyping conveyor system",mat_conveyor)

for idx,row in enumerate(RANGE_ROWS):
    px1,py1,px2,py2=row["pixels"]
    q=[pixel_to_local(px1,py1),pixel_to_local(px2,py2)]
    x1,x2=sorted((q[0][0],q[1][0])); y1,y2=sorted((q[0][1],q[1][1]))
    # Both vertical values are estimated proportions from available aerial and
    # Purdue photos; no as-built dimensions are present in those sources.
    length=x2-x1; width=y2-y1; eave=3.65; peak=5.95
    # low sill/base footprint
    base=Builder(row["label"]+" low concrete sill",mat_concrete)
    base.box(((x1+x2)/2,(y1+y2)/2,0.22),(length,width,0.44)); base.mesh()
    shell=Builder(row["label"]+" glazing",mat_glass)
    frame=Builder(row["label"]+" aluminum frame",mat_aluminum)
    dark=Builder(row["label"]+" galvanized roof trusses",mat_steel)
    gables=max(1,int(row["gables"]))
    span=width/gables
    # each main ridge runs along the E-W length; two to four pitched spans cover each range group
    for gi in range(gables):
        yl=y1+gi*span; yr=yl+span; ym=(yl+yr)/2
        # glass long-side walls and pitched roof panels
        shell.quad([(x1,yl,0.42),(x2,yl,0.42),(x2,yl,eave),(x1,yl,eave)])
        shell.quad([(x1,yr,0.42),(x1,yr,eave),(x2,yr,eave),(x2,yr,0.42)])
        shell.quad([(x1,yl,eave),(x2,yl,eave),(x2,ym,peak),(x1,ym,peak)])
        shell.quad([(x1,ym,peak),(x2,ym,peak),(x2,yr,eave),(x1,yr,eave)])
        # gable-end panes (rectangular lower section and two triangular peaks)
        shell.quad([(x1,yl,0.42),(x1,yr,0.42),(x1,yr,eave),(x1,yl,eave)])
        shell.triangle([(x1,yl,eave),(x1,ym,peak),(x1,yr,eave)])
        shell.quad([(x2,yl,0.42),(x2,yl,eave),(x2,yr,eave),(x2,yr,0.42)])
        shell.triangle([(x2,yl,eave),(x2,yr,eave),(x2,ym,peak)])
        # eave, ridge and base continuous members
        for yy,zz in ((yl,0.45),(yr,0.45),(yl,eave),(yr,eave),(ym,peak)):
            frame.rod((x1,yy,zz),(x2,yy,zz),0.11)
        # principal transverse portal frames and roof purlins every ~3.2 m
        station_count=max(2,int(math.ceil(length/3.2)))
        for j in range(station_count+1):
            xx=x1+length*j/station_count
            for yy in (yl,yr):
                frame.rod((xx,yy,0.42),(xx,yy,eave),0.085)
            frame.rod((xx,yl,eave),(xx,ym,peak),0.09)
            frame.rod((xx,ym,peak),(xx,yr,eave),0.09)
            # horizontal cross-tie strengthens the lightweight greenhouse frame
            frame.rod((xx,yl,2.25),(xx,yr,2.25),0.07)
        # secondary vertical glazing mullions and horizontal wall rails
        mullions=max(2,int(math.ceil(length/2.4)))
        for j in range(1,mullions):
            xx=x1+length*j/mullions
            for yy in (yl,yr): frame.rod((xx,yy,0.45),(xx,yy,eave),0.045)
        for z in (1.4,2.45,3.3):
            frame.rod((x1,yl,z),(x2,yl,z),0.055); frame.rod((x1,yr,z),(x2,yr,z),0.055)
        # roof ribs/purlins parallel to the ridge, with subtle vent frames along the peak
        for k in range(1,4):
            yy=yl+span*k/4
            zz=eave+(peak-eave)*(1-abs(yy-ym)/(span/2))
            frame.rod((x1,yy,zz),(x2,yy,zz),0.045)
        # ridge vent housings and operable roof panels
        for xx0 in (x1+length*0.22,x1+length*0.52,x1+length*0.82):
            dark.rod((xx0,ym,peak+0.05),(min(xx0+length*0.08,x2-0.3),ym,peak+0.16),0.07)
        # internal divider panels at room boundaries (Purdue plan references 14 named ranges)
        rooms=int(row["room_count"])
        for j in range(1,rooms):
            xx=x1+length*j/rooms
            shell.quad([(xx,yl,0.55),(xx,yr,0.55),(xx,yr,peak-0.18),(xx,yl,peak-0.18)])
            frame.rod((xx,yl,0.45),(xx,yl,eave),0.07)
            frame.rod((xx,yr,0.45),(xx,yr,eave),0.07)
            frame.rod((xx,ym,peak-0.18),(xx,ym,peak),0.055)
        # growing benches in each span; interior has paired beds and central walking aisles
        bench_len=max(4.0,length/rooms-1.0)
        for room_i in range(rooms):
            room_left=x1+length*room_i/rooms; room_right=x1+length*(room_i+1)/rooms
            bed_start=room_left+0.55; bed_end=room_right-0.55
            if bed_end-bed_start<1.4: continue
            for side in (-1,1):
                by=ym+side*span*0.23
                bw=min(1.35,span*0.31)
                cx=(bed_start+bed_end)/2; bl=bed_end-bed_start
                all_benches.box((cx,by,1.03),(bl,bw,0.10))
                all_trays.box((cx,by,1.11),(bl-0.2,bw-0.1,0.05))
                # bench legs and cross braces
                leg_n=max(2,int(bl/3.5))
                for lk in range(leg_n+1):
                    lx=bed_start+bl*lk/leg_n
                    for edge in (-1,1):
                        yy=by+edge*(bw/2-0.06)
                        all_benches.box((lx,yy,0.53),(0.07,0.07,0.96))
                # potted plant rows, botanically varied but restrained
                nplants=max(2,int(bl/2.8))
                for pi in range(nplants):
                    px=bed_start+bl*(pi+0.5)/nplants
                    py=by
                    all_pots.box((px,py,1.23),(0.34,0.34,0.22))
                    all_soil.box((px,py,1.35),(0.30,0.30,0.035))
                    all_stems.rod((px,py,1.36),(px,py,2.0),0.035)
                    for li in range(5):
                        ang=li*2*math.pi/5+pi*0.3
                        vx=px+math.cos(ang)*0.26; vy=py+math.sin(ang)*0.26
                        z=1.55+(li%3)*0.16
                        variant=(pi+li+idx)%3
                        # flattened ellipsoidal leaf made from two triangles, gently cupped
                        L=0.34; W=0.12
                        dx=math.cos(ang); dy=math.sin(ang); pxp=-dy; pyp=dx
                        leaf=all_plants[variant]
                        basept=(px,py,z); tip=(vx+dx*L,vy+dy*L,z+0.12)
                        edge1=(vx+pxp*W,vy+pyp*W,z+0.02); edge2=(vx-pxp*W,vy-pyp*W,z+0.02)
                        leaf.quad([basept,edge1,tip,edge2])
                # LED bars below truss chord for controlled crop-lighting
                for lx in (bed_start+0.7,(bed_start+bed_end)/2,bed_end-0.7):
                    all_lights.box((lx,by,3.22),(0.9,0.08,0.045))
        # ceiling conduit and climate-control mist header
        dark.rod((x1+0.6,ym,peak-0.35),(x2-0.6,ym,peak-0.35),0.045)
    shell.mesh(); frame.mesh(); dark.mesh()
    row_meta.append({"label":row["label"],"local_bounds_m":[[x1,x2],[y1,y2],[0,peak]],"room_count":row["room_count"],"gables":gables})

all_benches.mesh(); all_soil.mesh(); all_pots.mesh(); all_stems.mesh()
for i,b in enumerate(all_plants): b.mesh()
all_lights.mesh()

# Service/headhouse wing, read from the west-side block in the official aerial. Red brick end
# walls, glazed two-storey public/process frontage, utility doors, roof equipment and the sign
# shown in Purdue's 2026 exterior photo.
sx1,sy1,sx2,sy2=SERVICE_PIXELS
s1=pixel_to_local(sx1,sy1); s2=pixel_to_local(sx2,sy2)
sx0,sx1w=sorted((s1[0],s2[0])); sy0,sy1w=sorted((s1[1],s2[1]))
# 6.8 m is an estimated service-wing height from the photo silhouette only.
sw=sx1w-sx0; sd=sy1w-sy0; sh=6.8
svc=Builder("Greenhouse service wing brick masses",mat_brick)
svc.box(((sx0+sx1w)/2,(sy0+sy1w)/2,sh/2),(sw,sd,sh)); svc.mesh()
# concrete footing/cap and roof panel
foot=Builder("Service wing concrete base",mat_concrete); foot.box(((sx0+sx1w)/2,(sy0+sy1w)/2,0.25),(sw+0.3,sd+0.3,0.5)); foot.mesh()
roof=Builder("Service wing roof and coping",mat_roof); roof.box(((sx0+sx1w)/2,(sy0+sy1w)/2,sh+0.12),(sw+0.35,sd+0.35,0.24)); roof.mesh()
# Glazed curtain wall on the east face, with a brick parapet and repeated aluminum mullions.
front_x=sx1w+0.05
curtain=Builder("Service wing glass curtain wall",mat_glass)
curtain.quad([(front_x,sy0+0.7,0.75),(front_x,sy1w-0.7,0.75),(front_x,sy1w-0.7,sh-0.65),(front_x,sy0+0.7,sh-0.65)])
curtain.mesh()
curtain_frame=Builder("Service wing curtain wall mullions",mat_aluminum)
for z in (0.7,1.05,2.25,3.45,4.65,6.0): curtain_frame.rod((front_x+0.08,sy0+0.6,z),(front_x+0.08,sy1w-0.6,z),0.075)
segments=max(2,int(sd/2.2))
for i in range(segments+1):
 yy=sy0+0.6+(sd-1.2)*i/segments
 curtain_frame.rod((front_x+0.08,yy,0.7),(front_x+0.08,yy,6.05),0.06)
curtain_frame.mesh()
# Main entrance vestibule, loading doors, louvers, service-room windows and rooftop plant.
svc_details=Builder("Service wing doors louvers and roof equipment",mat_steel)
# south-facing loading/entry door panels along the short end
for xoff in (-0.32,0.32):
    svc_details.box((sx0+sw/2+xoff,sy0-0.09,1.6),(0.48,0.13,3.2))
# utility louvers along the exterior west elevation
for i in range(11):
    yy=sy0+4.5+i*(sd-9.0)/10
    svc_details.box((sx0-0.08,yy,3.4),(0.13,1.1,0.8))
# HVAC units distributed on flat roof
for i in range(4):
    yy=sy0+sd*(i+0.6)/5
    svc_details.box(((sx0+sx1w)/2,yy,sh+0.65),(sw*0.45,1.35,0.85))
svc_details.mesh()
# Modest roof drainage/gutter and downspouts along the long exterior wall.
gutter=Builder("Service wing roof drainage",mat_aluminum)
gutter.rod((sx0-0.08,sy0,sh-0.08),(sx0-0.08,sy1w,sh-0.08),0.13)
for yy in (sy0+3,sy0+sd/2,sy1w-3): gutter.rod((sx0-0.08,yy,sh-0.1),(sx0-0.08,yy,0.28),0.08)
gutter.mesh()

# Small sign board and 3D lettering on the service-building brick end (evidence: Purdue 2026 photo).
sign=Builder("Service building wayfinding panel",mat_steel)
sign.box((sx0-0.08,(sy0+sy1w)/2,4.55),(0.12,min(8.5,sd*0.25),1.45)); sign.mesh()
font=bpy.data.curves.new("Lilly greenhouse service sign text","FONT")
font.body="LILLY HALL OF LIFE SCIENCES\nGREENHOUSE SERVICE BUILDING"
font.size=0.35; font.space_line=1.15; font.extrude=0.002; font.align_x="CENTER"
text_obj=bpy.data.objects.new("Greenhouse service building sign",font); asset.objects.link(text_obj)
text_obj.location=(sx0-0.16,(sy0+sy1w)/2,4.32)
text_obj.rotation_euler=(math.radians(90),0,math.radians(90)); font.materials.append(mat_sign)

# Central clean-transfer conveyor line through connecting range corridor, with supports and stations.
conv=Builder("Central plant phenotyping conveyor",mat_conveyor)
# Corridor runs across the center of the complex along the campus Y axis; keep within source bounds.
conveyor_x=(min(pixel_to_local(x,y)[0] for x,y in [(656,400),(860,457)])+max(pixel_to_local(x,y)[0] for x,y in [(314,466),(858,526)]))/2
for yi in range(0,7):
    y=sy0+sd*(yi+0.5)/7
    conv.box((conveyor_x,y,1.25),(0.65,sd/7-0.12,0.18))
    conv.box((conveyor_x,y,0.72),(0.07,0.07,1.0))
    # small crop tray riding above the conveyor
    all_trays.box((conveyor_x,y,1.39),(0.42,0.42,0.1))
conv.mesh(); all_trays.mesh()

# Procedural interpretation of the 14 range numbers in the official 2022 campus plan. A small
# placard at each room entry provides scale; labels face the central service corridor.
range_labels=Builder("Range entry plaques",mat_aluminum)
for i,row in enumerate(row_meta,1):
    (x1,x2),(y1,y2),_=row["local_bounds_m"]
    y=(y1+y2)/2
    # repeated entry panels along the south/end wall are discreet and do not alter the roof footprint
    x=x1+0.75
    range_labels.box((x,y,2.4),(0.12,1.2,0.48))
range_labels.mesh()

# Review scene is separate from the exported library collection; master linking imports only asset.
review=bpy.data.scenes.new("Review_"+BUILDING_ID)
review.collection.children.link(asset)
review.render.engine="CYCLES"
review.cycles.samples=24
review.render.resolution_x=1400; review.render.resolution_y=1000; review.render.resolution_percentage=100; review.view_settings.exposure=1.0
review.render.image_settings.file_format="PNG"
review.render.film_transparent=False
review.view_settings.view_transform="AgX"
review.world=scene.world

def look_at(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
def make_camera(name,loc,target,ortho,scene_target):
    data=bpy.data.cameras.new(name); data.type="ORTHO"; data.ortho_scale=ortho
    ob=bpy.data.objects.new(name,data); scene_target.collection.objects.link(ob); ob.location=loc; look_at(ob,target)
    return ob
def area_light(name,loc,target,power,size):
    d=bpy.data.lights.new(name,"AREA"); d.energy=power; d.shape="DISK"; d.size=size
    o=bpy.data.objects.new(name,d); review.collection.objects.link(o); o.location=loc; look_at(o,target)
    return o
# daylight and broad soft fill
area_light("Soft daylight key",(-85,-95,125),(0,0,0),42000,70)
area_light("Sky fill",(80,45,100),(0,0,0),28000,85)
area_light("West facade fill",(-120,40,55),(0,0,0),18000,45)

exterior=make_camera("Exterior oblique review camera",(-125,-155,115),(0,0,1),177,review)
review.camera=exterior
review.render.filepath=str(EVIDENCE/"previews"/"exterior_oblique.png")
bpy.context.window.scene=review
bpy.ops.render.render(write_still=True)

# Top-down plan view makes the GIS outline and individual greenhouse roof ridges legible.
top=make_camera("Roof plan review camera",(-3,-4,200),(0,0,0),135,review)
review.camera=top; review.render.resolution_x=1500; review.render.resolution_y=1500
review.render.filepath=str(EVIDENCE/"previews"/"roof_plan.png")
bpy.ops.render.render(write_still=True)

# Interior perspective in a central multi-bay range; benches, research plants, lighting, and frame.
row=row_meta[3]; (rx1,rx2),(ry1,ry2),rz=row["local_bounds_m"]
inside=make_camera("Greenhouse interior review camera",(rx1+12,ry1+1.8,1.45),(rx1+18,(ry1+ry2)/2,1.85),26,review)
inside.data.type="PERSP"; inside.data.lens=34
review.camera=inside; review.render.resolution_x=1400; review.render.resolution_y=900
review.render.filepath=str(EVIDENCE/"previews"/"interior_research_bench.png")
bpy.ops.render.render(write_still=True)

# Return active project to the clean building scene and save the library.
bpy.context.window.scene=scene
scene.render.resolution_x=1400; scene.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
print(json.dumps({"asset":str(ASSET_PATH),"origin_xy_m":origin,"rows":row_meta,"object_count":len(asset.objects)}))







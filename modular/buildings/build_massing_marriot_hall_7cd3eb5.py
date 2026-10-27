"""Build Marriott Hall from Purdue's GIS footprint and source photographs.

Run: blender --background modular/buildings/massing_marriot_hall_7cd3eb5.blend --python modular/buildings/build_massing_marriot_hall_7cd3eb5.py
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ASSET_ID = "massing_marriot_hall_7cd3eb5"
OBJECT_NAME = "Marriot Hall"
COLLECTION_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "marriott_hall"
SOURCE = EVIDENCE / "sources" / "purdue_feature_862_raw.json"

with SOURCE.open(encoding="utf-8-sig") as f:
    response = json.load(f)
feature = response["feature"]
attrs = feature["attributes"]
if attrs.get("FID") != 862 or attrs.get("BLDG_ABBR") != "MRRT" or attrs.get("BUILDING_N") != "Marriott Hall":
    raise RuntimeError("Purdue GIS feature 862 does not match Marriott Hall")
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
if len(ring) != 33:
    raise RuntimeError(f"Expected 33 unique vertices, received {len(ring)}")

# ArcGIS service coordinates are Web Mercator (EPSG:3857); convert to WGS84,
# then to the documented local campus approximation (meters, X east/Y north).
EARTH_R = 6378137.0
LAT0 = 40.4274
LON0 = -86.9137
def project_to_campus(x, y):
    lon = math.degrees(x / EARTH_R)
    lat = math.degrees(2.0 * math.atan(math.exp(y / EARTH_R)) - math.pi / 2.0)
    return Vector(((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
                   (lat - LAT0) * 111040.0))
points = [project_to_campus(x, y) for x, y in ring]

obj = bpy.data.objects.get(OBJECT_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
if obj is None or collection is None or obj not in collection.objects[:]:
    raise RuntimeError("Expected source building object/collection missing")
if len(collection.objects) != 1:
    raise RuntimeError("Expected exactly one object in exported collection")

# Exterior proportions are estimates. The official GIS lists 4 levels and
# Extrution=39 without documenting units; the visible facade photo shows three
# above-grade facade bands, with a large gabled roof.
EAVE_Z = 9.6
RIDGE_RISE = 3.0
ROOF_OVERHANG = 0.75

materials = []
def material(name, color, roughness=0.8, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    materials.append(m)
    return len(materials) - 1

BRICK = material("MRRT_Red_Brick", (0.40, 0.13, 0.095))
BRICK_DARK = material("MRRT_Brick_Shadow", (0.27, 0.085, 0.065))
STONE = material("MRRT_Limestone_Bands", (0.72, 0.70, 0.63))
GLASS = material("MRRT_Glazing", (0.035, 0.13, 0.18), 0.19, 0.08)
FRAME = material("MRRT_Aluminum_Frames", (0.15, 0.18, 0.18), 0.42, 0.35)
ROOF = material("MRRT_Terracotta_Metal_Roof", (0.35, 0.105, 0.07), 0.6, 0.24)
CANOPY = material("MRRT_Canopy_Aluminum", (0.76, 0.75, 0.69), 0.4, 0.25)
verts, faces, face_materials = [], [], []
def face(coords, mat):
    start = len(verts)
    verts.extend(tuple(c) for c in coords)
    faces.append(tuple(range(start, len(verts))))
    face_materials.append(mat)
def quad(a,b,c,d,mat):
    face((a,b,c,d),mat)
def box(center, tangent, normal, width, depth, height, mat):
    c = Vector(center)
    t = Vector((tangent.x,tangent.y,0)).normalized()
    n = Vector((normal.x,normal.y,0)).normalized()
    z = Vector((0,0,1)); hw=width/2; hd=depth/2; hh=height/2
    corners=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),
             (-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
    k=len(verts)
    verts.extend(tuple(c+t*a+n*b+z*h) for a,b,h in corners)
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(k+i for i in f)); face_materials.append(mat)

# Perimeter structural walls exactly follow feature 862. Add broad stone base
# and horizontal belt courses, then glazed openings and dark metal mullions.
area2=sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))
sign=1.0 if area2>0 else -1.0
edges=[]
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]
    delta=b-a; length=delta.length
    if length < 0.001:
        continue
    tangent=Vector((delta.x/length,delta.y/length))
    tangent3=Vector((tangent.x,tangent.y,0))
    outward=Vector((tangent.y,-tangent.x))*sign
    outward3=Vector((outward.x,outward.y,0))
    edges.append((a,b,length,tangent,outward,i))
    a0=Vector((a.x,a.y,0)); b0=Vector((b.x,b.y,0))
    abase=Vector((a.x,a.y,0.78)); bbase=Vector((b.x,b.y,0.78))
    atop=Vector((a.x,a.y,EAVE_Z)); btop=Vector((b.x,b.y,EAVE_Z))
    quad(a0,b0,bbase,abase,STONE)
    quad(abase,bbase,btop,atop,BRICK)
    # Projected horizontal bands establish the facade's masonry rhythm.
    for z in (3.25,6.45):
        box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+outward3*0.035,tangent,outward,length+0.02,0.16,0.12,STONE)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,EAVE_Z-0.10))+outward3*0.045,tangent,outward,length+0.06,0.24,0.20,CANOPY)

    # Window bay modules: narrower punched windows on side wings, wider glazing
    # on the long State/University-facing walls; every dimension remains visual estimate.
    if length >= 3.2:
        primary = length >= 12.0
        bay_count=max(1,int((length-1.5)//(5.2 if primary else 4.1)))
        spacing=length/(bay_count+1)
        window_width=min(spacing*(0.72 if primary else 0.62), 3.1 if primary else 2.0)
        for floor,zbase in enumerate((0.78,3.25,6.45)):
            if primary and floor==2:
                # A two-storey glazed teaching/dining bay spans the two upper bands.
                continue
            sill=3.45 if primary and floor==1 else zbase+0.58
            h=5.75 if primary and floor==1 else 1.55
            if sill+h>EAVE_Z-0.25:
                continue
            for bay in range(bay_count):
                center2=a+tangent*(spacing*(bay+1))
                # Leave an opening for the principal double-door entrance near the center.
                entrance_edge=(length>=9.0 and outward.y < -0.45)
                if floor==0 and entrance_edge and abs(spacing*(bay+1)-length/2)<1.65:
                    continue
                c=Vector((center2.x,center2.y,sill+h/2))+outward3*0.075
                box(c,tangent,outward,window_width,0.09,h,GLASS)
                # Four-piece metal frame and central mullions.
                fc=c+outward3*0.055; frame_w=0.075
                box(fc+Vector((0,0,h/2)),tangent,outward,window_width+0.18,0.13,frame_w,FRAME)
                box(fc-Vector((0,0,h/2)),tangent,outward,window_width+0.18,0.13,frame_w,FRAME)
                box(fc-tangent3*(window_width/2),tangent,outward,frame_w,0.13,h+0.08,FRAME)
                box(fc+tangent3*(window_width/2),tangent,outward,frame_w,0.13,h+0.08,FRAME)
                if primary:
                    box(fc,tangent,outward,0.06,0.14,h,FRAME)
                    if primary and floor==1:
                        box(fc+Vector((0,0,0.0)),tangent,outward,window_width,0.14,0.07,FRAME)

# Sloped roof silhouette: ridge follows the long north/south building axis,
# while the eave-to-ridge height varies across the footprint's east/west span.
minx=min(p.x for p in points); maxx=max(p.x for p in points)
miny=min(p.y for p in points); maxy=max(p.y for p in points)
centerx=(minx+maxx)/2
half=(maxx-minx)/2+ROOF_OVERHANG
ridge_z=EAVE_Z+RIDGE_RISE
def roof_z(x):
    return EAVE_Z+RIDGE_RISE*max(0.0,1.0-abs(x-centerx)/half)
for tri in tessellate_polygon([points]):
    tri_pts=[points[int(i)] for i in tri]
    face([(p.x,p.y,roof_z(p.x)) for p in tri_pts],ROOF)
# Gable infill triangles on long crosswise end walls where the boundary supports them.
for a,b,length,tangent,outward,i in edges:
    if length<15.0 or abs(tangent.y)>0.12:
        continue
    xm=(a.x+b.x)/2
    if abs(xm-centerx)>0.28*half:
        continue
    ridge_x=centerx
    face(((a.x,a.y,EAVE_Z),(b.x,b.y,EAVE_Z),(ridge_x,(a.y+b.y)/2,ridge_z)),BRICK)
    # Accent trim traces the roof slopes at the gable.
    # (The main roof plane remains the source-based footprint surface.)

# Broad glass entrance doors, paired frames, and a deep modern canopy on the
# street-facing long wall. Locate on the most substantial south-facing segment.
entry=max((e for e in edges if e[4].y < -0.45 and e[2]>=8.0),key=lambda e:e[2],default=None)
if entry:
    a,b,length,tangent,outward,_=entry
    tangent3=Vector((tangent.x,tangent.y,0))
    outward3=Vector((outward.x,outward.y,0))
    p=(a+b)/2
    door_w=min(3.2,length*0.30)
    base=Vector((p.x,p.y,1.28))+outward3*0.14
    box(base,tangent,outward,door_w,0.12,2.55,GLASS)
    box(base+outward3*0.09,tangent,outward,0.10,0.22,2.7,FRAME)
    for offset in (-door_w/2,0,door_w/2):
        box(base+tangent3*offset+outward3*0.13,tangent,outward,0.075,0.19,2.62,FRAME)
    # Flat canopy carried by subtle metal supports, directly above the door.
    canopy_center=Vector((p.x,p.y,3.05))+outward3*0.70
    box(canopy_center,tangent,outward,min(7.0,length-0.5),1.45,0.20,CANOPY)
    for offset in (-2.65,2.65):
        if abs(offset)<length/2-0.4:
            box(Vector((p.x,p.y,1.55))+tangent3*offset+outward3*0.34,tangent,outward,0.12,0.13,2.7,FRAME)
    # Two shallow entry steps.
    box(Vector((p.x,p.y,0.12))+outward3*0.56,tangent,outward,min(5.2,length-0.5),0.58,0.24,STONE)
    box(Vector((p.x,p.y,0.30))+outward3*0.30,tangent,outward,min(4.5,length-0.5),0.42,0.16,STONE)

old_mesh=obj.data
mesh=bpy.data.meshes.new(OBJECT_NAME+"_source_detail")
mesh.from_pydata(verts,[],faces)
for m in materials: mesh.materials.append(m)
mesh.update()
for poly,mat_index in zip(mesh.polygons,face_materials):
    poly.material_index=mat_index
bm=bmesh.new(); bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(mesh); bm.free(); mesh.update()
obj.data=mesh; obj.name=OBJECT_NAME
obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
if old_mesh.users==0:
    bpy.data.meshes.remove(old_mesh)
mesh.name=OBJECT_NAME+"_mesh"
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("MARRIOTT_BUILD_RESULT="+json.dumps({
    "asset_id":ASSET_ID,"source_fid":attrs["FID"],"source_code":attrs["BLDG_ABBR"],
    "outline_vertices":len(points),"mesh_vertices":len(mesh.vertices),"mesh_faces":len(mesh.polygons),
    "collection_objects":len(collection.objects),"GIS_level_attribute":attrs.get("NUM_LEVELS"),
    "GIS_extrution_attribute_units_unpublished":attrs.get("Extrution"),
    "estimated_eave_height_m":EAVE_Z,"estimated_roof_ridge_m":ridge_z,
    "footprint":"transformed from EPSG:3857 official Purdue FID 862 outline; exact source ring at grade"
}))

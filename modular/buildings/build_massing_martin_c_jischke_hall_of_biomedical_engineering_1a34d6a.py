"""Rebuild MJIS from the Purdue GIS outline and Purdue-published exterior photo.

Run from the repository root with Blender 5.2:
  blender <asset path> --background --python <this file>
"""
import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIT = os.path.join(ROOT, "audit", "martin_c_jischke_hall")
with open(os.path.join(AUDIT, "build_config.json"), encoding="utf-8") as f:
    cfg = json.load(f)
with open(os.path.join(AUDIT, cfg["source_feature_file"]), encoding="utf-8-sig") as f:
    raw = json.load(f)
feature = raw["features"][0]
if feature["attributes"].get("FID") != 407 or feature["attributes"].get("BLDG_ABBR") != "MJIS":
    raise RuntimeError("Purdue GIS source identity mismatch")
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
lat0, lon0 = 40.4274, -86.9137
points = [Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0)) for lon,lat in ring]
source_points = list(points)

# Generalize dense survey/GIS edging without erasing plan corners. Threshold is
# below the source's approx 1 m uncertainty and preserves all significant steps.
def segment_distance(p, a, b):
    d = b-a
    if d.length_squared == 0:
        return (p-a).length
    t = max(0.0, min(1.0, (p-a).dot(d)/d.length_squared))
    return (p-(a+d*t)).length

def simplify_loop(src, tolerance=0.45):
    pts = list(src)
    changed = True
    while changed and len(pts) > 3:
        changed = False
        keep = []
        n = len(pts)
        for i,p in enumerate(pts):
            a,b = pts[(i-1)%n], pts[(i+1)%n]
            if segment_distance(p,a,b) < tolerance and (p-a).length < 4.0 and (b-p).length < 4.0:
                changed = True
            else:
                keep.append(p)
        if len(keep) < 3:
            break
        pts = keep
    return pts

points = simplify_loop(points)
if len(points) < 8:
    raise RuntimeError("Footprint simplification removed too many vertices")
source_vertex_deviation = max(min(segment_distance(p, points[i], points[(i+1)%len(points)]) for i in range(len(points))) for p in source_points)
area2 = sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))
orientation = 1.0 if area2 > 0 else -1.0

blend_path = bpy.data.filepath
obj = bpy.data.objects.get(cfg["object_name"])
coll = bpy.data.collections.get(cfg["collection_name"])
if not blend_path or obj is None or coll is None or obj not in coll.objects[:]:
    raise RuntimeError("Target Blender asset structure mismatch")
if len(coll.objects) != 1:
    raise RuntimeError("Expected exactly one object in the assigned asset collection")

tag = cfg["asset_id"].upper()
materials=[]
def material(name, color, rough=0.78, metallic=0.0):
    m=bpy.data.materials.get(tag+"_"+name) or bpy.data.materials.new(tag+"_"+name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*color,1)
        bs.inputs["Roughness"].default_value=rough
        bs.inputs["Metallic"].default_value=metallic
    materials.append(m)
    return len(materials)-1

panel=material("Pale_Cladding",cfg["wall_color"])
brick=material("Red_Brick",cfg["brick_color"])
glass=material("Blue_Green_Glazing",cfg["glass_color"],0.24,0.1)
roof=material("Roof",cfg["roof_color"])
frame=material("Dark_Metal_Frames",cfg["metal_color"],0.4,0.5)
verts=[]; faces=[]; mat_ids=[]
def face(indices,mi):
    faces.append(tuple(indices)); mat_ids.append(mi)
def quad(q,mi):
    k=len(verts); verts.extend(tuple(v) for v in q); face((k,k+1,k+2,k+3),mi)
def box(center,tangent,normal,w,d,h,mi):
    c=Vector(center); t=Vector((tangent.x,tangent.y,0)).normalized(); n=Vector((normal.x,normal.y,0)).normalized(); z=Vector((0,0,1))
    hw,hd,hh=w/2,d/2,h/2
    offsets=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
    k=len(verts); verts.extend(tuple(c+t*a+n*b+z*v) for a,b,v in offsets)
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face(tuple(k+j for j in f),mi)

H=float(cfg["height_m"]); F=int(cfg["modeled_floors"]); base=0.0
brick_h=3.65; floor_h=(H-brick_h)/2.0
edges=[]
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]; delta=b-a; length=delta.length
    if length < 0.35: continue
    t=Vector((delta.x/length,delta.y/length,0)); n=Vector((t.y,-t.x,0))*orientation
    edges.append((a,b,length,t,n))
    a0=Vector((a.x,a.y,base)); b0=Vector((b.x,b.y,base)); ab=Vector((a.x,a.y,brick_h)); bb=Vector((b.x,b.y,brick_h)); at=Vector((a.x,a.y,H)); bt=Vector((b.x,b.y,H))
    quad((a0,b0,bb,ab),brick)
    quad((ab,bb,bt,at),panel)

# A central glazed upper band and pale end bays follow the official photograph.
# The photo only documents one corner; this rhythm is a generalized visual cue.
for a,b,L,t,n in edges:
    if L < 5.0: continue
    bays=max(1,int((L-1.2)//3.6))
    spacing=L/(bays+1)
    ww=min(2.25,spacing*0.67)
    for fl in range(1,F):
        z=brick_h+floor_h*(fl-0.5)
        wh=min(1.55,floor_h*0.53)
        for bay in range(bays):
            p=a.lerp(b,spacing*(bay+1)/L)
            # Ground floor retains brick between windows; upper floors carry the large glazed band.
            c=Vector((p.x,p.y,z))+n*0.08
            box(c,t,n,ww,0.07,wh,glass)
            for off in (-ww/2,0,ww/2): box(c+t*off+n*0.06,t,n,0.055,0.12,wh+0.10,frame)
            box(c+n*0.06+Vector((0,0,wh/2)),t,n,ww+0.08,0.12,0.06,frame)
            box(c+n*0.06-Vector((0,0,wh/2)),t,n,ww+0.08,0.12,0.06,frame)

# Ground-floor punched windows align with the brick plinth band.
for a,b,L,t,n in edges:
    if L<7.0: continue
    bays=max(1,int((L-1.2)//4.8)); spacing=L/(bays+1)
    for bay in range(bays):
        p=a.lerp(b,spacing*(bay+1)/L); c=Vector((p.x,p.y,1.95))+n*0.08
        box(c,t,n,min(1.45,spacing*0.55),0.07,1.45,glass)
        box(c+n*0.06,t,n,0.07,0.13,1.56,frame)

# The official building-information page identifies public entrances on both
# west and east sides. Add one schematic marker per side; exact door locations
# are not supplied by the source and should not be read as measured positions.
for side in (-1.0,1.0):
    candidates=[e for e in edges if e[4].x*side>0.7 and e[2]>7.0]
    if not candidates: continue
    a,b,L,t,n=max(candidates,key=lambda e:e[2]); p=(a+b)*0.5
    box(Vector((p.x,p.y,1.35))+n*0.12,t,n,2.35,0.08,2.65,glass)
    box(Vector((p.x,p.y,1.35))+n*0.20-t*1.20,t,n,0.12,0.20,2.65,frame)
    box(Vector((p.x,p.y,1.35))+n*0.20+t*1.20,t,n,0.12,0.20,2.65,frame)
    box(Vector((p.x,p.y,1.35))+n*0.20,t,n,0.09,0.20,2.65,frame)
    box(Vector((p.x,p.y,2.92))+n*0.45,t,n,3.2,1.15,0.18,panel)
    # Subtle slab bands keep the floor divisions legible in the overview.
    for z in (brick_h, brick_h+floor_h, H-0.22):
        box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.07,t,n,L+0.03,0.16,0.12,frame if z < H-0.3 else panel)

# A low parapet completes the flat roof silhouette while keeping the height estimate explicit.
for a,b,L,t,n in edges:
    if L<0.35: continue
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.12))+n*0.08,t,n,L+0.08,0.24,0.24,panel)

# Tessellate the generalized campus-coordinate footprint as a single flat roof.
roof_points=[Vector((p.x,p.y,0)) for p in points]
for tri in tessellate_polygon([roof_points]):
    k=len(verts)
    for idx in tri:
        p=points[int(idx)]; verts.append((p.x,p.y,H))
    face((k,k+1,k+2),roof)

old=obj.data; old_name=old.name; mesh=bpy.data.meshes.new(old_name+"_MJIS_detail"); mesh.from_pydata(verts,[],faces)
for m in materials: mesh.materials.append(m)
mesh.update()
for p,mi in zip(mesh.polygons,mat_ids): p.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
obj.data=mesh; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=old_name
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
result={"asset_id":cfg["asset_id"],"source_fid":407,"source_ring_vertices":len(ring),"generalized_ring_vertices":len(points),"maximum_source_vertex_to_generalized_outline_m":source_vertex_deviation,"height_m":H,"height_status":cfg["height_status"],"faces":len(mesh.polygons),"vertices":len(mesh.vertices),"collection_objects":len(coll.objects),"campus_bounds_xy":[[min(p.x for p in points),max(p.x for p in points)],[min(p.y for p in points),max(p.y for p in points)]]}
print("BUILD_RESULT_JSON="+json.dumps(result))

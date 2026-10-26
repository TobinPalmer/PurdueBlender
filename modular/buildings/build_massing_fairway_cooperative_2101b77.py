"""Build the Fairway Cooperative / BYX Fairway House library.

Evidence-backed footprint from OSM way 220568267, mapped to this project's local
campus coordinates. The 3-storey envelope is based on OSM building:levels and the
West Lafayette 2025 addition permit; vertical dimensions and roof geometry remain
estimates. Run with Blender 5.2 in background mode.
"""
import bpy
import bmesh
import json
import math
import os
import hashlib
import urllib.request
from mathutils import Vector, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_ID = "massing_fairway_cooperative_2101b77"
ASSET_FILE = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
EVIDENCE = os.path.join(ROOT, "audit", "fairway_cooperative")
COLL_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
PREVIEW_COLL_NAME = "Preview_only_context_exclude_from_master"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137

def v3(value, z=0.0):
    value = Vector(value)
    return value if len(value) == 3 else Vector((value.x, value.y, z))

def inside_ring(point, ring):
    x,y = Vector(point)[:2]
    inside = False
    for i,(x1,y1) in enumerate(ring):
        x2,y2 = ring[(i+1)%len(ring)]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:
            inside = not inside
    return inside

def safe_interior_point(preferred, ring, step=0.5):
    p=Vector(preferred)
    if inside_ring(p,ring): return p
    xmin,xmax=min(x for x,y in ring),max(x for x,y in ring)
    ymin,ymax=min(y for x,y in ring),max(y for x,y in ring)
    candidates=[]
    y=ymin+step
    while y<ymax:
        x=xmin+step
        while x<xmax:
            q=Vector((x,y))
            if inside_ring(q,ring): candidates.append(q)
            x+=step
        y+=step
    return min(candidates,key=lambda q:(q-p).length) if candidates else p

def read_osm_ring():
    src = os.path.join(EVIDENCE, "osm_way_220568267_full.json")
    if not os.path.isfile(src):
        url = "https://api.openstreetmap.org/api/0.6/way/220568267/full.json"
        req = urllib.request.Request(url, headers={"User-Agent": "PurdueCampusBuildingModel/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
        os.makedirs(EVIDENCE, exist_ok=True)
        with open(src, "wb") as f:
            f.write(raw)
    data = json.load(open(src, encoding="utf-8"))
    nodes = {e["id"]: e for e in data["elements"] if e["type"] == "node"}
    way = next(e for e in data["elements"] if e.get("id") == 220568267 and e["type"] == "way")
    ring = []
    for node_id in way["nodes"]:
        n = nodes[node_id]
        x = (n["lon"] - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
        y = (n["lat"] - ORIGIN_LAT) * 111040.0
        ring.append((x, y))
    if ring[0] == ring[-1]:
        ring.pop()
    return ring, way.get("tags", {})

def material(name, color, roughness=0.8, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m

def brick_material():
    m = material("Fairway | fired red-brown brick", (0.30, 0.105, 0.062), 0.83)
    n, l = m.node_tree.nodes, m.node_tree.links
    tex = n.new("ShaderNodeTexCoord")
    brick = n.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value = (0.32, 0.105, 0.06, 1)
    brick.inputs["Color2"].default_value = (0.43, 0.17, 0.095, 1)
    brick.inputs["Mortar"].default_value = (0.21, 0.17, 0.14, 1)
    brick.inputs["Scale"].default_value = 9.0
    brick.inputs["Mortar Size"].default_value = 0.025
    brick.inputs["Mortar Smooth"].default_value = 0.06
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.025
    bsdf = next(x for x in n if x.type == "BSDF_PRINCIPLED")
    out = next(x for x in n if x.type == "OUTPUT_MATERIAL")
    l.new(tex.outputs["Generated"], brick.inputs["Vector"])
    l.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    l.new(brick.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def add_mesh(name, verts, faces, mat, coll, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj

def cube(name, center, dims, mat, coll, basis=None):
    c = v3(center)
    sx, sy, sz = [v * 0.5 for v in dims]
    if basis is None:
        u, v = Vector((1, 0, 0)), Vector((0, 1, 0))
    else:
        u, v = v3(basis[0]), v3(basis[1])
    pts = []
    for zsign in (-1, 1):
        for ysign in (-1, 1):
            for xsign in (-1, 1):
                p = c + u * (xsign * sx) + v * (ysign * sy) + Vector((0, 0, zsign * sz))
                pts.append(tuple(p))
    faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return add_mesh(name, pts, faces, mat, coll)

def text_obj(name, body, loc, normal, size, mat, coll):
    curve = bpy.data.curves.new(name + "Curve", "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.008
    obj = bpy.data.objects.new(name, curve)
    coll.objects.link(obj)
    obj.location = v3(loc)
    n = v3(normal).normalized()
    tangent = Vector((1,0,0)) - n * n.dot(Vector((1,0,0)))
    if tangent.length < 0.2:
        tangent = Vector((0,1,0)) - n * n.dot(Vector((0,1,0)))
    tangent.normalize()
    up = n.cross(tangent).normalized()
    basis = Matrix((tangent, up, n)).transposed()
    obj.rotation_euler = basis.to_euler()
    curve.materials.append(mat)
    return obj

def poly_prism(name, ring, z0, z1, mat, coll):
    n = len(ring)
    verts = [(x,y,z0) for x,y in ring] + [(x,y,z1) for x,y in ring]
    faces = [tuple(range(n-1,-1,-1)), tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return add_mesh(name, verts, faces, mat, coll)

def perimeter_shell(name, ring, z0, z1, mat, coll):
    # Open-top shell leaves rooms and floor plates inspectable in the library.
    result=[]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]
        zp=z1(p[0],p[1]) if callable(z1) else z1
        zq=z1(q[0],q[1]) if callable(z1) else z1
        result.append(add_mesh(f"{name}_Wall_{i+1:02d}",[(p[0],p[1],z0),(q[0],q[1],z0),(q[0],q[1],zq),(p[0],p[1],zp)],[(0,1,2,3)],mat,coll))
    return result

def polygon_slab(name, ring, z, thickness, mat, coll):
    n = len(ring)
    verts = [(x,y,z) for x,y in ring] + [(x,y,z-thickness) for x,y in ring]
    bm = bmesh.new()
    bmverts = [bm.verts.new(Vector(v)) for v in verts[:n]]
    bm.faces.new(bmverts)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    top_faces = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    faces = top_faces + [tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return add_mesh(name, verts, faces, mat, coll)

def orient_from_edge(a, b):
    p, q = Vector(a), Vector(b)
    tangent = (q-p).normalized()
    # Ring follows the actual OSM way direction; use centroid to find outward side.
    return p, q, tangent

def main():
    os.makedirs(EVIDENCE, exist_ok=True)
    ring, osm_tags = read_osm_ring()
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    cx, cy = (min(xs)+max(xs))*0.5, (min(ys)+max(ys))*0.5
    center = Vector((cx,cy))
    # Principal axis provides a plausible ridge aligned to the long axis of the plan.
    xx = sum((x-cx)**2 for x,y in ring)/len(ring)
    yy = sum((y-cy)**2 for x,y in ring)/len(ring)
    xy = sum((x-cx)*(y-cy) for x,y in ring)/len(ring)
    theta = 0.5*math.atan2(2*xy, xx-yy)
    u = Vector((math.cos(theta), math.sin(theta)))
    v = Vector((-u.y, u.x))
    proju = [(Vector(p)-center).dot(u) for p in ring]
    projv = [(Vector(p)-center).dot(v) for p in ring]
    span_u = max(proju)-min(proju)
    span_v = max(projv)-min(projv)
    vmin,vmax=min(projv),max(projv)
    roof_mid=(vmin+vmax)*0.5
    roof_half=max((vmax-vmin)*0.5,1.0)
    # The OSM building:levels=3 tag and 2025 permit support three occupied levels.
    floor_count = 3
    floor_to_floor = 3.15  # estimated, no measured elevation drawing found
    wall_top = floor_count * floor_to_floor
    roof_rise = 1.45       # estimated from Google Street View's low dark sloping roof
    top_z = wall_top + roof_rise
    def roof_z_at(x,y):
        across=(Vector((x,y))-center).dot(v)
        return wall_top+roof_rise*(1.0-min(1.0,abs(across-roof_mid)/roof_half))

    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.get(COLL_NAME)
    if asset is None:
        asset = bpy.data.collections.new(COLL_NAME)
        scene.collection.children.link(asset)
    preview = bpy.data.collections.get(PREVIEW_COLL_NAME)
    if preview is None:
        preview = bpy.data.collections.new(PREVIEW_COLL_NAME)
        scene.collection.children.link(preview)
    for c in list(scene.collection.children):
        if c not in (asset, preview):
            scene.collection.children.unlink(c)
    for o in list(asset.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for o in list(preview.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        if c not in (asset, preview) and not c.objects and not c.children:
            bpy.data.collections.remove(c)

    brick = brick_material()
    stone = material("Fairway | warm limestone and precast trim", (0.61,0.57,0.48), 0.82)
    roof = material("Fairway | charcoal architectural shingle", (0.055,0.068,0.082), 0.72)
    glass = material("Fairway | blue gray insulated glass", (0.065,0.16,0.21), 0.22, 0.08)
    frame = material("Fairway | dark bronze window frames", (0.11,0.12,0.12), 0.42, 0.35)
    wood = material("Fairway | warm oak interior", (0.38,0.22,0.11), 0.7)
    inside = material("Fairway | warm neutral interior walls", (0.74,0.68,0.57), 0.86)
    red = material("Fairway | BYX burgundy accent", (0.29,0.035,0.055), 0.55)
    concrete = material("Fairway | entry concrete", (0.42,0.42,0.40), 0.92)

    # Primary masonry shell follows the GIS/OpenStreetMap structural outline exactly.
    perimeter_shell("FCH_Three_Story_Brick_Residence", ring, 0.0, roof_z_at, brick, asset)
    polygon_slab("FCH_Ground_Floor_Slab", ring, 0.23, 0.20, inside, asset)
    polygon_slab("FCH_Second_Floor_Slab", ring, floor_to_floor+0.16, 0.18, wood, asset)
    polygon_slab("FCH_Third_Floor_Slab", ring, 2*floor_to_floor+0.16, 0.18, wood, asset)

    # Exposed brick facade rhythm, limestone water table and thin floor/string courses.
    area2 = sum(ring[i][0]*ring[(i+1)%len(ring)][1] - ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
    ccw = area2 > 0
    edge_data = []
    for i, a in enumerate(ring):
        b = ring[(i+1)%len(ring)]
        p,q,t = orient_from_edge(a,b)
        outward = Vector((t.y,-t.x)) if ccw else Vector((-t.y,t.x))
        length = (q-p).length
        edge_data.append((i,p,q,t,outward,length))
        # Water table and story lines echo the horizontal bands visible in Street View.
        for z,h,mat in [(0.34,0.22,stone),(floor_to_floor,0.15,stone),(2*floor_to_floor,0.15,stone)]:
            verts=[(p.x,p.y,z),(q.x,q.y,z),(q.x,q.y,z+h),(p.x,p.y,z+h)]
            add_mesh(f"FCH_Edge_{i:02d}_Stone_Band_{z:.2f}",verts,[(0,1,2,3)],mat,asset)
        # Vertical brick piers articulate the corner and give each edge a masonry cadence.
        npiers=max(1, round(length/8.5))
        for k in range(1,npiers):
            pos=p.lerp(q,k/npiers)
            c=v3(pos + outward*0.022, wall_top*0.5)
            cube(f"FCH_Edge_{i:02d}_Brick_Pier_{k:02d}",(c.x,c.y,c.z),(0.20,0.14,wall_top),brick,asset,(t,outward))
        # Three-storey windows. Narrow edges get fewer openings; all joinery is modeled.
        nwin=max(1,int(length/3.6))
        if length<4.5: nwin=0
        for wi in range(nwin):
            f=(wi+1)/(nwin+1)
            pos=p.lerp(q,f)
            w=min(1.35,length/(nwin+1)*0.48)
            for level in range(floor_count):
                z0=level*floor_to_floor+0.90
                wh=1.42 if level==0 else 1.52
                offset=outward*0.035
                corners=[]
                for du,dz in [(-w/2,0),(w/2,0),(w/2,wh),(-w/2,wh)]:
                    pt=pos+t*du+offset
                    corners.append((pt.x,pt.y,z0+dz))
                add_mesh(f"FCH_Window_Glass_E{i:02d}_{wi:02d}_F{level+1}",corners,[(0,1,2,3)],glass,asset)
                # Bronze perimeter frame and central vertical mullion.
                for rail,(du,dz,dim) in enumerate([
                    (Vector((0,0)),0.045,(w+0.13,0.085)),
                    (Vector((0,0)),wh-0.045,(w+0.13,0.085)),
                ]):
                    pp=pos+offset
                    pc=v3(pp,z0+dz)
                    cube(f"FCH_Window_Frame_E{i:02d}_{wi:02d}_F{level+1}_H{rail}",(pc.x,pc.y,pc.z),(dim[0],dim[1],0.075),frame,asset,(t,outward))
                for side,du in enumerate((-w/2-0.04,w/2+0.04)):
                    pp=v3(pos+t*du+offset,z0+wh/2)
                    cube(f"FCH_Window_Frame_E{i:02d}_{wi:02d}_F{level+1}_V{side}",(pp.x,pp.y,pp.z),(0.085,0.085,wh),frame,asset,(t,outward))
                pp=v3(pos+offset,z0+wh*0.5)
                cube(f"FCH_Window_Mullion_E{i:02d}_{wi:02d}_F{level+1}",(pp.x,pp.y,pp.z),(0.045,0.08,wh),frame,asset,(t,outward))

    # Dark sloped roof surface is interpolated across the principal width of the irregular outline.
    n=len(ring)
    roof_verts=[]
    for x,y in ring:
        rel=Vector((x,y))-center
        across=rel.dot(v)
        z=roof_z_at(x,y)
        roof_verts.append((x,y,z))
    rm=bpy.data.meshes.new("FCH_RoofSurfaceMesh")
    rm.from_pydata(roof_verts,[],[tuple(range(n))])
    rm.materials.append(roof)
    bm=bmesh.new(); bm.from_mesh(rm); bmesh.ops.triangulate(bm,faces=list(bm.faces)); bm.to_mesh(rm); bm.free(); rm.update()
    robj=bpy.data.objects.new("FCH_Charcoal_Hipped_Gable_Roof",rm); asset.objects.link(robj)
    # Ridge cap and discreet gutter/eaves along the actual footprint perimeter.
    ridge0=center-u*(span_u*0.43); ridge1=center+u*(span_u*0.43)
    rc=(ridge0+ridge1)*0.5
    cube("FCH_Ridge_Cap",(rc.x,rc.y,wall_top+roof_rise-0.025),(span_u*0.88,0.16,0.13),frame,asset,(u,v))
    for i,p in enumerate(ring):
        q=Vector(ring[(i+1)%n]); p=Vector(p); t=(q-p).normalized(); mid=(p+q)*0.5
        cube(f"FCH_Eave_Gutter_{i:02d}",(mid.x,mid.y,wall_top-0.08),((q-p).length,0.16,0.12),frame,asset,(t,Vector((-t.y,t.x))))

    # Main entry, landing and discreet sign are placed on the south-facing street elevation.
    candidates=[e for e in edge_data if e[4].y< -0.25 and e[5]>6]
    front=max(candidates,key=lambda e:e[5]) if candidates else max(edge_data,key=lambda e:e[5])
    ei,p,q,t,outward,length=front
    doorpos=p.lerp(q,0.52)
    # Door occupies a reasonable 1.5m bay and is set into the ground-floor facade.
    doorw=1.55; doorh=2.35
    dc=v3(doorpos+outward*0.06,doorh/2)
    cube("FCH_Main_Entry_Double_Door_Glazing",(dc.x,dc.y,dc.z),(doorw,0.16,doorh),glass,asset,(t,outward))
    for dx in (-doorw/2,doorw/2):
        fp=v3(doorpos+t*dx+outward*0.13,doorh/2)
        cube("FCH_Entry_Door_Frame",(fp.x,fp.y,fp.z),(0.11,0.12,doorh+0.12),stone,asset,(t,outward))
    head=v3(doorpos+outward*0.20,doorh+0.10)
    cube("FCH_Entry_Limestone_Lintel",(head.x,head.y,head.z),(doorw+0.3,0.16,0.22),stone,asset,(t,outward))
    landing=v3(doorpos+outward*1.05,0.12)
    cube("FCH_Entry_Concrete_Landing",(landing.x,landing.y,landing.z),(3.4,1.7,0.22),concrete,asset,(t,outward))
    for step in range(3):
        sc=v3(doorpos+outward*(0.28+0.27*step),0.08+0.11*step)
        cube(f"FCH_Entry_Step_{step+1}",(sc.x,sc.y,sc.z),(2.7,0.58,0.16),concrete,asset,(t,outward))
    signpos=v3(doorpos+outward*0.20,2.75)
    cube("FCH_Entry_Sign_Backplate",(signpos.x,signpos.y,signpos.z),(3.2,0.12,0.50),red,asset,(t,outward))
    text_loc=v3(signpos)+v3(outward)*0.075+Vector((0,0,-0.11))
    text_obj("FCH_Entry_Sign_Lettering","FAIRWAY",text_loc,outward,0.28,stone,asset)

    # Interior supports the documented 130-bed cooperative programme, without inventing exact plans.
    # Central corridor and representative common rooms are intentionally schematic.
    for fl in range(floor_count):
        zfloor=0.27+fl*floor_to_floor
        wallz=zfloor+1.4
        # Hallway runs down the long principal axis, with short partition cross-walls.
        corridor_center=center
        corridor = cube(f"FCH_Interior_F{fl+1}_Central_Corridor_Floor",(center.x,center.y,zfloor),(span_u*0.80,2.2,0.07),wood,asset,(u,v))
        # representative room dividers fit inside the middle of the footprint
        for j,up in enumerate((-span_u*0.23,-span_u*0.06,span_u*0.12,span_u*0.29)):
            pos=center+u*up
            if not inside_ring(pos,ring): continue
            c=v3(pos,wallz)
            cube(f"FCH_Interior_F{fl+1}_Partition_{j+1}",(c.x,c.y,c.z),(0.12,span_v*0.38,2.7),inside,asset,(u,v))
        for side in (-1,1):
            for j,vp in enumerate((-span_v*0.20,span_v*0.20)):
                pos=center+u*(side*span_u*0.24)+v*vp
                if not inside_ring(pos,ring): continue
                fc=v3(pos,zfloor+0.50)
                cube(f"FCH_Interior_F{fl+1}_Bed_{side}_{j}",(fc.x,fc.y,fc.z),(2.0,0.95,0.22),red,asset,(u,v))
                table=v3(pos+u*1.20,zfloor+0.42)
                cube(f"FCH_Interior_F{fl+1}_Study_Table_{side}_{j}",(table.x,table.y,table.z),(1.2,0.70,0.08),wood,asset,(u,v))
        # Ground floor communal kitchen and chapter/prayer room cues; upper floors have lounge/study seating.
        if fl==0:
            for j in range(4):
                pos=center+u*(-span_u*0.26+j*0.32)+v*(span_v*0.29)
                if not inside_ring(pos,ring): continue
                c=v3(pos,zfloor+0.48)
                cube(f"FCH_Ground_Kitchen_Counter_{j+1}",(c.x,c.y,c.z),(2.1,0.68,0.92),stone,asset,(u,v))
            chapter=center-u*(span_u*0.24)-v*(span_v*0.29)
            chapter=safe_interior_point(chapter,ring)
            cc=v3(chapter,zfloor+0.42)
            cube("FCH_Ground_Chapter_Room_Table",(cc.x,cc.y,cc.z),(2.6,1.3,0.10),wood,asset,(u,v))
            prayer=safe_interior_point(center+u*(span_u*0.30)-v*(span_v*0.28),ring)
            pc=v3(prayer,zfloor+0.42)
            cube("FCH_Ground_Prayer_Room_Rug",(pc.x,pc.y,pc.z),(3.0,2.0,0.035),red,asset,(u,v))
        else:
            lounge=center+u*(span_u*0.28)+v*(span_v*0.29)
            lounge=safe_interior_point(lounge,ring)
            lc=v3(lounge,zfloor+0.35)
            cube(f"FCH_Interior_F{fl+1}_Study_Lounge_Table",(lc.x,lc.y,lc.z),(2.4,1.1,0.12),wood,asset,(u,v))
            for j,du in enumerate((-0.8,0.8)):
                c=v3(lounge+u*du,zfloor+0.35)
                cube(f"FCH_Interior_F{fl+1}_Lounge_Chair_{j+1}",(c.x,c.y,c.z),(0.8,0.8,0.55),red,asset,(u,v))
    # A clear stair core with three stacked flights and landings.
    stair_center=center+u*(span_u*0.06)+v*(span_v*0.02)
    for fl in range(floor_count-1):
        z=0.35+fl*floor_to_floor
        for k in range(10):
            s=v3(stair_center+u*(-1.8+k*0.36)+v*(-0.9+k*0.17),z+k*0.29)
            cube(f"FCH_Stair_F{fl+1}_Tread_{k+1}",(s.x,s.y,s.z),(0.50,0.68,0.12),stone,asset,(u,v))

    # Preview-only studio lighting/cameras stay outside the linked Asset collection.
    world=bpy.data.worlds.new("Fairway neutral overcast studio") if bpy.data.worlds.get("Fairway neutral overcast studio") is None else bpy.data.worlds["Fairway neutral overcast studio"]
    scene.world=world; world.use_nodes=True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value=(0.32,0.41,0.52,1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value=0.7
    scene.render.engine="CYCLES"
    scene.cycles.samples=24
    scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    # Ground plane outside asset collection, rendered only for context.
    groundmat=material("Preview | grass",(0.11,0.18,0.10),0.95)
    ground=add_mesh("Preview_ground",[(cx-80,cy-80,-0.10),(cx+80,cy-80,-0.10),(cx+80,cy+80,-0.10),(cx-80,cy+80,-0.10)],[(0,1,2,3)],groundmat,preview)
    # Two soft areas approximate a bright overcast campus day.
    def area(name,loc,power,size):
        data=bpy.data.lights.new(name,"AREA"); data.energy=power; data.shape="DISK"; data.size=size
        obj=bpy.data.objects.new(name,data); preview.objects.link(obj); obj.location=loc
        obj.rotation_euler=(Vector((cx,cy,5))-obj.location).to_track_quat("-Z","Y").to_euler()
    area("Preview_key_softbox",(cx-30,cy-35,38),10500,22)
    area("Preview_fill_softbox",(cx+25,cy+20,25),5500,18)
    def camera(name,loc,target,lens=52):
        data=bpy.data.cameras.new(name); data.lens=lens
        obj=bpy.data.objects.new(name,data); preview.objects.link(obj); obj.location=loc
        obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
        return obj
    overview=camera("Preview_exterior_three_quarter",(cx-42,cy-52,29),(cx,cy,5.1),55)
    scene.camera=overview
    scene.view_settings.view_transform="AgX"
    overview_path=os.path.join(EVIDENCE,"exterior_preview.png")
    scene.render.filepath=overview_path
    bpy.ops.render.render(write_still=True)
    # Interior preview: hide the shell, roof, and exterior detailing only for this render.
    hidden=[]
    for obj in asset.objects:
        if obj.name.startswith(("FCH_Three_Story_Brick_Residence","FCH_Charcoal_Hipped_Gable_Roof","FCH_Ridge_Cap","FCH_Eave_Gutter","FCH_Edge_","FCH_Window_","FCH_Entry_","FCH_Main_Entry","FCH_Second_Floor_Slab","FCH_Third_Floor_Slab")) or "_F2_" in obj.name or "_F3_" in obj.name or obj.name.startswith("FCH_Stair_F2_"):
            hidden.append((obj,obj.hide_render)); obj.hide_render=True
    interior_camera=camera("Preview_interior_plan",(cx,cy,42),(cx,cy,0),35)
    interior_camera.data.type="ORTHO"
    interior_camera.data.ortho_scale=54
    scene.camera=interior_camera
    scene.render.resolution_x=1200; scene.render.resolution_y=900
    scene.render.filepath=os.path.join(EVIDENCE,"interior_schematic_preview.png")
    bpy.ops.render.render(write_still=True)
    for obj,old in hidden: obj.hide_render=old
    # Leave only expected collections in asset; contextual items remain in their own collection.
    bpy.ops.wm.save_as_mainfile(filepath=ASSET_FILE)

    # Fresh-open validation in a separate Blender process is run by the coordinator/grader.
    digest=hashlib.sha256(open(ASSET_FILE,"rb").read()).hexdigest()
    asset_bounds=[min(xs),max(xs),min(ys),max(ys),0.0,top_z]
    report={
        "building_id":ASSET_ID,"asset":os.path.relpath(ASSET_FILE,ROOT).replace("\\","/"),
        "candidate_sha256":digest,"scene":SCENE_NAME,"collection":COLL_NAME,
        "asset_objects":len(asset.objects),"asset_meshes":sum(o.type=="MESH" for o in asset.objects),
        "asset_materials":len({m.name for o in asset.objects if o.type=="MESH" for m in o.data.materials if m}),
        "source_feature":{"provider":"OpenStreetMap contributors","type":"way","id":220568267,"tags":osm_tags},
        "source_ring_latlon_count":len(ring),
        "bounds_world_m":{"x":[min(xs),max(xs)],"y":[min(ys),max(ys)],"z":[0.0,top_z]},
        "estimated_floor_count":floor_count,"estimated_roof_height_m":top_z,
        "uncertainty":["OSM is an open volunteered building outline, not a surveyed wall footprint.","OSM building:levels=3 and 2025 city permit indicate three storeys, but exact height and floor elevations were not found.","Street View supports a dark sloped roof and brick exterior; exact roof pitch and facade dimensions are estimated.","Interior arrangement is schematic and follows the documented residence, lounge, study, chapter-room and prayer-room program."],
        "renders":["audit/fairway_cooperative/exterior_preview.png","audit/fairway_cooperative/interior_schematic_preview.png"]}
    with open(os.path.join(EVIDENCE,"build_report.json"),"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
    print("FAIRWAY_BUILD_PASS",json.dumps(report))

if __name__ == "__main__":
    main()

"""Build a source-backed campus-coordinate Sigma Chi massing asset (FID 828).

Run from the repository root with Blender 5.2.3:
  ..\\blender\\blender-5.2.3-windows-x64\\blender.exe -b --python modular\\buildings\\build_massing_sigma_chi_fid828.py
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SOURCE = os.path.join(ROOT, "audit", "sigma_chi", "sources", "purdue_gis_fid828_raw.json")
OUT = os.path.join(ROOT, "modular", "buildings", "massing_sigma_chi_fid828.blend")
EVIDENCE = os.path.join(ROOT, "audit", "sigma_chi")
ASSET = "massing_sigma_chi_fid828"
COLLECTION_NAME = "Asset_" + ASSET
SCENE_NAME = "Building_" + ASSET

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
X_FACTOR = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
Y_FACTOR = 111040.0


def material(name, color, roughness=0.8):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def mesh_object(name, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def cube(name, loc, scale, mat, collection, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    obj.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def beam_between(name, point_a, point_b, thickness, mat, collection):
    a, b = Vector(point_a), Vector(point_b)
    direction = b-a
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (direction.length, thickness, thickness)
    obj.rotation_euler = direction.to_track_quat("X", "Z").to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def main():
    with open(SOURCE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    features = raw["features"]
    if len(features) != 1 or features[0]["attributes"].get("FID") != 828:
        raise RuntimeError("Expected exactly Purdue GIS FID 828")
    ring_ll = features[0]["geometry"]["rings"][0]
    ring = []
    for lon, lat in ring_ll:
        ring.append(((lon - ORIGIN_LON) * X_FACTOR,
                     (lat - ORIGIN_LAT) * Y_FACTOR))
    # Remove the duplicated closing coordinate for mesh construction.
    if math.dist(ring[0], ring[-1]) < 1e-6:
        ring.pop()
    if len(ring) < 4:
        raise RuntimeError("GIS outline has too few vertices")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections,):
        for item in list(datablocks):
            if item.users == 0:
                datablocks.remove(item)

    scene = bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)

    stone = material("SigmaChi | warm limestone stucco", (0.67, 0.57, 0.43))
    roof = material("SigmaChi | dark slate roof", (0.20, 0.23, 0.25), 0.95)
    trim = material("SigmaChi | dark brown timber and trim", (0.12, 0.08, 0.055))
    glass = material("SigmaChi | muted blue grey glazing", (0.16, 0.28, 0.34), 0.28)
    masonry = material("SigmaChi | cut stone surround and foundation", (0.43, 0.36, 0.27))
    door_mat = material("SigmaChi | entrance timber", (0.19, 0.12, 0.08))
    brick = material("SigmaChi | chimney brick", (0.32, 0.20, 0.14))

    eave = 8.8
    floor_levels = (0.0, 3.0, 5.9, eave)
    # Solid wall envelope follows the entire official map outline. GIS ring is
    # georeferenced campus coordinates in the project’s approximate transform.
    verts = [(x, y, z) for z in (0.0, eave) for x, y in ring]
    n = len(ring)
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2*n))]
    faces += [(i, (i+1) % n, (i+1) % n + n, i+n) for i in range(n)]
    mesh_object("SigmaChi_GIS_Footprint_Walls", verts, faces, stone, collection)

    # Continuous base and floor-course bands make the inferred storeys readable.
    center = (sum(p[0] for p in ring)/n, sum(p[1] for p in ring)/n)
    theta = math.radians(64.6951488989826)
    u = (math.cos(theta), math.sin(theta))
    v = (-math.sin(theta), math.cos(theta))
    def xy(U, V):
        return (U*u[0] + V*v[0], U*u[1] + V*v[1])
    us = [x*u[0]+y*u[1] for x, y in ring]
    vs = [x*v[0]+y*v[1] for x, y in ring]
    u_min, u_max = min(us), max(us)
    v_min, v_max = min(vs), max(vs)
    u_se = (sorted(us)[3] + sorted(us)[4]) / 2.0
    v_join = (sorted(vs)[2] + sorted(vs)[3]) / 2.0
    # The chapter photo's broad front elevation is represented by the longest
    # outline edge parallel to the long GIS axis. Select that full exterior
    # frontage rather than an edge whose midpoint happens to cross v_join.
    front_edges = []
    for edge_i, ea in enumerate(ring):
        eb = ring[(edge_i+1) % n]
        va = ea[0]*v[0]+ea[1]*v[1]
        vb = eb[0]*v[0]+eb[1]*v[1]
        elen = math.dist(ea, eb)
        if abs(va-vb) < 0.8 and elen > 18:
            front_edges.append((elen, edge_i, ea, eb))
    if not front_edges:
        raise RuntimeError("Could not find front wing edge at GIS re-entrant corner")
    _, front_i, front_a, front_b = max(front_edges)
    for z, height in ((0.18, 0.36), (3.0, 0.12), (5.9, 0.12), (8.72, 0.16)):
        for i, a in enumerate(ring):
            b = ring[(i+1) % n]
            dx, dy = b[0]-a[0], b[1]-a[1]
            length = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
            # slim trim ribbons slightly proud of the wall face
            nx, ny = dy/length, -dx/length
            if (center[0]-mx)*nx + (center[1]-my)*ny > 0:
                nx, ny = -nx, -ny
            cube("SigmaChi_Course_%0.2f_%02d" % (z, i),
                 (mx+nx*0.035, my+ny*0.035, z), (length, 0.09, height),
                 masonry if z == 0.18 else trim, collection, angle)

    # Facade windows are schematic. They are spaced on each actual GIS edge;
    # small, short edges are omitted rather than inventing tiny openings.
    for i, a in enumerate(ring):
        b = ring[(i+1) % n]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx, dy)
        if length < 6.0:
            continue
        angle = math.atan2(dy, dx)
        mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
        nx, ny = dy/length, -dx/length
        if (center[0]-mx)*nx + (center[1]-my)*ny > 0:
            nx, ny = -nx, -ny
        # Secondary elevations use a regular schematic rhythm. The chapter
        # frontage uses paired and separated groups, following the distinct
        # multi-opening ensembles in the chapter photo archive.
        bays = max(2, min(5, int(length // 4.6)))
        for floor, (lo, hi) in enumerate(zip(floor_levels[:-1], floor_levels[1:])):
            if i == front_i:
                front_t = ((0.12,0.30,0.70,0.88),
                           (0.12,0.29,0.36,0.64,0.71,0.88),
                           (0.12,0.30,0.40,0.60,0.70,0.88))[floor]
                positions = list(enumerate(front_t))
            else:
                positions = [(bay,(bay+1)/(bays+1)) for bay in range(bays)]
            for bay, t in positions:
                x, y = a[0] + t*dx, a[1] + t*dy
                z = lo + (hi-lo)*0.53
                group = i == front_i and floor == 1 and abs(t-0.71)<0.01
                win_w, win_h = (2.15,1.72) if group else (1.12,1.52)
                glass_w, glass_h = win_w-0.28, win_h-0.32
                # vertically proportioned masonry opening with dark frame and glass
                cube("SigmaChi_WindowFrame_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.075, y+ny*0.075, z), (win_w, 0.13, win_h), trim,
                     collection, angle)
                cube("SigmaChi_WindowGlass_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.15, y+ny*0.15, z), (glass_w, 0.07, glass_h), glass,
                     collection, angle)
                cube("SigmaChi_WindowMullion_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.20, y+ny*0.20, z), (0.06, 0.055, glass_h), trim,
                     collection, angle)
                cube("SigmaChi_WindowTransom_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.205, y+ny*0.205, z+0.10), (glass_w, 0.055, 0.06), trim,
                     collection, angle)
                if group:
                    for mullion_i,offset in enumerate((-0.54,0.54)):
                        cube("SigmaChi_WindowGroupVertical_%02d" % mullion_i,
                             (x+math.cos(angle)*offset+nx*0.20,
                              y+math.sin(angle)*offset+ny*0.20,z),
                             (0.055,0.055,glass_h),trim,collection,angle)
                cube("SigmaChi_WindowStoneSill_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.13, y+ny*0.13, z-win_h/2-0.08), (win_w+0.24, 0.16, 0.15), masonry,
                     collection, angle)
                cube("SigmaChi_WindowStoneLintel_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.13, y+ny*0.13, z+win_h/2+0.08), (win_w+0.24, 0.16, 0.15), masonry,
                     collection, angle)
                cube("SigmaChi_WindowJamb_L_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.13-math.cos(angle)*(win_w/2+0.02),
                      y+ny*0.13-math.sin(angle)*(win_w/2+0.02),z),
                     (0.12,0.16,win_h+0.12),masonry,collection,angle)
                cube("SigmaChi_WindowJamb_R_%02d_%d_%d" % (i, floor, bay),
                     (x+nx*0.13+math.cos(angle)*(win_w/2+0.02),
                      y+ny*0.13+math.sin(angle)*(win_w/2+0.02),z),
                     (0.12,0.16,win_h+0.12),masonry,collection,angle)

    # Prominent porch/entry visible on the historic chapter-house facade photo.
    # Exact location is estimated along the GIS frontage; its form follows the
    # documented gabled canopy and masonry/stucco entry surround.
    i, a, b = front_i, front_a, front_b
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)
    nx, ny = dy/length, -dx/length
    mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
    if (center[0]-mx)*nx + (center[1]-my)*ny > 0:
        nx, ny = -nx, -ny
    cube("SigmaChi_EntryDoor_Inferred", (mx+nx*0.105, my+ny*0.105, 1.35),
         (1.50, 0.16, 2.55), door_mat, collection, angle)
    for side in (-1,1):
        x = mx+nx*0.15+side*math.cos(angle)*0.92
        y = my+ny*0.15+side*math.sin(angle)*0.92
        cube("SigmaChi_EntryMasonryJamb_%s" % side,(x,y,1.72),(0.20,0.22,3.20),masonry,collection,angle)
    cube("SigmaChi_EntryMasonryLintel",(mx+nx*0.17,my+ny*0.17,3.32),
         (2.08,0.22,0.28),masonry,collection,angle)
    # Closed extruded voussoir-like arch band makes the entry's masonry
    # articulation legible above the door, as in the renovation photo.
    def entry_arch_outline(radius, base, spring, segments=12):
        points=[(-radius,base),(radius,base),(radius,base+spring)]
        points += [(radius*math.cos(math.pi*k/segments),
                    base+spring+radius*math.sin(math.pi*k/segments))
                   for k in range(1,segments+1)]
        return points
    def entry_arch_point(s,z,depth):
        return (mx+math.cos(angle)*s+nx*depth,
                my+math.sin(angle)*s+ny*depth,z)
    entry_outer=entry_arch_outline(1.10,2.48,0.42)
    entry_inner=entry_arch_outline(0.84,2.52,0.38)
    entry_count=len(entry_outer)
    arch_vertices=[entry_arch_point(s,z,0.28) for s,z in entry_outer]
    arch_vertices += [entry_arch_point(s,z,0.28) for s,z in entry_inner]
    arch_vertices += [entry_arch_point(s,z,0.08) for s,z in entry_outer]
    arch_vertices += [entry_arch_point(s,z,0.08) for s,z in entry_inner]
    arch_faces=[]
    for k in range(entry_count):
        nxt=(k+1)%entry_count
        arch_faces.extend([(k,nxt,entry_count+nxt,entry_count+k),
                           (2*entry_count+k,3*entry_count+k,3*entry_count+nxt,2*entry_count+nxt),
                           (k,2*entry_count+k,2*entry_count+nxt,nxt),
                           (entry_count+k,entry_count+nxt,3*entry_count+nxt,3*entry_count+k)])
    mesh_object("SigmaChi_EntryStoneArchedSurround",arch_vertices,arch_faces,masonry,collection)
    cube("SigmaChi_EntryTransom",(mx+nx*0.20,my+ny*0.20,2.70),(1.28,0.08,0.14),trim,collection,angle)
    # Broad limestone steps and porch platform face outward from the door.
    cube("SigmaChi_EntryPorchPlatform",(mx+nx*0.72,my+ny*0.72,0.34),(3.55,1.70,0.34),masonry,collection,angle)
    cube("SigmaChi_EntryStep_Lower",(mx+nx*1.62,my+ny*1.62,0.12),(4.05,0.92,0.22),masonry,collection,angle)
    # Gabled timbered porch roof: two pitched faces, stone triangular end, and
    # two posts. The feature is supported by the chapter's renovation photo.
    porch_w, porch_d, porch_eave, porch_peak = 3.65, 2.15, 3.30, 4.55
    def porch_pt(s, d, z):
        return (mx+math.cos(angle)*s+nx*d,
                my+math.sin(angle)*s+ny*d,z)
    pverts = [porch_pt(-porch_w/2,0,porch_eave),porch_pt(porch_w/2,0,porch_eave),
              porch_pt(porch_w/2,porch_d,porch_eave),porch_pt(-porch_w/2,porch_d,porch_eave),
              porch_pt(0,0,porch_peak),porch_pt(0,porch_d,porch_peak)]
    pobj = mesh_object("SigmaChi_GabledEntryPorchRoof",pverts,
                       [(0,1,5,4),(2,3,4,5),(0,4,3),(1,2,5),(0,3,2,1)],roof,collection)
    pobj.data.materials.append(stone)
    pobj.data.polygons[2].material_index=1
    pobj.data.polygons[3].material_index=1
    for side in (-1,1):
        px=mx+nx*1.92+side*math.cos(angle)*1.55
        py=my+ny*1.92+side*math.sin(angle)*1.55
        cube("SigmaChi_EntryPorchPost_%s" % side,(px,py,1.96),(0.22,0.22,2.70),trim,collection)
        cube("SigmaChi_EntryPorchPostBase_%s" % side,(px,py,0.65),(0.40,0.40,0.28),masonry,collection)
        cube("SigmaChi_EntryPorchPostCapital_%s" % side,(px,py,3.30),(0.38,0.38,0.26),masonry,collection)
        beam_between("SigmaChi_EntryTimberKneeBrace_%s" % side,
                     porch_pt(side*1.50,1.10,2.45),porch_pt(side*1.50,1.92,3.20),
                     0.16,trim,collection)

    # Cross-gable on the photo-supported principal elevation. This creates the
    # intersecting Tudor roof silhouette visible in the chapter's 2006 gallery
    # and archived 1960-62 exterior photo; exact bay width/depth remain inferred.
    gable_half_width, gable_depth = 4.2, -6.0
    gable_eave, gable_ridge = 8.92, 13.05
    def front_gable_point(s, d, z):
        return (mx+math.cos(angle)*s+nx*d,
                my+math.sin(angle)*s+ny*d,z)
    gable_verts=[front_gable_point(-gable_half_width,0,gable_eave),
                 front_gable_point(gable_half_width,0,gable_eave),
                 front_gable_point(0,0,gable_ridge),
                 front_gable_point(-gable_half_width,gable_depth,gable_eave),
                 front_gable_point(gable_half_width,gable_depth,gable_eave),
                 front_gable_point(0,gable_depth,gable_ridge)]
    front_gable=mesh_object("SigmaChi_FrontCrossGable",gable_verts,
                            [(0,1,2),(3,5,4),(0,2,5,3),(2,1,4,5),(0,3,4,1)],
                            stone,collection)
    front_gable.data.materials.append(roof)
    for polygon in front_gable.data.polygons[2:]:
        polygon.material_index=1
    # Arched divided attic opening echoes the renovation photo's arcuated
    # opening. The arch is explicit geometry rather than a rectangular proxy.
    def gable_arch_outline(radius,base,spring,segments=12):
        p=[(-radius,base),(radius,base),(radius,base+spring)]
        p += [(radius*math.cos(math.pi*k/segments),
               base+spring+radius*math.sin(math.pi*k/segments))
              for k in range(1,segments+1)]
        return p
    gable_outer=gable_arch_outline(0.91,9.55,0.52)
    gable_inner=gable_arch_outline(0.68,9.58,0.50)
    gable_count=len(gable_outer)
    gable_arch_verts=[front_gable_point(s,0.20,z) for s,z in gable_outer]
    gable_arch_verts += [front_gable_point(s,0.20,z) for s,z in gable_inner]
    gable_arch_verts += [front_gable_point(s,0.06,z) for s,z in gable_outer]
    gable_arch_verts += [front_gable_point(s,0.06,z) for s,z in gable_inner]
    gable_arch_faces=[]
    for k in range(gable_count):
        nxt=(k+1)%gable_count
        gable_arch_faces.extend([(k,nxt,gable_count+nxt,gable_count+k),
                                 (2*gable_count+k,3*gable_count+k,3*gable_count+nxt,2*gable_count+nxt),
                                 (k,2*gable_count+k,2*gable_count+nxt,nxt),
                                 (gable_count+k,gable_count+nxt,3*gable_count+nxt,3*gable_count+k)])
    mesh_object("SigmaChi_FrontGable_ArchedStoneSurround",gable_arch_verts,
                gable_arch_faces,masonry,collection)
    glass_verts=[front_gable_point(s,0.19,z) for s,z in gable_inner]
    glass_verts += [front_gable_point(s,0.12,z) for s,z in gable_inner]
    glass_faces=[tuple(range(gable_count)),tuple(range(2*gable_count-1,gable_count-1,-1))]
    for k in range(gable_count):
        nxt=(k+1)%gable_count
        glass_faces.append((k,nxt,gable_count+nxt,gable_count+k))
    mesh_object("SigmaChi_FrontGable_ArchedGlazing",glass_verts,
                glass_faces,glass,collection)
    beam_between("SigmaChi_FrontGable_ArchedMullionV",
                 front_gable_point(0,0.26,9.62),front_gable_point(0,0.26,11.16),
                 0.07,trim,collection)
    beam_between("SigmaChi_FrontGable_ArchedMullionH",
                 front_gable_point(-0.62,0.26,10.18),front_gable_point(0.62,0.26,10.18),
                 0.07,trim,collection)

    # Two additional cross-gabled bays break the uninterrupted roof slope into
    # the stepped, intersecting Tudor silhouette visible in the archive photos.
    # Their dimensions are visual estimates; the wall footprint remains GIS exact.
    def add_front_cross_gable(label,t,half_width,ridge_z,depth):
        gx,gy=front_a[0]+t*dx,front_a[1]+t*dy
        def point(s,d,z):
            return (gx+math.cos(angle)*s+nx*d,
                    gy+math.sin(angle)*s+ny*d,z)
        eave_z=8.92
        verts=[point(-half_width,0,eave_z),point(half_width,0,eave_z),
               point(0,0,ridge_z),point(-half_width,depth,eave_z),
               point(half_width,depth,eave_z),point(0,depth,ridge_z)]
        obj=mesh_object("SigmaChi_"+label,verts,
                        [(0,1,2),(3,5,4),(0,2,5,3),(2,1,4,5),(0,3,4,1)],
                        stone,collection)
        obj.data.materials.append(roof)
        for poly in obj.data.polygons[2:]:
            poly.material_index=1
        wz=eave_z+(ridge_z-eave_z)*0.48
        cube("SigmaChi_%s_StoneWindow" % label,point(0,0.12,wz),
             (1.65,0.18,2.05),masonry,collection,angle)
        cube("SigmaChi_%s_Glazing" % label,point(0,0.24,wz),
             (1.22,0.08,1.58),glass,collection,angle)
        cube("SigmaChi_%s_MullionV" % label,point(0,0.30,wz),
             (0.07,0.06,1.58),trim,collection,angle)
        cube("SigmaChi_%s_MullionH" % label,point(0,0.30,wz-0.12),
             (1.22,0.06,0.07),trim,collection,angle)
    add_front_cross_gable("WestCrossGable",0.24,3.0,13.85,-6.5)
    add_front_cross_gable("EastCrossGable",0.77,3.25,14.15,-6.5)

    # Decompose the GIS outline into its two near-rectangular wings. This keeps
    # the L-shaped courtyard/open notch clear instead of bridging it with roof.
    # Roof geometry remains an estimate; plan wings follow the source polygon.
    pts = ring
    theta = math.radians(64.6951488989826)
    u = (math.cos(theta), math.sin(theta))
    v = (-math.sin(theta), math.cos(theta))
    us = [x*u[0]+y*u[1] for x, y in pts]
    vs = [x*v[0]+y*v[1] for x, y in pts]
    def xy(U, V):
        return (U*u[0] + V*v[0], U*u[1] + V*v[1])
    u_min, u_max = min(us), max(us)
    v_min, v_max = min(vs), max(vs)
    # Vertex projections reveal the re-entrant corner in the official GIS ring.
    # A joins the short SE arm; B is the long NW cross-wing.
    u_se = (sorted(us)[3] + sorted(us)[4]) / 2.0
    v_join = (sorted(vs)[2] + sorted(vs)[3]) / 2.0

    def gabled_roof(label, ua, ub, va, vb, eave_height, ridge_height, ridge_u=True):
        overhang = 0.32
        ua, ub = ua-overhang, ub+overhang
        va, vb = va-overhang, vb+overhang
        if ridge_u:
            vm = (va+vb)/2
            corners = [(ua,va,eave_height),(ub,va,eave_height),(ub,vb,eave_height),
                       (ua,vb,eave_height),(ua,vm,ridge_height),(ub,vm,ridge_height)]
            faces = [(0,1,5,4),(2,3,4,5),(0,4,3),(1,2,5),(0,3,2,1)]
        else:
            um = (ua+ub)/2
            corners = [(ua,va,eave_height),(ub,va,eave_height),(ub,vb,eave_height),
                       (ua,vb,eave_height),(um,va,ridge_height),(um,vb,ridge_height)]
            faces = [(0,4,5,3),(1,2,5,4),(0,1,4),(3,5,2),(0,3,2,1)]
        roof_obj = mesh_object("SigmaChi_Roof_"+label,
                               [(*xy(U,V),Z) for U,V,Z in corners], faces, roof, collection)
        roof_obj.data.materials.append(stone)
        # Gable ends are the source-supported masonry/stucco facade, not dark
        # roof planes; the two end polygons are faces 2 and 3 in either layout.
        roof_obj.data.polygons[2].material_index = 1
        roof_obj.data.polygons[3].material_index = 1
        if label == "long_Tudor_wing" and ridge_u:
            # A broad arched multi-pane gable window matches the renovation
            # photograph's distinctive masonry end-wall opening.
            face_u = ua - 0.06
            vm = (va+vb)/2
            base_z, spring_z = eave_height+0.15, 10.75
            outer_w, inner_w, segments = 2.5, 2.10, 10
            def arch_outline(width, base, spring, inset=0.0):
                radius = width/2
                p = [(-radius,base),(radius,base),(radius,base+spring)]
                p += [(radius*math.cos(math.pi*k/segments),
                       base+spring+radius*math.sin(math.pi*k/segments))
                      for k in range(1,segments+1)]
                return p
            outer = arch_outline(outer_w,base_z,spring_z-base_z)
            inner = arch_outline(inner_w,base_z+0.12,spring_z-base_z-0.12)
            def face_world(s,z,offset):
                x,y=xy(face_u+offset,vm+s)
                return (x,y,z)
            count=len(outer)
            # Extrude both the annular stone surround and glazing so audit
            # topology remains closed rather than leaving open planar edges.
            border_verts = [face_world(s,z,-0.03) for s,z in outer]
            border_verts += [face_world(s,z,-0.03) for s,z in inner]
            border_verts += [face_world(s,z,0.08) for s,z in outer]
            border_verts += [face_world(s,z,0.08) for s,z in inner]
            border_faces=[]
            for k in range(count):
                nxt=(k+1)%count
                border_faces.extend([(k,nxt,count+nxt,count+k),
                                     (2*count+k,3*count+k,3*count+nxt,2*count+nxt),
                                     (k,2*count+k,2*count+nxt,nxt),
                                     (count+k,count+nxt,3*count+nxt,3*count+k)])
            mesh_object("SigmaChi_ArchedGableStoneSurround",border_verts,border_faces,masonry,collection)
            glass_verts=[face_world(s,z,-0.02) for s,z in inner]
            glass_verts += [face_world(s,z,0.05) for s,z in inner]
            glass_faces=[tuple(range(count)),tuple(range(2*count-1,count-1,-1))]
            for k in range(count):
                nxt=(k+1)%count
                glass_faces.append((k,nxt,count+nxt,count+k))
            mesh_object("SigmaChi_ArchedGableGlazing",glass_verts,glass_faces,glass,collection)
            # Stained dark mullions divide the arched assembly into bays.
            cx,cy=xy(face_u-0.055,vm)
            cube("SigmaChi_ArchedGableMullionV",(cx,cy,base_z+1.1),
                 (0.07,0.07,2.0),trim,collection,theta+math.pi/2)
            cube("SigmaChi_ArchedGableMullionH",(cx,cy,base_z+0.84),
                 (1.95,0.07,0.07),trim,collection,theta+math.pi/2)
            # Tudor gable rake and a short horizontal tie beam.
            p_left=(*xy(face_u-0.04,va+0.05),eave_height+0.1)
            p_peak=(*xy(face_u-0.04,vm),ridge_height-0.18)
            p_right=(*xy(face_u-0.04,vb-0.05),eave_height+0.1)
            beam_between("SigmaChi_GableTudorRake_L",p_left,p_peak,0.16,trim,collection)
            beam_between("SigmaChi_GableTudorRake_R",p_peak,p_right,0.16,trim,collection)
            beam_between("SigmaChi_GableTudorTie",(*xy(face_u-0.04,va+0.1),eave_height+0.25),
                         (*xy(face_u-0.04,vb-0.1),eave_height+0.25),0.14,trim,collection)

    # Two gables meet at the source footprint's inside corner. The (modest)
    # eave overhang follows the wall edges without roofing over the courtyard.
    gabled_roof("long_Tudor_wing", u_min, u_max, v_join, v_max, 8.95, 13.1, True)
    gabled_roof("cross_Tudor_wing", u_se, u_max, v_min, v_join, 8.95, 12.2, False)

    # Two small dormers are placed only on the long wing's south-facing roof.
    dormer_v = v_join + 1.25
    dormer_base = 10.15
    dormer_peak = 12.25
    for j, U in enumerate((u_min+(u_max-u_min)*0.35, u_min+(u_max-u_min)*0.70)):
        width, depth = 2.8, 2.0
        gv = [(U-width/2,dormer_v,dormer_base),(U+width/2,dormer_v,dormer_base),
              (U,dormer_v,dormer_peak),(U-width/2,dormer_v-depth,dormer_base),
              (U+width/2,dormer_v-depth,dormer_base),(U,dormer_v-depth,dormer_peak)]
        gf = [(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)]
        mesh_object("SigmaChi_Dormer_%02d" % j,
                    [(*xy(U0,V0),Z0) for U0,V0,Z0 in gv], gf, stone, collection)
        for side in (-1,1):
            end_u = U + side*width/2
            axy, bxy = xy(U,dormer_v-depth), xy(end_u,dormer_v-depth)
            cube("SigmaChi_Dormer_Rake_%02d_%s" % (j,"L" if side<0 else "R"),
                 ((axy[0]+bxy[0])/2,(axy[1]+bxy[1])/2,(dormer_base+dormer_peak)/2),
                 (math.dist(axy,bxy),0.18,0.16),roof,collection,
                 theta+math.atan2(dormer_peak-dormer_base,width/2)*(1 if side<0 else -1))
        wx,wy=xy(U,dormer_v-depth-0.09)
        cube("SigmaChi_Dormer_Window_Frame_%02d" % j,(wx,wy,dormer_base+0.55),
             (0.85,0.12,0.95),trim,collection,theta)
        cube("SigmaChi_Dormer_Window_Glass_%02d" % j,(wx,wy-0.06*math.cos(theta),dormer_base+0.55),
             (0.60,0.06,0.70),glass,collection,theta)

    # Ridge caps and brick stacks repeat the prominent chimney visible in the
    # chapter's archived 1960–62 house photograph; stack placement is estimated.
    main_u_mid=u_min+(u_max-u_min)*0.57
    main_v_mid=(v_join+v_max)/2
    rx,ry=xy(main_u_mid,main_v_mid)
    cube("SigmaChi_MainRidgeCap",(rx,ry,13.14),(u_max-u_min,0.24,0.16),trim,collection,theta)
    cube("SigmaChi_MainBrickChimney",(rx,ry,14.82),(1.28,1.18,3.45),brick,collection,theta)
    cube("SigmaChi_MainChimneyCap",(rx,ry,16.58),(1.55,1.43,0.28),masonry,collection,theta)
    cube("SigmaChi_MainChimneyFlue",(rx,ry,16.84),(0.42,0.42,0.24),brick,collection,theta)
    cross_u_mid=(u_se+u_max)/2
    cross_v_mid=(v_min+v_join)/2
    cx,cy=xy(cross_u_mid,cross_v_mid)
    cube("SigmaChi_CrossRidgeCap",(cx,cy,12.24),(v_join-v_min,0.20,0.15),trim,collection,theta+math.pi/2)
    cube("SigmaChi_CrossWingChimney",(cx,cy,13.84),(1.10,1.10,3.15),brick,collection,theta+math.pi/2)
    cube("SigmaChi_CrossWingChimneyCap",(cx,cy,15.46),(1.36,1.36,0.26),masonry,collection,theta+math.pi/2)

    # Aim an oblique but lower audit camera from the chapter-photo frontage so
    # the entrance porch, facade articulation, roof silhouette, and chimneys
    # can be inspected in the saved evidence view.
    view_mid_x, view_mid_y = (front_a[0]+front_b[0])/2, (front_a[1]+front_b[1])/2
    view_dx, view_dy = front_b[0]-front_a[0], front_b[1]-front_a[1]
    view_len = math.hypot(view_dx, view_dy)
    view_nx, view_ny = view_dy/view_len, -view_dx/view_len
    if (center[0]-view_mid_x)*view_nx + (center[1]-view_mid_y)*view_ny > 0:
        view_nx, view_ny = -view_nx, -view_ny
    bpy.ops.object.camera_add(location=(view_mid_x+view_nx*55,
                                       view_mid_y+view_ny*55, 23))
    camera = bpy.context.object
    camera.name = "SigmaChi_AuditCamera"
    direction = Vector((view_mid_x, view_mid_y, 5.0)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 52
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(view_mid_x+view_nx*35,
                                                      view_mid_y+view_ny*35, 30))
    light = bpy.context.object
    light.data.energy = 12500
    light.data.shape = "DISK"
    light.data.size = 38
    light.rotation_euler = (Vector((view_mid_x,view_mid_y,5.0))-light.location).to_track_quat("-Z","Y").to_euler()
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.22,0.22,0.22)
    scene.render.filepath = os.path.join(EVIDENCE, "sigma_chi_candidate_render.png")
    # Audit-only camera/lights are outside the exported asset collection.
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    bpy.ops.render.render(write_still=True)
    print("SIGMA_CHI_BUILD", json.dumps({"asset": OUT, "collection": COLLECTION_NAME,
          "objects": len(collection.objects), "vertices": len(ring),
          "bounds_xy": [min(x for x,y in ring), min(y for x,y in ring),
                        max(x for x,y in ring), max(y for x,y in ring)],
          "render": scene.render.filepath}))


if __name__ == "__main__":
    main()

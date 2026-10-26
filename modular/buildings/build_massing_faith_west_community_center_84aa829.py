"""Build the modular Faith West Community Center library from the OSM outline and references.

Run with Blender 5.2 in background from the repository root. This asset stays in campus
coordinates because its manifest kind is `massing`; the master supplies identity placement.
"""
import bpy
import json
import math
import urllib.request
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "faith_west_community_center"
ASSET = ROOT / "modular" / "buildings" / "massing_faith_west_community_center_84aa829.blend"
ID = "massing_faith_west_community_center_84aa829"
SCENE_NAME = "Building_" + ID
COLLECTION_NAME = "Asset_" + ID
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137


def xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def ensure_research():
    fp = EVIDENCE / "osm_buildings_near_faith_west.json"
    if not fp.exists():
        raise FileNotFoundError(fp)
    data = json.loads(fp.read_text(encoding="utf-8"))
    match = [e for e in data.get("elements", []) if e.get("tags", {}).get("name") == "Faith West Community Center"]
    if len(match) != 1 or not match[0].get("geometry"):
        raise RuntimeError("The expected named OSM footprint way was not uniquely found")
    outline = [xy(p["lon"], p["lat"]) for p in match[0]["geometry"]]
    return outline, match[0]


def clip(poly, axis, value, keep_greater):
    """Clip one simple ring to an axis-aligned half plane."""
    if not poly:
        return []
    out = []
    def inside(p):
        return p[axis] >= value if keep_greater else p[axis] <= value
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        ia, ib = inside(a), inside(b)
        if ia:
            out.append(a)
        if ia != ib:
            den = b[axis] - a[axis]
            t = (value - a[axis]) / den if abs(den) > 1e-12 else 0.0
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    # Drop consecutive duplicates introduced by a vertex on the clipping line.
    cleaned = []
    for p in out:
        if not cleaned or math.dist(p, cleaned[-1]) > 1e-6:
            cleaned.append(p)
    if len(cleaned) > 2 and math.dist(cleaned[0], cleaned[-1]) <= 1e-6:
        cleaned.pop()
    return cleaned if len(cleaned) >= 3 else []


def clip_rect(poly, xmin, xmax, ymin, ymax):
    for axis, value, greater in ((0, xmin, True), (0, xmax, False), (1, ymin, True), (1, ymax, False)):
        poly = clip(poly, axis, value, greater)
        if not poly:
            break
    return poly


def polygon_area(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))) * 0.5


def material(name, color, roughness=0.75, metallic=0.0, texture=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    if texture == "brick":
        tex = nt.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Color1"].default_value = (0.38, 0.09, 0.055, 1)
        tex.inputs["Color2"].default_value = (0.25, 0.055, 0.04, 1)
        tex.inputs["Mortar"].default_value = (0.24, 0.22, 0.19, 1)
        tex.inputs["Scale"].default_value = 2.2
        tex.inputs["Mortar Size"].default_value = 0.025
        tex.inputs["Brick Width"].default_value = 0.5
        tex.inputs["Row Height"].default_value = 0.25
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = (1.0, 1.0, 1.0)
        nt.links.new(coord.outputs["Generated"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 95.0
        noise.inputs["Detail"].default_value = 2.0
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.16
        bump.inputs["Distance"].default_value = 0.018
        nt.links.new(coord.outputs["Generated"], noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    elif texture == "siding":
        coord = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 28.0
        noise.inputs["Detail"].default_value = 2.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.2
        ramp.color_ramp.elements[0].color = (*tuple(c * 0.88 for c in color), 1)
        ramp.color_ramp.elements[1].position = 0.8
        ramp.color_ramp.elements[1].color = (*tuple(min(1, c * 1.05) for c in color), 1)
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.08
        bump.inputs["Distance"].default_value = 0.006
        nt.links.new(coord.outputs["Generated"], noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    elif texture == "shingle":
        coord = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 65.0
        noise.inputs["Detail"].default_value = 2.5
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.018, 0.022, 0.028, 1)
        ramp.color_ramp.elements[1].color = (0.105, 0.12, 0.14, 1)
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.18
        bump.inputs["Distance"].default_value = 0.01
        nt.links.new(coord.outputs["Generated"], noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def object_mesh(name, verts, faces, mat, parent_collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    parent_collection.objects.link(obj)
    return obj


def extrude_ring(name, poly, z0, z1, mat, parent_collection, close_top=True, side_walls=True):
    n = len(poly)
    verts = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    faces = []
    if side_walls and polygon_area(poly) > 0:
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, j, n + j, n + i))
    elif side_walls:
        for i in range(n):
            j = (i + 1) % n
            faces.append((j, i, n + i, n + j))
    if close_top:
        faces += [tuple(range(n, n * 2))]
    return object_mesh(name, verts, faces, mat, parent_collection)


def batch_mesh(name, mat, parent_collection):
    return {"name": name, "mat": mat, "collection": parent_collection, "verts": [], "faces": []}


def add_box(b, center, tangent, normal, width, depth, height, zcenter):
    c = Vector((center[0], center[1], zcenter))
    t = Vector((tangent[0], tangent[1], 0)).normalized() * width * 0.5
    n = Vector((normal[0], normal[1], 0)).normalized() * depth * 0.5
    z = Vector((0, 0, height * 0.5))
    base = len(b["verts"])
    b["verts"] += [tuple(c - t - n - z), tuple(c + t - n - z), tuple(c + t + n - z), tuple(c - t + n - z), tuple(c - t - n + z), tuple(c + t - n + z), tuple(c + t + n + z), tuple(c - t + n + z)]
    b["faces"] += [tuple(base + i for i in f) for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0))]


def add_quad(b, points):
    k = len(b["verts"])
    b["verts"].extend(points)
    b["faces"].append((k, k + 1, k + 2, k + 3))


def build_facade(poly, levels, wall_batches, frame_batch, glass_batch, trim_batch, balcony_batch, is_upper=False):
    # OSM footprint has a clockwise ring. Pick outward normals from its signed area.
    ccw = polygon_area(poly) > 0
    for i, a in enumerate(poly):
        bpt = poly[(i + 1) % len(poly)]
        dx, dy = bpt[0] - a[0], bpt[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 0.2:
            continue
        tangent = (dx / length, dy / length)
        normal = (tangent[1], -tangent[0]) if ccw else (-tangent[1], tangent[0])
        for level_index, (zbase, floor_height) in enumerate(levels):
            wc, wh = (1.38, 1.52) if is_upper else (1.65, 1.75)
            has_windows=length >= (3.3 if is_upper else 4.2)
            nwin=max(1,int(length//(3.3 if is_upper else 3.0))) if has_windows else 0
            step=length/(nwin+1) if nwin else length
            if step < 2.0:
                wc=max(0.85,step*0.58)
            wall=wall_batches[level_index]
            offset=Vector((normal[0]*0.025,normal[1]*0.025,0))
            def wall_quad(s0,s1,h0,h1):
                p0=Vector((a[0]+tangent[0]*s0,a[1]+tangent[1]*s0,0))+offset
                p1=Vector((a[0]+tangent[0]*s1,a[1]+tangent[1]*s1,0))+offset
                add_quad(wall,[(p0.x,p0.y,zbase+h0),(p1.x,p1.y,zbase+h0),(p1.x,p1.y,zbase+h1),(p0.x,p0.y,zbase+h1)])
            if not nwin:
                wall_quad(0,length,0,floor_height)
                continue
            intervals=[]
            for k in range(1,nwin+1):
                along=step*k
                actual_w=min(wc,step*0.70)
                intervals.append((along-actual_w/2,along+actual_w/2,actual_w))
            cursor=0.0
            for left,right,actual_w in intervals:
                if left>cursor: wall_quad(cursor,left,0,floor_height)
                sill_h=min(0.95,floor_height-wh-0.08)
                wall_quad(left,right,0,sill_h)
                wall_quad(left,right,sill_h+wh,floor_height)
                cursor=right
            if cursor<length: wall_quad(cursor,length,0,floor_height)
            for interval_i,(left,right,actual_w) in enumerate(intervals):
                along=(left+right)*0.5
                wc=actual_w
                cx, cy = a[0] + tangent[0] * along, a[1] + tangent[1] * along
                sill = zbase + min(0.95,floor_height-wh-0.08)
                center_z = sill + wh * 0.5
                # Glazing and frame are slightly proud of the wall to read at campus scale.
                add_quad(glass_batch, [(cx - tangent[0]*wc/2 + normal[0]*0.035, cy - tangent[1]*wc/2 + normal[1]*0.035, sill),
                                       (cx + tangent[0]*wc/2 + normal[0]*0.035, cy + tangent[1]*wc/2 + normal[1]*0.035, sill),
                                       (cx + tangent[0]*wc/2 + normal[0]*0.035, cy + tangent[1]*wc/2 + normal[1]*0.035, sill + wh),
                                       (cx - tangent[0]*wc/2 + normal[0]*0.035, cy - tangent[1]*wc/2 + normal[1]*0.035, sill + wh)])
                # Frame rails and jambs; they are one merged mesh by material.
                add_box(frame_batch, (cx, cy), tangent, normal, wc + 0.16, 0.12, 0.085, sill - 0.02)
                add_box(frame_batch, (cx, cy), tangent, normal, wc + 0.16, 0.12, 0.075, sill + wh + 0.02)
                add_box(frame_batch, (cx - tangent[0] * (wc / 2 + 0.03), cy - tangent[1] * (wc / 2 + 0.03)), tangent, normal, 0.07, 0.12, wh + 0.12, center_z)
                add_box(frame_batch, (cx + tangent[0] * (wc / 2 + 0.03), cy + tangent[1] * (wc / 2 + 0.03)), tangent, normal, 0.07, 0.12, wh + 0.12, center_z)
                add_box(trim_batch, (cx, cy), tangent, normal, wc + 0.26, 0.17, 0.10, sill - 0.08)
                # Small selective black balcony rails at the residential wings.
                if is_upper and level_index in (0, 1) and (interval_i % 3 == 1) and length > 6.0:
                    add_box(balcony_batch, (cx + normal[0] * 0.72, cy + normal[1] * 0.72), tangent, normal, wc + 0.50, 1.35, 0.15, sill - 0.20)
                    railz = sill + 0.82
                    add_box(balcony_batch, (cx + normal[0] * 1.35, cy + normal[1] * 1.35), tangent, normal, wc + 0.50, 0.07, 0.075, railz)
                    for side in (-1, 1):
                        px, py = cx + tangent[0] * side * (wc / 2 + 0.19) + normal[0] * 1.35, cy + tangent[1] * side * (wc / 2 + 0.19) + normal[1] * 1.35
                        add_box(balcony_batch, (px, py), tangent, normal, 0.055, 0.055, 0.82, sill + 0.30)
                    for r in range(1, 6):
                        frac = r / 6
                        px, py = cx + normal[0] * 1.35, cy + normal[1] * 1.35
                        add_box(balcony_batch, (px, py), tangent, normal, 0.035, 0.035, 0.76, sill + 0.18 + frac * 0.10)


def add_text(name, body, location, rotation, size, mat, collection):
    curve = bpy.data.curves.new(name + "Curve", "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.012
    curve.bevel_depth = 0.002
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj


def scene_setup(scene, collection):
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)
    for col in list(bpy.data.collections):
        if col != collection and col.name != "Collection":
            bpy.data.collections.remove(col)
    for child in list(scene.collection.children):
        scene.collection.children.unlink(child)
    scene.collection.children.link(collection)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.color = (0.12, 0.15, 0.2)
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Standard"
    scene.render.filepath = str(EVIDENCE / "faith_west_exterior_preview.png")
    scene.camera = None


def make_camera(scene, target, eye, lens=47):
    data = bpy.data.cameras.new("FaithWest_ReviewCamera")
    camera = bpy.data.objects.new("FaithWest_ReviewCamera", data)
    scene.collection.objects.link(camera)
    camera.location = eye
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    scene.camera = camera
    return camera


def build():
    outline, source_feature = ensure_research()
    geo_data=json.loads((EVIDENCE/"faith_west_geometry.json").read_text(encoding="utf-8"))
    upper_polygons=geo_data["upper_footprint_polygons"]
    patio_polygons=geo_data["patio_polygons"]
    low_roof_polygons=geo_data["low_roof_polygons"]
    hvac_sites=geo_data["hvac_representative_points_world_m"]
    scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.get(COLLECTION_NAME) or bpy.data.collections.new(COLLECTION_NAME)
    scene_setup(scene, collection)

    brick = material("FaithWest_Deep_Red_Brick", (0.32, 0.075, 0.052), texture="brick")
    brick_light = material("FaithWest_Accent_Brick", (0.47, 0.13, 0.085), texture="brick")
    siding_gold = material("FaithWest_Warm_Tan_Siding", (0.68, 0.47, 0.24), texture="siding")
    siding_cream = material("FaithWest_Cream_Siding", (0.82, 0.78, 0.66), texture="siding")
    roofmat = material("FaithWest_Charcoal_Shingle_Roof", (0.065, 0.08, 0.10), texture="shingle")
    roof_trim = material("FaithWest_White_Roof_Fascia", (0.88, 0.84, 0.72))
    frame = material("FaithWest_White_Window_Trim", (0.84, 0.84, 0.79), roughness=0.38)
    glass = material("FaithWest_Glazing", (0.085, 0.15, 0.19), roughness=0.18, metallic=0.15)
    balcony_mat = material("FaithWest_Balcony_Black_Metal", (0.055, 0.075, 0.09), roughness=0.35, metallic=0.7)
    concrete = material("FaithWest_Patio_Concrete", (0.42, 0.43, 0.41), roughness=0.84)
    white = material("FaithWest_Sign_Lettering", (0.93, 0.73, 0.19), roughness=0.55, metallic=0.12)
    wood = material("FaithWest_Gym_Wood_Floor", (0.40, 0.25, 0.12), roughness=0.6)
    court = material("FaithWest_Gym_Court_Lines", (0.92, 0.83, 0.59), roughness=0.7)
    blacktop = material("FaithWest_EPDM_Roof", (0.11, 0.12, 0.13), roughness=0.92)
    landscaping = material("FaithWest_Outdoor_Green", (0.16, 0.28, 0.12), roughness=0.95)
    orange = material("FaithWest_Cafe_Umbrella_Orange", (0.9, 0.20, 0.025), roughness=0.66)
    metal = material("FaithWest_Outdoor_Metal", (0.12, 0.14, 0.14), roughness=0.4, metallic=0.65)

    bounds_x = [min(p[0] for p in outline), max(p[0] for p in outline)]
    bounds_y = [min(p[1] for p in outline), max(p[1] for p in outline)]
    # The source describes a four-story building: one public-services level and three
    # student-housing levels. The northwest/rear and long east wings carry the upper levels.
    if not upper_polygons:
        raise RuntimeError("Upper-level footprint clip failed")
    z0, zpodium = 0.0, 4.05
    floor_heights = [3.28, 3.25, 3.25]
    upper_top = zpodium + sum(floor_heights)
    # Broad upper housing wings with warm tan lower cladding and a cream top story.
    z = zpodium
    for i, h in enumerate(floor_heights):
        wallmat = siding_gold if i < 2 else siding_cream
        z += h
    for poly_i, upper in enumerate(upper_polygons):
        extrude_ring(f"FaithWest_Housing_Shingle_Roof_Deck_{poly_i+1:02d}",upper,upper_top-0.14,upper_top+0.02,roofmat,collection,True)
    for roof_i, roof_poly in enumerate(low_roof_polygons):
        extrude_ring(f"FaithWest_Flat_EPDM_Roof_Community_Wing_{roof_i+1:02d}",roof_poly,zpodium-0.015,zpodium+0.04,blacktop,collection,True)

    # Floor bands, corner piers, and brick pilasters distinguish the housing blocks.
    horizontal = batch_mesh("FaithWest_White_Story_Bands", frame, collection)
    pilasters = batch_mesh("FaithWest_Brick_Pilasters", brick_light, collection)
    for poly, base, height in [(outline, 0.0, zpodium)] + [(u,zpodium,upper_top-zpodium) for u in upper_polygons]:
        ccw = polygon_area(poly) > 0
        for i, a in enumerate(poly):
            b = poly[(i+1) % len(poly)]
            dx, dy = b[0]-a[0], b[1]-a[1]
            length = math.hypot(dx,dy)
            if length < 4: continue
            t=(dx/length,dy/length)
            n=(t[1],-t[0]) if ccw else (-t[1],t[0])
            for floorz in ([1.0, zpodium] if poly is outline else [zpodium+floor_heights[0], zpodium+sum(floor_heights[:2]), upper_top]):
                cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2
                add_box(horizontal,(cx+n[0]*0.08,cy+n[1]*0.08),t,n,length,0.16,0.14,floorz)
            # Brick vertical accents every 10-14m across upper wings.
            if poly is not outline:
                count=max(1, int(length//12.0))
                for j in range(count+1):
                    u=length*j/(count+1)
                    cx,cy=a[0]+t[0]*u, a[1]+t[1]*u
                    add_box(pilasters,(cx+n[0]*0.065,cy+n[1]*0.065),t,n,0.27,0.14,height,base+height*0.5)

    # Repeated windows, pale surrounds, and selective dark steel balconies.
    glassb=batch_mesh("FaithWest_Glazing_Panels",glass,collection)
    frameb=batch_mesh("FaithWest_Window_Frames",frame,collection)
    trim_b=batch_mesh("FaithWest_Window_Sills",roof_trim,collection)
    balcony_b=batch_mesh("FaithWest_Balconies_and_Rails",balcony_mat,collection)
    wall_batches=[batch_mesh("FaithWest_Public_Podium_Walls_With_Window_Openings",brick,collection)]
    build_facade(outline,[(0.0,zpodium)],wall_batches,frameb,glassb,trim_b,balcony_b,False)
    levels=[]
    z=zpodium
    for h in floor_heights:
        levels.append((z,h))
        z+=h
    upper_wall_batches=[]
    for i in range(len(levels)):
        upper_wall_batches.append(batch_mesh(f"FaithWest_Housing_Level_{i+2:02d}_Walls_With_Window_Openings",siding_gold if i<2 else siding_cream,collection))
    for upper in upper_polygons:
        build_facade(upper,levels,upper_wall_batches,frameb,glassb,trim_b,balcony_b,True)
    for b in (glassb,frameb,trim_b,balcony_b,horizontal,pilasters,*wall_batches,*upper_wall_batches):
        if b["verts"]:
            object_mesh(b["name"],b["verts"],b["faces"],b["mat"],b["collection"])

    # Flat EPDM roof zone over the low community/gym wing and shingle roof forms above housing.

    # Dormer-like gabled roof strips supported by the published aerial: grey sloped roof
    # planes follow the long residence wings, with cream fascia and short ridge caps.
    def gable_strip_x(name, xmin, xmax, ymin, ymax, eave, ridge, material_roof):
        ym=(ymin+ymax)/2
        verts=[(xmin,ymin,eave),(xmax,ymin,eave),(xmax,ymax,eave),(xmin,ymax,eave),
               (xmin,ym,ridge),(xmax,ym,ridge)]
        faces=[(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5)]
        object_mesh(name,verts,faces,material_roof,collection)
    def gable_strip_y(name, xmin, xmax, ymin, ymax, eave, ridge, material_roof):
        xm=(xmin+xmax)/2
        verts=[(xmin,ymin,eave),(xmax,ymin,eave),(xmax,ymax,eave),(xmin,ymax,eave),
               (xm,ymin,ridge),(xm,ymax,ridge)]
        faces=[(0,4,5,3),(4,1,2,5),(0,1,4),(3,5,2)]
        object_mesh(name,verts,faces,material_roof,collection)
    # Wing rectangles intentionally stay within the source outline. Their approximate extents
    # reproduce the long gray roof ridges visible in KJG's exterior and Titan's aerial image.
    eave=upper_top+0.14
    gable_strip_x("FaithWest_North_Housing_Wing_Gable_Roof",-688.0,-641.0,2213.0,2224.0,eave,upper_top+2.0,roofmat)
    gable_strip_y("FaithWest_East_Housing_Wing_Gable_Roof",-649.0,-638.0,2152.0,2205.0,eave,upper_top+1.9,roofmat)
    gable_strip_y("FaithWest_Central_Housing_Wing_Gable_Roof",-680.0,-665.0,2182.0,2205.0,eave,upper_top+2.1,roofmat)
    # The aerial confirms two broad residential roof ridges. The west mass remains low in the
    # OSM/site view, so no unsupported roof is added outside the upper outline.

    # Rooftop HVAC units over the flat public wing, in dark housings with light access caps.
    hvac=batch_mesh("FaithWest_Rooftop_HVAC_Units",metal,collection)
    for x,y in hvac_sites:
        for ox,oy in ((-2.2,0),(1.2,1.5)):
            add_box(hvac,(x+ox,y+oy),(1,0),(0,1),1.5,0.95,0.55,zpodium+0.34)
    if hvac["verts"]: object_mesh(hvac["name"],hvac["verts"],hvac["faces"],hvac["mat"],collection)

    # Public-facing café patio: concrete terrace, orange umbrellas, and tables/chairs.
    for patio_i,patio_poly in enumerate(patio_polygons):
        extrude_ring(f"FaithWest_Cafe_Patio_Paving_{patio_i+1:02d}",patio_poly,0.02,0.14,concrete,collection,True)
    tables=batch_mesh("FaithWest_Cafe_Tables_and_Seats",wood,collection)
    umbrella=batch_mesh("FaithWest_Orange_Cafe_Umbrellas",orange,collection)
    for i,(x,y) in enumerate(((-661,2145),(-655,2146),(-650,2144),(-645,2146),(-639,2145))):
        add_box(tables,(x,y),(1,0),(0,1),1.35,1.35,0.09,0.95)
        for dx in (-0.58,0.58):
            for dy in (-0.50,0.50):
                add_box(tables,(x+dx,y+dy),(1,0),(0,1),0.07,0.07,0.80,0.45)
        # broad polygonal umbrella canopy, represented with a faceted shallow roof.
        ring=[]
        for j in range(12):
            ang=2*math.pi*j/12
            ring.append((x+math.cos(ang)*1.5,y+math.sin(ang)*1.15,3.4))
        apex=(x,y,3.75)
        base=len(umbrella["verts"]); umbrella["verts"].extend(ring+[apex])
        for j in range(12): umbrella["faces"].append((base+j,base+(j+1)%12,base+12))
        add_box(tables,(x,y),(1,0),(0,1),0.05,0.05,2.55,2.15)
    for b in (tables,umbrella):
        if b["verts"]: object_mesh(b["name"],b["verts"],b["faces"],b["mat"],collection)

    # A representative gym floor, multipurpose court markings, apartment partitions and furniture
    # sit inside the shell; these do not claim a source-measured room plan.
    gym_x0,gym_x1=-696,-672
    gym_y0,gym_y1=2153,2177
    gym_floor_poly=[(gym_x0,gym_y0),(gym_x1,gym_y0),(gym_x1,gym_y1),(gym_x0,gym_y1)]
    extrude_ring("FaithWest_Indoor_Gym_Wood_Court",gym_floor_poly,0.22,0.30,wood,collection,True)
    court_batch=batch_mesh("FaithWest_Gym_Court_Markings",court,collection)
    # Thin line boxes, court outline and center line.
    for a,bp in [((gym_x0+2,gym_y0+2),(gym_x1-2,gym_y0+2)),((gym_x1-2,gym_y0+2),(gym_x1-2,gym_y1-2)),((gym_x1-2,gym_y1-2),(gym_x0+2,gym_y1-2)),((gym_x0+2,gym_y1-2),(gym_x0+2,gym_y0+2)),((gym_x0+2,(gym_y0+gym_y1)/2),(gym_x1-2,(gym_y0+gym_y1)/2))]:
        cx,cy=(a[0]+bp[0])/2,(a[1]+bp[1])/2
        length=math.dist(a,bp); tang=((bp[0]-a[0])/length,(bp[1]-a[1])/length)
        add_box(court_batch,(cx,cy),tang,(tang[1],-tang[0]),length,0.03,0.075,0.315)
    object_mesh(court_batch["name"],court_batch["verts"],court_batch["faces"],court_batch["mat"],collection)

    # Interior circulation and schematic room blocks on each housing floor.
    floors=batch_mesh("FaithWest_Residential_Floor_Plates",concrete,collection)
    partitions=batch_mesh("FaithWest_Apartment_Partitions",siding_cream,collection)
    furniture=batch_mesh("FaithWest_Representative_Apartment_Furniture",wood,collection)
    for floor_i in range(3):
        zfloor=zpodium+floor_i*3.25+0.15
        for poly_i,upper in enumerate(upper_polygons):
            extrude_ring(f"FaithWest_Interior_Floor_Slab_Level_{floor_i+2:02d}_{poly_i+1:02d}",upper,zfloor-0.10,zfloor+0.02,wood,collection,True)
        # Each representative room is schematic, with a corridor-side partition and furniture.
        for x in (-677,-669,-661,-653,-645):
            if x < bounds_x[0]+12 or x>bounds_x[1]-2: continue
            add_box(floors,(x,2200),(1,0),(0,1),6.2,3.8,0.12,zfloor)
            add_box(partitions,(x,2200),(1,0),(0,1),0.10,3.5,2.8,zfloor+1.45)
            add_box(furniture,(x-1.1,2199.2),(1,0),(0,1),1.8,0.95,0.18,zfloor+0.32)
            add_box(furniture,(x+0.7,2200.8),(1,0),(0,1),0.9,0.9,0.48,zfloor+0.50)
        # Corridor rails and repeated dividing walls inside the west wing.
        for y in (2190,2198,2206):
            add_box(partitions,(-693,y),(1,0),(0,1),12.0,0.12,2.9,zfloor+1.45)
    for b in (floors,partitions,furniture):
        if b["verts"]: object_mesh(b["name"],b["verts"],b["faces"],b["mat"],collection)

    # Preschool play yard and low boundary elements; restrained near the east wing.
    play = batch_mesh("FaithWest_Preschool_Playground_Equipment",orange,collection)
    for x,y in ((-640,2194),(-644,2196),(-638,2187)):
        add_box(play,(x,y),(1,0),(0,1),2.1,1.0,1.4,0.9)
    if play["verts"]: object_mesh(play["name"],play["verts"],play["faces"],play["mat"],collection)

    # Source-photo signage is on the south-facing entry frontage (approximate location).
    # Text has front-facing typography at campus scale, with an explicit building sign material.
    signrot=(math.radians(90),0,0)
    add_text("FaithWest_Community_Center_Sign","FAITH WEST COMMUNITY CENTER",(-654.5,2140.70,3.2),signrot,0.72,white,collection)
    add_text("FaithWest_Fitness_Sign","FITNESS",(-679.5,2153.1,3.25),signrot,0.50,white,collection)
    add_text("FaithWest_Preschool_Sign","PRESCHOOL",(-640.3,2188.0,3.2),(math.radians(90),0,math.radians(90)),0.35,white,collection)

    # Provide subdued site planting on the patios, no claims of exact landscape coordinates.
    planters=batch_mesh("FaithWest_Patio_Planters",landscaping,collection)
    for x,y in ((-667,2145),(-658,2143),(-648,2143),(-638,2147),(-635,2160)):
        add_box(planters,(x,y),(1,0),(0,1),1.2,0.75,0.48,0.40)
    if planters["verts"]: object_mesh(planters["name"],planters["verts"],planters["faces"],planters["mat"],collection)

    # Lights, world, camera and render for evidence review.
    for data in list(bpy.data.lights): bpy.data.lights.remove(data)
    ldata=bpy.data.lights.new("FaithWest_Sun","SUN"); ldata.energy=1.25
    light=bpy.data.objects.new("FaithWest_Sun",ldata); scene.collection.objects.link(light)
    light.rotation_euler=(math.radians(27),math.radians(-25),math.radians(-28))
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value=(0.20,0.30,0.48,1)
    bg.inputs["Strength"].default_value=0.3
    center=((bounds_x[0]+bounds_x[1])/2,(bounds_y[0]+bounds_y[1])/2,7.0)
    exterior_camera=make_camera(scene,center,(center[0]+112,center[1]-142,center[2]+34),55)
    scene.render.resolution_x=1400; scene.render.resolution_y=1050
    scene.render.filepath=str(EVIDENCE/"faith_west_exterior_preview.png")
    scene.camera.data.dof.use_dof=False
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    bpy.ops.render.render(write_still=True)

    # An interior cutaway review image removes the near shell and roof surfaces temporarily.
    hide_names=("Walls_With_Window_Openings","Glazing_Panels","Window_Frames","Window_Sills","Balconies_and_Rails","White_Story_Bands","Brick_Pilasters","Roof_Deck","Gable_Roof","EPDM_Roof","Interior_Floor_Slab","Cafe_Umbrellas","Cafe_Tables","Playground","Patio_Planters","Cafe_Patio")
    changed=[]
    for obj in scene.objects:
        if any(token in obj.name for token in hide_names):
            changed.append((obj,obj.hide_render))
            obj.hide_render=True
    scene.render.filepath=str(EVIDENCE/"faith_west_interior_cutaway.png")
    interior_camera=make_camera(scene,(center[0]-5,center[1]+2,5.0),(center[0]+62,center[1]-72,42),55)
    scene.camera=interior_camera
    bpy.ops.render.render(write_still=True)
    for obj,was_hidden in changed:
        obj.hide_render=was_hidden
    scene.render.filepath=str(EVIDENCE/"faith_west_exterior_preview.png")

    # Save the export in a clean, single-scene library with its expected collection.
    for obj in list(bpy.data.objects):
        if obj.name.startswith("FaithWest_ReviewCamera") or obj.name == "FaithWest_Sun":
            # Camera and lighting are useful for review; keep them out of the export collection.
            for c in list(obj.users_collection): c.objects.unlink(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.camera=None
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

    # Structured candidate report and evidence record.
    all_pts=[(x,y,z) for x,y in outline for z in (0,)] + [(x,y,upper_top+2.1) for x,y in outline]
    bmin=[min(p[i] for p in all_pts) for i in range(3)]
    bmax=[max(p[i] for p in all_pts) for i in range(3)]
    objects=list(collection.objects)
    report={"building_id":ID,"asset":str(ASSET.relative_to(ROOT)).replace("\\","/"),"scene":SCENE_NAME,"collection":COLLECTION_NAME,"object_count":len(objects),"mesh_object_count":sum(o.type=="MESH" for o in objects),"text_object_count":sum(o.type=="FONT" for o in objects),"material_count":len([m for m in bpy.data.materials if m.name.startswith("FaithWest_")]),"source_feature":{"provider":"OpenStreetMap Overpass API","type":source_feature["type"],"id":source_feature["id"],"tags":source_feature["tags"]},"outline_vertex_count":len(outline),"outline_area_m2":abs(polygon_area(outline)),"outline_bounds_world_m":[[bmin[0],bmin[1],bmin[2]],[bmax[0],bmax[1],bmax[2]]],"upper_footprint_vertex_count":len(upper),"model_roof_height_estimate_m":upper_top+2.1,"image_dependencies":[],"preview":"audit/faith_west_community_center/faith_west_exterior_preview.png","validation":"saved from Blender 5.2.3; fresh open pending"}
    report["interior_geometry"]={"floor_slab_levels":3,"schematic_apartment_rooms_per_level":5,"gym_court_dimensions_m":[24,24],"cutaway_preview":"audit/faith_west_community_center/faith_west_interior_cutaway.png","source_backed_room_plan":False}
    (EVIDENCE/"build_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    evidence={"identity":"Faith West Community Center, 1920 Northwestern Ave, West Lafayette, IN","sources":[
        {"url":"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates","provider":"ArcGIS World Geocoding Service","retrieval_date":"2026-10-26","result_address":"1920 Northwestern Ave, West Lafayette, Indiana, 47906","score":100,"coordinates_lon_lat":[-86.92152523758,40.447113411709]},
        {"url":"https://overpass-api.de/api/interpreter","provider":"OpenStreetMap via Overpass API","retrieval_date":"2026-10-26","feature":"way 743763888 Faith West Community Center","source_crs":"WGS84 / EPSG:4326","measurement_method":"40-point named building outline transformed with project local geographic approximation; footprint includes all mapped wings","uncertainty":"OSM outline is volunteer mapping and not a surveyed wall line; positional and facade detail need independent imagery comparison."},
        {"url":"https://www.kjgarchitecture.com/portfolio-1/faith-west-community-center","provider":"KJG Architecture project page","retrieval_date":"2026-10-26","source_image":"kjg_exterior_01.jpg","supports":"four-story mixed-use facility; ground-level community uses, upper student housing; brick and light siding, repetitive windows, balconies, charcoal pitched roof"},
        {"url":"https://www.titanconstructionservices.com/commercial-projects/faith-west-community-center","provider":"Titan Construction project page","retrieval_date":"2026-10-26","source_image":"faithwest_aerial.jpg","supports":"large irregular wings, curved fitness frontage, courtyard/patio, four levels, rooftop service elements, 92,410 square foot project; structural steel/masonry/stud construction"},
        {"url":"https://www.faithlafayette.org/church/locations/west-campus","provider":"Faith Church","retrieval_date":"2026-10-26","source_image":"faithwest_campus_photo.jpg","supports":"front entrance, brick podium, yellow sign lettering, entrance glazing, patio"},
        {"url":"https://www.faithlafayette.org/church/about/history","provider":"Faith Church history page","retrieval_date":"2026-10-26","supports":"facility program includes community sports gymnasium, preschool/childcare, meeting areas, fitness center, cafe, covenant housing for 119"},
        {"url":"https://www.faithlafayette.org/community-centers/west/virtual-tour","provider":"Faith Church virtual tour","retrieval_date":"2026-10-26","supports":"common areas, fitness and gym, outdoor seating, walking trail, playground, patio"},
        {"url":"https://www.wbaa.org/business-economy-and-consumer-affairs/2013-08-06/faith-west-opens-in-west-lafayette","provider":"WBAA public radio, 2013 report","retrieval_date":"2026-10-26","supports":"opening in 2013, residents, fitness center, preschool, restaurant and leased cafe details"}
    ],"geometry":{"projection":"Project local geographic approximation: X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0","source_outline_vertices":len(outline),"source_outline_area_m2":abs(polygon_area(outline)),"bounds_world_m":[[bmin[0],bmin[1],bmin[2]],[bmax[0],bmax[1],bmax[2]]],"model_to_OSM_footprint":"outline used directly, transformed from OSM WGS84 coordinates","vertical_dimensions":"Estimated from published four-story description and project massing record; not measured elevation data"},"design_notes":{"base":"Full source outline as one-story red-brick community podium","upper":"Clipped footprint for three residential stories, tan lower cladding, cream top story, repetitive windows and selective balconies","roof":"Gray pitched roof approximated as three wing roof ridges; roof lines estimated from KJG and Titan aerial imagery","interior":"Gym court, representative apartment room layout and cafe patio furniture are schematic, not a measured plan"},"uncertainty":["No as-built elevation or roof height drawing was found.","The exact residential floor plate shape and allocation of uses are inferred from aerial imagery and public project descriptions.","OSM floor outline is volunteer-mapped and may include parapets, canopies, or minor footprint simplification."]}
    (EVIDENCE/"evidence.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
    print("FAITH_WEST_BUILD_PASS " + json.dumps(report))


if __name__ == "__main__":
    build()

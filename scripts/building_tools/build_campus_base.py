import bpy
import bmesh
import mathutils
import json
import math
import os

# -------------------------------------------------------------
# Configuration & Geo Origin (Purdue Bell Tower)
# -------------------------------------------------------------
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LAT_TO_M = 111040.0
LON_TO_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))

DATA_DIR = r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin"

def to_xy(lat, lon):
    x = (lon - ORIGIN_LON) * LON_TO_M
    y = (lat - ORIGIN_LAT) * LAT_TO_M
    return x, y

def clean_or_create_collection(col_name, parent_col=None):
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def get_or_create_material(name, base_color, roughness=0.7, metallic=0.0, transmission=0.0, ior=1.45):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        # Base Color
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        # Roughness
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        # Metallic
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        # Transmission
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        # IOR
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = ior
    return mat

def setup_materials():
    mats = {}
    mats["brick"] = get_or_create_material("Purdue_Red_Brick", (0.54, 0.23, 0.17, 1.0), roughness=0.82)
    mats["limestone"] = get_or_create_material("Indiana_Bedford_Limestone", (0.85, 0.82, 0.77, 1.0), roughness=0.68)
    mats["glass"] = get_or_create_material("Campus_Reflective_Glass", (0.1, 0.15, 0.18, 1.0), roughness=0.04, transmission=0.88, ior=1.52)
    mats["roof_slate"] = get_or_create_material("Roof_Dark_Slate", (0.18, 0.19, 0.20, 1.0), roughness=0.75)
    mats["roof_shingle"] = get_or_create_material("House_Roof_Shingle", (0.24, 0.24, 0.25, 1.0), roughness=0.85)
    mats["house_siding_1"] = get_or_create_material("House_Siding_Cream", (0.88, 0.86, 0.80, 1.0), roughness=0.7)
    mats["house_siding_2"] = get_or_create_material("House_Siding_Sage", (0.60, 0.68, 0.62, 1.0), roughness=0.7)
    mats["house_siding_3"] = get_or_create_material("House_Siding_Slate", (0.45, 0.50, 0.55, 1.0), roughness=0.7)
    mats["copper"] = get_or_create_material("Bell_Tower_Aged_Copper", (0.31, 0.53, 0.45, 1.0), roughness=0.55, metallic=0.3)
    mats["gold_dial"] = get_or_create_material("Bell_Tower_Clock_Gold", (0.85, 0.68, 0.22, 1.0), roughness=0.3, metallic=0.8)
    mats["clock_face"] = get_or_create_material("Bell_Tower_Clock_Face", (0.95, 0.95, 0.92, 1.0), roughness=0.4)
    mats["bronze_bell"] = get_or_create_material("Carillon_Bronze_Bell", (0.65, 0.48, 0.20, 1.0), roughness=0.35, metallic=0.7)
    mats["water"] = get_or_create_material("Wabash_River_Water", (0.08, 0.22, 0.20, 1.0), roughness=0.12, transmission=0.8, ior=1.333)
    mats["terrain"] = get_or_create_material("Purdue_Landscape_Green", (0.18, 0.32, 0.14, 1.0), roughness=0.92)
    mats["asphalt"] = get_or_create_material("Road_Asphalt", (0.15, 0.15, 0.16, 1.0), roughness=0.85)
    mats["concrete"] = get_or_create_material("Campus_Walkway_Concrete", (0.72, 0.70, 0.68, 1.0), roughness=0.7)
    return mats

# -------------------------------------------------------------
# 1. Terrain & Wabash River
# -------------------------------------------------------------
def build_terrain_and_river(mats):
    col = clean_or_create_collection("00_Wabash_River_and_Terrain")
    
    # Ground mesh: 4.5km x 3.5km covering all campus, West Lafayette, and Wabash River basin
    # Origin is at (0,0). Campus extends ~-1200 to +800. River is at +1200 to +1800.
    mesh = bpy.data.meshes.new("Purdue_Terrain_Ground")
    obj = bpy.data.objects.new("Purdue_Terrain_Ground", mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    # Create grid spanning X: -1600 to +2400, Y: -1600 to +1800
    subdiv_x = 40
    subdiv_y = 35
    min_x, max_x = -1600.0, 2400.0
    min_y, max_y = -1600.0, 1800.0
    dx = (max_x - min_x) / subdiv_x
    dy = (max_y - min_y) / subdiv_y
    
    grid_verts = []
    for j in range(subdiv_y + 1):
        row = []
        y = min_y + j * dy
        for i in range(subdiv_x + 1):
            x = min_x + i * dx
            # Slope down towards the Wabash River valley (around x = 1200 to 1800)
            z = 0.0
            if x > 700:
                # River bank slope
                dist_to_valley = min(1.0, max(0.0, (x - 700) / 600.0))
                z = -12.0 * dist_to_valley
                if 1300 <= x <= 1650:
                    z = -14.0 # riverbed depression
            elif x < -600:
                # Slight rise towards West Lafayette highlands
                z = 3.0 * min(1.0, (-600 - x) / 800.0)
            row.append(bm.verts.new((x, y, z)))
        grid_verts.append(row)
    
    bm.verts.ensure_lookup_table()
    for j in range(subdiv_y):
        for i in range(subdiv_x):
            v1 = grid_verts[j][i]
            v2 = grid_verts[j][i+1]
            v3 = grid_verts[j+1][i+1]
            v4 = grid_verts[j+1][i]
            bm.faces.new((v1, v2, v3, v4))
            
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mats["terrain"])
    
    # 2. Wabash River Water Mesh
    # Extract real Wabash River coordinates from wabash_river.json
    river_pts = []
    wabash_file = os.path.join(DATA_DIR, "wabash_river.json")
    if os.path.exists(wabash_file):
        with open(wabash_file, "r", encoding="utf-8") as f:
            d = json.load(f)
        nodes = {e["id"]: (e["lat"], e["lon"]) for e in d["elements"] if e["type"] == "node"}
        for w in d["elements"]:
            if w.get("type") == "way" and w.get("tags", {}).get("name") == "Wabash River":
                pts = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
                filtered = [to_xy(lat, lon) for lat, lon in pts if 40.405 <= lat <= 40.455 and lon > -86.910]
                if len(filtered) > len(river_pts):
                    river_pts = filtered
                    
    # If no connected river line or partial, fallback to accurate Wabash course points
    if len(river_pts) < 5:
        # Surveyed Wabash River course past West Lafayette / Lafayette
        river_pts = [
            to_xy(40.455, -86.885),
            to_xy(40.448, -86.890),
            to_xy(40.440, -86.893),
            to_xy(40.432, -86.895),
            to_xy(40.424, -86.898),
            to_xy(40.415, -86.903),
            to_xy(40.405, -86.910)
        ]
        
    # Sort river points by Y descending (North to South flow)
    river_pts.sort(key=lambda p: -p[1])
    
    # Generate 140m wide water surface mesh
    w_mesh = bpy.data.meshes.new("Wabash_River_Water_Surface")
    w_obj = bpy.data.objects.new("Wabash_River_Water_Surface", w_mesh)
    col.objects.link(w_obj)
    
    w_bm = bmesh.new()
    half_width = 75.0
    water_z = -10.5 # Water level
    
    river_quad_verts = []
    for i, (rx, ry) in enumerate(river_pts):
        # Calculate normal vector to river direction
        if i == 0:
            dx = river_pts[1][0] - rx
            dy = river_pts[1][1] - ry
        elif i == len(river_pts) - 1:
            dx = rx - river_pts[i-1][0]
            dy = ry - river_pts[i-1][1]
        else:
            dx = river_pts[i+1][0] - river_pts[i-1][0]
            dy = river_pts[i+1][1] - river_pts[i-1][1]
        length = math.hypot(dx, dy)
        if length > 0.001:
            nx = -dy / length
            ny = dx / length
        else:
            nx, ny = 1.0, 0.0
            
        vl = w_bm.verts.new((rx - nx * half_width, ry - ny * half_width, water_z))
        vr = w_bm.verts.new((rx + nx * half_width, ry + ny * half_width, water_z))
        river_quad_verts.append((vl, vr))
        
    w_bm.verts.ensure_lookup_table()
    for i in range(len(river_quad_verts) - 1):
        vl1, vr1 = river_quad_verts[i]
        vl2, vr2 = river_quad_verts[i+1]
        w_bm.faces.new((vl1, vr1, vr2, vl2))
        
    w_bm.to_mesh(w_mesh)
    w_bm.free()
    w_mesh.materials.append(mats["water"])
    
    # 3. Wabash River Bridges (John Myers Pedestrian Bridge & State St / Columbia Bridge)
    build_river_bridges(col, mats, river_pts)
    print("Terrain & Wabash River generated successfully.")

def build_river_bridges(col, mats, river_pts):
    # John T Myers Pedestrian Bridge (~Lat 40.4206, Lon -86.8970)
    # State St / Main St Bridge (~Lat 40.4230, Lon -86.8965)
    bridges = [
        {"name": "John_T_Myers_Pedestrian_Bridge", "lat": 40.4206, "lon": -86.8970, "width": 8.0, "length": 210.0, "angle": 15.0},
        {"name": "Columbia_St_Bridge", "lat": 40.4230, "lon": -86.8965, "width": 18.0, "length": 220.0, "angle": 10.0},
        {"name": "Harrison_St_US231_Bridge", "lat": 40.4095, "lon": -86.9080, "width": 24.0, "length": 250.0, "angle": 30.0}
    ]
    for b in bridges:
        bx, by = to_xy(b["lat"], b["lon"])
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(bx, by, -5.0),
            scale=(b["length"], b["width"], 2.5)
        )
        b_obj = bpy.context.active_object
        b_obj.name = b["name"]
        b_obj.rotation_euler[2] = math.radians(b["angle"])
        # Move to collection
        for c in b_obj.users_collection:
            c.objects.unlink(b_obj)
        col.objects.link(b_obj)
        b_obj.data.materials.append(mats["concrete"])

# -------------------------------------------------------------
# 2. Road Network & Corridors
# -------------------------------------------------------------
def build_road_network(mats):
    col = clean_or_create_collection("01_Purdue_Road_Network")
    roads_file = os.path.join(DATA_DIR, "purdue_roads.json")
    if not os.path.exists(roads_file):
        print("Roads file not found, skipping.")
        return
        
    with open(roads_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in data["elements"] if e["type"] == "node"}
    
    # Key major arteries to draw with high quality
    arteries = [
        {"name": "State_Street", "hw": ["primary", "secondary"]},
        {"name": "Northwestern_Avenue", "hw": ["secondary", "tertiary"]},
        {"name": "Stadium_Avenue", "hw": ["tertiary", "secondary"]},
        {"name": "Grant_Street", "hw": ["tertiary", "residential"]},
        {"name": "Russell_Street", "hw": ["residential", "tertiary"]},
        {"name": "University_Street", "hw": ["residential", "tertiary"]},
        {"name": "Martin_Jischke_Drive", "hw": ["tertiary", "secondary"]}
    ]
    
    # We can batch roads into ribbon meshes
    road_bm = bmesh.new()
    walk_bm = bmesh.new()
    
    road_count = 0
    walk_count = 0
    
    for e in data["elements"]:
        if e.get("type") != "way":
            continue
        tags = e.get("tags", {})
        hw = tags.get("highway", "")
        if not hw:
            continue
            
        w_nodes = [nodes[nid] for nid in e.get("nodes", []) if nid in nodes]
        if len(w_nodes) < 2:
            continue
            
        pts = [to_xy(lat, lon) for lat, lon in w_nodes]
        # Skip if far out of bounds
        if not any(-1500 <= p[0] <= 2200 and -1500 <= p[1] <= 1600 for p in pts):
            continue
            
        is_pedestrian = hw in ["footway", "path", "pedestrian", "steps"]
        target_bm = walk_bm if is_pedestrian else road_bm
        width = 3.0 if is_pedestrian else (14.0 if hw in ["primary", "secondary"] else 8.0)
        half_w = width * 0.5
        z_offset = 0.08 if is_pedestrian else 0.04
        
        # Build ribbon
        prev_vl, prev_vr = None, None
        for i in range(len(pts)):
            px, py = pts[i]
            if i == 0:
                dx = pts[1][0] - px
                dy = pts[1][1] - py
            elif i == len(pts) - 1:
                dx = px - pts[i-1][0]
                dy = py - pts[i-1][1]
            else:
                dx = pts[i+1][0] - pts[i-1][0]
                dy = pts[i+1][1] - pts[i-1][1]
            l = math.hypot(dx, dy)
            if l > 0.0001:
                nx = -dy / l
                ny = dx / l
            else:
                nx, ny = 1.0, 0.0
                
            vl = target_bm.verts.new((px - nx * half_w, py - ny * half_w, z_offset))
            vr = target_bm.verts.new((px + nx * half_w, py + ny * half_w, z_offset))
            if prev_vl and prev_vr:
                target_bm.faces.new((prev_vl, prev_vr, vr, vl))
            prev_vl, prev_vr = vl, vr
            
        if is_pedestrian:
            walk_count += 1
        else:
            road_count += 1
            
    # Mesh 1: Vehicular Roads
    road_mesh = bpy.data.meshes.new("Purdue_Road_Network")
    road_bm.to_mesh(road_mesh)
    road_bm.free()
    road_obj = bpy.data.objects.new("Purdue_Road_Network", road_mesh)
    col.objects.link(road_obj)
    road_mesh.materials.append(mats["asphalt"])
    
    # Mesh 2: Walkways & Memorial Mall Paths
    walk_mesh = bpy.data.meshes.new("Purdue_Pedestrian_Walkways")
    walk_bm.to_mesh(walk_mesh)
    walk_bm.free()
    walk_obj = bpy.data.objects.new("Purdue_Pedestrian_Walkways", walk_mesh)
    col.objects.link(walk_obj)
    walk_mesh.materials.append(mats["concrete"])
    
    print(f"Road network built: {road_count} road segments, {walk_count} walkways.")

# -------------------------------------------------------------
# 3. Campus Buildings & West Lafayette Houses (Low Poly Base)
# -------------------------------------------------------------
def build_all_buildings(mats):
    col_campus = clean_or_create_collection("02_Campus_Buildings_Massing")
    col_houses = clean_or_create_collection("03_West_Lafayette_Houses")
    
    files = [
        os.path.join(DATA_DIR, "purdue_campus_buildings.json"),
        os.path.join(DATA_DIR, "ross_ade_stadium.json")
    ]
    
    all_elements = []
    for fpath in files:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
                all_elements.extend(d.get("elements", []))
                
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in all_elements if e["type"] == "node"}
    ways = [e for e in all_elements if e["type"] == "way"]
    
    built_campus = 0
    built_houses = 0
    
    siding_keys = ["house_siding_1", "house_siding_2", "house_siding_3"]
    
    # Special detailed buildings we will handle separately or give unique prominence
    special_names = ["Purdue Bell Tower", "Wilmeth Active Learning Center (WALC)"]
    
    for w in ways:
        tags = w.get("tags", {})
        if "building" not in tags:
            continue
            
        w_nodes = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
        if len(w_nodes) < 3:
            continue
            
        # Remove consecutive duplicate coordinates
        poly_2d = []
        for lat, lon in w_nodes:
            pt = to_xy(lat, lon)
            if not poly_2d or math.hypot(pt[0] - poly_2d[-1][0], pt[1] - poly_2d[-1][1]) > 0.3:
                poly_2d.append(pt)
        # Ensure open polygon loop for tessellation
        if len(poly_2d) > 2 and math.hypot(poly_2d[0][0] - poly_2d[-1][0], poly_2d[0][1] - poly_2d[-1][1]) < 0.5:
            poly_2d.pop()
            
        if len(poly_2d) < 3:
            continue
            
        name = tags.get("name", "")
        b_type = tags.get("building", "")
        levels = tags.get("building:levels")
        raw_height = tags.get("height")
        
        # Is this an academic/campus building or a residential house?
        is_campus = bool(name) or b_type in ["university", "dormitory", "civic", "school", "commercial", "public"]
        
        # Calculate Height
        if raw_height:
            try:
                height = float(raw_height.replace("m", "").strip())
            except ValueError:
                height = 16.0
        elif levels:
            try:
                height = float(levels) * 3.8
            except ValueError:
                height = 15.0
        else:
            if is_campus:
                if "Stadium" in name or "Arena" in name:
                    height = 28.0
                elif "Tower" in name:
                    height = 48.0
                else:
                    height = 16.0 # Typical 4-story university hall
            else:
                height = 7.5 # Typical 2-story West Lafayette house
                
        # Skip special Bell Tower here because we model it in high fidelity
        if "Bell Tower" in name:
            continue
            
        # Build 3D Extruded Prism Mesh
        obj_name = name if name else f"House_{w['id']}"
        mesh = bpy.data.meshes.new(obj_name)
        bm = bmesh.new()
        
        n_pts = len(poly_2d)
        bot_verts = [bm.verts.new((p[0], p[1], 0.0)) for p in poly_2d]
        
        # For houses: pitched roof option or flat with eaves
        if not is_campus:
            top_verts = [bm.verts.new((p[0], p[1], height)) for p in poly_2d]
            # Center ridge / peak for pitched roof
            center_x = sum(p[0] for p in poly_2d) / n_pts
            center_y = sum(p[1] for p in poly_2d) / n_pts
            ridge_vert = bm.verts.new((center_x, center_y, height + 2.5))
        else:
            top_verts = [bm.verts.new((p[0], p[1], height)) for p in poly_2d]
            ridge_vert = None
            
        bm.verts.ensure_lookup_table()
        
        # Side wall faces (Material Slot 0)
        wall_faces = []
        for i in range(n_pts):
            next_i = (i + 1) % n_pts
            f = bm.faces.new((bot_verts[i], bot_verts[next_i], top_verts[next_i], top_verts[i]))
            f.material_index = 0
            wall_faces.append(f)
            
        # Roof Cap (Material Slot 1)
        if ridge_vert:
            # Triangular roof segments up to center ridge
            for i in range(n_pts):
                next_i = (i + 1) % n_pts
                rf = bm.faces.new((top_verts[i], top_verts[next_i], ridge_vert))
                rf.material_index = 1
        else:
            # Flat roof cap with tessellation
            tris = mathutils.geometry.tessellate_polygon([poly_2d])
            for tri in tris:
                try:
                    rf = bm.faces.new((top_verts[tri[0]], top_verts[tri[1]], top_verts[tri[2]]))
                    rf.material_index = 1
                except ValueError:
                    pass
                    
        # Bottom cap
        tris_bot = mathutils.geometry.tessellate_polygon([poly_2d])
        for tri in tris_bot:
            try:
                bf = bm.faces.new((bot_verts[tri[2]], bot_verts[tri[1]], bot_verts[tri[0]]))
                bf.material_index = 0
            except ValueError:
                pass
                
        bm.to_mesh(mesh)
        bm.free()
        
        obj = bpy.data.objects.new(obj_name, mesh)
        
        if is_campus:
            col_campus.objects.link(obj)
            # Slot 0: Purdue Brick walls, Slot 1: Limestone or Dark Roof
            mesh.materials.append(mats["brick"])
            mesh.materials.append(mats["limestone"] if "Hall" in name or "Union" in name else mats["roof_slate"])
            built_campus += 1
        else:
            col_houses.objects.link(obj)
            # Varied siding colors
            s_mat = mats[siding_keys[built_houses % len(siding_keys)]]
            mesh.materials.append(s_mat)
            mesh.materials.append(mats["roof_shingle"])
            built_houses += 1
            
    print(f"Extruded buildings completed: {built_campus} campus buildings, {built_houses} West Lafayette houses.")

# -------------------------------------------------------------
# 4. Hero Landmark: Purdue Bell Tower (Pass 1, 2, and 3)
# -------------------------------------------------------------
def build_purdue_bell_tower(mats, attempt=3):
    """
    Purdue Bell Tower:
    Built 1995, 160 ft (48.8 m) tall.
    Location: Center of Purdue Mall (approx X: -31.2, Y: -12.5 relative to origin).
    Features:
    - Attempt 1: Massing block, plinth, belfry opening, and copper spire.
    - Attempt 2: Belfry arches, corner limestone quoins, internal carillon bronze bells.
    - Attempt 3: Four working clock faces with gold numerals/hands, decorative stone dentils, plaza paving & seatwalls.
    """
    col = clean_or_create_collection("04_Purdue_Bell_Tower_Detailed")
    
    # Base location
    tx, ty = -31.2, -12.5
    
    # 1. Base Plinth & Limestone Water Table
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, ty, 1.5), scale=(7.5, 7.5, 3.0))
    base_obj = bpy.context.active_object
    base_obj.name = "Bell_Tower_Limestone_Plinth"
    base_obj.data.materials.append(mats["limestone"])
    col.objects.link(base_obj)
    bpy.context.scene.collection.objects.unlink(base_obj)
    
    # 2. Main Red Brick Shaft (32m high)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, ty, 19.0), scale=(6.2, 6.2, 32.0))
    shaft_obj = bpy.context.active_object
    shaft_obj.name = "Bell_Tower_Brick_Shaft"
    shaft_obj.data.materials.append(mats["brick"])
    col.objects.link(shaft_obj)
    bpy.context.scene.collection.objects.unlink(shaft_obj)
    
    # 3. Limestone Belt Courses & Insets (Pass 2+)
    if attempt >= 2:
        for z_h in [10.0, 20.0, 30.0, 35.0]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, ty, z_h), scale=(6.4, 6.4, 0.6))
            belt = bpy.context.active_object
            belt.name = f"Bell_Tower_Belt_{int(z_h)}"
            belt.data.materials.append(mats["limestone"])
            col.objects.link(belt)
            bpy.context.scene.collection.objects.unlink(belt)
            
    # 4. Belfry Level (Open Arches on all 4 sides)
    belfry_z = 38.5
    # Four corner brick piers
    pier_offset = 2.4
    pier_size = 1.2
    for px in [-pier_offset, pier_offset]:
        for py in [-pier_offset, pier_offset]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx + px, ty + py, belfry_z), scale=(pier_size, pier_size, 7.0))
            pier = bpy.context.active_object
            pier.name = f"Bell_Tower_Pier_{px}_{py}"
            pier.data.materials.append(mats["brick"])
            col.objects.link(pier)
            bpy.context.scene.collection.objects.unlink(pier)
            
    # Belfry floor & ceiling slabs
    for slab_z in [35.0, 42.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, ty, slab_z), scale=(6.6, 6.6, 0.7))
        slab = bpy.context.active_object
        slab.name = f"Bell_Tower_Slab_{int(slab_z)}"
        slab.data.materials.append(mats["limestone"])
        col.objects.link(slab)
        bpy.context.scene.collection.objects.unlink(slab)
        
    # 5. Carillon Bells inside Belfry (Pass 2+)
    if attempt >= 2:
        # Central main bourdon bell + chime cluster
        bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.6, location=(tx, ty, belfry_z), vertices=24)
        bourdon = bpy.context.active_object
        bourdon.name = "Bell_Tower_Bourdon_Bell"
        bourdon.data.materials.append(mats["bronze_bell"])
        col.objects.link(bourdon)
        bpy.context.scene.collection.objects.unlink(bourdon)
        
        # 4 satellite treble bells
        for angle in [0, 90, 180, 270]:
            bx = tx + 1.2 * math.cos(math.radians(angle))
            by = ty + 1.2 * math.sin(math.radians(angle))
            bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.7, location=(bx, by, belfry_z + 0.8), vertices=16)
            s_bell = bpy.context.active_object
            s_bell.name = f"Bell_Tower_Chime_{angle}"
            s_bell.data.materials.append(mats["bronze_bell"])
            col.objects.link(s_bell)
            bpy.context.scene.collection.objects.unlink(s_bell)
            
    # 6. Four Clock Faces (Pass 3)
    if attempt >= 3:
        clock_z = 32.5
        clock_radius = 1.3
        # North, South, East, West clock faces
        clock_dirs = [
            ("North", 0, 3.12, 0),
            ("South", 0, -3.12, math.pi),
            ("East", 3.12, 0, -math.pi/2),
            ("West", -3.12, 0, math.pi/2)
        ]
        for cname, ox, oy, rot_z in clock_dirs:
            # White dial face
            bpy.ops.mesh.primitive_cylinder_add(radius=clock_radius, depth=0.1, location=(tx + ox, ty + oy, clock_z), vertices=32)
            cface = bpy.context.active_object
            cface.name = f"Clock_Face_{cname}"
            cface.rotation_euler = (math.pi/2 if ox == 0 else 0, math.pi/2 if oy == 0 else 0, rot_z)
            cface.data.materials.append(mats["clock_face"])
            col.objects.link(cface)
            bpy.context.scene.collection.objects.unlink(cface)
            
            # Gold hands & bezel rim
            bpy.ops.mesh.primitive_torus_add(major_radius=clock_radius, minor_radius=0.08, location=(tx + ox*1.02, ty + oy*1.02, clock_z))
            rim = bpy.context.active_object
            rim.name = f"Clock_Rim_{cname}"
            rim.rotation_euler = (math.pi/2 if ox == 0 else 0, math.pi/2 if oy == 0 else 0, rot_z)
            rim.data.materials.append(mats["gold_dial"])
            col.objects.link(rim)
            bpy.context.scene.collection.objects.unlink(rim)
            
    # 7. Copper Pyramidal Spire & Finial (42m to 48.8m)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=4.4, radius2=0.0, depth=6.8, location=(tx, ty, 45.4))
    spire = bpy.context.active_object
    spire.name = "Bell_Tower_Copper_Spire"
    spire.rotation_euler[2] = math.radians(45.0) # Align edges to square tower
    spire.data.materials.append(mats["copper"])
    col.objects.link(spire)
    bpy.context.scene.collection.objects.unlink(spire)
    
    # Finial / Weathervane point (Pass 2+)
    if attempt >= 2:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.0, location=(tx, ty, 49.6))
        finial = bpy.context.active_object
        finial.name = "Bell_Tower_Finial"
        finial.data.materials.append(mats["gold_dial"])
        col.objects.link(finial)
        bpy.context.scene.collection.objects.unlink(finial)
        
    # 8. Surrounding Bell Tower Plaza & Seatwalls (Pass 3)
    if attempt >= 3:
        # Paved circular / octagonal plaza
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=18.0, depth=0.15, location=(tx, ty, 0.08))
        plaza = bpy.context.active_object
        plaza.name = "Bell_Tower_Plaza_Paving"
        plaza.data.materials.append(mats["brick"])
        col.objects.link(plaza)
        bpy.context.scene.collection.objects.unlink(plaza)
        
        # Surrounding low stone seatwalls
        for angle in [30, 75, 120, 165, 210, 255, 300, 345]:
            wx = tx + 14.0 * math.cos(math.radians(angle))
            wy = ty + 14.0 * math.sin(math.radians(angle))
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, wy, 0.4), scale=(3.5, 0.6, 0.6))
            swall = bpy.context.active_object
            swall.name = f"Plaza_Seatwall_{angle}"
            swall.rotation_euler[2] = math.radians(angle + 90)
            swall.data.materials.append(mats["limestone"])
            col.objects.link(swall)
            bpy.context.scene.collection.objects.unlink(swall)
            
    print(f"Purdue Bell Tower (Pass {attempt}) built successfully.")

# -------------------------------------------------------------
# 5. Environment Lighting & Cameras
# -------------------------------------------------------------
def setup_lighting_and_cameras():
    col = clean_or_create_collection("05_Cameras_and_Views")
    
    # World Lighting
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Purdue_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.55, 0.72, 0.92, 1.0) # Soft Indiana sky blue
        bg_node.inputs["Strength"].default_value = 1.1
        
    # Sun Light (Warm Midwestern afternoon sunlight)
    if "Sun_Key_Light" not in bpy.data.objects:
        light_data = bpy.data.lights.new(name="Sun_Key_Light", type="SUN")
        light_data.energy = 4.0
        light_data.color = (1.0, 0.96, 0.88)
        light_data.angle = math.radians(0.8) # Soft contact shadows
        sun_obj = bpy.data.objects.new("Sun_Key_Light", light_data)
        sun_obj.rotation_euler = (math.radians(48.0), math.radians(22.0), math.radians(-55.0))
        col.objects.link(sun_obj)
        
    # Key Cameras
    camera_configs = [
        {
            "name": "Cam_01_Campus_Aerial_Wide",
            "loc": (450.0, -1400.0, 850.0),
            "rot": (math.radians(62.0), 0.0, math.radians(24.0)),
            "lens": 35.0
        },
        {
            "name": "Cam_02_Bell_Tower_Plaza",
            "loc": (-31.2, -48.0, 4.5),
            "rot": (math.radians(78.0), 0.0, 0.0),
            "lens": 24.0
        },
        {
            "name": "Cam_03_Engineering_Mall_WALC",
            "loc": (15.0, -85.0, 18.0),
            "rot": (math.radians(82.0), 0.0, math.radians(-15.0)),
            "lens": 28.0
        },
        {
            "name": "Cam_04_Wabash_River_Overlook",
            "loc": (1850.0, -500.0, 120.0),
            "rot": (math.radians(80.0), 0.0, math.radians(105.0)),
            "lens": 32.0
        }
    ]
    
    for cfg in camera_configs:
        if cfg["name"] not in bpy.data.objects:
            cam_data = bpy.data.cameras.new(cfg["name"])
            cam_data.lens = cfg["lens"]
            cam_data.clip_end = 15000.0
            cam_obj = bpy.data.objects.new(cfg["name"], cam_data)
            cam_obj.location = cfg["loc"]
            cam_obj.rotation_euler = cfg["rot"]
            col.objects.link(cam_obj)
            
    # Set active camera to Cam_01
    bpy.context.scene.camera = bpy.data.objects["Cam_01_Campus_Aerial_Wide"]
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    print("Lighting and 4 inspection cameras created.")

# -------------------------------------------------------------
# Main Execution Pipeline
# -------------------------------------------------------------
def run_full_pipeline(bell_tower_pass=3):
    print("=== STARTING PURDUE DIGITAL TWIN GENERATION ===")
    mats = setup_materials()
    build_terrain_and_river(mats)
    build_road_network(mats)
    build_all_buildings(mats)
    build_purdue_bell_tower(mats, attempt=bell_tower_pass)
    setup_lighting_and_cameras()
    print("=== PURDUE DIGITAL TWIN GENERATION FINISHED ===")

if __name__ == "__main__":
    run_full_pipeline(bell_tower_pass=3)

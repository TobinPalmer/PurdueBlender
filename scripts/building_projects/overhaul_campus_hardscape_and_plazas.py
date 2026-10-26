import bpy
import bmesh
import mathutils
import math
import json
import os

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

def get_or_create_material(name, base_color, roughness=0.7, metallic=0.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat

def overhaul_hardscape():
    print("=== OVERHAULING PURDUE CAMPUS HARDSCAPE, PATH WIDTHS & PLAZAS ===")
    
    col_name = "01_Purdue_Road_Network"
    col = clean_or_create_collection(col_name)
    
    # Materials
    mat_concrete = get_or_create_material("Plaza_Architectural_Concrete", (0.80, 0.78, 0.75, 1.0), roughness=0.68)
    mat_brick = get_or_create_material("Plaza_Purdue_Red_Brick_Pavers", (0.50, 0.22, 0.16, 1.0), roughness=0.82)
    mat_stone = get_or_create_material("Indiana_Bedford_Limestone", (0.85, 0.82, 0.77, 1.0), roughness=0.68)
    mat_turf = get_or_create_material("Manicured_Campus_Lawn", (0.16, 0.36, 0.12, 1.0), roughness=0.92)
    mat_bike = get_or_create_material("Purdue_Bike_Lane_KellyGreen", (0.10, 0.48, 0.22, 1.0), roughness=0.62)
    mat_asphalt = get_or_create_material("Street_Asphalt_Dark", (0.12, 0.12, 0.13, 1.0), roughness=0.88)
    
    # -------------------------------------------------------------
    # 1. Centennial Mall & WALC Grand Pedestrian Plaza (No Sea of Grass!)
    # -------------------------------------------------------------
    # In real life, the entire space between WALC, Bell Tower, EE, and Schleman Hall
    # is a massive continuous brick and concrete paved plaza.
    print("1. Building Centennial Mall & WALC Grand Plaza...")
    
    # Base Concrete Plaza Slab (140m East-West x 130m North-South)
    # Centered between WALC (X=40) and Bell Tower (X=-31)
    bm_walc_plaza = bmesh.new()
    px_min, px_max = -55.0, 85.0
    py_min, py_max = -65.0, 65.0
    pz = 0.10 # Raised above baseline terrain
    
    # Large paved field
    v1 = bm_walc_plaza.verts.new((px_min, py_min, pz))
    v2 = bm_walc_plaza.verts.new((px_max, py_min, pz))
    v3 = bm_walc_plaza.verts.new((px_max, py_max, pz))
    v4 = bm_walc_plaza.verts.new((px_min, py_max, pz))
    bm_walc_plaza.faces.new((v1, v2, v3, v4))
    
    m_wp = bpy.data.meshes.new("Centennial_Mall_WALC_Plaza_Concrete_Base")
    bm_walc_plaza.to_mesh(m_wp)
    bm_walc_plaza.free()
    o_wp = bpy.data.objects.new("Centennial_Mall_WALC_Plaza_Concrete_Base", m_wp)
    m_wp.materials.append(mat_concrete)
    col.objects.link(o_wp)
    
    # Herringbone Red Brick Inlay Apron around WALC entrances & Centennial Mall spine
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(35.0, 0.0, pz + 0.01),
        scale=(55.0, 85.0, 0.02)
    )
    walc_brick_apron = bpy.context.active_object
    walc_brick_apron.name = "WALC_Entrance_Herringbone_Brick_Apron"
    walc_brick_apron.data.materials.append(mat_brick)
    col.objects.link(walc_brick_apron)
    bpy.context.scene.collection.objects.unlink(walc_brick_apron)
    
    # Raised Limestone Planters & Seatwall Terraces around WALC Plaza
    # Rather than wild sprawling grass, green space exists in crisp limestone planter terraces!
    planters = [
        # Terrace 1: South of WALC entrance
        {"x": 15.0, "y": -35.0, "w": 28.0, "d": 12.0},
        # Terrace 2: North of WALC
        {"x": 15.0, "y": 35.0, "w": 28.0, "d": 12.0},
        # Terrace 3: West of WALC along Centennial Mall walkway
        {"x": -10.0, "y": 18.0, "w": 16.0, "d": 18.0},
        # Terrace 4: Southwest corner
        {"x": -10.0, "y": -22.0, "w": 16.0, "d": 18.0}
    ]
    for i, pl in enumerate(planters):
        # Limestone retaining curb (0.45m high)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(pl["x"], pl["y"], pz + 0.25),
            scale=(pl["w"], pl["d"], 0.5)
        )
        curb_obj = bpy.context.active_object
        curb_obj.name = f"WALC_Plaza_Seatwall_Planter_{i+1}"
        curb_obj.data.materials.append(mat_stone)
        col.objects.link(curb_obj)
        bpy.context.scene.collection.objects.unlink(curb_obj)
        
        # Inset manicured turf lawn inside the planter
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(pl["x"], pl["y"], pz + 0.4),
            scale=(pl["w"] - 1.2, pl["d"] - 1.2, 0.2)
        )
        lawn_obj = bpy.context.active_object
        lawn_obj.name = f"WALC_Planter_Manicured_Turf_{i+1}"
        lawn_obj.data.materials.append(mat_turf)
        col.objects.link(lawn_obj)
        bpy.context.scene.collection.objects.unlink(lawn_obj)
        
    # -------------------------------------------------------------
    # 2. Third Street Pedestrian & Bicycle Promenade (Building-to-Building Hardscape)
    # -------------------------------------------------------------
    # Spans from University St all the way past WALC, Wiley Hall, Tarkington, and Co-Rec.
    # Total 18m wide continuous paved hardscape corridor!
    print("2. Building Third Street Student Promenade (Building-to-Building)...")
    
    # Length: X = -650m to +50m (700 meters long!). Y centered at +125.0m
    t3_len = 700.0
    t3_cx = -300.0
    t3_cy = 125.0
    t3_w = 20.0 # 20 meters wide total corridor
    
    # Red Brick Paver Promenade Surface
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(t3_cx, t3_cy, 0.09),
        scale=(t3_len, t3_w, 0.04)
    )
    t3_brick = bpy.context.active_object
    t3_brick.name = "Third_Street_Promenade_Brick_Corridor"
    t3_brick.data.materials.append(mat_brick)
    col.objects.link(t3_brick)
    bpy.context.scene.collection.objects.unlink(t3_brick)
    
    # Center 2-Way Kelly Green Cycle Track (4.2m wide running down the entire promenade!)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(t3_cx, t3_cy, 0.105),
        scale=(t3_len, 4.2, 0.02)
    )
    t3_cycle = bpy.context.active_object
    t3_cycle.name = "Third_Street_Promenade_Center_CycleTrack"
    t3_cycle.data.materials.append(mat_bike)
    col.objects.link(t3_cycle)
    bpy.context.scene.collection.objects.unlink(t3_cycle)
    
    # Flanking Concrete Curbs & Bollards along Third Street
    for side in [-10.1, 10.1]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(t3_cx, t3_cy + side, 0.18),
            scale=(t3_len, 0.35, 0.18)
        )
        t3_curb = bpy.context.active_object
        t3_curb.name = f"Third_Street_Granite_Curb_{'North' if side > 0 else 'South'}"
        t3_curb.data.materials.append(mat_stone)
        col.objects.link(t3_curb)
        bpy.context.scene.collection.objects.unlink(t3_curb)
        
    # -------------------------------------------------------------
    # 3. Engineering Mall Concourse & Symmetrical Four Lawn Quadrants
    # -------------------------------------------------------------
    print("3. Building Engineering Mall Concourse & Quad Turf Panels...")
    
    # Central Mall Concourse: 16m wide concrete promenade from Y = 25m to 365m
    em_len = 340.0
    em_cy = 195.0
    em_w = 16.0
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, em_cy, 0.09),
        scale=(em_w, em_len, 0.04)
    )
    em_conc = bpy.context.active_object
    em_conc.name = "Engineering_Mall_Central_Concourse"
    em_conc.data.materials.append(mat_concrete)
    col.objects.link(em_conc)
    bpy.context.scene.collection.objects.unlink(em_conc)
    
    # Engineering Fountain Grand Circular Plaza (52m diameter paved arena!)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=26.0,
        depth=0.06,
        location=(0.0, 195.0, 0.095),
        vertices=48
    )
    f_arena = bpy.context.active_object
    f_arena.name = "Engineering_Fountain_Grand_Plaza_Arena"
    f_arena.data.materials.append(mat_concrete)
    col.objects.link(f_arena)
    bpy.context.scene.collection.objects.unlink(f_arena)
    
    # Four Symmetrical Sunken Turf Quadrants (The Authentic Engineering Mall Lawns)
    quads = [
        # NW Lawn Panel (between ME and Fountain)
        {"x": -26.0, "y": 265.0, "w": 22.0, "h": 90.0},
        # NE Lawn Panel (between Hampton and Fountain)
        {"x": 26.0, "y": 265.0, "w": 22.0, "h": 90.0},
        # SW Lawn Panel (between ME/Gatewood and Fountain)
        {"x": -26.0, "y": 125.0, "w": 22.0, "h": 90.0},
        # SE Lawn Panel (between MSEE/EE and Fountain)
        {"x": 26.0, "y": 125.0, "w": 22.0, "h": 90.0}
    ]
    for i, q in enumerate(quads):
        # Perimeter Limestone Curb border
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(q["x"], q["y"], 0.16),
            scale=(q["w"] + 0.6, q["h"] + 0.6, 0.14)
        )
        q_border = bpy.context.active_object
        q_border.name = f"Engineering_Mall_Lawn_Curb_{i+1}"
        q_border.data.materials.append(mat_stone)
        col.objects.link(q_border)
        bpy.context.scene.collection.objects.unlink(q_border)
        
        # Manicured Sunken Green Turf
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(q["x"], q["y"], 0.12),
            scale=(q["w"], q["h"], 0.08)
        )
        q_turf = bpy.context.active_object
        q_turf.name = f"Engineering_Mall_Lawn_Turf_{i+1}"
        q_turf.data.materials.append(mat_turf)
        col.objects.link(q_turf)
        bpy.context.scene.collection.objects.unlink(q_turf)
        
    # -------------------------------------------------------------
    # 4. Re-Scale All Walkway Widths (8.0m to 12.0m Promenades)
    # -------------------------------------------------------------
    print("4. Rebuilding all campus walkways with authentic wide multi-modal widths...")
    # Remove older narrow sidewalk object
    if "Purdue_Elevated_Sidewalks" in col.objects:
        obj = col.objects["Purdue_Elevated_Sidewalks"]
        bpy.data.objects.remove(obj, do_unlink=True)
        print("Removed older narrow sidewalk mesh.")
        
    roads_file = os.path.join(DATA_DIR, "purdue_roads.json")
    with open(roads_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in data["elements"] if e["type"] == "node"}
    ways = [e for e in data["elements"] if e["type"] == "way"]
    
    bm_wide_walks = bmesh.new()
    wide_count = 0
    
    for w in ways:
        tags = w.get("tags", {})
        hw = tags.get("highway", "")
        if hw not in ["footway", "path", "pedestrian", "steps"]:
            continue
            
        w_nodes = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
        if len(w_nodes) < 2:
            continue
            
        name = tags.get("name", "").lower()
        pts = [to_xy(lat, lon) for lat, lon in w_nodes]
        
        # Skip if far out of bounds
        if not any(-1400 <= p[0] <= 1800 and -1400 <= p[1] <= 1500 for p in pts):
            continue
            
        # Is this in the core campus? Scale width dramatically!
        is_core = any(-600 <= p[0] <= 300 and -400 <= p[1] <= 450 for p in pts)
        
        if "mall" in name or "promenade" in name or "centennial" in name:
            width = 14.0 # Grand Mall Boulevards
        elif "memorial" in name or is_core:
            width = 8.5  # Core Campus Wide Pedestrian Promenades
        else:
            width = 4.5  # Outer / Residential Sidewalks (not skinny 1.8m!)
            
        half_w = width * 0.5
        z_top = 0.12
        
        prev_l, prev_r = None, None
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
                nx, ny = -dy / l, dx / l
            else:
                nx, ny = 1.0, 0.0
                
            vl = bm_wide_walks.verts.new((px - nx * half_w, py - ny * half_w, z_top))
            vr = bm_wide_walks.verts.new((px + nx * half_w, py + ny * half_w, z_top))
            if prev_l and prev_r:
                bm_wide_walks.faces.new((prev_l, prev_r, vr, vl))
            prev_l, prev_r = vl, vr
        wide_count += 1
        
    m_ww = bpy.data.meshes.new("Purdue_Elevated_Sidewalks_Wide")
    bm_wide_walks.to_mesh(m_ww)
    bm_wide_walks.free()
    o_ww = bpy.data.objects.new("Purdue_Elevated_Sidewalks_Wide", m_ww)
    m_ww.materials.append(mat_concrete)
    col.objects.link(o_ww)
    print(f"Wide pedestrian promenades generated: {wide_count} walkways (widths 4.5m to 14.0m).")
    
    # -------------------------------------------------------------
    # 5. Core Campus Ground Base Mask (Tone down wild green grass)
    # -------------------------------------------------------------
    # Under the academic core (from State St north to Stadium Ave, Russell to Grant),
    # replace the wild rural green terrain with an urban gravel/paved underlayment
    mat_urban_ground = get_or_create_material("Purdue_Urban_Core_Ground", (0.55, 0.58, 0.52, 1.0), roughness=0.95)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(-150.0, 80.0, 0.02),
        scale=(950.0, 850.0, 0.04)
    )
    urban_ground = bpy.context.active_object
    urban_ground.name = "Purdue_Urban_Campus_Underlayment"
    urban_ground.data.materials.append(mat_urban_ground)
    col.objects.link(urban_ground)
    bpy.context.scene.collection.objects.unlink(urban_ground)
    
    print("=== CAMPUS HARDSCAPE & PLAZA OVERHAUL COMPLETE ===")

if __name__ == "__main__":
    overhaul_hardscape()

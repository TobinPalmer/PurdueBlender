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

def setup_street_materials():
    mats = {}
    # Dark textured asphalt
    mats["asphalt"] = get_or_create_material("Street_Asphalt_Dark", (0.12, 0.12, 0.13, 1.0), roughness=0.88)
    # Purdue Signature Kelly Green Bike Lane Epoxy
    mats["bike_green"] = get_or_create_material("Purdue_Bike_Lane_KellyGreen", (0.10, 0.48, 0.22, 1.0), roughness=0.62)
    # Raised Concrete Curb & Gutter
    mats["curb"] = get_or_create_material("Street_Curb_Concrete", (0.78, 0.76, 0.72, 1.0), roughness=0.58)
    # Elevated Sidewalk Concrete
    mats["sidewalk"] = get_or_create_material("Street_Sidewalk_Concrete", (0.75, 0.73, 0.70, 1.0), roughness=0.72)
    # Yellow Road Dividing Stripes
    mats["stripe_yellow"] = get_or_create_material("Road_Stripe_Yellow", (0.92, 0.72, 0.10, 1.0), roughness=0.45)
    # White Traffic Thermoplastic Marking
    mats["stripe_white"] = get_or_create_material("Road_Stripe_White", (0.96, 0.96, 0.96, 1.0), roughness=0.40)
    # Red Brick Paver Accent
    mats["brick_paver"] = get_or_create_material("Sidewalk_Purdue_Brick_Accent", (0.48, 0.20, 0.15, 1.0), roughness=0.82)
    return mats

def build_accurate_roads_and_bike_lanes():
    print("=== STARTING STREET-VIEW ACCURATE ROAD & BIKE LANE MODELING ===")
    mats = setup_street_materials()
    
    col_name = "01_Purdue_Road_Network"
    col = clean_or_create_collection(col_name)
    
    # Remove older flat road objects if present
    for old_name in ["Purdue_Road_Network", "Purdue_Pedestrian_Walkways"]:
        if old_name in col.objects:
            obj = col.objects[old_name]
            bpy.data.objects.remove(obj, do_unlink=True)
            print(f"Removed older flat layer: {old_name}")
            
    roads_file = os.path.join(DATA_DIR, "purdue_roads.json")
    if not os.path.exists(roads_file):
        print(f"Error: {roads_file} not found.")
        return
        
    with open(roads_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in data["elements"] if e["type"] == "node"}
    ways = [e for e in data["elements"] if e["type"] == "way"]
    
    # 4 BMesh Builders for High-Detail Street Layers
    bm_road = bmesh.new()       # Vehicular asphalt
    bm_bike = bmesh.new()       # Dedicated green bike lanes
    bm_curb = bmesh.new()       # 15cm raised concrete curbs
    bm_walk = bmesh.new()       # Raised sidewalks
    bm_stripe = bmesh.new()     # Yellow & white centerline striping
    
    road_count = 0
    bike_count = 0
    curb_count = 0
    walk_count = 0
    
    # Campus Key Corridors (High-detail multi-modal profiles)
    key_bike_streets = [
        "state street", "third street", "3rd street", "northwestern", 
        "stadium avenue", "west stadium avenue", "martin jischke", 
        "grant street", "salisbury", "macarthur", "stadium mall"
    ]
    
    for w in ways:
        tags = w.get("tags", {})
        hw = tags.get("highway", "")
        if not hw:
            continue
            
        w_nodes = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
        if len(w_nodes) < 2:
            continue
            
        name = tags.get("name", "").lower()
        pts = [to_xy(lat, lon) for lat, lon in w_nodes]
        
        # Filter within project bounds (-1600 to +2300, -1600 to +1700)
        if not any(-1600 <= p[0] <= 2300 and -1600 <= p[1] <= 1700 for p in pts):
            continue
            
        # Is this an explicit bike route or signature multi-modal street?
        has_bike_tag = any(k in tags for k in ['cycleway', 'cycleway:left', 'cycleway:right', 'cycleway:both', 'bicycle'])
        is_signature_bike_corridor = any(k in name for k in key_bike_streets) or has_bike_tag
        is_pedestrian = hw in ["footway", "path", "pedestrian", "steps"]
        
        # ---------------------------------------------------------
        # Case A: Pedestrian Walks & Mall Promenades
        # ---------------------------------------------------------
        if is_pedestrian:
            w_width = 3.6 if ("mall" in name or "promenade" in name) else 2.4
            half_w = w_width * 0.5
            z_top = 0.18 # Elevated sidewalk height
            
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
                    
                vl = bm_walk.verts.new((px - nx * half_w, py - ny * half_w, z_top))
                vr = bm_walk.verts.new((px + nx * half_w, py + ny * half_w, z_top))
                if prev_l and prev_r:
                    bm_walk.faces.new((prev_l, prev_r, vr, vl))
                prev_l, prev_r = vl, vr
            walk_count += 1
            continue
            
        # ---------------------------------------------------------
        # Case B: Vehicular Roads & Multi-Modal Corridors
        # ---------------------------------------------------------
        # Dimensions based on Street View & highway classification
        if "third street" in name or "3rd street" in name:
            # Pedestrian & Bike Promenade: 3.6m center green cycle track + 3.0m side brick walkways
            road_w = 0.0 # No cars on central Third St promenade!
            bike_w = 3.8
            walk_w = 3.2
        elif hw in ["primary", "secondary"] or "state street" in name or "northwestern" in name or "stadium" in name:
            road_w = 9.0  # 2 full car lanes
            bike_w = 2.0 if is_signature_bike_corridor else 0.0
            walk_w = 2.8
        elif hw in ["tertiary", "residential"] or is_signature_bike_corridor:
            road_w = 7.5
            bike_w = 1.6 if is_signature_bike_corridor else 0.0
            walk_w = 2.2
        else:
            road_w = 6.4
            bike_w = 0.0
            walk_w = 1.8
            
        z_road = 0.05
        z_bike = 0.07  # Raised slightly over asphalt
        z_curb = 0.20  # 15cm curb height
        curb_w = 0.18
        
        # Build Profile Segments
        prev_pts = None
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
                
            # Cross-section offsets from centerline (0):
            # Centerline (0) -> Road Edge -> Bike Lane -> Curb -> Sidewalk Edge
            r_half = road_w * 0.5
            b_half = r_half + bike_w
            c_half = b_half + curb_w
            w_half = c_half + walk_w
            
            # Vertices for this slice:
            # 1. Vehicular Road (Left to Right)
            if road_w > 0:
                v_r_l = bm_road.verts.new((px - nx * r_half, py - ny * r_half, z_road))
                v_r_r = bm_road.verts.new((px + nx * r_half, py + ny * r_half, z_road))
                # Yellow Centerline Stripe
                v_st_l = bm_stripe.verts.new((px - nx * 0.1, py - ny * 0.1, z_road + 0.008))
                v_st_r = bm_stripe.verts.new((px + nx * 0.1, py + ny * 0.1, z_road + 0.008))
            else:
                v_r_l, v_r_r, v_st_l, v_st_r = None, None, None, None
                
            # 2. Green Bike Lanes (Left & Right Flanks)
            if bike_w > 0:
                if road_w > 0:
                    v_bk_l1 = bm_bike.verts.new((px - nx * r_half, py - ny * r_half, z_bike))
                    v_bk_l2 = bm_bike.verts.new((px - nx * b_half, py - ny * b_half, z_bike))
                    v_bk_r1 = bm_bike.verts.new((px + nx * r_half, py + ny * r_half, z_bike))
                    v_bk_r2 = bm_bike.verts.new((px + nx * b_half, py + ny * b_half, z_bike))
                else:
                    # Pure bike promenade (Third St)
                    v_bk_l1 = bm_bike.verts.new((px - nx * (bike_w*0.5), py - ny * (bike_w*0.5), z_bike))
                    v_bk_l2 = bm_bike.verts.new((px + nx * (bike_w*0.5), py + ny * (bike_w*0.5), z_bike))
                    v_bk_r1, v_bk_r2 = None, None
            else:
                v_bk_l1, v_bk_l2, v_bk_r1, v_bk_r2 = None, None, None, None
                
            # 3. Raised 3D Concrete Curb (Left & Right)
            # Extruded vertical face from z_road to z_curb, then top face
            v_cb_l_bot = bm_curb.verts.new((px - nx * b_half, py - ny * b_half, z_road))
            v_cb_l_top1 = bm_curb.verts.new((px - nx * b_half, py - ny * b_half, z_curb))
            v_cb_l_top2 = bm_curb.verts.new((px - nx * c_half, py - ny * c_half, z_curb))
            
            v_cb_r_bot = bm_curb.verts.new((px + nx * b_half, py + ny * b_half, z_road))
            v_cb_r_top1 = bm_curb.verts.new((px + nx * b_half, py + ny * b_half, z_curb))
            v_cb_r_top2 = bm_curb.verts.new((px + nx * c_half, py + ny * c_half, z_curb))
            
            # 4. Elevated Sidewalk (Left & Right)
            v_wk_l1 = bm_walk.verts.new((px - nx * c_half, py - ny * c_half, z_curb))
            v_wk_l2 = bm_walk.verts.new((px - nx * w_half, py - ny * w_half, z_curb))
            v_wk_r1 = bm_walk.verts.new((px + nx * c_half, py + ny * c_half, z_curb))
            v_wk_r2 = bm_walk.verts.new((px + nx * w_half, py + ny * w_half, z_curb))
            
            curr_pts = {
                "r_l": v_r_l, "r_r": v_r_r, "st_l": v_st_l, "st_r": v_st_r,
                "bk_l1": v_bk_l1, "bk_l2": v_bk_l2, "bk_r1": v_bk_r1, "bk_r2": v_bk_r2,
                "cb_l_bot": v_cb_l_bot, "cb_l_top1": v_cb_l_top1, "cb_l_top2": v_cb_l_top2,
                "cb_r_bot": v_cb_r_bot, "cb_r_top1": v_cb_r_top1, "cb_r_top2": v_cb_r_top2,
                "wk_l1": v_wk_l1, "wk_l2": v_wk_l2, "wk_r1": v_wk_r1, "wk_r2": v_wk_r2
            }
            
            if prev_pts:
                # 1. Road face
                if curr_pts["r_l"] and prev_pts["r_l"]:
                    bm_road.faces.new((prev_pts["r_l"], prev_pts["r_r"], curr_pts["r_r"], curr_pts["r_l"]))
                    bm_stripe.faces.new((prev_pts["st_l"], prev_pts["st_r"], curr_pts["st_r"], curr_pts["st_l"]))
                    
                # 2. Bike lane faces
                if curr_pts["bk_l1"] and prev_pts["bk_l1"]:
                    if curr_pts["bk_r1"]:
                        bm_bike.faces.new((prev_pts["bk_l1"], prev_pts["bk_l2"], curr_pts["bk_l2"], curr_pts["bk_l1"]))
                        bm_bike.faces.new((prev_pts["bk_r1"], prev_pts["bk_r2"], curr_pts["bk_r2"], curr_pts["bk_r1"]))
                    else:
                        bm_bike.faces.new((prev_pts["bk_l1"], prev_pts["bk_l2"], curr_pts["bk_l2"], curr_pts["bk_l1"]))
                        
                # 3. 3D Curb vertical riser & top curb stone
                # Left curb vertical face
                bm_curb.faces.new((prev_pts["cb_l_bot"], prev_pts["cb_l_top1"], curr_pts["cb_l_top1"], curr_pts["cb_l_bot"]))
                # Left curb top surface
                bm_curb.faces.new((prev_pts["cb_l_top1"], prev_pts["cb_l_top2"], curr_pts["cb_l_top2"], curr_pts["cb_l_top1"]))
                # Right curb vertical face
                bm_curb.faces.new((prev_pts["cb_r_bot"], prev_pts["cb_r_top1"], curr_pts["cb_r_top1"], curr_pts["cb_r_bot"]))
                # Right curb top surface
                bm_curb.faces.new((prev_pts["cb_r_top1"], prev_pts["cb_r_top2"], curr_pts["cb_r_top2"], curr_pts["cb_r_top1"]))
                
                # 4. Sidewalk faces
                bm_walk.faces.new((prev_pts["wk_l1"], prev_pts["wk_l2"], curr_pts["wk_l2"], curr_pts["wk_l1"]))
                bm_walk.faces.new((prev_pts["wk_r1"], prev_pts["wk_r2"], curr_pts["wk_r2"], curr_pts["wk_r1"]))
                
            prev_pts = curr_pts
            
        road_count += 1
        if is_signature_bike_corridor:
            bike_count += 1
            
    # -------------------------------------------------------------
    # Commit BMesh Layers to Scene Objects
    # -------------------------------------------------------------
    # Object 1: 3D Asphalt Vehicular Roadbed
    m_road = bpy.data.meshes.new("Purdue_Road_Asphalt_Surface")
    bm_road.to_mesh(m_road)
    bm_road.free()
    o_road = bpy.data.objects.new("Purdue_Road_Asphalt_Surface", m_road)
    m_road.materials.append(mats["asphalt"])
    col.objects.link(o_road)
    
    # Object 2: Purdue Kelly Green Dedicated Bike Lanes
    m_bike = bpy.data.meshes.new("Purdue_Dedicated_Green_Bike_Lanes")
    bm_bike.to_mesh(m_bike)
    bm_bike.free()
    o_bike = bpy.data.objects.new("Purdue_Dedicated_Green_Bike_Lanes", m_bike)
    m_bike.materials.append(mats["bike_green"])
    col.objects.link(o_bike)
    
    # Object 3: 15cm Raised Concrete Curbs
    m_curb = bpy.data.meshes.new("Purdue_Raised_Concrete_Curbs")
    bm_curb.to_mesh(m_curb)
    bm_curb.free()
    o_curb = bpy.data.objects.new("Purdue_Raised_Concrete_Curbs", m_curb)
    m_curb.materials.append(mats["curb"])
    col.objects.link(o_curb)
    
    # Object 4: Elevated Pedestrian Sidewalks
    m_walk = bpy.data.meshes.new("Purdue_Elevated_Sidewalks")
    bm_walk.to_mesh(m_walk)
    bm_walk.free()
    o_walk = bpy.data.objects.new("Purdue_Elevated_Sidewalks", m_walk)
    m_walk.materials.append(mats["sidewalk"])
    col.objects.link(o_walk)
    
    # Object 5: Yellow Centerline Striping
    m_stripe = bpy.data.meshes.new("Purdue_Road_Yellow_Striping")
    bm_stripe.to_mesh(m_stripe)
    bm_stripe.free()
    o_stripe = bpy.data.objects.new("Purdue_Road_Yellow_Striping", m_stripe)
    m_stripe.materials.append(mats["stripe_yellow"])
    col.objects.link(o_stripe)
    
    # -------------------------------------------------------------
    # Intersection Zebra Crosswalks (High-Visibility Continental Bars)
    # -------------------------------------------------------------
    build_major_intersections_and_crosswalks(col, mats)
    
    print(f"Street-view road layers successfully generated:")
    print(f"  Vehicular roads: {road_count} segments")
    print(f"  Dedicated green bike corridors: {bike_count} corridors")
    print(f"  Pedestrian walkways: {walk_count} walkways")

def build_major_intersections_and_crosswalks(col, mats):
    # Key campus intersections from Google Street View
    intersections = [
        # 1. State St & Grant St (Purdue Memorial Union main entrance crosswalk)
        {"name": "Crosswalk_State_and_Grant_PMU", "x": 235.0, "y": -295.0, "angle": 0.0, "bars": 10, "bar_len": 3.2},
        # 2. State St & Sheetz St (Memorial Mall southern gateway)
        {"name": "Crosswalk_State_and_Sheetz_Mall", "x": 50.0, "y": -285.0, "angle": 0.0, "bars": 12, "bar_len": 3.4},
        # 3. State St & University St (Hovde / Stewart Center axis)
        {"name": "Crosswalk_State_and_University", "x": -85.0, "y": -280.0, "angle": 0.0, "bars": 10, "bar_len": 3.2},
        # 4. State St & Russell St (South residences corridor)
        {"name": "Crosswalk_State_and_Russell", "x": -350.0, "y": -275.0, "angle": 0.0, "bars": 10, "bar_len": 3.2},
        # 5. Stadium Ave & Northwestern Ave (Neil Armstrong Hall gateway)
        {"name": "Crosswalk_Stadium_and_Northwestern_ARMS", "x": -108.0, "y": 440.0, "angle": 15.0, "bars": 14, "bar_len": 3.6},
        # 6. Stadium Ave & University St (Cary Quad & Ross-Ade corridor)
        {"name": "Crosswalk_Stadium_and_University_Cary", "x": -270.0, "y": 445.0, "angle": 0.0, "bars": 10, "bar_len": 3.2},
        # 7. Northwestern Ave & Engineering Mall (East gateway)
        {"name": "Crosswalk_Northwestern_EngineeringMall", "x": 125.0, "y": 205.0, "angle": 90.0, "bars": 12, "bar_len": 3.4},
        # 8. Third St & Martin Jischke Dr (Wiley Hall & Co-Rec crossing)
        {"name": "Crosswalk_Third_and_Jischke_Wiley", "x": -510.0, "y": 125.0, "angle": 90.0, "bars": 8, "bar_len": 3.0},
        # 9. Third St & University St (WALC / Bell Tower crossing)
        {"name": "Crosswalk_Third_and_University_WALC", "x": -60.0, "y": 125.0, "angle": 90.0, "bars": 10, "bar_len": 3.2},
        # 10. Third St & Russell St (Honors College & Windsor crossing)
        {"name": "Crosswalk_Third_and_Russell", "x": -350.0, "y": 125.0, "angle": 90.0, "bars": 8, "bar_len": 3.0}
    ]
    
    bm_crosswalk = bmesh.new()
    bar_w = 0.6
    bar_spacing = 1.1
    z_bar = 0.058 # Sits directly on asphalt surface
    
    for inter in intersections:
        ix, iy = inter["x"], inter["y"]
        ang = math.radians(inter["angle"])
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        # Normal vector for bar length
        nx, ny = -sin_a, cos_a
        # Tangent vector for bar step
        tx, ty = cos_a, sin_a
        
        n_bars = inter["bars"]
        bar_len = inter["bar_len"]
        start_offset = -((n_bars - 1) * bar_spacing) * 0.5
        
        for b in range(n_bars):
            offset = start_offset + b * bar_spacing
            bx = ix + tx * offset
            by = iy + ty * offset
            
            # 4 corners of the white continental stripe bar
            hl = bar_len * 0.5
            hw = bar_w * 0.5
            
            c1 = (bx - nx * hl - tx * hw, by - ny * hl - ty * hw, z_bar)
            c2 = (bx + nx * hl - tx * hw, by + ny * hl - ty * hw, z_bar)
            c3 = (bx + nx * hl + tx * hw, by + ny * hl + ty * hw, z_bar)
            c4 = (bx - nx * hl + tx * hw, by - ny * hl + ty * hw, z_bar)
            
            v1 = bm_crosswalk.verts.new(c1)
            v2 = bm_crosswalk.verts.new(c2)
            v3 = bm_crosswalk.verts.new(c3)
            v4 = bm_crosswalk.verts.new(c4)
            bm_crosswalk.faces.new((v1, v2, v3, v4))
            
    m_cw = bpy.data.meshes.new("Purdue_Intersection_Crosswalk_Stripes")
    bm_crosswalk.to_mesh(m_cw)
    bm_crosswalk.free()
    o_cw = bpy.data.objects.new("Purdue_Intersection_Crosswalk_Stripes", m_cw)
    m_cw.materials.append(mats["stripe_white"])
    col.objects.link(o_cw)
    print(f"High-visibility continental crosswalks added at {len(intersections)} key intersections.")

if __name__ == "__main__":
    build_accurate_roads_and_bike_lanes()

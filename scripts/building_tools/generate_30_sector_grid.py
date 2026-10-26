import json
import math
import os

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LAT_TO_M = 111040.0
LON_TO_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))

def to_latlon(x, y):
    lon = ORIGIN_LON + x / LON_TO_M
    lat = ORIGIN_LAT + y / LAT_TO_M
    return lat, lon

def generate_grid():
    # Campus bounds: X from -1600 to +2400 (4000m), Y from -1600 to +1800 (3400m)
    cols = 6
    rows = 5
    min_x, max_x = -1600.0, 2400.0
    min_y, max_y = -1600.0, 1800.0
    dx = (max_x - min_x) / cols # 666.67m
    dy = (max_y - min_y) / rows # 680.0m
    
    col_names = [
        "Far West (Airport & Outer Fields)",
        "Mid West (Residence Halls & Co-Rec)",
        "Central Core (Engineering, Academic & Malls)",
        "East Campus & Chauncey Village",
        "Wabash River & Levee District",
        "East Bank (Lafayette Riverfront)"
    ]
    
    row_names = [
        "North Sector (North West Lafayette Residential)",
        "North-Central Sector (Athletics, Ross-Ade & Mackey)",
        "Central Core (Engineering Mall, WALC & Bell Tower)",
        "South-Central Sector (State St, PMU & Agriculture)",
        "South Sector (Discovery Park & US-231 Bypass)"
    ]
    
    sector_catalog = []
    
    sector_num = 1
    for r in range(rows - 1, -1, -1): # From North (Row 4) down to South (Row 0)
        y1 = min_y + r * dy
        y2 = y1 + dy
        r_label = row_names[4 - r]
        
        for c in range(cols):
            x1 = min_x + c * dx
            x2 = x1 + dx
            c_label = col_names[c]
            
            lat1, lon1 = to_latlon(x1, y1)
            lat2, lon2 = to_latlon(x2, y2)
            
            s_id = f"S_{sector_num:02d}"
            name = f"{r_label} - {c_label}"
            
            # Key landmarks in this sector
            landmarks = []
            if -300 <= (x1+x2)/2 <= 300:
                if 440 <= (y1+y2)/2 <= 1120:
                    landmarks.extend(["Ross-Ade Stadium", "Mackey Arena", "Brees Center", "Mollenkopf Indoor Facility", "Northwestern Ave Strip"])
                elif -240 <= (y1+y2)/2 <= 440:
                    landmarks.extend(["Neil Armstrong Hall (ARMS)", "Purdue Engineering Fountain", "Engineering Mall", "WALC", "Purdue Bell Tower", "MSEE", "EE", "Hampton Hall"])
                elif -920 <= (y1+y2)/2 <= -240:
                    landmarks.extend(["Purdue Memorial Union (PMU)", "Stewart Center", "Hovde Hall", "Memorial Mall", "University Hall", "State Street Multi-Modal Corridor"])
            elif -933 <= (x1+x2)/2 <= -300:
                if -240 <= (y1+y2)/2 <= 440:
                    landmarks.extend(["Wiley Hall & Dining Court", "Third Street Promenade", "Tarkington Hall", "Owen Hall", "Cary Quadrangle", "Co-Rec Sports Center"])
                elif -920 <= (y1+y2)/2 <= -240:
                    landmarks.extend(["Windsor Halls", "Honors College & Residences", "Earhart Hall", "Shreve Hall", "Harrison Hall"])
            elif 400 <= (x1+x2)/2 <= 1100:
                if -920 <= (y1+y2)/2 <= 440:
                    landmarks.extend(["Chauncey Hill Mall", "State Street Levee", "Greek Quad Houses", "Northwestern Commercial Corridor"])
            elif 1100 <= (x1+x2)/2 <= 1800:
                landmarks.extend(["Wabash River Channel", "Wabash Heritage Trail", "Tapawingo Park", "John T. Myers Pedestrian Bridge", "Columbia St Bridge"])
                
            sector_catalog.append({
                "sector_id": s_id,
                "sector_number": sector_num,
                "name": name,
                "grid_col": c + 1,
                "grid_row": r + 1,
                "bounds_xy": {"min_x": round(x1, 1), "max_x": round(x2, 1), "min_y": round(y1, 1), "max_y": round(y2, 1)},
                "bounds_latlon": {
                    "min_lat": round(min(lat1, lat2), 5), "max_lat": round(max(lat1, lat2), 5),
                    "min_lon": round(min(lon1, lon2), 5), "max_lon": round(max(lon1, lon2), 5)
                },
                "key_landmarks": landmarks
            })
            sector_num += 1
            
    manifest = {
        "title": "Purdue University 30-Sector Geospatial & Digital Twin Grid Manifest",
        "grid_dimensions": {"columns": cols, "rows": rows, "total_sectors": len(sector_catalog)},
        "bounding_box_meters": {"width": 4000.0, "height": 3400.0},
        "sectors": sector_catalog
    }
    
    out_path = r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin\purdue_30_sector_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Generated 30-sector manifest: {out_path} ({len(sector_catalog)} sectors).")

if __name__ == "__main__":
    generate_grid()

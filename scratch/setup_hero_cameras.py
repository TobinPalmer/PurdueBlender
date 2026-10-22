import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path('.').resolve()
queue = json.loads((ROOT / 'materials/review/detailed_queue.json').read_text())
extra = [
    {"id": "dudley_hall", "file": "buildings/dudley_hall.blend", "collection": "Asset_dudley_hall"},
    {"id": "lambertus_hall", "file": "buildings/lambertus_hall.blend", "collection": "Asset_lambertus_hall"}
]
all_b = queue + extra

cams = {o.name: o for o in bpy.data.objects if o.type == 'CAMERA'}

# Curated best hero cameras for buildings that have existing cameras
curated_cameras = {
    'armory': 'Cam_87_Armory_UniversitySt_Hero',
    'beering_hall': 'Cam_10_Beering_Hall_North_Cl50_Overlook',
    'bell_tower': 'Cam_01_BellTower_Ground_Hero',
    'class_of_1950': 'Cam_82_CL50_OvalDrive_Hero',
    'elliott_hall_of_music': 'Cam_47_Elliott_Hall_South_StreetView',
    'felix_haas_hall': 'Cam_97_HAAS_East_MemorialSteps_Hero',
    'frieda_parker_hall': 'Cam_42_Frieda_Parker_East_StreetView',
    'hovde_hall': 'Cam_77_Hovde_South_Hero',
    'mackey_arena': 'Cam_62_Mackey_Arena_North_WoodenPlaza_Hero',
    'math_sciences': 'Cam_92_MATH_UniversitySt_Hero',
    'neil_armstrong_hall': 'Cam_57_Neil_Armstrong_North_StreetView',
    'owen_hall': 'Cam_27_Owen_Hall_StadiumAve_StreetView',
    'purdue_memorial_union': 'Cam_67_PMU_StateStreet_South_Hero',
    'ross_ade': 'Cam_36_Ross_Ade_StadiumAve_ExteriorGate',
    'south_hall': 'Cam_11_South_Hall_MacArthur_StreetView',
    'stewart_center': 'Cam_72_Stewart_South_Hero',
    'tarkington_hall': 'Cam_22_Tarkington_Hall_Jischke_StreetView',
    'university_hall': 'Cam_52_University_Hall_East_MemorialMall_StreetView',
    'walc': 'Cam_03_Engineering_Mall_WALC',
    'wiley_hall': 'Cam_07_Wiley_Hall_StreetView',
    'winifred_parker_hall': 'Cam_37_Winifred_Parker_ThirdSt_StreetView',
    'hansen_life_sciences': 'Cam_02_Oblique_East_Perspective',
    'hicks_library': 'Cam_HIKS_02_North_Plaza_Hero',
    'krannert_building': 'Cam_KRAN_02_SW_StateSt_Entrance',
    'lawson_hall': 'Cam_Hero_Perspective',
    'niswonger_aviation_tech': 'Cam_02_Oblique_NorthEast_Aerial',
    'rawls_hall': 'Cam_RAWL_01_North_StateSt',
    'stanley_coulter_hall': 'Cam_SC_02_MemorialMall_East_Hero',
}

assigned = {}

# Check collections / placements for all buildings
cam_col = bpy.data.collections.get('Render_Hero_Cameras')
if not cam_col:
    cam_col = bpy.data.collections.new('Render_Hero_Cameras')
    bpy.context.scene.collection.children.link(cam_col)

for b in all_b:
    b_id = b['id']
    if b_id in curated_cameras and curated_cameras[b_id] in cams:
        assigned[b_id] = curated_cameras[b_id]
        continue
        
    # Check if a placement empty exists
    placement_name = f"Placement_{b_id}"
    placement = bpy.data.objects.get(placement_name)
    
    # Or find objects belonging to this building
    col_name = b.get('collection', f"Asset_{b_id}")
    col = bpy.data.collections.get(col_name)
    
    pos = None
    if placement:
        pos = placement.location.copy()
    elif col and len(col.all_objects) > 0:
        # compute center of collection objects
        pts = [o.matrix_world.translation for o in col.all_objects]
        pos = sum(pts, Vector((0,0,0))) / len(pts)
    else:
        # search for objects by name
        matches = [o for o in bpy.data.objects if b_id in o.name.lower()]
        if matches:
            pts = [o.matrix_world.translation for o in matches]
            pos = sum(pts, Vector((0,0,0))) / len(pts)

    if pos is not None:
        cam_name = f"Cam_Render_{b_id}"
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(cam_name)
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            cam_col.objects.link(cam_obj)
            
        cam_obj.data.lens = 38
        cam_obj.data.clip_end = 2500
        # Position camera at a nice angle: south-east, elevated
        offset = Vector((75, -85, 45))
        cam_pos = pos + offset
        cam_obj.location = cam_pos
        # Aim camera at building center + 10m height
        target = pos + Vector((0, 0, 10))
        direction = target - cam_pos
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        assigned[b_id] = cam_name
    else:
        print(f"WARNING: Could not find position for {b_id}")

print("Camera assignment completed:")
for b_id, cname in assigned.items():
    print(f"  {b_id:<26} -> {cname}")

(ROOT / 'scratch/assigned_cameras.json').write_text(json.dumps(assigned, indent=2))

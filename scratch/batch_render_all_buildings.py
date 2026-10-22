import bpy, sys, os, json, time
from pathlib import Path
from mathutils import Vector

ROOT = Path('.').resolve()
RENDERS_DIR = ROOT / 'renders'
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

queue = json.loads((ROOT / 'materials/review/detailed_queue.json').read_text())
extra = [
    {"id": "dudley_hall", "file": "buildings/dudley_hall.blend", "collection": "Asset_dudley_hall"},
    {"id": "lambertus_hall", "file": "buildings/lambertus_hall.blend", "collection": "Asset_lambertus_hall"}
]
all_b = queue + extra

s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.view_settings.exposure = -0.65
s.eevee.shadow_resolution_scale = 0.25
if hasattr(s.eevee, 'light_threshold'):
    s.eevee.light_threshold = 0.1
opts = {i.identifier for i in s.eevee.bl_rna.properties['shadow_pool_size'].enum_items}
if '512' in opts:
    s.eevee.shadow_pool_size = '512'

s.render.resolution_x = 1600
s.render.resolution_y = 1000
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.eevee.taa_render_samples = 48

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

manifest_file = RENDERS_DIR / 'renders_manifest.json'
manifest = json.loads(manifest_file.read_text()) if manifest_file.exists() else {}

cam_col = bpy.data.collections.get('Render_Hero_Cameras')
if not cam_col:
    cam_col = bpy.data.collections.new('Render_Hero_Cameras')
    bpy.context.scene.collection.children.link(cam_col)

for idx, b in enumerate(all_b):
    b_id = b['id']
    b_dir = RENDERS_DIR / b_id
    b_dir.mkdir(parents=True, exist_ok=True)
    out_file = b_dir / f"{b_id}_render.png"
    
    # Also check if hero file exists from earlier test
    test_hero_file = b_dir / f"{b_id}_campus_hero.png"
    if test_hero_file.exists() and not out_file.exists():
        import shutil
        shutil.copy2(test_hero_file, out_file)
        
    if out_file.exists() and out_file.stat().st_size > 100000:
        print(f"[{idx+1}/{len(all_b)}] Skipping {b_id}, already rendered: {out_file.name}")
        manifest[b_id] = {
            'file': str(out_file.relative_to(ROOT)),
            'size': out_file.stat().st_size,
            'status': 'complete'
        }
        continue
        
    # Determine camera
    cam_name = curated_cameras.get(b_id)
    cam = bpy.data.objects.get(cam_name) if cam_name else None
    
    if not cam:
        # Create a framed camera looking at the building
        placement_name = f"Placement_{b_id}"
        placement = bpy.data.objects.get(placement_name)
        col_name = b.get('collection', f"Asset_{b_id}")
        col = bpy.data.collections.get(col_name)
        
        pos = None
        if placement:
            pos = placement.location.copy()
        elif col and len(col.all_objects) > 0:
            pts = [o.matrix_world.translation for o in col.all_objects]
            pos = sum(pts, Vector((0,0,0))) / len(pts)
        else:
            matches = [o for o in bpy.data.objects if b_id in o.name.lower()]
            if matches:
                pts = [o.matrix_world.translation for o in matches]
                pos = sum(pts, Vector((0,0,0))) / len(pts)
                
        if pos is None:
            pos = Vector((0, 0, 0))
            
        cam_name = f"Cam_Framed_{b_id}"
        cam = bpy.data.objects.get(cam_name)
        if not cam:
            cam_data = bpy.data.cameras.new(cam_name)
            cam = bpy.data.objects.new(cam_name, cam_data)
            cam_col.objects.link(cam)
            
        cam.data.lens = 38
        cam.data.clip_end = 2500
        cam_pos = pos + Vector((70, -80, 40))
        cam.location = cam_pos
        direction = (pos + Vector((0, 0, 10))) - cam_pos
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        
    s.camera = cam
    s.render.filepath = str(out_file)
    print(f"[{idx+1}/{len(all_b)}] Rendering {b_id} using {cam.name} -> {out_file.name}...", flush=True)
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    fsize = out_file.stat().st_size
    print(f"[{idx+1}/{len(all_b)}] Rendered {b_id} in {dt:.1f}s ({fsize/1024:.0f} KB)", flush=True)
    
    manifest[b_id] = {
        'file': str(out_file.relative_to(ROOT)),
        'size': fsize,
        'camera': cam.name,
        'render_time_s': round(dt, 1),
        'status': 'complete'
    }
    manifest_file.write_text(json.dumps(manifest, indent=2))

print("ALL BUILDINGS RENDERED SUCCESSFULLY!", flush=True)

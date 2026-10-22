import bpy, sys, os, json, shutil
from pathlib import Path

ROOT = Path('.').resolve()
sys.path.insert(0, str(ROOT / 'scratch'))
import upgrade_all_building_colors as uabc

queue = json.loads((ROOT / 'materials/review/detailed_queue.json').read_text())
extra = [
    {"id": "dudley_hall", "file": "buildings/dudley_hall.blend", "collection": "Asset_dudley_hall"},
    {"id": "lambertus_hall", "file": "buildings/lambertus_hall.blend", "collection": "Asset_lambertus_hall"}
]
all_b = queue + extra

results = {}

for b in all_b:
    b_id = b['id']
    rel_path = b['file']
    fpath = ROOT / 'modular' / rel_path
    if not fpath.exists():
        print(f"Skipping {b_id}, file not found")
        continue
        
    backup_file = ROOT / 'materials/backups/detailed_buildings' / f"{b_id}_orig.blend"
    if not backup_file.exists():
        shutil.copy2(fpath, backup_file)
        
    bpy.ops.wm.open_mainfile(filepath=str(fpath.resolve()))
    
    col_name = b.get('collection', f"Asset_{b_id}")
    col = bpy.data.collections.get(col_name) or bpy.context.scene.collection
    
    # 1. Enhance all existing materials
    upgraded_mats = 0
    for m in bpy.data.materials:
        if uabc.enhance_material(m):
            upgraded_mats += 1
            
    # 2. Fix unassigned meshes
    fixed_objs = uabc.fix_unassigned_meshes(col)
    
    # Save the updated blend file
    bpy.ops.wm.save_as_mainfile(filepath=str(fpath.resolve()))
    
    results[b_id] = {
        'status': 'updated',
        'materials_enhanced': upgraded_mats,
        'unassigned_fixed': fixed_objs
    }
    print(f"Updated {b_id}: {upgraded_mats} mats enhanced, {fixed_objs} unassigned meshes fixed.")

(ROOT / 'scratch/color_upgrade_report.json').write_text(json.dumps(results, indent=2))
print("All buildings color upgrades completed successfully!")

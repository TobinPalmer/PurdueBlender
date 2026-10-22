import bpy, json
from pathlib import Path

# Load all detailed buildings
queue = json.loads(Path('materials/review/detailed_queue.json').read_text())
b_ids = [item['id'] for item in queue] + ['dudley_hall', 'lambertus_hall']

cams = [o for o in bpy.data.objects if o.type == 'CAMERA']
print(f"Total cameras in master: {len(cams)}")

mapping = {}
for b_id in b_ids:
    mapping[b_id] = []

for c in cams:
    name_lower = c.name.lower()
    matched = False
    for b_id in b_ids:
        # Check matching tokens
        parts = b_id.split('_')
        # Check abbreviations or full name
        abbrs = {
            'class_of_1950': ['cl50', 'class_of_1950'],
            'felix_haas_hall': ['haas', 'felix_haas'],
            'math_sciences': ['math'],
            'purdue_memorial_union': ['pmu', 'memorial_union'],
            'neil_armstrong_hall': ['armstrong', 'neil_armstrong'],
            'elliott_hall_of_music': ['elliott'],
            'hansen_life_sciences': ['hansen'],
            'hicks_library': ['hiks', 'hicks'],
            'krannert_building': ['kran', 'krannert'],
            'lawson_hall': ['lwsn', 'lawson'],
            'niswonger_aviation_tech': ['nisw', 'niswonger'],
            'rawls_hall': ['rawl', 'rawls'],
            'stanley_coulter_hall': ['sc_', 'stanley_coulter', 'coulter'],
            'stewart_center': ['stewart'],
            'university_hall': ['university_hall'],
            'benjamin_harrison_hall': ['harrison'],
            'mccutcheon_hall': ['mccutcheon'],
            'frieda_parker_hall': ['frieda'],
            'winifred_parker_hall': ['winifred'],
            'tarkington_hall': ['tarkington'],
            'owen_hall': ['owen'],
            'wiley_hall': ['wiley'],
            'ross_ade': ['ross_ade', 'rossade'],
            'mackey_arena': ['mackey'],
            'bell_tower': ['belltower', 'bell_tower', 'bell'],
            'beering_hall': ['beering'],
            'armory': ['armory'],
            'hovde_hall': ['hovde'],
            'knoy_hall': ['knoy'],
            'south_hall': ['south_hall'],
            'walc': ['walc'],
            'electrical_engineering': ['electrical_engineering', 'ee_'],
            'mechanical_engineering': ['mechanical_engineering', 'me_'],
            'potter_engineering': ['potter'],
            'dudley_hall': ['dudley'],
            'lambertus_hall': ['lambertus']
        }
        tokens = abbrs.get(b_id, [b_id])
        if any(t in name_lower for t in tokens):
            mapping[b_id].append(c.name)
            matched = True
            break

for b_id, clist in mapping.items():
    print(f"{b_id}: {len(clist)} cameras -> {clist}")

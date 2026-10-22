"""Build an inventory-checked, conservative exterior shell selection index."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
objects = json.loads((ROOT / 'building_objects.json').read_text())
# Collection prefix, ID, official code, name regex, generating evidence, limitation.
specs = [
('01_WALC_', 'walc', 'WALC', r'^(Masonry lower plinth|Brick horizontal spandrels|Brick vertical piers|End brick spandrels|End brick piers|Rear brick bands|Rear brick piers|Clear insulated glazing)$', 'import_walc_from_scratch.py', 'Facade pieces; reconstruct closed perimeter; avoid a hull spanning recessed wings.'),
('01_Wiley_Masonry', 'wiley_hall', 'WILY', r'.*', 'test_wiley_import.py', 'Imported material-joined masonry objects; geometry must be inspected for disconnected interior pieces. Selection is provisional.'),
('09_Mechanical_', 'mechanical_engineering', 'ME', r'^ME_(Historic_Core_Masonry|Gatewood_Wing_Structure)$', 'correct_walc_orientation_and_detail_surroundings.py', 'Gatewood addition must be matched to its official feature separately if coded separately.'),
('10_Potter_', 'potter_engineering', 'POTR', r'^Potter_Center_Masonry_Core$', 'correct_walc_orientation_and_detail_surroundings.py', ''),
('11_Electrical_', 'electrical_engineering', 'EE', r'^EE_Historic_Masonry_Core$', 'correct_walc_orientation_and_detail_surroundings.py', ''),
('12_South_Hall_Exterior', 'south_hall', 'SH', r'^SouthHall_(GroundFloor_Glass_Podium|Residential_Masonry_Core)$', 'build_south_hall_photorealistic.py', 'Skybridge deliberately excluded; review separately.'),
('14_Beering_Hall_Exterior', 'beering_hall', 'BRNG', r'^BRNG_.*(Masonry|Masonry_Drum_Core)$', 'build_beering_hall_photorealistic.py', 'Use union of separate wing and tower outlines, preserving rotunda curvature.'),
('17_Tarkington_Hall_Exterior', 'tarkington_hall', 'TARK', r'^Tark_.*(Brick_Shaft|GF_Wall_[NSEW])$', 'build_tarkington_hall_photorealistic.py', 'Multiple wings: preserve courtyard voids.'),
('20_Owen_Hall_Exterior', 'owen_hall', 'OWEN', r'^Owen_.*(Brick_Shaft|GF_Wall_[NSEW])$', 'build_owen_hall_photorealistic.py', 'Multiple wings: preserve courtyard voids.'),
('23_Ross_Ade_', 'ross_ade_stadium', 'STDM', r'^RossAde_(LowerBowl_.*_Riser_\d+|UpperBowl_.*_Riser_\d+)$', 'build_ross_ade_stadium_photorealistic.py', 'Bowl risers are structural tier outlines, not enclosed wall footprint; compare with STDM family together. Pavilion shell selected additionally below.'),
('27_Winifred_Parker_Hall_Exterior', 'winifred_parker_hall', 'PKRW', r'^Parker_.*MainMass.*$', 'build_winifred_parker_hall_photorealistic.py', 'Inventory retains original EastWing_MainMass alongside subdivided replacements: inspect overlap/duplicates before accepting footprint.'),
('30_Frieda_Parker_Hall_Exterior', 'frieda_parker_hall', 'PKRF', r'^Frieda_(EastWing_Upper_.*|Breezeway_Upper_Bridge|WestWing_Upper|NorthWing_Upper)$', 'build_frieda_parker_hall_photorealistic.py', 'Upper envelope bridges breezeway: distinguish projected overhang from ground-contact outline.'),
('33_Elliott_Hall_of_Music_Exterior', 'elliott_hall_of_music', 'ELLT', r'^ELLT_(Auditorium_Wall_.*|FlyTower_Wall_.*|South_Recessed_Wall_Top)$', 'build_elliott_hall_v2.py', 'Thin walls need perimeter reconstruction; do not compare wall-strip area directly.'),
('36_University_Hall_Exterior', 'university_hall', 'UNIV', r'^UNIV_(Wall_.*|Tower_Brick_Shaft)$', 'build_university_hall_photorealistic.py', 'Thin walls need perimeter reconstruction.'),
('39_Neil_Armstrong_Hall_Exterior', 'neil_armstrong_hall', 'ARMS', r'^ARMS_(East_Wall_.*|West_Wall_.*|Atrium_South_Wall)$', 'build_neil_armstrong_hall_photorealistic.py', 'Atrium glazing boundary needs additional inspection; selected walls alone may not close courtyard boundaries.'),
('42_Mackey_Arena_Exterior', 'mackey_arena', 'MACK', r'^MACK_(Exterior_Lower_Brick_Wall|Exterior_Concourse_Glass|North_Pavilion_Vestibule)$', 'build_mackey_arena_photorealistic.py', 'Official MACK includes irregular associated envelope; circular arena alone cannot match entire polygon.'),
('45_Purdue_Memorial_Union_Exterior', 'purdue_memorial_union', 'PMU', r'^PMU_(Wall_.*|Tower_Wall_.*|EastWing_Wall_.*|WestWing_Wall_.*)$', 'build_purdue_memorial_union.py', 'Multiple wings/courtyard: reconstruct connected boundary rather than convex hull.'),
('48_Stewart_Center_Exterior', 'stewart_center', 'STEW', r'^STEW_(Ext_Wall_.*|Portico_Back_Wall|Portico_Side_Wall_.*)$', 'build_stewart_center.py', 'Portico recess and entrance gaps require perimeter reconstruction.'),
('51_Hovde_Hall_Exterior', 'hovde_hall', 'HOVD', r'^HOVD_Wall_.*$', 'build_hovde_hall.py', 'Portico columns excluded from main wall envelope; official outline may include portico.'),
('54_Class_of_1950_Exterior', 'class_of_1950', 'CL50', r'^CL50_(Wall_.*|CurtainWall_East|Entrance_Glass_Wall)$', 'build_class_of_1950.py', 'Colonnade excluded from enclosed-wall boundary; review official definition.'),
('57_Armory_Exterior', 'armory', 'AR', r'^Armory_(Wall_.*|Tower_Shaft_.*)$', 'build_purdue_armory.py', 'Corner towers must be included; steps and cheek walls excluded.'),
('60_Math_Sciences_Exterior', 'math_sciences', 'MATH', r'^MATH_(Corner_Tower_.*_Brick|End_Wall_.*_Brick|Ground_Curtain_.*|Spandrel_.*|Ribbon_Glass_.*)$', 'build_math_building_attempt2.py', 'Upper shell overhangs pilotis; distinguish projected envelope from ground-contact outline.'),
('63_Felix_Haas_Hall_Exterior', 'felix_haas_hall', 'HAAS', r'^HAAS_Brick_Wall_.*$', 'build_haas_hall.py', 'Entrance pavilion excluded from main rectangular walls; compare it separately if official polygon includes it.'),
('04_Purdue_Bell_Tower_Detailed', 'bell_tower', None, r'^Bell_Tower_(Brick_Shaft_Upper|GroundPier_.*)$', 'upgrade_bell_tower_pass4.py', 'Open tower, no standard enclosed ground footprint. Ground piers and upper shaft are distinct envelope definitions.'),
]
rows = []
for prefix, group, code, pattern, script, limit in specs:
    selected = [o['name'] for o in objects if o['type'] == 'MESH' and any(c.startswith(prefix) for c in o['collections']) and re.fullmatch(pattern, o['name'])]
    if group == 'ross_ade_stadium':
        selected += [o['name'] for o in objects if o['name'] == 'RossAde_WestPavilion_MainMass']
    assert selected, group
    rows.append(dict(group_id=group, official_codes=[code] if code else [], collection_prefix=prefix, object_names=selected, name_regex=pattern, evidence_script=script, selection_reason='Only named structural exterior walls, masonry masses, or explicit exterior glazing; site paving, furniture, roofs, landscaping, signage and interior collections excluded.', limitations=limit or 'Principal exterior mass only; validate exact boundary using evaluated mesh.', review_status='candidate shell selected; geometry comparison still required'))
out = dict(schema_version=1, inventory='building_objects.json', reference='audit/official_building_references.json', extraction_warning='Object selections are not certified ground footprints. Extract evaluated world-space structural perimeter. Wall strips need enclosed-boundary reconstruction; do not union thin-wall area or convex-hull entire site. Preserve courtyards and curved boundaries. No AABB-derived correction is authorized by this index.', buildings=rows)
(ROOT / 'audit/shell_selectors.json').write_text(json.dumps(out, indent=2)+'\n')
print([(r['group_id'], len(r['object_names'])) for r in rows])


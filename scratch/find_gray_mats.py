import json

data = json.load(open('scratch/building_materials_summary.json'))
gray_mats = []
for b_id, b_info in data.items():
    for m_name, m_data in b_info['materials'].items():
        base = m_data.get('base_color')
        if base:
            r, g, b = base[0], base[1], base[2]
            # check if default gray ~0.8 and not pbr_image
            if abs(r - 0.8) < 0.02 and abs(g - 0.8) < 0.02 and abs(b - 0.8) < 0.02 and not m_data.get('has_pbr_image'):
                gray_mats.append((b_id, m_name, base))

print(f"Found {len(gray_mats)} default gray materials across buildings:")
for b_id, m_name, base in gray_mats:
    print(f"  {b_id} -> {m_name}")

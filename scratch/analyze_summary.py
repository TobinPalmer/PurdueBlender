import json

data = json.load(open('scratch/building_materials_summary.json'))
for b_id, b_info in data.items():
    has_pbr = any(m.get('has_pbr_image') for m in b_info['materials'].values())
    has_bump = any(m.get('has_bump') for m in b_info['materials'].values())
    mats = list(b_info['materials'].keys())
    print(f"[{b_id}] (objs: {b_info['object_count']}, mats: {b_info['total_materials']}, pbr_img: {has_pbr}, bump: {has_bump}):")
    for m_name, m_data in b_info['materials'].items():
        base = m_data.get('base_color')
        if base:
            base_str = f"({base[0]:.2f}, {base[1]:.2f}, {base[2]:.2f})"
        else:
            base_str = "None"
        pbr_str = " [PBR_TEX]" if m_data.get('has_pbr_image') else (" [BUMP]" if m_data.get('has_bump') else "")
        print(f"   - {m_name}: col={base_str}{pbr_str}")

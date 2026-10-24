import json
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
audit = ROOT / 'audit/complete_knoy'
evidence = json.loads((audit / 'evidence_round20.json').read_text(encoding='utf-8'))
evidence['revision'] = 21
evidence['scope'] = 'R21 adds an official 2019 emergency-plan cross-check for named basement levels and room references. No building geometry, materials, transforms, or placement changed.'
evidence['interior_level_source_check_r21'] = {
    'title': 'Knoy Hall Condensed Building Emergency Plan',
    'provider': 'Purdue Polytechnic Institute / Purdue University',
    'url': 'https://polytechnic.purdue.edu/sites/default/files/files/BEP%20March%2015%202019.pdf',
    'source_date': 'Revised 2019-03-14',
    'retrieved': '2026-10-24',
    'feature_identifier': 'Knoy Hall (KNOY)',
    'source_crs': 'Not spatially referenced; operational emergency plan, not a measured floor plan.',
    'verified_text': [
        '2019 plan distinguishes lower-basement shelter areas for Administration/Business Office/CMT/ECN and upper-basement areas for CGT/CIT/SOET.',
        'Plan lists room references KNOY G-011 and KNOY 457.'
    ],
    'model_comparison': {
        'existing_asset_object': 'KNOY_FloorSlab_Basement',
        'local_frame_z_bounds_m': [-6.706, -6.406],
        'observation': 'The asset has one schematic basement slab object. The emergency plan supports named upper and lower basement areas, but cannot assign either to this slab or establish whether/where a second slab should exist.',
        'geometry_change': False
    },
    'what_it_does_not_support': [
        'Plan boundaries or room locations for either basement level.',
        'Slab elevations or registration into the local Blender frame.',
        'Stair/elevator placement, dimensions, connectivity, accessibility, or route continuity.',
        'Any new basement partition or circulation geometry.'
    ],
    'actionable_gap': 'The single modeled basement slab cannot yet be reconciled with the operational upper/lower basement distinction. Obtain a suitable authorized plan before adding or repositioning geometry.'
}
evidence['geometry_change'] = False
evidence['new_source_search_r21'] = {
    'review_date': '2026-10-24',
    'result': 'Targeted official-source search found no public calibrated Knoy elevation/window schedule, roof plan, or measured basement circulation plan. The public emergency plan adds non-spatial evidence only.',
    'additional_leads': [
        {
            'title': 'UA 62 Office of Marketing and Media photographs finding aid',
            'provider': 'Purdue University Archives and Special Collections',
            'url': 'https://archives.lib.purdue.edu/fa/UA62_Series3.pdf',
            'finding': 'Search index describes 1985 Knoy/New Technology Building construction images and a rendering, plus images of the newly opened building from 1989. The finding aid does not supply calibrated, face-identified image files.',
            'use': 'Archive retrieval lead only; not used for geometry.'
        },
        {
            'title': 'Berglund Project Overview and Plans (third-party student project reproduction)',
            'url': 'https://www.scribd.com/document/455649939/document',
            'finding': 'Search result excerpt exposes claimed elevation/window/roof-plan sheet labels and a complete construction-sheet list, but provenance and as-built relationship are not established.',
            'use': 'Not treated as authoritative; do not use to change geometry. Seek original plans through authorized Purdue facilities/archive channels.'
        }
    ]
}
(audit / 'evidence_round21.json').write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('Wrote', audit / 'evidence_round21.json')

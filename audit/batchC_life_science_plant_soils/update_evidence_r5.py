import json
from pathlib import Path
p=Path('audit/batchC_life_science_plant_soils_evidence.json')
d=json.loads(p.read_text(encoding='utf-8'))
d['modeled_features'].append('R5: added one combined shallow dark-metal frame/transom mesh across 76 existing facade glazing panels. The frame detail is a generic architectural readability refinement, not measured from the qualitative Street View; no facade dimensions are asserted.')
d['validation'].update({'saved':True,'asset_object_count':641,'mesh_object_count':639,'materials':19,'cold_room_proxy_count':1,'legacy_small_cold_room_boxes_remaining':0,'window_frame_mesh_count':1,'framed_glazing_panel_count':76,'render_preview':'audit/batchC_life_science_plant_soils/exterior_west_r5.png','roof_preview':'audit/batchC_life_science_plant_soils/roof_top_r5.png','basement_preview':'audit/batchC_life_science_plant_soils/basement_cutaway_r5.png'})
d['specific_evidence_boundary'] += ' R5 adds a combined, schematic dark-metal frame/transom detail over 76 existing glazing panels to improve facade depth/readability. Frame widths, divisions, and locations are not measured or source-confirmed.'
d['uncertainties'].append('R5 window frame/transom details are generic visual cues; the available 2019 Street View does not resolve dimensions or exact divisions.')
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')

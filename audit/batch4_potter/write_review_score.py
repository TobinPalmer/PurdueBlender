import json
from pathlib import Path
p=Path('audit/batch4_potter/independent_review_round4_scorecard.json')
data={
  'asset':'modular/buildings/potter_engineering.blend',
  'review':'independent_review_round4',
  'date':'2026-10-23',
  'overall':6.9,
  'previous_round':6.7,
  'categories':{
    'footprint_placement_massing':7.0,
    'exterior_form_facade_fidelity':5.8,
    'materials_surface_detail':6.8,
    'interior_completeness_circulation':5.2,
    'architectural_details_rooftop':6.8,
    'technical_health_modular_export':9.0,
    'evidence_source_discipline':8.2
  },
  'verified':{
    'fresh_blender_reopen':True,
    'blender_version':'5.2.3 LTS',
    'collection':'Asset_potter_engineering',
    'object_count':503,
    'root_origin':[0.0,0.0,0.0],
    'structural_shell_xy_m':[58.4515,67.4320],
    'structural_shell_height_m':13.4112,
    'stair_flight_objects':10,
    'basement_start_landings':3,
    '4S04_enclosure_parts':6,
    'roof_apertures_center_ray':[True,True,False],
    'roof_openings_center_ray_blocked_by_slab':[True,True,False],
    'unsupported_S01_S02_roof_stairs_removed':True,
    'basement_route_grounded':False,
    'basement_landing_gap_to_lowest_flight_bbox_m':0.3425,
    'basement_corridor_or_door_connection':False,
    'missing_external_images':[],
    'report_updated_for_round4':True,
    'current_exterior_render_after_round4':False,
    'roof_profile':'Historic-plan-based T-shaped Room401 mass and 4S04 opening; broad roof remains unverified and visually featureless',
    'architectural_or_code_compliance_claimed':False
  },
  'highest_impact_fixes':[
    'Resolve and document the basement connection from source plan labels/geometry; current landing is not joined to the lowest flight (about 0.34 m plan gap from object bounds) and no corridor or doorway is modeled.',
    'Check all stair-flight/landing interfaces and full opening clearances, then provide a cutaway that includes the surrounding floor and corridors rather than isolated cropped slab pieces.',
    'Recheck the 4S04 enclosure doorway against the Room401 penthouse footprint; current estimate does not demonstrate a clear physical route into the penthouse.',
    'Render the round-4 saved roof to current evidence, and use current, orientation-known roof/elevation references before adding roof equipment or face-specific entrance details.',
    'Reduce facade repetition and replace raster-derived partition fragments with verified/current room layouts where sources permit.'
  ]
}
p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

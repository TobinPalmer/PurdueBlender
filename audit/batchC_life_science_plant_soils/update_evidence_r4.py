import json
from pathlib import Path
p=Path('audit/batchC_life_science_plant_soils_evidence.json'); d=json.loads(p.read_text(encoding='utf-8'))
# Append the retrievable Purdue facilities report, which supersedes the inaccessible 2021 PDF for inventory facts.
d['references'].append({'provider':'Purdue University Department of Agronomy, Background Information: Facilities & Equipment (PDF, page 30)','url':'https://www.agry.purdue.edu/csrees/bg-facilities.pdf','accessed':'2026-10-24','use':'Primary source for LSPS program: fifteen large sample dryers, four grinding units with dust arresters, 1,163 sq ft (108.05 m2) basement walk-in climate-controlled seed-storage room completed 2004, and 790 sq ft additional long-term seed-storage installation started fall 2008. Exact room dimensions/positions and later completion/status are not supplied.'})
d['vertical_geometry']['basement_status']='Two schematic below-grade plates added using official GIS fields B=-12 and SB=-24 as approximate 12-foot intervals; field units are undocumented. One 1,163 sq ft seed-room volume is represented at the modeled B level because the report says basement but does not specify sublevel. Its square proportions, location, entrance/circulation and exact B/SB assignment are schematic; the surface GIS outline is reused only as a diagrammatic plate.'
d['references']=[r for r in d['references'] if r.get('provider')!='Purdue University, Department of Agronomy, 5-year report (2021)'] + [r for r in d['references'] if r.get('provider')=='Purdue University, Department of Agronomy, 5-year report (2021)']
for r in d['references']:
 if r.get('provider')=='Purdue University, Department of Agronomy, 5-year report (2021)':
  r['use']='Supplemental source indexed for 2021 use/cold-storage context. Direct PDF retrieval returned 404 during R4; inventory counts are instead supported by the accessible Purdue Background Information report.'
d['modeled_features'].extend([
 'R4: removed all four inherited rooftop mechanical curb boxes because three extended outside the GIS roof outline; retained eight low-profile source-informed service-unit proxies entirely on the broad roof, with count and exact positions still illustrative.',
 'R4: replaced five unsupported small basement cold-room boxes with one walk-in climate-controlled seed-storage room whose reported area is 1,163 sq ft (108.05 m²), based on Purdue Agronomy Facilities & Equipment. Its square plan proportions/position and modeled B-level assignment are schematic; the source confirms basement location only.',
 'R4: added an internal shelving arrangement and open central aisle inside the walk-in seed room as a cutaway illustration; detailed circulation, door placement, equipment type/count and room orientation remain unverified.',
 'R4: facade and greenhouse glazing darkened to a more reflective gray-green cue from qualitative 2019 Street View; optical parameters are visual estimates, not measured material properties.'
])
d['specific_evidence_boundary'] += ' R4 corrects the four inherited roof curb elements that protruded beyond the selected GIS roof ring. Purdue Agronomy Facilities & Equipment (page 30) supports 15 sample dryers, four soil grinding units and dust arresters, and a 1,163 sq ft climate-controlled walk-in seed-storage room in the basement. R4 represents that reported area, but uses schematic proportions, position and a tentative B-level assignment because neither sublevel nor plans are specified. A further 790 sq ft seed-storage installation began in fall 2008; current status/location are unclear and it is not modeled.'
d['validation'].update({
 'render_preview':'audit/batchC_life_science_plant_soils/exterior_west_r4.png',
 'roof_preview':'audit/batchC_life_science_plant_soils/roof_top_r4.png',
 'basement_preview':'audit/batchC_life_science_plant_soils/basement_cutaway_r4.png',
 'asset_object_count':640,'mesh_object_count':638,'interior_object_count':160,'materials':19,
 'below_grade_floor_count':2,'basement_walk_in_seed_storage_room_count':1,'reported_seed_room_area_sqft':1163,'reported_seed_room_area_m2':108.05,
 'roof_service_unit_proxy_count':8,'unsupported_rooftop_curbs_remaining':0,
 'sample_dryer_count':15,'soil_grinder_with_dust_arrester_count':4,
 'master_or_manifest_edited':False
})
d['uncertainties']=[u for u in d.get('uncertainties',[]) if 'The 2023 Indiana orthophoto' not in u and 'Dryer and grinder positions' not in u and 'current inventory' not in u]
d['uncertainties'].extend([
 'The 2023 Indiana orthophoto shows rooftop service equipment generally but not its exact count or type. Eight roof-unit proxies are illustrative; the four previously out-of-footprint inherited curb boxes were removed.',
 'The accessible Purdue Background Information report supports the dryer/grinder quantities and a 1,163 sq ft basement walk-in climate room. Exact room dimensions, position, entrance, circulation and B/SB sublevel are not provided; those are schematic.',
 'The same report notes an additional 790 sq ft long-term seed-storage installation began in fall 2008, but its present completion/status and location are unknown; it is omitted.',
 'Purdue vertical GIS values remain ambiguous: modeled above-grade datums are about 9 ft apart while F01-F04 differ by 12 undocumented units; no facade elevation or floor section has resolved the discrepancy.'
])
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')

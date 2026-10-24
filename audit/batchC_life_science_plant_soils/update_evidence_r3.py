import json, math
from pathlib import Path
p=Path('audit/batchC_life_science_plant_soils_evidence.json')
d=json.loads(p.read_text(encoding='utf-8'))
d['vertical_geometry'].update({
 'GIS_level_fields': {'SB':-24,'B':-12,'G':0,'F01':0,'F02':12,'F03':24,'F04':36,'Extrution':36,'NUM_LEVELS':4,'Elevation':621.4},
 'status':'Estimated only. The GIS schema does not document units or the semantics of Extrution/F01-F04/SB/B. The 12-unit F-level intervals are consistent with feet but do not prove feet. The 36-unit Extrution and 4-level count are not a surveyed roof elevation.',
 'model_floor_spacing_m':2.743,
 'model_floor_spacing_note':'Existing above-grade datums are approximately 9 ft apart, while GIS F01-F04 fields differ by 12 units. This discrepancy is unresolved; floor datums, wall height, and roof elevation remain estimated.',
 'basement_status':'Two schematic below-grade plates added using B=-12 and SB=-24 as approximate 12-foot intervals. Units and basement footprint/wall extents are unverified; plates reuse the surface GIS polygon as a diagrammatic outline.'
})
d['references'].extend([
 {'provider':'Indiana Geographic Information Office / Indiana Current Imagery ImageServer','url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer','accessed':'2026-10-24','image_date':'2023 (catalog identify at building location)','pixel_size':'06 in. / 0.1524 m nominal','source_crs':'EPSG:3857 (WKID 102100)','query_url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer/identify?geometry=-9675748%2C4927632&geometryType=esriGeometryPoint&sr=3857&returnGeometry=false&returnCatalogItems=true&f=pjson','local_image':'audit/batchC_life_science_plant_soils/indiana_current_orthophoto_2022_2025.jpg','overlay_image':'audit/batchC_life_science_plant_soils/orthophoto_gis_overlay.png','use':'Independent overhead check. The Purdue GIS ring overlays the visible roof outline with close visual agreement and confirms the long-axis orientation, local placement, flat/light roof, and several small roof-mounted service units. Overlay is a visual comparison on orthorectified imagery; imagery and GIS are not survey control.'},
 {'provider':'Purdue University Department of Agronomy — Research Facilities','url':'https://ag.purdue.edu/department/agry/research/research-facilities.html','accessed':'2026-10-24','use':'States that Life Science Ranges greenhouse facilities are attached to the Plant and Soils Building; verifies a greenhouse connection as a program/context cue but not exact geometry or facade dimensions.'},
 {'provider':'Google Maps place listing for Life Science Plant and Soils Laboratory','url':'https://www.google.com/maps/place/Life+Science+Plant+and+Soils+Laboratory/@40.4231921,-86.9194291,163m/data=!3m2!1e3!4b1!4m6!3m5!1s0x8812e2b71ec32175:0x2dbc13bf851d0609!8m2!3d40.4231921!4d-86.9187854!16s%2Fg%2F11cnb8bwrl?entry=ttu','accessed':'2026-10-24','coordinate':'40.4231921, -86.9187854','use':'POI coordinate is about 4.56 m west and 0.85 m south of the GIS footprint bounding-box midpoint after project conversion; useful as a location plausibility check only, not a surveyed entrance/control point.'}
])
d['modeled_features'].extend([
 'R3: added eight low-profile roof service-unit proxies distributed over the broad flat roof using visual positions from the 2023 Indiana GIO orthophoto; exact equipment count, type, and position are not verified.',
 'R3: added schematic B and SB basement floor plates and cold-room enclosure proxies. Purdue GIS records B=-12 and SB=-24, and the 2021 Agronomy report describes basement cold storage; unit semantics, extents, room count, dimensions, and locations remain unverified.',
 'R3: the GIS-to-orthophoto overlay confirms the 12-vertex outline aligns closely with the visible roof perimeter and its long axis. The manifest marker XY matches the evidence-recommended transformed GIS bbox midpoint; external geographic registration remains approximate, not survey-grade.',
 'R3: expanded procedural materials to 19 unique export materials.'
])
d['specific_evidence_boundary'] += ' The Indiana GIO 2023 orthophoto provides a current, orthorectified roof/perimeter and orientation cross-check; overlay agreement is visual and not survey control. The Google place coordinate is a POI, not a surveyed control. GIS level fields SB/B/F01-F04 and Extrution have undocumented units/semantics; model heights and floor datums remain estimates, including the unresolved 9-foot model versus 12-unit GIS interval difference. Basement rooms and rooftop unit layout are schematic proxies.'
d['validation'].update({
 'render_preview':'audit/batchC_life_science_plant_soils/exterior_west_r3.png',
 'roof_preview':'audit/batchC_life_science_plant_soils/roof_top_r3.png',
 'basement_preview':'audit/batchC_life_science_plant_soils/basement_cutaway_r3.png',
 'asset_object_count':613,'mesh_object_count':611,'interior_object_count':129,'materials':19,
 'below_grade_floor_count':2,'roof_service_unit_proxy_count':8,
 'cold_room_proxy_count':5,
 'floorplate_geometry':'Six ground/upper/basement plates match the transformed 12-vertex GIS ring within 0.00001 m in local coordinates; basement reuse of surface footprint is schematic.',
 'independent_orthophoto_check':'Visual GIS-ring overlay on Indiana GIO 2023 Tippecanoe County orthophoto; close roof-outline and orientation match; not survey-grade.',
 'master_marker_check':'manifest marker [-426.819, -466.398] m matches recommended transformed GIS bbox midpoint within 1 mm; master was read-only and unchanged.',
 'master_or_manifest_edited':False
})
# Reconcile stale references and make uncertainty explicit.
d['uncertainties']=[u for u in d.get('uncertainties',[]) if 'current Street View imagery was not independently captured' not in u and 'Basement cold-storage rooms described' not in u and 'Heights are interpreted' not in u and 'GIS horizontal footprint is a good source' not in u]
d['uncertainties'].extend([
 'GIS horizontal footprint is a strong plan source; Indiana orthophoto overlay visually confirms the roof perimeter/orientation, but no surveyed control point has verified the local projection or master placement to a stated tolerance.',
 'Google Maps POI coordinate is approximate and may mark the place/building centroid or entrance vicinity; it is not survey control.',
 'GIS Extrution, Elevation, SB, B, and F01-F04 units/semantics are undocumented. The modeled 9-foot above-grade datums conflict with 12-unit GIS intervals; height and floor elevations remain unresolved estimates.',
 'The 2023 Indiana orthophoto shows roof equipment generally but cannot establish exact equipment type/count. Eight proxy units are illustrative.',
 'August 2019 Street View is historical, perspective-distorted, and only partially exposes the exterior. It supports qualitative material cues, not dimensions or all elevations.',
 'Dryer/grinder positions and basement cold-room room layouts are schematic. Purdue sources support uses/counts, not modeled room locations or current inventory.',
 'The 2021 report is indexed at the cited Purdue URL but direct PDF retrieval returned 404 in this pass; a separately found legacy Appendix-D.pdf is a general Agronomy review document, not LSPS floor plans.'
])
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')

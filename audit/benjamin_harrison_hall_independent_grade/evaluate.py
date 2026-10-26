from pathlib import Path
import json, math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROBE=json.loads((HERE/"blender_probe.json").read_text(encoding="utf-8"))
MEASURE=json.loads((HERE/"structural_object_measurements.json").read_text(encoding="utf-8"))
GIS=json.loads((ROOT/"audit/official_building_references.json").read_text(encoding="utf-8"))
source=next(b for b in GIS["buildings"] if b["code"]=="HARR")
plinth=next(o for o in MEASURE if o["name"]=="HARR_Ground_Plinth_Base")
origin=PROBE["placement"]["manifest_origin_xy_m"]
source_ring=[[float(x-origin[0]),float(y-origin[1])] for x,y in source["rings_xy_m"][0]][:-1]
model_ring=plinth["base_xy"]
def directed_vertex_error(a,b): return max(min(math.dist(p,q) for q in b) for p in a)
source_to_model=directed_vertex_error(source_ring,model_ring)
model_to_source=directed_vertex_error(model_ring,source_ring)
source_bounds=PROBE["source_polygon_local_bounds_m"]
model_bounds=PROBE["structural_bounds_local_m"][:2]
bounds_error=[abs(model_bounds[i][j]-source_bounds[i][j]) for i in range(2) for j in range(2)]
size=[source["aabb_xy_m"][2]-source["aabb_xy_m"][0],source["aabb_xy_m"][3]-source["aabb_xy_m"][1]]
source_angle=source["minimum_rotated_rectangle"]["angle_degrees_east_ccw"]

criteria=[
 {"criterion":"Correct identity and source-backed footprint","score":2.0,"max_score":2.0,
  "evidence":[f"Official Purdue campus-map ArcGIS feature {source['fid']} is code HARR, named {source['name']}.",f"The saved GIS ring has {len(source_ring)} distinct vertices; the Blender asset's HARR_Ground_Plinth_Base has {len(model_ring)} base vertices.",f"Vertex comparison after applying the manifest local-frame offset: max source-to-model {source_to_model:.6f} m; max model-to-source {model_to_source:.6f} m.","The hero/top-down renders show the three-wing residence-hall arrangement described in Purdue's current emergency plan."],
  "findings":["The GIS record is an official campus-map polygon, not a certified survey; it verifies horizontal shape and identity rather than facade or vertical geometry."]},
 {"criterion":"Position, orientation, and scale/dimensions","score":2.0,"max_score":2.0,
  "evidence":[f"Model structural bounds and source GIS local bounds differ by at most {max(bounds_error):.6f} m on any side.",f"Source GIS AABB measures {size[0]:.3f} x {size[1]:.3f} m; model base plinth spans {model_bounds[0][1]-model_bounds[0][0]:.3f} x {model_bounds[1][1]-model_bounds[1][0]:.3f} m.",f"GIS minimum rotated rectangle angle is {source_angle:.3f} degrees; model perimeter is aligned to the same campus axes.",f"The saved local geometry and manifest placement origin are consistent; source centroid minus manifest origin is {PROBE['placement']['source_center_minus_origin_m']} m, while the exact perimeter was compared in that local frame."]},
 {"criterion":"Evidence-backed height, floors, and roof form","score":1.5,"max_score":2.0,
  "evidence":["Purdue OEP states the north and south wings are 8 stories and the central section is 2 stories; the model renders corresponding tall paired wings and a low central connector.",f"Reopened major north/south brick cores span z={MEASURE[1]['bounds'][2][0]:.2f}..{MEASURE[1]['bounds'][2][1]:.2f} m locally; total asset geometry reaches z={PROBE['evaluated_building_bounds_local_m'][2][1]:.2f} m.","The model depicts roof decks/parapets and mechanical penthouses."],
  "findings":["No authoritative total building height, roof elevation, roof construction, or floor-to-floor dimensions were located; total height and current roof form remain unverified.","The GIS record carries a 10-level attribute, but its accompanying source review marks vertical GIS fields unverified; the direct OEP story description is preferred."]},
 {"criterion":"Facade, entrances, and distinctive architecture","score":1.4,"max_score":2.0,
  "evidence":["Reopened renders show red-brown brick wing masses, repeated vertical window bays, a central entrance canopy/storefront, courtyard glazing, and a west solar-screen grid.","The Purdue emergency plan and Residences page substantiate the three-part wing arrangement and central common-area connector.","An official Purdue Residences page identifies a photo taken outside the Harrison Hall entrance, but provides no measured exterior facade information."],
  "findings":["The exact brick/window composition, solar-screen dimensions, and canopy/entrance design are not corroborated by elevation drawings or a sufficiently detailed exterior source in the asset's evidence record."]},
 {"criterion":"Modular export, portability, and evidence completeness","score":0.8,"max_score":2.0,
  "evidence":[f"The actual asset reopened in Blender {PROBE['blender_version']} with the manifest scene, collection, {PROBE['original_collection_object_count']} objects, and exact manifest object name/count agreement.",f"Collection-only export reopened with {PROBE['export_collection_object_count']} objects; there are no external images or linked libraries.","The manifest preserves local geometry and a campus placement origin."],
  "findings":["The exported building collection contains 3 cameras and 1 light alongside the geometry.","No canonical `modular/buildings/build_benjamin_harrison_hall.py` or building-specific source/evidence folder exists; manifest source_metadata is empty, so the model cannot be reproduced from a documented source-backed build workflow.","The asset was saved in Blender 5.0.2 and reopened by Blender 4.5.15; its legacy `BLENDER_EEVEE` engine identifier is unavailable in the older runtime. Geometry and collection export reopened, and preview renders succeeded after switching render engine in memory."]}
]
score=round(sum(c["score"] for c in criteria),2)
result={"building_id":"benjamin_harrison_hall","score":score,"max_score":10,"pass_threshold":8,"passed":score>=8,"criteria":criteria,
 "evidence":{"blender_probe":"audit/benjamin_harrison_hall_independent_grade/blender_probe.json","structural_measurements":"audit/benjamin_harrison_hall_independent_grade/structural_object_measurements.json","source_review":"audit/benjamin_harrison_hall_independent_grade/source_review.json","rendered_views":["audit/benjamin_harrison_hall_independent_grade/cam_hero_perspective.png","audit/benjamin_harrison_hall_independent_grade/cam_topdown_footprint.png","audit/benjamin_harrison_hall_independent_grade/cam_west_entrance.png"],"official_gis_snapshot":"audit/official_building_references.json","official_sources":["https://www.purdue.edu/operations/emergency-preparedness/harr/","https://www.housing.purdue.edu/my-housing/options/residence-halls/harrison.html","https://www.housing.purdue.edu/campus-living/get-involved/work-with-us/awards/pastwinners.html"]},
 "findings":["The model has an excellent source-backed horizontal shell and matches the GIS ring to submillimeter accuracy.","The official Purdue emergency plan supports the three-wing layout and 8-story/2-story massing, but does not verify total height or roof geometry.","The main completion gap is evidence and reproducibility: no dedicated builder/source record exists and render cameras/lights are part of the exported asset collection.","Overall independent grade is below the repository's 8/10 finish threshold."]}
(HERE/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2,ensure_ascii=False))

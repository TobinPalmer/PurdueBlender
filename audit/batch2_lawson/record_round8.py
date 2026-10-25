"""Record Lawson R8 source, geometry, validation, and remaining uncertainties."""
import copy
import json
from pathlib import Path

ROOT=Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
AUD=ROOT/"audit/batch2_lawson"
old=json.loads((AUD/"evidence_round7.json").read_text(encoding="utf8"))
validated=json.loads((AUD/"independent_reopen_round8.json").read_text(encoding="utf8"))
planfit=json.loads((AUD/"upper_plan_registration_round8.json").read_text(encoding="utf8"))
record=copy.deepcopy(old)
record.update({
    "revision":8,
    "review_date":"2026-10-25",
    "build_script":"audit/batch2_lawson/build_upper_floors_round8.py",
    "geometry_correction_script":"audit/batch2_lawson/refine_rooftop_round8.py",
    "validation":"audit/batch2_lawson/independent_reopen_round8.json",
    "geometry_overlay":"audit/batch2_lawson/gis_plan_overlay_l2_round8.png; audit/batch2_lawson/gis_plan_overlay_l3_round8.png",
    "changes":old["changes"]+[{
        "feature":"Official second- and third-floor plans, registered to GIS",
        "action":"Downloaded Purdue CS LWSN second-floor and third-floor plan PDFs, rasterized at 120 dpi, registered them to the R7 north-up L1/GIS affine using the same wall-control points after 10/9 pixel rescaling, and compared the GIS ring to source outline strokes. Added GIS footprint slabs and plan-traced schematic L2/L3 partition walls (75 and 87 retained long orthogonal source segments).",
        "evidence":"Official source pages: lawson_2.PDF and lawson_3.PDF. Red GIS overlays are gis_plan_overlay_l2_round8.png and gis_plan_overlay_l3_round8.png. Nearest teal perimeter stroke: L2 975/1,113 samples recognized, mean 0.121 m, max 0.725 m; 905/975 recognized within 0.30 m. L3 1,027/1,113 recognized, mean 0.106 m, max 0.670 m; 950/1,027 within 0.30 m. Three-control transform is 0.0828945 X and 0.0831040 Y m/pixel; see upper_plan_registration_round8.json.",
        "limits":"The floor sheets are raster images and the source stroke is not survey linework; max offsets indicate local plan/GIS envelope differences and/or line-pick limits. Raster extraction captures long orthogonal partition lines, not every wall/door. Story Z, partition thickness (0.12 m), height (2.55 m), and furniture are schematic and unmeasured. L2/L3 plan stair symbols and directions are documented, but no continuous 3D stair flights or section are claimed."
    },{
        "feature":"Third-floor Tolonga Terrace and roof footprint",
        "action":"Used the official L3 plan label Tolonga Terrace and Purdue CS Building Hours listing for a 3rd-floor terrace/balcony to notch the roof deck across the source-drawn terrace zone. The exterior ring follows GIS FID 59; the terrace inner edge is traced from the registered L3 plan. The R8 roof remains at the previous model datum of 13.8 m, unverified.",
        "evidence":"Purdue LWSN third-floor PDF and Lawson Building Hours source. R8 exterior preview and reopened roof mesh are included in evidence.",
        "limits":"The terrace plan boundary trace has about 0.3 m raster pick/registration uncertainty. Roof elevation and terrace guard/rail detail are not established by the plan."
    },{
        "feature":"Photo-referenced rooftop silhouette",
        "action":"Reduced the long, bulky penthouse and equipment group to proportions closer to Purdue's 2006 exterior/aerial photos. The penthouse now measures 8.5 x 20.0 x 3.8 m, rooftop equipment group 8 x 14 x 1.4 m, with overall model maximum Z=19.0 m.",
        "evidence":"Purdue CS March 2006 building update image and official dedication aerial/exterior photograph; raw local copies are listed below. Geometry details are recorded in roof_photo_refinement_round8.json.",
        "limits":"Perspective photos support only relative silhouette. Resized values and all roof/penthouse/equipment heights remain visual estimates; no dimensioned roof/elevation drawing was found."
    }],
    "sources":old["sources"]+[
        {"provider":"Purdue Department of Computer Science","title":"Lawson Computer Science Building, LWSN Second Floor","url":"https://www.cs.purdue.edu/resources/docs/lawson_2.PDF","retrieved":"2026-10-25","source_date":"Undated floor plan PDF","source_crs":"North-up plan with compass rose and graphical scale 1:16","local_snapshot":"audit/batch2_lawson/lawson_2.pdf; audit/batch2_lawson/plan_l2_round8.png","method":"Reused R7 L1/GIS three-control affine transform after 10/9 raster pixel rescale; compared official perimeter stroke against GIS ring and traced long orthogonal interior partitions.","uncertainty":"Approx. 0.3 m control/line pick uncertainty; local outline comparison max nearest teal stroke 0.725 m among recognized samples. Z and wall dimensions unknown."},
        {"provider":"Purdue Department of Computer Science","title":"Lawson Computer Science Building, LWSN Third Floor","url":"https://www.cs.purdue.edu/resources/docs/lawson_3.PDF","retrieved":"2026-10-25","source_date":"Undated floor plan PDF","source_crs":"North-up plan with compass rose and graphical scale 1:16","local_snapshot":"audit/batch2_lawson/lawson_3.pdf; audit/batch2_lawson/plan_l3_round8.png","method":"Reused R7 L1/GIS three-control affine transform after 10/9 raster pixel rescale; compared official perimeter stroke against GIS ring and traced long orthogonal interior partitions. Identifies Tolonga Terrace.","uncertainty":"Approx. 0.3 m control/line pick uncertainty; local outline comparison max nearest teal stroke 0.670 m among recognized samples. Z and wall dimensions unknown."},
        {"provider":"Purdue Department of Computer Science","title":"Lawson Building Hours","url":"https://www.cs.purdue.edu/resources/building-hours.html","retrieved":"2026-10-25","source_date":"Page reports last updated 2025-07-11","source_crs":"Not applicable","local_snapshot":"audit/batch2_lawson/lawson_building_hours.html","method":"Official current facility listing includes a 3rd Floor Terrace/Balcony; used to confirm terrace function in addition to the L3 plan label.","uncertainty":"Confirms room/terrace designation, not terrace dimensions, balustrade design, or roof height."},
        {"provider":"Purdue Department of Computer Science","title":"Lawson Building Update","url":"https://www.cs.purdue.edu/news/articles/2006/building-update-march.html","retrieved":"2026-10-25","source_date":"2006-03-17","source_crs":"Perspective exterior photograph","local_snapshot":"audit/batch2_lawson/lawson_2006_building_update.html; audit/batch2_lawson/lawson_2006_building_march1.jpg; audit/batch2_lawson/lawson_2006_building_march3.jpg","method":"Visual-only reference for exterior brick, glazing, limestone banding, and relative rooftop/penthouse silhouette.","uncertainty":"Perspective photos are not measured elevations; date is 2006 construction/completion view."},
        {"provider":"Purdue Department of Computer Science","title":"Lawson Dedication Proved to be Both High Tech and Highly Touching","url":"https://www.cs.purdue.edu/news/articles/2006/lawson-dedication.html","retrieved":"2026-10-25","source_date":"2006-09-18","source_crs":"Aerial/perspective exterior photograph","local_snapshot":"audit/batch2_lawson/lawson_2006_dedication.html; audit/batch2_lawson/lawson_2006_dedication4.jpg","method":"Visual-only completed-building reference for upper facade, roofline, and rooftop structures.","uncertainty":"Perspective photograph supports relative visual form only; no measured roof or parapet heights."}
    ],
    "previews":old["previews"]+["audit/batch2_lawson/exterior_round8.png","audit/batch2_lawson/floor2_layout_round8.png","audit/batch2_lawson/floor3_layout_round8.png"],
    "supplemental_geometry_evidence":old["supplemental_geometry_evidence"]+["audit/batch2_lawson/gis_plan_overlay_l2_round8.png","audit/batch2_lawson/gis_plan_overlay_l3_round8.png","audit/batch2_lawson/upper_plan_registration_round8.json","audit/batch2_lawson/roof_photo_refinement_round8.json"],
    "remaining_uncertainty":[
        "No dimensioned/current roof or whole-building elevation was found. The main roof datum (13.8 m), maximum Z (19.0 m), penthouse size and equipment dimensions remain visually estimated, not measured.",
        "Purdue GIS reports NUM_LEVELS=5 but does not document the height field's units/measurement method. Upper L2/L3 floor Z values (4.0 and 7.2 m) and partition dimensions remain schematic.",
        "Official L1/L2/L3 plans show stair symbols and UP/DOWN directions, but no section or complete fourth-floor/basement plans verified continuous stair route; upper stair flights are intentionally not fabricated.",
        "The second/third floor partition traces are long orthogonal centerlines from raster plans. Smaller partitions, door openings, wall thickness, furniture, and room heights remain illustrative.",
        "The L3 plan labels Tolonga Terrace and official building hours confirm a 3rd-floor terrace/balcony. The roof notch follows its plan footprint; no measured terrace rail detail or elevation found.",
        "GIS-to-floorplan outline samples show local differences up to 0.725 m (L2) and 0.670 m (L3) among recognized perimeter strokes; plan/GIS raster overlay remains approximate, with about 0.3 m control-pick uncertainty.",
        "Exterior window cadence beyond visible photos and material/glazing specifications remain visual; the 2006 facade photos are historical perspective references."
    ],
    "review_status":"Ready for fresh independent grading; no R8 score assigned."
})
record["validation_summary"]=validated
record["plan_registration_metrics"]=planfit
record["photo_roof_refinement"]=json.loads((AUD/"roof_photo_refinement_round8.json").read_text(encoding="utf8"))
(AUD/"evidence_round8.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

with (AUD/"review.md").open("a",encoding="utf8") as f:
    f.write("\n\n## R8 — Purdue upper-floor plans and photo-referenced roof\n\n")
    f.write("Added source snapshots for Purdue's LWSN second- and third-floor plans (`lawson_2.pdf`, `lawson_3.pdf`), the official building-hours page, and official March/September 2006 exterior photos. Reused the R7 north-up GIS/L1 registration after adjusting for the R8 raster size. GIS/perimeter overlays are in `gis_plan_overlay_l2_round8.png` and `gis_plan_overlay_l3_round8.png`; pixel-outline metrics are in `upper_plan_registration_round8.json`. The official L3 plan names the Tolonga Terrace; its footprint now creates a notch in the roof surface. L2/L3 partition linework is included as schematic geometry, with levels/heights/partitions explicitly unmeasured. The penthouse/equipment were reduced to photo-derived proportions; their dimensions and roof heights remain estimates.\n\n")
    f.write("Reopened and validated the saved blend in Blender 5.2.3 LTS: 619 objects, 616 meshes, identity root, no unmaterialed meshes or missing image files, and the unchanged 1,134/1,134 GIS shell-edge samples remain within 0.10 m. The reopened checksum and all R8 detail are recorded in `independent_reopen_round8.json`.\n\n")
    f.write("**Remaining:** no measured roof/height drawing or complete basement/fourth-floor plan; floor/story/partition vertical dimensions and roof proportions remain schematic; upper stair flights and continuous stair sections are not verified. L2/L3 GIS outline checks have local raster deviations up to 0.725 m and 0.670 m. No R8 self-grade assigned; ready for independent review.\n")
print(json.dumps({"written":"audit/batch2_lawson/evidence_round8.json","sources":len(record["sources"]),"changes":len(record["changes"]),"object_count":validated["object_count"],"grade":"not self-assigned; ready for independent review"},indent=2))

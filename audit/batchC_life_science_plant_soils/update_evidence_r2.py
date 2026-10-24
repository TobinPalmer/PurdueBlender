import json
from pathlib import Path

p=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_life_science_plant_soils_evidence.json")
d=json.loads(p.read_text(encoding="utf-8"))
refs=d.setdefault("references", [])
refs.extend([
  {
    "provider":"Google Maps / Google Street View",
    "url":"https://www.google.com/maps/place/Life+Science+Plant+and+Soils+Laboratory/@40.4231921,-86.9194291,163m/data=!3m2!1e3!4b1!4m6!3m5!1s0x8812e2b71ec32175:0x2dbc13bf851d0609!8m2!3d40.4231921!4d-86.9187854!16s%2Fg%2F11cnb8bwrl?entry=ttu",
    "accessed":"2026-10-24",
    "image_date":"August 2019",
    "use":"Qualitative exterior check from 135 S Russell Dr. Visible red-brown brick wings, lower gray glazed/panel volume, and a narrow vertical glazed bay. Camera bearing, dimensions, and obscured details are not measured."
  },
  {
    "provider":"Purdue University, Department of Agronomy, 5-year report (2021)",
    "url":"https://ag.purdue.edu/department/agry/_docs/final-agronomy-5-year-report-v2-2021.pdf",
    "accessed":"2026-10-24",
    "use":"Building date/use and 2021 operational inventory: 15 large sample dryers, four grinding units with dust arresters, seed/soil cold storage, and 1959 original construction. The original floor-plan appendix URL was not retrievable in this pass; equipment room positions are illustrative."
  }
])
d["modeled_features"].extend([
  "R2: ground slab and all three upper floor plates rebuilt as exact extrusions of the 12-vertex Purdue GIS footprint ring; former bounding-box rectangles removed.",
  "R2: 15 schematic sample dryer cabinets and four schematic soil grinding/dust-arrester units added to the interior; quantities follow Purdue Agronomy's 2021 report, while their room locations remain illustrative.",
  "R2: brick shader adds running-bond courses using axis-aware world-position projections; facade window and greenhouse glazing tuned to the August 2019 Street View palette."
])
d["specific_evidence_boundary"] += " The August 2019 Street View is qualitative and perspective-distorted. It supports brick/glazing/material cues only. The 2021 report supports dryer/grinder counts, not their modeled room locations. Floor slabs are now clipped to the exact official GIS ring; the GIS CRS transformation remains an approximate campus-local conversion."
d["validation"].update({
  "generated_at_local":"2026-10-24",
  "asset_object_count":521,
  "mesh_object_count":519,
  "interior_collection":"LSPS_Interior",
  "interior_object_count":77,
  "interior_mesh_count":77,
  "sample_dryer_count":15,
  "soil_grinder_with_dust_arrester_count":4,
  "floorplate_geometry":"Exact 12-vertex GIS footprint extrusion at ground and levels 1-3",
  "render_preview":"audit/batchC_life_science_plant_soils/exterior_west_r2.png",
  "interior_detail_preview":"audit/batchC_life_science_plant_soils/interior_equipment_r2.png",
  "master_or_manifest_edited":False
})
d.setdefault("uncertainties",[]).extend([
  "August 2019 Street View is historical, perspective-distorted, and only partially exposes the exterior; facade segment dimensions and camera bearing were not calibrated.",
  "Dryer and grinder room placements are schematic because the official floor-plan appendix could not be retrieved. The source-supported counts do not establish current inventory.",
  "Basement cold-storage rooms described in Purdue's 2021 report are not yet represented; exact current room geometry and floor levels remain unverified."
])
p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
print(p)

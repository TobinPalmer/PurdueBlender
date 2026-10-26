"""Independent evaluation for Grissom Hall. Run with Blender:
blender --background --python evaluate_grissom.py -- <repository-root>
"""
import bpy
import json
import math
import sys
from pathlib import Path

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = Path(args[0]).resolve() if args else Path.cwd().resolve()
ID = "massing_grissom_hall_01fd0e0"
AUDIT = ROOT / "audit" / ID
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
EVIDENCE_PATH = AUDIT / "evidence.json"
GIS_PATH = AUDIT / "sources" / "gis.json"
OUT = AUDIT / "grader" / "result.json"

# Load the deliverable itself in a fresh Blender process; no builder-side scene state is used.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
with EVIDENCE_PATH.open(encoding="utf-8") as f:
    record = json.load(f)
with GIS_PATH.open(encoding="utf-8") as f:
    gis = json.load(f)

coll_name = f"Asset_{ID}"
collection = bpy.data.collections.get(coll_name)
scene_name = f"Building_{ID}"
scene = bpy.data.scenes.get(scene_name)
all_objs = list(collection.all_objects) if collection else []
mesh_objs = [o for o in all_objs if o.type == "MESH"]
shell = bpy.data.objects.get("Grissom Hall")
if shell not in all_objs:
    shell = next((o for o in mesh_objs if o.name == "Grissom Hall"), None)

def bounds(objects):
    pts=[]
    for o in objects:
        if o.type != "MESH":
            continue
        pts.extend([o.matrix_world @ v.co for v in o.data.vertices])
    if not pts:
        return None
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]

shell_bounds = bounds([shell]) if shell else None
collection_bounds = bounds(all_objs)
feature = next((x for x in gis.get("features", [])
                if x.get("attributes", {}).get("Name") == "Grissom Hall"
                and x.get("attributes", {}).get("ABBR") == "GRIS"), None)
gis_local_bounds = None
feature_id = None
if feature:
    attr = feature.get("attributes", {})
    feature_id = attr.get("OBJECTID") or attr.get("objectid") or attr.get("FID")
    ring = feature["geometry"]["rings"][0]
    lat0=40.4274
    xy=[((lon+86.9137)*111412.84*math.cos(math.radians(lat0)),
         (lat-lat0)*111040.0) for lon,lat in ring]
    gis_local_bounds=[[min(p[0] for p in xy),max(p[0] for p in xy)],
                      [min(p[1] for p in xy),max(p[1] for p in xy)]]

edge_deltas=None
if shell_bounds and gis_local_bounds:
    edge_deltas=[[shell_bounds[i][0]-gis_local_bounds[i][0],
                  shell_bounds[i][1]-gis_local_bounds[i][1]] for i in range(2)]

image_datablocks=[i for i in bpy.data.images if i.source == "FILE"]
unpacked=[i.filepath for i in image_datablocks if not i.packed_file]
external_unpacked=[]
for path in unpacked:
    if path and not Path(bpy.path.abspath(path)).exists():
        external_unpacked.append(path)

# Criterion points are independent reviewer judgments informed by the measured scene,
# raw source snapshots, source image, and stated uncertainties.
criteria=[
  {"name":"Correct identity and source-backed footprint","score":1.5,"max_score":2,
   "status":"partially verified","evidence":[
     "Saved ArcGIS snapshot contains a building feature named Grissom Hall with abbreviation GRIS and address 315 N. Grant Street.",
     f"Freshly loaded structural shell bounds are {shell_bounds[0][0]:.2f}..{shell_bounds[0][1]:.2f} m X and {shell_bounds[1][0]:.2f}..{shell_bounds[1][1]:.2f} m Y; transformed live feature bounds are {gis_local_bounds[0][0]:.2f}..{gis_local_bounds[0][1]:.2f} m X and {gis_local_bounds[1][0]:.2f}..{gis_local_bounds[1][1]:.2f} m Y.",
     f"Shell minus current GIS envelope deltas (min,max) are {edge_deltas}; west edge differs by about {abs(edge_deltas[0][0]):.2f} m while the other envelope edges agree closely.",
     "A before-model snapshot exists, but the evidence record says the earlier official GIS identifier 236 has no accompanying raw snapshot, leaving the western shell jog not independently traced to a reproducible source."
   ],"findings":["Resolve the projecting west entry/wall jog against a saved official source polygon or dimensioned plan; preserve the source snapshot and feature identifier."]},
  {"name":"Position, orientation, and scale/dimensions","score":1.5,"max_score":2,
   "status":"partially verified","evidence":[
     f"Fresh load confirms shell world bounds {shell_bounds}; reported structural dimensions are {shell_bounds[0][1]-shell_bounds[0][0]:.2f} x {shell_bounds[1][1]-shell_bounds[1][0]:.2f} x {shell_bounds[2][1]-shell_bounds[2][0]:.2f} m.",
     "Asset retains campus-coordinate geometry and identity transform; footprint envelope agrees with three sides of the current Purdue GIS polygon.",
     "No independently sourced bearing, control point, dimensioned plan, or survey is included; the local geographic conversion is explicitly approximate, and polygon disagreement at the west side complicates orientation/scale validation."
   ],"findings":["Add a second control source or dimensioned plan to establish footprint bearing, dimensions, and the west-side alignment independently."]},
  {"name":"Evidence-backed height, floors, and roof form","score":0.5,"max_score":2,
   "status":"estimated / unverified","evidence":[
     f"Freshly loaded shell height is {shell_bounds[2][1]-shell_bounds[2][0]:.2f} m; the saved evidence identifies it as an inherited legacy estimate, not a measured elevation.",
     "The archive snapshot supports two historic main floors plus attic; the current source material does not include measured elevations or a current dimensioned section.",
     "The model has three horizontal façade levels and a flat parapet/cornice roof. Neither exact current floor heights nor hidden roof construction are established by the supplied evidence."
   ],"findings":["Obtain a current elevation/section or reliable height source; until then keep the 11.4 m height, floor spacing, and roof assembly explicitly estimated."]},
  {"name":"Facade, entrances, and distinctive architecture","score":1.5,"max_score":2,
   "status":"partially verified","evidence":[
     "Purdue's saved exterior photograph directly supports red brick, pale stone courses/surrounds, multi-pane windows, monumental pale columns, and a glazed entry.",
     f"The reopened exported collection contains {len(all_objs)} objects, including the shell, repeated windows/stone bands, entry doors, column objects, architrave and pediment; these features are visible in the supplied previews.",
     "The single oblique photo has foliage occlusion and only shows part of the building. The modeled six-column portico count and position, repeated regular window rhythm on all elevations, and shallow pediment shape are not verified by the photo; the visible reference appears to integrate larger columns within a distinct facade composition."
   ],"findings":["Compare the portico column count/spacing and facade bays against additional elevation-specific photos or plans; keep unseen elevations and dimensions labeled approximate."]},
  {"name":"Modular export, portability, and complete evidence","score":1.5,"max_score":2,
   "status":"mostly verified","evidence":[
     f"Fresh load opens the saved .blend; expected collection {coll_name!r} exists with {len(all_objs)} objects, and scene {scene_name!r} is {'present' if scene else 'missing'}.",
     f"The collection's measured bounds are {collection_bounds}; the shell and added geometry remain in the expected campus-coordinate frame.",
     f"External file images: {len(image_datablocks)}; unpacked image files missing on disk: {external_unpacked}.",
     "Evidence includes raw GIS, Purdue facilities/project and archive snapshots, an architect project page, a current Purdue exterior image, source metadata, uncertainty notes and three previews.",
     "The shared manifest still lists only the shell and object_count 1, while the actual asset collection contains multiple detail objects. This is an index mismatch outside the graded building file."
   ],"findings":["Coordinator should update the shared manifest object list/count to match the exported collection before integration."]}
]
score=round(sum(c["score"] for c in criteria),2)
result={
  "building_id":ID,
  "score":score,
  "max_score":10,
  "passing_threshold":8,
  "passed":score>=8,
  "criteria":criteria,
  "evidence":{
    "asset_path":str(ASSET.relative_to(ROOT)).replace("\\","/"),
    "loaded_file":bpy.data.filepath,
    "collection":coll_name,
    "collection_object_count":len(all_objs),
    "mesh_object_count":len(mesh_objs),
    "scene_present":bool(scene),
    "shell_bounds_world_m":shell_bounds,
    "collection_bounds_world_m":collection_bounds,
    "gis_feature_id":feature_id,
    "gis_transformed_envelope_local_m":gis_local_bounds,
    "shell_minus_gis_edge_deltas_m":edge_deltas,
    "file_images":len(image_datablocks),
    "unpacked_image_files_missing":external_unpacked,
    "source_files_present":sorted(p.name for p in (AUDIT/"sources").iterdir() if p.is_file()),
    "previews_present":sorted(p.name for p in (AUDIT/"previews").iterdir() if p.is_file())
  },
  "findings":[finding for c in criteria for finding in c["findings"]],
  "grader_note":"Independent geometry inspection and source comparison. The score deducts for unsupported height/roof, incomplete evidence for the west footprint jog and orientation, unverified facade repetition/portico dimensions, and stale shared manifest object inventory."
}
def evaluate():
    """Return the independently computed Grissom evaluation record."""
    return result

result = evaluate()
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))




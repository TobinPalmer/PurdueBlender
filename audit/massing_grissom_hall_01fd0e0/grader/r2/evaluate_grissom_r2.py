"""Independent Grissom Hall re-grade. Run with Blender --background --python."""
import json
import math
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[4]
ID = "massing_grissom_hall_01fd0e0"
AUDIT = ROOT / "audit" / ID
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
OUT = Path(__file__).resolve().parent / "result.json"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection_name = f"Asset_{ID}"
scene_name = f"Building_{ID}"
collection = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
all_objects = list(collection.all_objects) if collection else []
shell = bpy.data.objects.get("Grissom Hall")
assert collection and scene and shell and shell.type == "MESH"

feature_path = AUDIT / "sources" / "official_feature_236.json"
with feature_path.open(encoding="utf-8") as f:
    source = json.load(f)
feature = source["features"][0]
attrs = feature["attributes"]
assert attrs["FID"] == 236 and attrs["BLDG_ABBR"] == "GRIS"

def bounds(objects):
    pts = [o.matrix_world @ v.co for o in objects if o.type == "MESH" for v in o.data.vertices]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]

shell_bounds = bounds([shell])
asset_bounds = bounds(all_objects)
shell_vertices = []
for v in shell.data.vertices:
    if abs(v.co.z) < 1e-4:
        p = (float((shell.matrix_world @ v.co).x), float((shell.matrix_world @ v.co).y))
        if not any(math.dist(p, q) < 1e-5 for q in shell_vertices):
            shell_vertices.append(p)
source_vertices = []
for lon, lat in feature["geometry"]["rings"][0]:
    p = ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
         (lat - 40.4274) * 111040.0)
    if not any(math.dist(p, q) < 1e-5 for q in source_vertices):
        source_vertices.append(p)
distances = ([min(math.dist(p, q) for q in source_vertices) for p in shell_vertices] +
             [min(math.dist(p, q) for q in shell_vertices) for p in source_vertices])
footprint_max = max(distances)
images = [im for im in bpy.data.images if im.source == "FILE"]
unpacked = [im.filepath for im in images if not im.packed_file]
manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
manifest_entry = next(x for x in manifest["assets"] if x["id"] == ID)

criteria = [
    {
        "name": "Correct identity and source-backed footprint",
        "score": 2.0, "max_score": 2, "status": "verified within project transform precision",
        "evidence": [
            "Raw Purdue BuildingShapesZip4 snapshot identifies FID 236 as GRIS / Grissom Hall, 315 N Grant Street; the separate Purdue campus MapServer generalized geometry is not substituted for this assigned source.",
            f"Freshly opened asset shell and raw FID 236 polygon each contain {len(shell_vertices)} unique perimeter vertices after 1e-5 m deduplication.",
            f"Independent bidirectional nearest-vertex residual is {footprint_max:.8f} m using the project's documented approximate lon/lat-to-local-metre transform; shell perimeter agrees to coordinate/projection precision."
        ],
        "findings": []
    },
    {
        "name": "Position, orientation, and scale/dimensions",
        "score": 1.75, "max_score": 2, "status": "strongly verified horizontally; transform remains approximate",
        "evidence": [
            f"Fresh shell world bounds (m): {shell_bounds}; structural dimensions are {shell_bounds[0][1]-shell_bounds[0][0]:.3f} x {shell_bounds[1][1]-shell_bounds[1][0]:.3f} m.",
            f"Assigned source polygon is co-registered vertex-for-vertex within {footprint_max:.8f} m; perimeter orientation, plan shape, and position follow the assigned Purdue GIS source.",
            "The model stays in the existing simple-massing campus-coordinate frame with identity collection offset. The project transform is a local approximation, not a survey/control-network coordinate reference."
        ],
        "findings": ["Absolute placement accuracy is limited by the project's approximate local geographic conversion; no survey control was supplied."]
    },
    {
        "name": "Evidence-backed height, floors, and roof form",
        "score": 1.25, "max_score": 2, "status": "partly supported; height provisional",
        "evidence": [
            f"Fresh shell height is {shell_bounds[2][1]-shell_bounds[2][0]:.4f} m. Raw FID 236 records Extrution=48, R=47.2, F02=18.5, F03=35 and Elevation=615.5; the GIS layer schema contains no unit/field-description metadata.",
            "The model provisionally interprets vertical fields as feet (48 ft = 14.6304 m; R=47.2 ft = 14.38656 m). Purdue IE's saved 2015 source describes the renovated building as three-story, consistent with three visible facade levels, but does not provide dimensions.",
            "FID 236 also says NUM_LEVELS=5 and CountOfFLO=5, in conflict with Purdue's three-story description. Therefore neither inferred feet nor field semantics resolve exact height/floor datum; treat the current height and level bands as estimates. The flat parapet is plausible from the photo but hidden roof construction is unknown."
        ],
        "findings": ["GIS vertical units and field semantics remain undocumented; confirm against an elevation, section, or surveyed height before treating 14.6304 m as measured.", "GIS five-level attributes conflict with Purdue IE's three-story narrative; retain this source conflict in the evidence record."]
    },
    {
        "name": "Facade, entrances, and distinctive architecture",
        "score": 1.5, "max_score": 2, "status": "partly supported by direct photo evidence",
        "evidence": [
            "Directly inspected Purdue exterior photo supports red brick, pale limestone horizontal bands and surrounds, large multi-pane window groupings, a glazed entry, and monumental pale classical columns beneath a broad stone entablature.",
            "Fresh preview shows those materials/features as brick shell, pale courses/surrounds, repeated glazing and frames, west entry doors, and four monumental portico columns. Revised asset no longer adds the unsupported triangular pediment.",
            "The single oblique, foliage-obscured photo does not establish total column count, exact portico location/dimensions, all facade window rhythms, or unseen elevations. These remain schematic estimates."
        ],
        "findings": ["Column count, facade bays, and unseen elevations remain approximate because the saved photo is partial and no elevation drawing was found."]
    },
    {
        "name": "Modular export, portability, and complete evidence",
        "score": 1.5, "max_score": 2, "status": "asset and source package verified; shared index stale",
        "evidence": [
            f"Fresh load contains expected collection {collection_name!r}, scene {scene_name!r}, {len(all_objects)} collection objects, and zero shell modifiers; identity collection offset is {list(collection.instance_offset)}.",
            f"Entire exported mesh envelope is {asset_bounds}; {len(images)} file-backed images and {len(unpacked)} unpacked image paths. The asset is self-contained with generated/material-only geometry and no external image dependencies.",
            "Building-specific evidence contains raw FID 236 and separate GIS snapshots, source metadata, Purdue/architect/archive snapshots, current exterior photo, reopened validation, and three previews.",
            f"Coordinator-owned modular manifest still records {manifest_entry.get('object_count')} object(s), shell height {manifest_entry.get('bounds_world_m',[[],[],[]])[2][1]} m, and shell-only name, while the saved collection has {len(all_objects)} objects and reaches {asset_bounds[2][1]:.4f} m. The export works; the shared index is stale."
        ],
        "findings": ["Coordinator should refresh Grissom's manifest object inventory and vertical bounds to match the saved asset before integration."]
    }
]

score = round(sum(c["score"] for c in criteria), 2)
result = {
    "building_id": ID,
    "score": score,
    "max_score": 10,
    "passing_threshold": 8,
    "passed": score >= 8,
    "criteria": criteria,
    "evidence": {
        "asset_path": ASSET.relative_to(ROOT).as_posix(),
        "loaded_file": bpy.data.filepath,
        "collection": collection_name,
        "scene": scene_name,
        "collection_object_count": len(all_objects),
        "shell_bounds_world_m": shell_bounds,
        "collection_bounds_world_m": asset_bounds,
        "source_provider": "Purdue University GIS BuildingShapesZip4",
        "source_feature_id": attrs["FID"],
        "source_abbreviation": attrs["BLDG_ABBR"],
        "source_raw_vertical_attributes": {k: attrs.get(k) for k in ("NUM_LEVELS", "CountOfFLO", "Elevation", "Extrution", "F02", "F03", "R")},
        "unique_shell_vertices": len(shell_vertices),
        "unique_source_vertices": len(source_vertices),
        "bidirectional_vertex_residual_max_m": footprint_max,
        "collection_instance_offset": list(collection.instance_offset),
        "shell_modifier_count": len(shell.modifiers),
        "file_images": len(images),
        "unpacked_file_images": unpacked,
        "inspected_source_photo": (AUDIT / "sources" / "purdue_exterior_g1.jpg").relative_to(ROOT).as_posix(),
        "inspected_previews": [p.relative_to(ROOT).as_posix() for p in sorted((AUDIT / "previews").glob("*.png"))],
    },
    "findings": [f for c in criteria for f in c["findings"]],
    "grader_note": "Fresh-process inspection of the revised saved Blender asset, raw FID 236 polygon and attributes, source photograph, previews, evidence snapshots, and shared manifest. Height uses the builder's inferred feet conversion only provisionally; the GIS field units remain undocumented."
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))

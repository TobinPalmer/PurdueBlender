"""Independent R3 reviewer for Niswonger; run with Blender in background."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUDIT = ROOT / 'audit/niswonger_aviation_tech_refine'
ASSET = ROOT / 'modular/buildings/niswonger_aviation_tech.blend'
MASTER = ROOT / 'purdue_campus_master.blend'
MANIFEST = ROOT / 'modular/manifest.json'
OUT = AUDIT / 'independent_grade_r3.json'
REPORT = AUDIT / 'independent_grade_r3.md'


def evaluate(facts):
    """Return evidence-backed rubric result; observations are independently visual-reviewed."""
    criteria = [
        {"name":"Identity and source-backed footprint", "score":1.7, "max_score":2,
         "evidence":["R3 render shows a coherent airport classroom/hangar complex with brick wings, glazed connector and attached hangar volumes.", "The submitted Esri z20 overhead tile shows the matching roof-zone arrangement and separate hangar mass; no source-date or georegistration metadata is provided, so this verifies qualitative identity more than metric footprint.", "Mesh envelope is [-50,50] x [-65.5,65.5] m, but the manifest exact-bound comparison is not an independent polygon trace."],
         "finding":"Identity is convincing. Exact wall footprint and roof perimeter are not independently registered to a current survey or as-built plan."},
        {"name":"Position, orientation and scale", "score":1.9, "max_score":2,
         "evidence":["The master links Asset_niswonger_aviation_tech through Placement_niswonger_aviation_tech at (-1325,-1229.5,0), zero rotation, unit scale, matching the manifest placement origin.", "Local XY envelope and building origin are consistent across the asset and master record."],
         "finding":"Placement is internally consistent; this review lacks a survey control point proving the building's geospatial registration to sub-meter accuracy."},
        {"name":"Evidence-backed height, floors and roof form", "score":1.3, "max_score":2,
         "evidence":["R3 now renders the previously hidden sloping connector roof and hangar roof, and adds narrow roof edges and lap cues on the two added wing tops.", "The orthophoto supports multiple roof zones and a service-equipment cluster, while the model still uses broad, simple planes and omits that cluster.", "No as-built roof plan was found; exact elevations, slope, plate perimeters and mechanical layout remain explicitly unverified."],
         "finding":"The major roof forms are present and legible, but the added plates remain approximate and the roof silhouette/detailing is less articulated than the aerial reference."},
        {"name":"Facade, entrances and distinctive architecture", "score":1.6, "max_score":2,
         "evidence":["The R3 render shows long brick classroom wings, repeated glazed bays, a glazed entrance/connector and a distinctive pitched glazed volume.", "MSKTD photographs support the brick, metal frame, extensive glazing and visible aircraft/hangar interior, but are mostly interior views and do not validate the current exterior camera side directly."],
         "finding":"The signature materials and volumes are represented; exterior window/door rhythm, entrance placement and full elevations are not directly photo-matched in the submitted review views."},
        {"name":"Modular export, portability and complete evidence", "score":1.3, "max_score":2,
         "evidence":["Fresh Blender 5.2 reopen record reports 2,313 collection objects / 2,227 meshes, no unmaterialed meshes, no missing external image dependencies, origin at zero and visible roof shells.", "The checked-in manifest still lists 2,300 objects and 2,300 expected names, so 13 R3 objects are not yet indexed; the master reopen record also predates the R3 2,313-object file.", "Evidence includes six MSKTD project photos and a local Esri imagery mosaic; the mosaic's acquisition date is unavailable."],
         "finding":"The asset itself is portable and material-complete, but shared manifest/master integration records are stale for this revision, and source metadata for the aerial is incomplete."}
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    return {"asset":"niswonger_aviation_tech", "revision":"R3", "score":score, "max_score":10,
            "pass_threshold":8, "passed":score >= 8, "asset_sha256":facts['asset_sha256'],
            "fresh_reopen_facts":facts, "criteria":criteria,
            "evidence":["audit/niswonger_aviation_tech_refine/exterior_r3.png", "audit/niswonger_aviation_tech_refine/roofplan_r3.png", "audit/niswonger_aviation_tech_refine/arcgis_world_imagery/composite_z20.jpg", "audit/niswonger_aviation_tech_refine/msktd_project_1.jpg through msktd_project_6.jpg", "audit/niswonger_aviation_tech_refine/roof_source_evidence_r3.md"],
            "findings":["Score is below the 8/10 minimum.", "Manifest and master evidence are stale relative to the 2,313-object saved R3 asset.", "Roof plates need better evidence-backed articulation, and source dates/registration should be recorded if available.", "A close exterior comparison view should be added against MSKTD imagery where the facade side is identifiable."],
            "source_urls":["https://msktd.com/project/purdue-university-niswonger-aviation-technology/", "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer", "https://www.purdue.edu/bot/meetings/past-meetings/2019/06.%20aug/pfc/508_Airport-HVAC-Window-Overhead-Door.pdf"]}

# Independently reopen the asset in this Blender process and inspect names, geometry bounds,
# materials, image portability, render visibility and the current manifest discrepancy.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
coll = bpy.data.collections.get('Asset_niswonger_aviation_tech')
assert coll is not None
objs = list(coll.all_objects)
meshes = [o for o in objs if o.type == 'MESH']
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
record = next(a for a in manifest['assets'] if a['id'] == 'niswonger_aviation_tech')
expected = set(record['objects'])
actual = {o.name for o in objs}
mesh_bounds = [Vector((float('inf'),)*3), Vector((float('-inf'),)*3)]
for ob in meshes:
    for corner in ob.bound_box:
        q = ob.matrix_world @ Vector(corner)
        mesh_bounds[0] = Vector([min(mesh_bounds[0][i], q[i]) for i in range(3)])
        mesh_bounds[1] = Vector([max(mesh_bounds[1][i], q[i]) for i in range(3)])
missing_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
materialless = [ob.name for ob in meshes if not ob.data.materials or all(m is None for m in ob.data.materials)]
roof_names = ['NISW_R2_Roof_Brick_Wing','NISW_R2_Roof_Classroom_Wing','NISW_Photographic_Sloping_Roof','NISW_Flat_Roof_Membrane']
roof_hidden = {n: bpy.data.objects[n].hide_render for n in roof_names if n in bpy.data.objects}
facts = {"asset_path":str(ASSET), "asset_sha256":hashlib.sha256(ASSET.read_bytes()).hexdigest(),
         "object_count":len(objs), "manifest_expected_object_count":record.get('object_count'),
         "mesh_count":len(meshes), "manifest_missing_names":sorted(expected-actual),
         "manifest_extra_names":sorted(actual-expected),
         "mesh_bounds_local_m":[[round(float(v),4) for v in mesh_bounds[0]], [round(float(v),4) for v in mesh_bounds[1]]],
         "root_location":list(bpy.data.objects['AssetRoot_niswonger_aviation_tech'].location),
         "materialless_meshes":materialless, "missing_external_images":missing_images,
         "roof_hide_render":roof_hidden}
# Record master placement and linked library source independently.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
links = []
for ob in bpy.data.objects:
    if ob.instance_type == 'COLLECTION' and ob.instance_collection and 'niswonger' in ob.instance_collection.name.lower():
        lib = ob.instance_collection.library
        links.append({"object":ob.name, "location":list(ob.location), "rotation":list(ob.rotation_euler), "scale":list(ob.scale), "collection":ob.instance_collection.name, "library_path":lib.filepath if lib else None})
facts['master_links'] = links
result = evaluate(facts)
OUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
lines = [f"# Independent grade — Niswonger Aviation Technology R3", "", f"**Score: {result['score']:.1f}/10** (minimum pass: 8/10).", f"**Asset SHA-256:** `{facts['asset_sha256']}`", "", "## Rubric", "", "| Criterion | Score | Evidence and finding |", "|---|---:|---|"]
for c in result['criteria']:
    lines.append(f"| {c['name']} | {c['score']:.1f}/2 | {' '.join(c['evidence'])} **Finding:** {c['finding']} |")
lines += ["", "## Required follow-up", ""] + [f"- {f}" for f in result['findings']]
lines += ["", "## Primary evidence", "", "- [MSKTD project page](https://msktd.com/project/purdue-university-niswonger-aviation-technology/) shows architect photographs and summarizes the classroom, collaborative and office program.", "- [Purdue Board of Trustees Airport project PDF](https://www.purdue.edu/bot/meetings/past-meetings/2019/06.%20aug/pfc/508_Airport-HVAC-Window-Overhead-Door.pdf) confirms HVAC/window work but not roof geometry.", "- Esri World Imagery tile mosaic is saved locally; tile service exposes no acquisition date in the recorded retrieval.", ""]
REPORT.write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps(result, indent=2))

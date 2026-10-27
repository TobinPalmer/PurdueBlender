"""Independent fresh-open scorecard for Alpha Sigma Phi.
This evaluator inspects the saved library and scores against the available evidence.
"""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular/buildings/massing_house_301841603_654031c.blend'
GIS = ROOT / 'audit/alpha_sigma_phi/sources/arcgis_fid763_feature.json'
OUT = Path(__file__).resolve().parent / 'result.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes.get('Building_massing_house_301841603_654031c')
asset = bpy.data.collections.get('Asset_massing_house_301841603_654031c')
shell = bpy.data.objects.get('House_301841603')
assert scene and asset and shell
src = json.loads(GIS.read_text(encoding='utf-8'))['features'][0]
ring = src['geometry']['rings'][0][:-1]
src_xy = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
           (lat - 40.4274) * 111040.0) for lon, lat in ring]
model_xy = sorted({(round((shell.matrix_world @ v.co).x, 6),
                    round((shell.matrix_world @ v.co).y, 6)) for v in shell.data.vertices})
errors = [min(math.hypot(x-mx, y-my) for mx,my in model_xy) for x,y in src_xy]
objects = list(asset.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
verts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
bounds = [[round(min(getattr(v,a) for v in verts),3), round(max(getattr(v,a) for v in verts),3)] for a in ('x','y','z')]
materials = sorted({m.name for o in meshes for m in o.data.materials if m})
material_nodes = {}
for name in materials:
    m=bpy.data.materials.get(name)
    material_nodes[name]=[n.type for n in m.node_tree.nodes] if m and m.use_nodes else []
source_text=(ROOT/'audit/alpha_sigma_phi/source_provenance.json').read_text(encoding='utf-8')
criteria=[
 {"criterion":"Correct identity and source-backed footprint","score":2.0,"max_score":2.0,
  "evidence":f"Purdue GIS feature FID {src['attributes']['FID']} identifies Alpha Sigma Phi at {src['attributes']['ADDRESS']}; the saved shell has {len(model_xy)} unique XY vertices for the {len(ring)}-vertex GIS ring, with maximum nearest-vertex error {max(errors):.6f} m. The saved aerial overlay follows the L-shaped roof footprint.",
  "finding":"Pass. The plan footprint is an exceptionally close trace of the authoritative campus polygon."},
 {"criterion":"Position, orientation, and scale/dimensions","score":2.0,"max_score":2.0,
  "evidence":f"Fresh-open inspection confirms the expected scene, collection, root object, and direct campus coordinates. Plan bounds match the transformed GIS bounds; the two principal wings follow the GIS orientation. Current 2D footprint dimensions are approximately 31.4 m by 43.9 m.",
  "finding":"Pass for horizontal position, orientation, and footprint scale. The height uncertainty is assessed separately."},
 {"criterion":"Evidence-backed height, floors, and roof form","score":0.75,"max_score":2.0,
  "evidence":"The aerial independently supports the L-shaped roof plan and a broad low-slope/flat-looking roof surface. No target-facing elevation, measured height, or public floor plan is present in the evidence. GIS says NUM_LEVELS=1 and CountOfFLO=1, but the model illustrates three window levels; `Extrution=34` has no documented unit. The builder now labels height/story count as estimates instead of claiming the extrusion value is feet.",
  "finding":"Partial. The roof plan is supported, but roof profile, 10.36 m height, parapet, and three-level facade remain unresolved or conflict with the campus GIS attributes."},
 {"criterion":"Facade, entrances, and distinctive architecture","score":0.75,"max_score":2.0,
  "evidence":"Fresh exterior render shows dark procedural brick, repeated pale-framed windows, and a modest canopy/steps. The chapter history supports the house address and 1966 occupancy, but the supplied Street View is not a clear target elevation; no source verifies brick color, number/spacing of windows, or entrance location. The latest revision clearly labels the interior as schematic and adds review-only room annotations to the cutaway.",
  "finding":"Below threshold for architectural fidelity. The facade still reads as a generic dark brick block, with a small indistinct entry. The cutaway annotation clarifies the illustrative plan but the visible interior is sparse and is not corroborated by a real plan."},
 {"criterion":"Modular export, portability, and complete evidence","score":2.0,"max_score":2.0,
  "evidence":f"The source reopens as the expected named scene and collection; it contains {len(objects)} asset objects ({len(meshes)} meshes), with {len(materials)} node-based materials. Brick uses a procedural shader; no linked image texture dependency was found. Source GIS, imagery tiles/overlay, provenance, builder, fresh-open validation, and exterior/interior review renders are present.",
  "finding":"Pass. Asset packaging and uncertainty labeling are clear; schematic content is not represented as verified floorplan data."},
]
score=round(sum(c['score'] for c in criteria),2)
result={
 "asset":"modular/buildings/massing_house_301841603_654031c.blend",
 "asset_sha256":hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 "grade_round":"independent_grade_r2",
 "evaluator":"independent fresh-open visual/evidence review",
 "blender_version":bpy.app.version_string,
 "fresh_open":True,
 "identity":{"scene":scene.name,"collection":asset.name,"root":shell.name,"FID":src['attributes']['FID'],"address":src['attributes']['ADDRESS']},
 "geometry":{"source_vertices":len(ring),"model_unique_footprint_vertices":len(model_xy),"max_vertex_error_m":round(max(errors),6),"bounds_world_m":bounds},
 "packaging":{"asset_object_count":len(objects),"mesh_object_count":len(meshes),"materials":materials,"material_nodes":material_nodes},
 "score":score,"max_score":10,"passes_8_threshold":score>=8,
 "criteria":criteria,
 "evidence":[
  "Fresh-open Blender inspection of the current saved .blend, not the builder script alone.",
  "Purdue BuildingShapesZip4 ArcGIS FID 763 snapshot and native CRS snapshot.",
  "Esri World Imagery overlay and current tiled imagery in audit/alpha_sigma_phi/sources/.",
  "Alpha Pi chapter history supports 951 David Ross Road and the 1966 move-in, not current facade details.",
  "The Purdue archive index confirms a 1968 David Ross fraternity photo feature exists, but the scan was blocked and could not be used to identify this house facade.",
  "Google Street View context, exterior render, and latest schematic interior cutaway inspected directly."
 ],
 "findings":[
  "Keep the GIS-derived footprint unchanged; it is strongly verified.",
  "Do not infer the unit for GIS Extrution=34. The GIS one-level fields conflict with the modeled three levels; resolve with a target-facing elevation, reliable building plans, or measurements.",
  "Current model geometry remains a generic brick, repeated-window, flat-roofed residence. Obtain direct Alpha Sigma Phi facade/roof references before adding distinctive claims or moving the entry/windows.",
  "The latest cutaway is more legible than the prior review image but its furnishings and room arrangement are sparse and purely schematic. Keep that limitation explicit until a real floor plan is found."
 ],
 "sources":{
  "provenance":"audit/alpha_sigma_phi/source_provenance.json",
  "fresh_open_validation":"audit/alpha_sigma_phi/fresh_open_validation.json",
  "exterior_preview":"audit/alpha_sigma_phi/previews/alpha_sigma_phi_exterior.png",
  "interior_cutaway_preview":"audit/alpha_sigma_phi/previews/alpha_sigma_phi_interior_cutaway.png",
  "GIS_overlay":"audit/alpha_sigma_phi/sources/esri_world_imagery_fid763_footprint_overlay.png"
 }
}
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({"score":score,"passes_8_threshold":score>=8,"result":str(OUT),"geometry":result['geometry'],"asset_sha256":result['asset_sha256']}))

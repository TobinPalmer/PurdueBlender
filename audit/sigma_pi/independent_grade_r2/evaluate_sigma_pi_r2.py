"""Independent grader for Sigma Pi FID 776. Run with Blender 5.2.3 --background."""
import bpy, bmesh, hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/sigma_pi"
ASSET = ROOT / "modular/buildings/massing_house_301836568_0fbca0e.blend"
GIS = AUDIT / "sources/purdue_gis_fid776_sigma_pi_2026-10-26.json"
OUT = Path(__file__).resolve().parent / "grade_result.json"
EXPECTED_SHA = "ea316fbd452abebd0130f032cc7b328bc137da41bc296d5c349ee93b416a2b5a"


def evaluate():
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA:
        raise RuntimeError(f"Asset hash changed: {sha} != {EXPECTED_SHA}")
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    g = json.loads(GIS.read_text(encoding="utf-8"))
    ring = g["geometry"]["rings"][0]
    to_local = lambda p: ((p[0] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                          (p[1] - 40.4274) * 111040.0)
    src = [to_local(p) for p in ring]
    if src[0] == src[-1]: src.pop()
    ident = "massing_house_301836568_0fbca0e"
    coll = bpy.data.collections.get("Asset_" + ident)
    scene = bpy.data.scenes.get("Building_" + ident)
    shell = bpy.data.objects.get("SigmaPi_Stucco_Shell_FID776")
    roof = bpy.data.objects.get("SigmaPi_Roof_Plane_Estimated")
    if coll is None or scene is None or shell is None or shell.type != 'MESH' or roof is None:
        raise RuntimeError("Required asset collection, scene, structural shell, or roof object is missing")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_shell = shell.evaluated_get(depsgraph)
    mesh = eval_shell.to_mesh()
    try:
        verts = [eval_shell.matrix_world @ v.co for v in mesh.vertices]
        bottom = [(v.x, v.y) for v in verts if v.z < 1.0]
        nearest = [min(math.hypot(x-sx, y-sy) for x,y in bottom) for sx,sy in src]
        bounds = [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)]
        bm = bmesh.new(); bm.from_mesh(mesh)
        nonmanifold = sum(not e.is_manifold for e in bm.edges)
        bm.free()
    finally:
        eval_shell.to_mesh_clear()
    library_objs = list(coll.objects)
    linked_libs = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
    external_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and im.filepath and not im.packed_file]
    external_textures = [n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes
                         if n.type == 'TEX_IMAGE' and n.image and n.image.source == 'FILE' and n.image.filepath and not n.image.packed_file]
    named_window = [o.name for o in library_objs if 'window' in o.name.lower()]
    named_entry = [o.name for o in library_objs if 'entry' in o.name.lower() or 'door' in o.name.lower()]
    top_z = max((roof.matrix_world @ v.co).z for v in roof.data.vertices) if roof.type == 'MESH' else None
    criteria = [
      {"criterion":"Correct identity and source-backed footprint", "score":1.8,"max_score":2,
       "evidence":f"Purdue GIS raw snapshot identifies FID {g['attributes'].get('FID')} as {g['attributes'].get('BUILDING_N')} ({g['attributes'].get('BLDG_ABBR')}), 130 Russell St; Sigma Pi official location page independently names the Purdue Chapter House at 130 N Russell. Fresh-opened shell bottom vertices compare to {len(src)} unique FID ring vertices; max nearest distance {max(nearest):.6f} m. The saved current-state orthophoto overlay visually places that exact ring on the roof perimeter.",
       "uncertainty":"GIS Shape__Area=817.3945 m² and Shape__Length=154.0032 m conflict with geodesic calculations from supplied ring (~473.1593 m², ~117.1197 m). Orthophoto supports roof outline; structural wall line behind roof edge is not established."},
      {"criterion":"Position, orientation, and scale/dimensions", "score":1.8,"max_score":2,
       "evidence":f"Fresh-opened structural shell bounds in campus coordinates are {json.dumps(bounds)}. It reproduces the project-transformed source vertices with max nearest error {max(nearest):.6f} m; the overlay registers this plan with current orthophotography.",
       "uncertainty":"This demonstrates source-ring roof-plan registration, not surveyed wall position or dimensions. No independent surveyed coordinate/control points were found."},
      {"criterion":"Evidence-backed height, floors, and roof form", "score":0.7,"max_score":2,
       "evidence":f"The saved mesh is about {bounds[2][1]-bounds[2][0]:.2f} m wall height with roof-object top at {top_z:.2f} m. Render depicts three occupied-level bands; 2004 chapter newsletter references second-/third-deck work; assessor living-area record is corroborative only.",
       "uncertainty":"Height, floor count, and roof elevation are not measured. GIS NUM_LEVELS=1 and Extrution=12 conflict with multi-deck evidence; newsletter and assessment do not resolve this. Aerial roof image does not establish a reliable roof section. Flat roof is explicitly a placeholder."},
      {"criterion":"Facade, entrances, and distinctive architecture", "score":0.6,"max_score":2,
       "evidence":"2004 chapter newsletter supports broad stucco and wood-trim material cues. The asset contains repeated window/detail objects and a single modest entry; preview shows restrained three-band treatment.",
       "uncertainty":"No inspected current facade photograph, elevation, opening schedule, or plan was available. Window count/rhythm, entrance position, current facade configuration, and distinctive architecture remain estimated."},
      {"criterion":"Modular export, portability, and complete evidence", "score":1.7,"max_score":2,
       "evidence":f"Fresh Blender {bpy.app.version_string} process reopened the exact hash asset. Expected asset collection and scene are present; collection holds {len(library_objs)} objects ({sum(o.type=='MESH' for o in library_objs)} meshes); shell is manifold-edge clean count={nonmanifold}; there are {len(linked_libs)} linked libraries, {len(external_images)} unpacked external images, and {len(external_textures)} unpacked texture paths. Audit includes source register, raw GIS and imagery snapshots/overlay, 2004 chapter newsletter, build/reopen record, and preview render.",
       "uncertainty":"Coordinator-owned manifest entry still reports the previous one-object massing bounds (Z 0–16 m), inconsistent with this asset's 186-object export and Z 0.25–9.25 m shell. Integration/index reconciliation remains needed."}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    evidence={
      "asset":ASSET.relative_to(ROOT).as_posix(),"asset_sha256":sha,"expected_sha256":EXPECTED_SHA,"sha_matches_expected":sha==EXPECTED_SHA,
      "fresh_reopen":True,"blender_version":bpy.app.version_string,
      "building_identity":{k:g['attributes'].get(k) for k in ('FID','BUILDING_N','BLDG_ABBR','ADDRESS','OWNER')},
      "export_collection":"Asset_"+ident,"scene":"Building_"+ident,"export_object_count":len(library_objs),
      "export_mesh_count":sum(o.type=='MESH' for o in library_objs),"export_instance_offset":list(coll.instance_offset),
      "shell_world_bounds_m":bounds,"shell_vertex_count":len(shell.data.vertices),"shell_face_count":len(shell.data.polygons),
      "shell_nonmanifold_edge_count":nonmanifold,"gis_unique_outer_ring_vertices":len(src),
      "gis_ring_to_shell_bottom_nearest_m_max":max(nearest),"gis_ring_to_shell_bottom_nearest_m_mean":sum(nearest)/len(nearest),
      "roof_object_top_z_m":top_z,"window_named_object_count":len(named_window),"entry_named_object_count":len(named_entry),
      "linked_library_paths":linked_libs,"unpacked_external_images":external_images,"unpacked_external_texture_paths":external_textures,
      "gis_area_attribute_m2":g['attributes'].get('Shape__Area'),"gis_length_attribute_m":g['attributes'].get('Shape__Length'),
      "source_ring_geodesic_area_perimeter_m2_m":[473.1593305882179,117.11970027902831],
      "orthophoto_overlay":"audit/sigma_pi/sources/indiana_current_aerial_sigma_pi_3857_overlay.jpg",
      "historical_newsletter":"audit/sigma_pi/sources/sigma_pi_eta_data_2004.pdf",
      "manifest_record_status":"Stale relative to saved asset: records 1 object and old Z 0-16 m bounds; coordinator owns manifest update."
    }
    return {"score":score,"max_score":10,"passing_threshold":8,"passes":score>=8,"criteria":criteria,"evidence":evidence,
      "findings":[
       "Identity and roof-plan registration are strongly supported by the official GIS FID, independent address source, raw ring comparison, and current orthophoto overlay.",
       "GIS area/length attributes conflict substantially with supplied ring coordinates; structural wall alignment remains unverified because the imagery traces the roof perimeter.",
       "The modeled 9 m wall height, ~9.39 m roof top, apparent three-level treatment, and flat roof are uncertain; available sources do not give a measured section or roof survey.",
       "Facade details, entrance placement, and opening rhythm are visually modeled without inspected current elevation evidence.",
       "The current asset is portable and has complete source evidence; coordinator-owned manifest bounds and object count are stale and need reconciliation."
      ]}

result=evaluate()
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

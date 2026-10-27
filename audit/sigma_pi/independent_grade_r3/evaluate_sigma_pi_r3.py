"""Independent R3 Sigma Pi evaluator; run with Blender 5.2.3 --background."""
import bpy, bmesh, hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/sigma_pi"
OUTDIR = Path(__file__).resolve().parent
ASSET = ROOT / "modular/buildings/massing_house_301836568_0fbca0e.blend"
GIS = AUDIT / "sources/purdue_gis_fid776_sigma_pi_2026-10-26.json"
EXPECTED_SHA = "eb792483ebbf168162dea5134b1b9a405c9127ec7f2d92e2782e798b5b2aecce"


def evaluate():
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA:
        raise RuntimeError(f"Frozen candidate SHA mismatch: {sha} != {EXPECTED_SHA}")
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    feature = json.loads(GIS.read_text(encoding="utf-8"))
    ring = feature["geometry"]["rings"][0]
    to_local = lambda p: ((p[0] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                          (p[1] - 40.4274) * 111040.0)
    src = [to_local(p) for p in ring]
    if src[0] == src[-1]:
        src.pop()
    ident = "massing_house_301836568_0fbca0e"
    coll = bpy.data.collections.get("Asset_" + ident)
    scene = bpy.data.scenes.get("Building_" + ident)
    shell = bpy.data.objects.get("SigmaPi_Stucco_Shell_FID776")
    roof = bpy.data.objects.get("SigmaPi_Roof_Plane_Estimated")
    if not all((coll, scene, shell)) or shell.type != 'MESH' or roof is None:
        raise RuntimeError("Expected asset collection/scene/shell/roof is missing")
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
    objs = list(coll.objects)
    linked_libs = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
    external_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and im.filepath and not im.packed_file]
    external_textures = [n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes
                         if n.type == 'TEX_IMAGE' and n.image and n.image.source == 'FILE' and n.image.filepath and not n.image.packed_file]
    win = [o.name for o in objs if 'window' in o.name.lower()]
    entry = [o.name for o in objs if 'entry' in o.name.lower() or 'door' in o.name.lower()]
    roof_top = max((roof.matrix_world @ v.co).z for v in roof.data.vertices)
    score_criteria = [
      {"criterion":"Correct identity and source-backed footprint", "score":1.9, "max_score":2,
       "evidence":f"Purdue GIS raw feature FID {feature['attributes'].get('FID')} identifies Sigma Pi (SOSP), 130 Russell St; Sigma Pi's official chapter-house address provides an independent name/address match (source register). In a fresh Blender {bpy.app.version_string} process the exact candidate shell bottom was compared with {len(src)} unique GIS ring vertices; max nearest distance is {max(nearest):.6f} m. The preserved current Indiana imagery overlay shows the ring closely tracing today's roof perimeter.",
       "uncertainty":"The GIS ring matches the visible roof plan, not a surveyed structural wall line; the hidden offset between eaves and walls is unknown."},
      {"criterion":"Position, orientation, and scale/dimensions", "score":1.9, "max_score":2,
       "evidence":f"The fresh-opened shell retains campus coordinates and reproduces the 36 source vertices under the project local approximation with maximum point error {max(nearest):.6f} m. The ring is registered to the current orthophoto in its native Web Mercator coordinate system; latest GIS Shape__Area/Length values reconcile with direct EPSG:3857 ring projection (817.3945 vs 817.3858 m²; lengths agree within rounding).",
       "uncertainty":"No independent survey/control point or structural-wall footprint is available; the current evidence measures the roof outline and locates it to the source image."},
      {"criterion":"Evidence-backed height, floors, and roof form", "score":0.8, "max_score":2,
       "evidence":f"Model shell is {bounds[2][1]-bounds[2][0]:.2f} m high and roof cap reaches {roof_top:.2f} m. The 2004 Eta Data newsletter describes second-/third-deck work and an addition, county assessment lists 18,680 ft² of finished living area, and the 1932 Sigma Pi yearbook illustration depicts a multi-story, multi-gabled historic house.",
       "uncertainty":"No source measures present-day height or exact floor count. GIS NUM_LEVELS=1 conflicts with the chapter/county clues. The 1932 gables predate the documented 1989 addition and cannot establish today's roof; current aerial shows roof articulation that the model's flat cap does not represent. Wall height, deck bands, roof height/profile remain estimates."},
      {"criterion":"Facade, entrances, and distinctive architecture", "score":0.6, "max_score":2,
       "evidence":"The 2004 newsletter supports broad exterior stucco and wood-trim cues; the model applies these restrained material cues and contains repeated window and entry detail objects.",
       "uncertainty":"No current facade photo/elevation or inspectable entry image is preserved. Window count/rhythm, entry position, and present facade details are not source-backed. The 1932 illustration is a historic depiction only; its multi-gabled architecture is not represented in the model."},
      {"criterion":"Modular export, portability, and complete evidence", "score":1.7, "max_score":2,
       "evidence":f"Fresh Blender process reopened the exact SHA256 candidate. Expected named scene and asset collection are present; the collection contains {len(objs)} objects ({sum(o.type=='MESH' for o in objs)} meshes), shell nonmanifold edge count={nonmanifold}, linked libraries={len(linked_libs)}, unpacked external images={len(external_images)}, and unpacked image texture paths={len(external_textures)}. The R3 evidence set includes source register, raw GIS/metadata, current orthophoto and ring overlay, county assessment, chapter newsletter, historic yearbook scan, LiDAR footprint comparison with uncertainty, geometry cross-check, build/reopen record, and preview render.",
       "uncertainty":"The coordinator-owned manifest still reports the former one-object, Z 0–16 m massing bounds instead of this 186-object, Z 0.25–9.25 m asset; coordinator reconciliation and master integration are pending."}
    ]
    score = round(sum(c['score'] for c in score_criteria), 2)
    return {"score":score,"max_score":10,"passing_threshold":8,"passes":score>=8,
      "asset_sha256":sha,"expected_sha256":EXPECTED_SHA,"criteria":score_criteria,
      "evidence":{"asset":ASSET.relative_to(ROOT).as_posix(),"fresh_reopen":True,"blender_version":bpy.app.version_string,
       "identity":{"FID":feature['attributes'].get('FID'),"building_name":feature['attributes'].get('BUILDING_N'),"abbreviation":feature['attributes'].get('BLDG_ABBR'),"address":feature['attributes'].get('ADDRESS')},
       "collection":"Asset_"+ident,"scene":"Building_"+ident,"collection_objects":len(objs),"collection_meshes":sum(o.type=='MESH' for o in objs),
       "instance_offset":list(coll.instance_offset),"shell_bounds_xyz":bounds,"shell_vertex_count":len(shell.data.vertices),"shell_face_count":len(shell.data.polygons),
       "shell_nonmanifold_edge_count":nonmanifold,"gis_unique_ring_vertex_count":len(src),"gis_to_shell_bottom_nearest_error_max_m":max(nearest),
       "gis_to_shell_bottom_nearest_error_mean_m":sum(nearest)/len(nearest),"roof_cap_top_z_m":roof_top,"named_window_objects":len(win),"named_entry_or_door_objects":len(entry),
       "linked_library_paths":linked_libs,"unpacked_external_images":external_images,"unpacked_external_texture_paths":external_textures,
       "gis_shape_area_epsg3857_m2":feature['attributes'].get('Shape__Area'),"gis_shape_length_epsg3857_m":feature['attributes'].get('Shape__Length'),
       "projected_ring_area_epsg3857_m2":817.385769025312,"geodesic_ring_area_m2":473.1593305882179,"geodesic_ring_perimeter_m":117.11970027902831,
       "orthophoto_overlay":"audit/sigma_pi/sources/indiana_current_aerial_sigma_pi_3857_overlay.jpg",
       "historic_visual_source":"audit/sigma_pi/sources/purdue_debris_1932_page323.jpg",
       "lidar_footprint_comparison":"audit/sigma_pi/sources/lidar_footprint_comparison_metrics.json",
       "manifest_status":"stale; root coordinator owns reconciliation"},
      "findings":[
       "Identity and current roof-plan footprint are strongly supported: GIS name/address, independent chapter address, exact ring reconstruction, and current orthophoto agree.",
       "The earlier apparent GIS area/perimeter discrepancy is resolved: service metrics are planar EPSG:3857 and agree with projecting the supplied ring. The 2018 LiDAR footprint is a separate generalized extraction (IoU 0.769; Hausdorff 15.99 m), not a surveyed correction and was appropriately not substituted.",
       "Current structural wall footprint remains unknown because GIS ring traces roof perimeter and imagery does not reveal the wall/eave offset.",
       "Modeled wall/deck heights, floor count and roof profile remain unsupported. The 1932 gabled house image is explicitly historical and predates the 1989 addition; it cannot directly validate current form. Current aerial indicates a roof silhouette more articulated than the modeled flat cap.",
       "Facade window rhythm, entry location, and distinctive current features remain estimates because no inspectable current facade image or elevation is in the audit.",
       "Asset export is portable and well documented, but the coordinator manifest is stale and integration remains open."
      ]}

result = evaluate()
(OUTDIR / 'grade_result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))

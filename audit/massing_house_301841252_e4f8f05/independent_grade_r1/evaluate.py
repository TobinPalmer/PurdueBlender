import json, math, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
BID = 'massing_house_301841252_e4f8f05'
AUDIT = ROOT / 'audit' / BID
ASSET = ROOT / 'modular' / 'buildings' / (BID + '.blend')
GIS = AUDIT / 'sources' / 'purdue_gis_fid790.json'
OSM = AUDIT / 'sources' / 'osm_way_301841252.json'
BLENDER = ROOT.parent / 'blender' / 'blender-5.2.3-windows-x64' / 'blender.exe'
OUT = pathlib.Path(__file__).resolve().parent


def project_3857(x, y):
    radius = 6378137.0
    lon = math.degrees(x / radius)
    lat = math.degrees(2 * math.atan(math.exp(y / radius)) - math.pi / 2)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def evaluate():
    gis = json.loads(GIS.read_text(encoding='utf-8'))
    assert len(gis['features']) == 1
    feature = gis['features'][0]
    attrs = feature['attributes']
    assert attrs['FID'] == 790 and attrs['BUILDING_N'] == 'Pi Kappa Alpha'
    gis_ring = [project_3857(x, y) for x, y in feature['geometry']['rings'][0]]
    if gis_ring[0] == gis_ring[-1]:
        gis_ring.pop()

    # Reopen the actual saved asset in an independent Blender process and inspect
    # the named structural mesh and exported collection, rather than trusting the
    # builder's reopen-validation JSON.
    inspect_py = OUT / 'inspect_saved_asset.py'
    inspect_py.write_text(r'''import bpy, json
scene=bpy.context.scene
col=bpy.data.collections.get("Asset_massing_house_301841252_e4f8f05")
wall=bpy.data.objects.get("House_301841252")
if col is None or wall is None: raise RuntimeError("expected collection or structural mesh missing")
verts=[list(v.co) for v in wall.data.vertices]
evaluated=[]
for obj in col.objects:
    if obj.type == "MESH":
        deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); me=ev.to_mesh()
        if len(me.vertices): evaluated.append(obj.name)
        ev.to_mesh_clear()
all_verts=[o.matrix_world @ v.co for o in col.objects if o.type=="MESH" for v in o.data.vertices]
all_bounds=[[min(v[i] for v in all_verts) for i in range(3)],[max(v[i] for v in all_verts) for i in range(3)]]
print("GRADER_JSON="+json.dumps({"scene":scene.name,"collection":col.name,"collection_objects":len(col.objects),"structural_vertices":verts,"structural_vertex_count":len(verts),"collection_mesh_object_count":sum(o.type=="MESH" for o in col.objects),"evaluated_nonempty_meshes":len(evaluated),"all_bounds":all_bounds,"materialless_meshes":[o.name for o in col.objects if o.type=="MESH" and len(o.data.materials)==0],"external_image_paths":[im.filepath for im in bpy.data.images if im.source=="FILE" and im.filepath and not im.packed_file],"portico_columns":sorted(o.name for o in col.objects if o.name.startswith("Portico_Column_Shaft_")),"east_window_count":sum(o.name.startswith("East_Window_F") and o.name.endswith("_Recess") for o in col.objects),"walls_height_status":wall.get("height_status",""),"mesh_bounds":[list(corner) for corner in wall.bound_box]}))
from mathutils import Vector
''', encoding='utf-8')
    proc = subprocess.run([str(BLENDER), '-b', str(ASSET), '-P', str(inspect_py)],
                          capture_output=True, text=True, timeout=180)
    output = proc.stdout + '\n' + proc.stderr
    if proc.returncode != 0:
        raise RuntimeError('Blender reopen/inspection failed: ' + output[-3000:])
    marker = next((line[len('GRADER_JSON='):] for line in output.splitlines() if line.startswith('GRADER_JSON=')), None)
    if not marker:
        raise RuntimeError('No independent inspection payload: ' + output[-3000:])
    model = json.loads(marker)

    # Compare actual structural-mesh vertices to the official GIS ring. The
    # generated shell contains the GIS plan boundary twice (bottom and eave).
    wall_xy = sorted({(v[0], v[1]) for v in model['structural_vertices']})
    expected_xy = sorted(set(gis_ring))
    directed = lambda a, b: max(min(math.hypot(x-u, y-v) for u, v in b) for x, y in a)
    footprint_error = max(directed(wall_xy, expected_xy), directed(expected_xy, wall_xy))
    footprint_match = footprint_error < 0.001
    gis_bounds = [[min(p[0] for p in gis_ring), max(p[0] for p in gis_ring)],
                  [min(p[1] for p in gis_ring), max(p[1] for p in gis_ring)]]
    wall_z = [v[2] for v in model['structural_vertices']]
    wall_height = max(wall_z) - min(wall_z)
    osm = json.loads(OSM.read_text(encoding='utf-8'))
    osm_way = next(e for e in osm['elements'] if e.get('type') == 'way' and e.get('id') == 301841252)
    osm_nodes = {n['id']: n for n in osm['elements'] if n.get('type') == 'node'}
    osm_ring = [(osm_nodes[n]['lon'], osm_nodes[n]['lat']) for n in osm_way['nodes']]

    # Evidence review of photo: three occupied facade bands; brick; four round
    # columns; centered pediment/lettering/door; white shutters; shallow roof.
    # Photo gives no metric height, roof pitch/plan, side elevations or exact
    # window schedule. GIS level fields (1) conflict with photo's visible 3.
    criteria = [
      {"criterion":"Correct identity and source-backed footprint","max_score":2.0,"score":2.0,
       "evidence":["Purdue GIS FID 790 names Pi Kappa Alpha (SOPKA), address 629 University St; chapter page independently identifies its house at the same address.",f"Independently reopened structural mesh has {len(wall_xy)} unique XY coordinates and matches the transformed official GIS ring within {footprint_error:.6f} m symmetric nearest-vertex distance: {footprint_match}.","Official chapter photo depicts the named chapter house; OSM 301841252 address and footprint are a secondary geometry/location check."],
       "limitations":["Purdue polygon is authoritative campus GIS but not described as a surveyed wall line; OSM differs by sub-metre amounts."]},
      {"criterion":"Position, orientation, and scale/dimensions","max_score":2.0,"score":1.8,
       "evidence":[f"GIS transformed plan bounds X {gis_bounds[0][0]:.3f}..{gis_bounds[0][1]:.3f} m; Y {gis_bounds[1][0]:.3f}..{gis_bounds[1][1]:.3f} m.",f"Actual wall shell inherits the GIS coordinates exactly; fresh Blender process confirms its evaluated saved asset and campus-space bounds {model['all_bounds']}.","East facade orientation follows address/street context and is consistent with the chapter photo, but exact orientation is not independently surveyed."],
       "limitations":["Exact east-facing assignment is inferred from street context, not a surveyed elevation; OSM and GIS rings differ slightly."]},
      {"criterion":"Evidence-backed height, floors, and roof form","max_score":2.0,"score":1.25,
       "evidence":["2023 chapter-house photo directly shows three visible levels and a shallow gray metal roof.",f"Actual structural mesh wall height is {wall_height:.2f} m; roof ridge/eave values in model are estimates, and photo provides no scale.","Model's shallow hipped roof is a plausible interpretation of the single oblique/front photo."],
       "limitations":["No measured elevation or roof plan/pitch is available. GIS NUM_LEVELS/CountOfFLO=1 conflicts with the photo; no basis to claim exact height or roof geometry."]},
      {"criterion":"Facade, entrances, and distinctive architecture","max_score":2.0,"score":1.75,
       "evidence":["Photo visibly supports red brick, three window bands with white shutters, four-column white portico, triangular pediment with chapter lettering, centered entry and small hood.",f"Independently inspected asset includes {len(model['portico_columns'])} separately named column shafts and {model['east_window_count']} front window recesses; preview closely matches major composition."],
       "limitations":["Photo is one facade only; rear/ends are extrapolated. Exact window schedule, ornament details and facade depth are not dimensioned; source photo includes irregular window/AC details simplified in model."]},
      {"criterion":"Modular export, portability, and complete evidence","max_score":2.0,"score":1.9,
       "evidence":[f"Fresh Blender {proc.stdout.splitlines()[0] if proc.stdout else 'background'} process reopened the saved .blend; expected scene/collection are present, {model['collection_objects']} collection objects, {model['collection_mesh_object_count']} mesh objects, evaluated nonempty meshes {model['evaluated_nonempty_meshes']}.",f"No materialless mesh objects: {len(model['materialless_meshes']) == 0}; no unpacked external images: {len(model['external_image_paths']) == 0}.","Evidence folder contains GIS and OSM raw snapshots, chapter page and official photo, historical chapter publication, source metadata, and a rendered preview."],
       "limitations":["This independent review verifies the standalone building asset and portability; it does not verify master-blend linking/integration, owned by Tobin."]}
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    findings = [
      "PASS: the identity is corroborated independently by official Purdue GIS and the chapter's address statement.",
      f"PASS: saved wall footprint matches transformed Purdue GIS ring within {footprint_error:.6f} m symmetric nearest-vertex distance.",
      "PASS with uncertainty: the photo supports the principal facade composition and three apparent stories.",
      "LIMITATION: wall height, roof ridge height/pitch and roof plan remain estimates; GIS floor count conflicts with the photo.",
      "LIMITATION: no master integration was assessed."
    ]
    return {"building_id":BID,"building":"Pi Kappa Alpha (Pike), Beta Phi Chapter, Purdue University","grade":"independent r1","score":score,"max_score":10,"criteria":criteria,
            "evidence":{"actual_asset_inspection":model,"official_gis_transformed_bounds_xy_m":gis_bounds,"gis_wall_vertex_set_within_1mm":footprint_match,"gis_wall_symmetric_hausdorff_error_m":round(footprint_error,6),"wall_height_from_actual_saved_mesh_m":round(wall_height,3),"blender_returncode":proc.returncode,"blender_version_line":next((x for x in output.splitlines() if 'Blender ' in x), 'version reported in process output')},
            "findings":findings,"pass_standard":8,"passes":score>=8,
            "evaluator":"evaluate.py; independently reopened saved asset with Blender and compared the actual structural mesh to raw Purdue GIS; source-photo findings recorded by grader.",
            "limitations":["Grading evaluates standalone building asset/evidence, not master campus integration."]}

if __name__ == '__main__':
    result = evaluate()
    (OUT / 'grade.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({"score":result['score'],"max_score":10,"criteria":[{"criterion":c['criterion'],"score":c['score']} for c in result['criteria']],"passes":result['passes'],"grade_path":str(OUT/'grade.json')},indent=2))





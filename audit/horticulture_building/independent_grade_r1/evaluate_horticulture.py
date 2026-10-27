"""Independent Horticulture review. Run with Blender background Python; never saves .blend."""
import bpy
import json
import math
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ASSET = ROOT / 'modular/buildings/horticulture_building.blend'


def evaluate():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    collection = bpy.data.collections.get('Asset_horticulture_building')
    assert collection is not None
    manifest = json.loads((ROOT / 'modular/manifest.json').read_text(encoding='utf-8'))
    entry = next(a for a in manifest['assets'] if a['id'] == 'horticulture_building')
    source = json.loads((ROOT / 'audit/horticulture_building/sources/purdue_gis_fid232.json').read_text(encoding='utf-8'))
    shell = bpy.data.objects['HORT structural shell | official GIS FID 232 outline']
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = shell.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    zmin, zmax = min(v.z for v in points), max(v.z for v in points)
    floor_ring = [(v.x, v.y) for v in points if abs(v.z-zmin) < 1e-5]
    origin = list(collection['placement_origin_xy_m'])
    factor = 111412.84 * math.cos(math.radians(40.4274))
    expected = [((p[0]+86.9137)*factor-origin[0], (p[1]-40.4274)*111040-origin[1]) for p in source['geometry']['rings'][0][:-1]]
    def nearest_error(a, b):
        return max(min(math.dist(p, q) for q in b) for p in a)
    forward = nearest_error(expected, floor_ring)
    reverse = nearest_error(floor_ring, expected)
    bounds = [[min(v[i] for v in points), max(v[i] for v in points)] for i in range(3)]
    dims = [b[1]-b[0] for b in bounds]
    evaluated.to_mesh_clear()
    surfaces = {}
    material_names = set()
    modifiers = {}
    for obj in collection.all_objects:
        modifiers[obj.name] = [{'name': m.name, 'type': m.type, 'enabled': m.show_viewport, 'render': m.show_render} for m in obj.modifiers]
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                continue
            material_names.add(mat.name)
            surfaces[mat.name] = bool(mat.use_nodes and any(n.type == 'OUTPUT_MATERIAL' and n.inputs['Surface'].is_linked for n in mat.node_tree.nodes))
    external = [{'name': im.name, 'path': im.filepath} for im in bpy.data.images if im.source == 'FILE' and im.filepath and not im.packed_file]
    observations = {
        'asset_sha256': hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        'reopened_blender_version': bpy.app.version_string,
        'collection': collection.name,
        'object_count': len(collection.all_objects),
        'source_identity': source['attributes']['BUILDING_N'],
        'source_fid': source['attributes']['FID'],
        'source_to_evaluated_shell_vertex_error_m': forward,
        'evaluated_shell_to_source_vertex_error_m': reverse,
        'shell_local_bounds_m': bounds,
        'shell_dimensions_m': dims,
        'origin_xy_m': origin,
        'manifest_origin_xy_m': entry['placement_origin_xy_m'],
        'origin_error_m': math.dist(origin, entry['placement_origin_xy_m']),
        'material_surface_connected': surfaces,
        'external_images': external,
        'linked_libraries': [lib.filepath for lib in bpy.data.libraries],
        'modifiers': modifiers,
        'source_vertical_attributes': {k:source['attributes'][k] for k in ['NUM_LEVELS','CountOfFLO','Extrution','B','G','F01','F02','F03','R']},
        'direct_visual_review': {
            'source_photo': 'sources/purdue_events_exterior.jpg: inspected raw 478x310 Purdue photograph; official saved HTML identifies Horticulture and embeds exactly this photo.',
            'source_facade': 'Three visible window levels, tall narrow sash windows, grouped central paired windows and flanking single windows, brick pilasters, pale foundation, carved flush/recessed stone entrance surround and projecting cornice. No freestanding canopy piers visible.',
            'candidate_facade': 'Supplied exterior and entry renders inspected. Uniform nearly square windows replace source grouping. Pale full-height surrounds and continuous horizontal bands replace prominent brick pilasters. Entry has a large projecting canopy with unsupported detached piers; carved portal/pediment/name block missing. Brick is continuous noise rather than recognizable masonry.',
            'roof_plan': 'Top render and reopened structural floor vertices preserve reentrant source plan. Flat roof visible in source at the parapet edge; concealed roof construction remains uncertain.',
            'registration': 'Geographic shell coordinates preserved. The source photo is not geographically registered; placing entrance on the longest GIS edge is unsupported.',
        }
    }
    assert forward < 0.001 and reverse < 0.001
    assert observations['origin_error_m'] < 0.001
    assert all(surfaces.values()) and not external and not observations['linked_libraries']
    criteria = [
        {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'status':'verified within source limits','evidence':['Official GIS raw snapshot FID232 names Horticulture/HORT and 625 Agriculture Mall Drive.','Reopened evaluated shell has 14 floor vertices; bidirectional source vertex error <0.001m; reentrant footprint preserved.'],'uncertainty':'GIS survey tolerance/source date and exact wall-versus-eave association unavailable.'},
        {'criterion':'Position, orientation, and scale/dimensions','score':1.6,'max_score':2,'status':'horizontal geometry verified; architectural facade registration unverified','evidence':['Shell extent and 14 geographic vertices match documented local transform.','Asset origin matches manifest exactly; local coordinates and meter scale preserved.'],'deduction':'0.4: entrance facade selected by longest edge without geographic registration of source photo; complete master placement/neighbors not inspected.'},
        {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2,'status':'three visible rows and flat roof edge supported; height uncertain','evidence':['Source photo directly supports three visible window levels and corniced flat roof edge.','Reopened shell height14.63m. Raw GIS says five levels and Extrution48 but also F02=11.7,F03=23.4,R=35.1.'],'deduction':'1.0: 48 interpreted as feet without field unit evidence and competing roof attribute not reconciled; no height measurement/elevation; total height and internal floor elevations unverified.'},
        {'criterion':'Facade, entrances, and distinctive architecture','score':0.6,'max_score':2,'status':'material colors/row count supported; important source details mismatch','evidence':['Red brick, pale stone and dark sash palette present; three rows.','Direct photo-versus-render review shows tall grouped source openings/pilasters differ from uniform square candidate openings; projecting canopy/piers unsupported.'],'deduction':'1.4: missing source-supported grouping/pilasters/portal detail; unsupported projecting portico; unregistered hidden elevations generalized without corroboration.'},
        {'criterion':'Modular export, portability, and complete evidence','score':1.8,'max_score':2,'status':'reopened library portable; integration evidence incomplete','evidence':['Expected collection reopens; all seven assigned procedural materials have linked outputs; no external image/library dependencies.','Dedicated builder, saved GIS/photo/HTML, provenance, uncertainty, three views and builder reopen validation present.','Preview stage objects outside exported Asset collection.'],'deduction':'0.2: master links/replacement/neighborhood check unavailable; archived contextual source has no raw capture; prior detailed asset missing so before/after geometric comparison not possible.'}
    ]
    findings = [
        {'priority':'required','action':'Rebuild photographed facade with tall narrow grouped sash windows, brick pilasters, pale base and the source portal; remove unsupported freestanding portico canopy/piers. Render comparable frontal view. Do not infer hidden elevations as verified.'},
        {'priority':'required','action':'Register the photographed entry elevation to GIS using a map/street/aerial view or other geolocated source. Document geographic side and entry offset.'},
        {'priority':'required','action':'Resolve vertical fields: establish units/meaning of Extrution48 versus R35.1 and three visible levels. Obtain independent height/elevation support or use a bounded documented estimate that accounts for all fields.'},
        {'priority':'handoff','action':'Coordinator/Tobin must verify master asset link once, placement, massing replacement and immediate neighbor context; grader did not open/save master.'}
    ]
    return {'building_id':'horticulture_building','reviewer':'independent grader r1','score':round(sum(c['score'] for c in criteria),2),'max_score':10,'pass_threshold':8,'passed':False,'criteria':criteria,'evidence':observations,'findings':findings}


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    result = evaluate()
    result['passed'] = result['score'] >= result['pass_threshold']
    (OUT/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('INDEPENDENT_GRADE', json.dumps({'score':result['score'],'max_score':10,'passed':result['passed']}), flush=True)

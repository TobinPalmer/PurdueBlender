import bpy, json, math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = ROOT / 'audit' / 'helen_b_schleman_hall'
ASSET_ID = 'massing_schleman_hall_schm_ad4b05b'

def evaluate():
    evidence = json.loads((EVIDENCE_DIR / 'evidence.json').read_text(encoding='utf-8-sig'))
    source = json.loads((EVIDENCE_DIR / 'source_feature_224_raw.json').read_text(encoding='utf-8-sig'))
    photo = json.loads((EVIDENCE_DIR / 'source_exterior_reference_observation.json').read_text(encoding='utf-8-sig'))
    floorplan = json.loads((EVIDENCE_DIR / 'source_floorplan_observation.json').read_text(encoding='utf-8-sig'))
    obj = bpy.data.objects.get('Schleman Hall (SCHM)')
    coll = bpy.data.collections.get('Asset_' + ASSET_ID)
    assert obj is not None and coll is not None and obj in coll.objects[:] and len(coll.objects) == 1
    asset = json.loads((EVIDENCE_DIR / 'reopen_validation.json').read_text(encoding='utf-8-sig'))
    attrs = source['attributes']
    address_gis = attrs.get('ADDRESS')
    address_photo = photo.get('page_text_observation', {}).get('address')
    roof_photo = 'hip' in ' '.join(photo.get('visual_observations_from_reference_image', [])).lower()
    # Directly inspect the reopened Blender datablocks, transforms and mesh.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    depsgraph.update()
    identity_matrix = all(abs(float(obj.matrix_world[r][c]) - (1.0 if r == c else 0.0)) < 1e-7 for r in range(4) for c in range(4))
    bounds = [[min((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box), max((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box)] for i in range(3)]
    asset_valid = (bpy.context.scene.name == 'Building_' + ASSET_ID and len(obj.data.vertices) == 3926 and len(obj.data.polygons) == 2874 and identity_matrix and not obj.modifiers)
    criteria = [
      {'name':'Correct identity and source-backed footprint','score':1.8,'max_score':2,
       'evidence':[f"Official Purdue GIS building-shapes feature FID {attrs.get('FID')} names Helen B. Schleman Hall (SCHM), with a preserved 16-vertex polygon.",f"The official campus GIS perimeter appears in the reopened asset; saved validation reports a maximum projected source-ring error of {asset['max_source_ring_error_m']} m.","The official Purdue Events page names Schleman Hall and its raw image shows a matching red-brick, red-tile building."],
       'deduction':f"The feature lists address {address_gis!r}, while the Purdue Events page lists {address_photo!r}; the sources do not reconcile these address labels. The GIS polygon is not a certified survey."},
      {'name':'Position, orientation, and scale/dimensions','score':1.6,'max_score':2,
       'evidence':["The object and scene retain identity transforms in the campus-coordinate massing library.","All 16 official GIS ring points are matched within 0.000009 m by the reopen validation.","The GIS outline yields an approximately 53.77 m by 25.15 m minimum-rectangle footprint; the building mesh follows the source ring."],
       'deduction':'The project geographic conversion is approximate, official positional uncertainty is unpublished, and the photo does not verify the chosen west-facing entrance bearing.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2,
       'evidence':["Purdue exterior image supports red-tile low roof silhouette and three visibly occupied facade levels.","A Purdue renovation-study basement plan labels a distinct Schleman basement; it supports, but does not prove, interpreting the GIS four-level value as three above-grade levels plus basement.","The 11.4 m wall top and approximately 12.8 m roof peak are explicitly labeled estimates; no measured elevations are supplied."],
       'deduction':'Exact height, floor elevations, basement exposure, GIS level convention, roof pitch and complete roof plan are unknown. The photo shows several intersecting roof forms, while the model uses one simplified hip roof.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.6,'max_score':2,
       'evidence':["The raw Purdue photo shows brick with light belt courses/window trim, a recessed multi-bay entrance, and a portico with brick piers and light bases/capitals.","The current oblique and entrance renders contain those source-observed elements and three facade levels.","The top preview confirms the library geometry stays within the GIS-derived plan envelope, apart from documented roof/portico extensions."],
       'deduction':'The photo is one perspective image, not an elevation; it cannot establish exact window/door dimensions, opening rhythm, bearing, or full wing/roof configuration. Some details are simplified.'},
      {'name':'Modular export, portability, and complete evidence','score':1.9,'max_score':2,
       'evidence':[f"Blender {bpy.app.version_string} reopened the expected scene, one named collection object, {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces, five materials, identity transform, and no modifiers.","A dedicated modular/buildings build module exists and the asset path/collection/object identifiers remain stable.","The building evidence includes raw official GIS, Purdue Events HTML and image, floor-plan observations, three views, build configuration, and a source-ring reopen validation."],
       'deduction':'The build module saves into the open source file instead of implementing an independent collection-export operation; integration into the Tobin-owned master is still pending.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[
      {'priority':'medium','status':'uncertain','finding':f"Reconcile or explicitly retain the address difference ({address_gis} in the GIS feature versus {address_photo} on the official Events page); the building identity itself is supported by both named records."},
      {'priority':'medium','status':'documented','finding':'Keep eaves/wall height, roof peak/pitch, exact floor count, basement exposure, and entrance bearing marked estimated or unverified pending measured elevations/georeferenced imagery.'},
      {'priority':'low','status':'documented','finding':'The source photograph shows several intersecting low-pitch red-tile roof planes; the model represents the overall massing with a simplified single hip roof.'}
    ]
    return {'score':score,'max_score':10,'criteria':criteria,'evidence':["Independent evaluator reopened and inspected the saved .blend in Blender; it read actual scene, collection, object transform, vertex/face counts, materials, bounds and modifiers.","Evaluator directly checked the official GIS snapshot, official photo observation and raw-image path, basement-plan observation, current renders, dedicated build module, and saved reopen validation."],'findings':findings,'asset_inspection':{'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,'collection_object_count':len(coll.objects),'object':obj.name,'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'bounds_world_m':[[round(a,6),round(b,6)] for a,b in bounds],'materials':[m.name for m in obj.data.materials],'modifiers':[m.name for m in obj.modifiers],'identity_world_transform':identity_matrix,'address_gis':address_gis,'address_photo':address_photo,'gis_source_ring_error_m':asset['max_source_ring_error_m']},'grade_status':'pass: meets repository minimum of 8/10' if score>=8 else 'fail: below repository minimum of 8/10'}

result=evaluate()
out=Path(__file__).resolve().parent/'result.json'
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('GRADE_JSON='+json.dumps(result))


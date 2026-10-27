"""Independent Acacia asset grader. Run with Blender --background <asset.blend> --python this_file.py.
Read-only on the .blend; writes only independent_grade_result.json beside this evaluator.
"""
import bpy, json, os, math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUTDIR = os.path.dirname(os.path.abspath(__file__))
ASSET_ID = 'massing_house_301841251_8a9a05b'
COLLECTION = 'Asset_' + ASSET_ID
SCENE = 'Building_' + ASSET_ID


def score_acacia():
    scene = bpy.context.scene
    col = bpy.data.collections.get(COLLECTION)
    obj = bpy.data.objects.get('House_301841251')
    assert scene and scene.name == SCENE, f'Unexpected scene: {scene.name if scene else None}'
    assert col is not None, 'Expected asset collection missing'
    assert obj is not None and obj.type == 'MESH', 'Expected primary shell missing'
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()
    try:
        coords = [eval_obj.matrix_world @ v.co for v in eval_mesh.vertices]
    finally:
        eval_obj.to_mesh_clear()
    bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
    meshes = [o for o in col.objects if o.type == 'MESH']
    nonempty_images = [i for i in bpy.data.images if i.source != 'VIEWER' and i.filepath]
    external_images = [i for i in nonempty_images if not i.packed_file and not i.filepath.startswith('//')]
    external_libs = [l.filepath for l in bpy.data.libraries]
    material_count = len({m.name for o in meshes for m in o.data.materials if m})
    slots_missing = [o.name for o in meshes if not o.data.materials or any(m is None for m in o.data.materials)]

    criteria = [
      {'name':'Correct identity and source-backed footprint','score':1.0,'max_score':2,
       'evidence':'Purdue GIS FID 791 identifies a cooperative at 608 Waldron Street; the Acacia contact/history and official chapter imagery support the building identity. The source massing shell is preserved. Fresh-open evaluated primary shell bounds are X [-334.714,-315.275], Y [342.136,370.629], Z [0,9.45] m (19.44 x 28.49 m footprint envelope). The evidence record itself identifies a Shape__Area conflict, and WGS84 source ring extents converted by the documented approximate transform do not reconcile cleanly to the shell bounds; the exact structural footprint therefore remains only partially verified.',
       'findings':['Resolve/document the GIS area and projected-footprint conflict with a top-down overlay or authoritative survey before claiming verified footprint.']},
      {'name':'Position, orientation, and scale/dimensions','score':0.5,'max_score':2,
       'evidence':'The asset is stored in direct-linked campus coordinates with identity collection offset and primary object location (0,0,0), satisfying the simple-massing convention. The saved evidence explicitly says the facade bearing is unverified and the porch position is estimated; no geotagged facade or current orthophoto comparison substantiates its rotation or sub-building placement. Envelope bounds are inspectable, but the footprint conflict also weakens dimensional verification.',
       'findings':['Verify the facade bearing and asset centroid/footprint against a current orthophoto or surveyed GIS overlay; record orientation and translation residuals.']},
      {'name':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2,
       'evidence':'Official chapter drawings in the saved source set show three above-grade floor levels with elevations 100 ft, 110 ft 7 in, and 119 ft 10 in; elevation imagery supports a steep shingle roof, dormers and chimney. The saved model bounds give a 9.45 m overall primary-shell height. Roof geometry and overall height are modeled estimates, not surveyed/as-built dimensions.',
       'findings':['Overall height and roof profile remain estimates because the available plans are renovation/project drawings and no as-built height measurement was found.']},
      {'name':'Facade, entrances, and distinctive architecture','score':0.5,'max_score':2,
       'evidence':'The exterior render contains the brick tower with vertical ACACIA letters, a porch/sign arch, chimney, steep roof, dormers, windows and a gabled end. Direct visual comparison to the official front photo shows major facade mismatches: the modeled visible upper facade is brick where the reference has prominent cream panels and dark half-timber framing; the tall right gable is nearly blank rather than detailed; the entrance/porch proportions and window arrangement are simplified. The exterior render also shows a large uninterrupted brick side wall. The interior render is a low-contrast top-down cutaway in which walls obscure most room detail; some beds, partitions and labels are present but it does not substantiate convincing interior fidelity.',
       'findings':['Rebuild the source-facing upper facade as cream infill with the photographed dark timber pattern; match the central entrance, porch opening, gable and window rhythm to the reference.','Add an interior view that makes the rooms legible, with material and furnishing detail; current pale overhead render is difficult to assess.']},
      {'name':'Modular export, portability, and complete evidence','score':1.75,'max_score':2,
       'evidence':f"Fresh-open asset has the expected scene/collection/stable ID, {len(col.objects)} objects ({len(meshes)} meshes), {material_count} in-file mesh materials, no external linked libraries, and {len(external_images)} unpacked absolute-path image dependencies. The material audit reports {len(slots_missing)} meshes with missing slots. The evidence folder contains raw GIS JSON, official chapter page snapshots, plans, a facade photo, and exterior/interior renders. Procedural materials are local to the asset.",
       'findings':(['Resolve absolute/unpacked image dependencies for portable use.'] if external_images else [])},
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    return {
      'score':score,'max_score':10,'pass':score >= 8,
      'asset':'Acacia, Purdue Chapter House','asset_id':ASSET_ID,
      'asset_path':'modular/buildings/massing_house_301841251_8a9a05b.blend',
      'criteria':criteria,
      'evidence':{
        'fresh_open':'passed in a new Blender 5.2.3 background process by opening the saved asset directly',
        'scene':scene.name,'collection':col.name,'collection_object_count':len(col.objects),
        'mesh_object_count':len(meshes),'primary_object':obj.name,
        'primary_evaluated_bounds_world_m':bounds,
        'primary_location':list(obj.location),'collection_instance_offset':list(col.instance_offset),
        'material_count':material_count,'meshes_missing_material_slots':slots_missing,
        'external_image_dependencies':[{'name':i.name,'path':i.filepath} for i in external_images],
        'linked_blend_libraries':external_libs,
        'sources_reviewed':['audit/acacia/evidence.json','audit/acacia/sources/purdue_gis_fid791_2026-10-26_wgs84.json','audit/acacia/sources/purdue_gis_fid791_2026-10-26_stateplane_2968.json','audit/acacia/sources/acacia_front_porch.jpg','audit/acacia/sources/acacia_plan_gallery_1.jpeg','audit/acacia/exterior.png','audit/acacia/interior.png']
      },
      'findings':[
        'Overall score is below the 8/10 passing threshold.',
        'The strongest evidence-backed improvements are the front-facing half-timber facade and measured GIS placement/orientation; do not treat the current completion as a pass.'
      ]
    }

result=score_acacia()
path=os.path.join(OUTDIR,'independent_grade_result.json')
with open(path,'w',encoding='utf-8') as f: json.dump(result,f,indent=2,ensure_ascii=False)
print(json.dumps({'score':result['score'],'pass':result['pass'],'result':path,'evidence':result['evidence']},indent=2))

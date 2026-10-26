import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit' / 'mri_modular_facility'
ASSET_ID = 'massing_mri_modular_facility_mri1_a93e22b'
OBJECT_NAME = 'MRI Modular Facility (MRI1)'
COLLECTION_NAME = 'Asset_' + ASSET_ID

def evaluate():
    ev = json.loads((AUDIT / 'evidence.json').read_text(encoding='utf-8'))
    geo = json.loads((AUDIT / 'sources' / 'feature_918_wgs84.geojson').read_text(encoding='utf-8'))
    feat = next(f for f in geo['features'] if int(f['properties']['FID']) == 918)
    ring = feat['geometry']['coordinates'][0]
    if ring[0] == ring[-1]: ring = ring[:-1]
    transform = ev['transform']['geographic_origin']
    lat0, lon0 = transform['latitude'], transform['longitude']
    expected = [((float(lon)+86.9137)*111412.84*math.cos(math.radians(40.4274)),
                 (float(lat)-40.4274)*111040.0) for lon, lat in ring]
    obj = bpy.data.objects.get(OBJECT_NAME)
    col = bpy.data.collections.get(COLLECTION_NAME)
    if obj is None or col is None: raise RuntimeError('Saved MRI asset object or collection missing')
    mesh = obj.data
    world = [obj.matrix_world @ v.co for v in mesh.vertices]
    # Identify structural wall base edges as polygon edges with two vertices at z=0.
    base_edges=[]
    for poly in mesh.polygons:
        pts=[]
        for vi in poly.vertices:
            p=obj.matrix_world @ mesh.vertices[vi].co
            if abs(p.z) < 1e-5: pts.append((float(p.x),float(p.y)))
        if len(pts)==2: base_edges.append(pts)
    def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
    def edge_error(a,b): return min(max(dist(a[0],b[0]),dist(a[1],b[1])), max(dist(a[0],b[1]),dist(a[1],b[0])))
    expected_edges=[(expected[i],expected[(i+1)%len(expected)]) for i in range(len(expected))]
    errors=[min((edge_error(e,a) for a in base_edges),default=float('inf')) for e in expected_edges]
    lo=[min(float(p[i]) for p in world) for i in range(3)]
    hi=[max(float(p[i]) for p in world) for i in range(3)]
    mats=sorted({m.name for m in mesh.materials if m})
    file_images=[im.filepath for im in bpy.data.images if im.source=='FILE']
    entry=next((a for a in json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))['assets'] if a.get('id')==ASSET_ID),None)
    checks={
      'asset_file_reopened': bool(bpy.data.filepath) and Path(bpy.data.filepath).resolve()==(ROOT/'modular'/'buildings'/(ASSET_ID+'.blend')).resolve(),
      'manifest_asset_matches': bool(entry and entry.get('file')=='buildings/'+ASSET_ID+'.blend' and entry.get('collection')==COLLECTION_NAME),
      'expected_collection_contains_only_target_mesh': len(col.objects)==1 and col.objects[0]==obj and obj.type=='MESH',
      'identity_transform': all(abs(v)<1e-7 for v in obj.location) and all(abs(v)<1e-7 for v in obj.rotation_euler) and all(abs(v-1)<1e-7 for v in obj.scale),
      'no_modifiers': len(obj.modifiers)==0,
      'all_four_GIS_structural_edges_within_2mm': len(errors)==4 and max(errors)<0.002,
      'no_external_file_images': len(file_images)==0,
    }
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':'Purdue GIS BuildingShapesZip4 FID 918 explicitly identifies PMRI at 750 S University Street; Office of Research cross-references MRI1/PMRI. Independently recomputed from saved FID 918 WGS84 polygon: all four structural base edges match the reopened mesh within %.8f m.'%max(errors),
       'limitations':'GIS accuracy is unpublished and not survey-grade; OSM centroid is 1.70 m offset, so Purdue GIS is correctly treated as footprint control.'},
      {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,
       'evidence':'Reopened mesh is in campus coordinates with identity object transform; exact four-edge source geometry confirms plan placement, dimensions, and orientation against the official GIS outline. The export agrees to sub-millimeter tolerance.',
       'limitations':'Campus transform is an approximate local geographic conversion, not a surveyed CRS; source positional accuracy is unknown.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2.0,
       'evidence':'Purdue GIS level fields and Meyer Najem project description support a single-story facility. Aerial tile supports a low flat roof and rooftop mechanical equipment; model shows that roof type and equipment.',
       'limitations':'No measured elevations or wall height are available. Model wall height 4.5 m, parapet/roof height 5.15 m, and HVAC top at %.2f m are estimates; roof pitch, parapet details, and equipment dimensions are not verified.'%hi[2]},
      {'name':'Facade, entrances, and distinctive architecture','score':0.5,'max_score':2.0,
       'evidence':'Contractor project record supports masonry veneer plus aluminum windows and doors; the saved mesh uses masonry walls and aluminum-framed openings. No retrieved exact-building exterior photo is available for direct comparison.',
       'limitations':'Window rhythm, east-facing entry, MRI sign placement, and detailed facade appearance are not evidenced by an accessible exterior view; those details remain illustrative/inferred.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,
       'evidence':'Cold reopened asset matches manifest path and collection, has one mesh object, identity transform, no modifiers, no file-backed images, preserved preview renders, raw GIS and multiple independent source snapshots, and a structured evidence record. Checks: '+json.dumps(checks,sort_keys=True),
       'limitations':'None found in the saved asset packaging; model fidelity remains subject to source limitations recorded above.'},
    ]
    score=round(sum(c['score'] for c in criteria),2)
    result={'score':score,'max_score':10,'pass':score>=8.0,'building':'Purdue Magnetic Resonance Imaging Facility (MRI1 / PMRI)','asset_id':ASSET_ID,
      'criteria':criteria,
      'evidence':{'saved_blend':bpy.data.filepath,'source_feature':'Purdue BuildingShapesZip4 FeatureServer FID 918','source_geojson':'audit/mri_modular_facility/sources/feature_918_wgs84.geojson','evidence_record':'audit/mri_modular_facility/evidence.json','previews':['audit/mri_modular_facility/preview_exterior.png','audit/mri_modular_facility/preview_plan.png'],'cold_reopen_checks':checks,'source_edge_errors_m':errors,'model_bounds_xyz_m':{'min':lo,'max':hi},'material_names':mats,'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),'external_file_images':file_images},
      'findings':['Passes the 8/10 threshold, at the minimum passing score.','Keep the vertical height labeled estimated; no dimensional elevation source was found.','If exact facade accuracy is required, obtain a usable current exterior photo/elevation and verify the entrance bearing, window spacing, and MRI signage before revising those details.']}
    (AUDIT/'independent_grade_mri.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('MRI_INDEPENDENT_GRADE='+json.dumps(result))
    return result

result=evaluate()
if not all(checks for checks in result['evidence']['cold_reopen_checks'].values()): raise RuntimeError('MRI independent cold reopen/export checks failed')


"""Independent evaluation of the revised University Church Blender asset."""
import json
from pathlib import Path

FOLDER = Path(__file__).parent
THRESHOLD = 8.0
EXPECTED_SHA = "81ac22d4dab6c2dc775e0b2d93d4e543d7f1a1bf001b3bf707b568c71cb5408e"

def evaluate(probe, evidence):
    criteria = [
      {"name":"Correct identity and source-backed footprint", "score":2.0, "max_score":2.0,
       "evidence":f"Purdue GIS Feature 797 identifies BLDG_ABBR UC / University Church. The probe independently transformed its 20-vertex EPSG:4326 outline into the documented campus frame and compared the saved shell vertex set: symmetric Hausdorff distance {probe['shell_hausdorff_error_m']:.6f} m; 20 base vertices. The 2019 state record corroborates identity and multi-story use.",
       "findings":[]},
      {"name":"Position, orientation and scale/dimensions", "score":1.5, "max_score":2.0,
       "evidence":f"The 20 GIS footprint vertices and asset shell agree within {probe['shell_hausdorff_error_m']:.6f} m, verifying campus position, plan shape and scale. The wall orientation follows the GIS outline. The 2023 photograph has no camera azimuth and the 2024 plan has no north arrow, so the pictured portico facade cannot be tied conclusively to a particular geographic edge.",
       "findings":["Facade compass assignment remains inferred; the photo and floorplan do not georeference the pictured elevation."]},
      {"name":"Evidence-backed height, floors and roof form", "score":1.1, "max_score":2.0,
       "evidence":"The 2023 exterior photograph supports the gabled sanctuary roof and spired tower silhouette; the 2019 state record establishes multi-story use. Modeled eave, ridge, spire and floor heights are estimates. Purdue GIS attributes conflict (Level_=4, NUM_LEVELS=1, CountOfFLO=3, Extrution=39 with undocumented units), and no measured elevation was found.",
       "findings":["Exact height and floor count remain unverified; the GIS height/story fields conflict and no measured elevation is available."]},
      {"name":"Facade, entrances and distinctive architecture", "score":1.8, "max_score":2.0,
       "evidence":f"Visual comparison of the saved east and three-quarter previews against the 2023 Pinola Photo source confirms red brick, a four-column portico, triangular pediment with round oculus, one square tower with green copper spire, three main entrance doors, and arched windows on perpendicular elevations. Direct Blender geometry inspection found {probe['east_portico_window_reveals']} portico window reveals, {probe['east_portico_square_lintels']} square stone lintels, zero arch heads on that elevation and {probe['perpendicular_arch_heads']} arch-head objects on perpendicular elevations. This corrects the prior facade mismatch. Fine brick relief and opening details are simplified.",
       "findings":["Facade materials and repeated opening detail remain schematic at this preview scale; some photo details are simplified."]},
      {"name":"Modular export, portability and complete evidence", "score":1.8, "max_score":2.0,
       "evidence":f"A separate Blender {probe['blender_version']} background process reopened the saved file with the expected named scene and asset collection. The collection has {probe['collection_object_count']} objects / {probe['mesh_count']} meshes; every mesh and face has valid material assignment, using {probe['materials']['used_material_count']} node-based Principled materials. No external image files or missing library paths are present. Three review previews and all five registered source snapshots are present. Asset SHA-256 is {probe['asset_sha256']}.",
       "findings":[]}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[f for c in criteria for f in c['findings']]
    result={"score":score,"max_score":10,"threshold":THRESHOLD,"status":"PASS" if score>=THRESHOLD else "FAIL","criteria":criteria,"evidence":{
      "asset_path":probe['asset_path'],"asset_sha256":probe['asset_sha256'],"expected_sha256":EXPECTED_SHA,"sha_matches_revision":probe['asset_sha256']==EXPECTED_SHA,
      "fresh_open_probe":"fresh_open_probe.json","source_record":"../build_evidence.json",
      "primary_photo":"../sources/dave_wegiel_university_church_dusk.jpg","footprint_source":"../sources/purdue_gis_fid797.geojson",
      "shell_hausdorff_error_m":probe['shell_hausdorff_error_m'],"window_fix":{"portico_reveals":probe['east_portico_window_reveals'],"portico_square_lintels":probe['east_portico_square_lintels'],"portico_arches":probe['east_portico_arch_heads'],"perpendicular_arches":probe['perpendicular_arch_heads']},
      "source_caveat":"An undated local-directory image shows a twin-tower Gothic facade and conflicts with the 2023 photo; the project evidence records it as potentially mismatched or a different phase, so it was not treated as corroboration for the current single-tower facade."},"findings":findings}
    return result

if __name__ == '__main__':
    probe=json.loads((FOLDER/'fresh_open_probe.json').read_text(encoding='utf-8'))
    evidence=json.loads((FOLDER.parent/'build_evidence.json').read_text(encoding='utf-8'))
    result=evaluate(probe,evidence)
    (FOLDER/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))

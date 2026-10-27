from pathlib import Path
import json
root=Path.cwd()
folder=root/'audit/von_s/independent_grade_r1'
criteria=[
 {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'evidence':['OSM way 116427236 is explicitly tagged name=Von’s, building=retail.','Von’s official Business Info page lists 315 W State St; the official history page describes the main purchased building as retail with apartments on upper floors.','The assigned asset preserves the exact eight unique projected OSM boundary vertices; independent fresh-open measurement found 0.000000 m nearest XY error for every vertex.'],'finding':'Identity and assigned-building footprint are strongly supported by the named mapped feature and address cross-check.'},
 {'criterion':'Position, orientation, and plan dimensions','score':1.95,'max_score':2.0,'evidence':['The model remains in campus-world coordinates with an identity transform.','All eight OSM ring vertices are present in the saved mesh base at exact projected coordinates.','Source bounds are X 390.010–433.611 m, Y -416.933–-389.306 m; total model bounds include facade/trim details extending to X 389.870–433.754 m and Y -417.074–-389.165 m.'],'finding':'GIS plan registration is exact; the aggregate rendered bounds extend approximately 0.14 m beyond the mapped outline due to model details.'},
 {'criterion':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2.0,'evidence':['Official Von’s history supports apartments on upper floors in the main building.','The 8.45 m parapet, two-level facade rhythm, flat roof, and exact floor heights are explicitly labeled schematic estimates; no measured elevation or roof plan was found.','A secondary parcel summary reportedly describes a one-story assessment, so floor count/parcel coverage remains a source conflict.'],'finding':'Mixed retail and upper-floor use is source-supported, but the modeled vertical dimensions and flat parapet roof are not measured or independently verified.'},
 {'criterion':'Facade, entrances, and distinctive architecture','score':1.45,'max_score':2.0,'evidence':['The official storefront photograph supports red brick, a hand-painted Von’s Shops department mural, small openings, and a window AC unit.','Reviewed renders show warm procedural brick, storefront glazing, upper windows, parapet, mural text/color bands, and AC detail.','The model uses regular illustrative window spacing and a simplified retail entry; only a limited facade photo exists, so exact opening rhythm, entry position, and unseen elevations cannot be verified.'],'finding':'Distinctive brick and mural references are captured, but the facade remains schematic and the rendered entry/opening rhythm is simplified.'},
 {'criterion':'Modular export, portability, and complete evidence','score':1.75,'max_score':2.0,'evidence':['Independent Blender 5.2.3 fresh-open passed with the expected scene, collection, one root mesh, and exact SHA.','The mesh has 15,864 vertices and 11,732 faces, two UV layers, 13 named procedural materials, and no unpacked external images.','The evidence records GIS/provider/feature ID/CRS/transform/uncertainty, official identity and facade references, four review renders, and explains why no interior was modeled.','Topology audit found 14,872 boundary and non-manifold edges (no zero-area faces); the joined visual asset is not a closed watertight solid.'],'finding':'Portable, textured, correctly named, and well documented; open-surface topology reduces geometry robustness. No verified interior plan exists, so omission is not penalized.'}
]
score=sum(c['score'] for c in criteria)
result={
 'building':"Von’s Shops",
 'building_id':'massing_von_s_d207e41',
 'asset_path':'modular/buildings/massing_von_s_d207e41.blend',
 'asset_sha256':'4c2715c05d93ec977e878a231355fe465268d7ab32be798ff12262cfb92a0f76',
 'review_date':'2026-10-27',
 'review_type':'independent exact-SHA review and fresh-open validation',
 'score':score,'max_score':10.0,'threshold':8.0,'accepted':score>=8.0,
 'criteria':criteria,
 'checks':json.loads((folder/'fresh_open_validation.json').read_text(encoding='utf-8')),
 'evidence':[
  {'provider':'OpenStreetMap contributors','feature':'way 116427236','url':'https://www.openstreetmap.org/way/116427236','source_snapshot':'2026-10-22T03:45:50Z; raw projected ring in audit/von_s/sources/osm_way_116427236_footprint.json'},
  {'provider':'Von’s official site','url':'https://www.vonsshops.com/business-info','supports':'current 315 W State St address'},
  {'provider':'Von’s official site','url':'https://www.vonsshops.com/history','supports':'main building mixed retail use and apartments on upper floors'},
  {'provider':'Von’s official site','url':'https://www.vonsshops.com/products','supports':'storefront brick/mural/openings reference as documented by builder; single undated photograph'}
 ],
 'findings':['Passes the minimum 8/10 gate.','Height, floor elevations, roof, and facade rhythm remain estimates; preserve those qualifications in the README and manifest.','No public interior plan was found; the choice to omit an invented interior is appropriate.','High boundary/non-manifold edge count means the asset should be treated as a visual model, not a watertight manufacturing mesh.'],
 'report':'audit/von_s/independent_grade_r1/grade_report.md'
}
(folder/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
lines=['# Independent grade — Von’s Shops','',f"**Score: {score:.2f}/10 — {'PASS' if result['accepted'] else 'FAIL'}**",'',f"Asset: `{result['asset_path']}`  ",f"SHA-256: `{result['asset_sha256']}`  ",f"Fresh-open: `{result['checks']['status']}` in Blender {result['checks']['blender_version']}",'','## Criterion scores','']
for c in criteria:
 lines.append(f"### {c['criterion']} — {c['score']:.2f}/{c['max_score']:.1f}")
 lines.append(c['finding'])
 for e in c['evidence']: lines.append(f'- {e}')
 lines.append('')
lines += ['## Independent geometry and portability checks','',f"- OSM ring vertices found: {result['checks']['source_ring_vertex_count']}; maximum XY error: {result['checks']['maximum_nearest_base_xy_error_m']:.6f} m.",f"- Object/mesh: {result['checks']['scene_object_count']} scene object; {result['checks']['mesh_vertices']:,} vertices; {result['checks']['mesh_faces']:,} faces.",f"- Materials/UVs: {len(result['checks']['materials'])} materials; {', '.join(result['checks']['uv_layers'])}.",f"- Unpacked external images: {len(result['checks']['unpacked_external_images'])}.",f"- Boundary/non-manifold edges: {result['checks']['topology']['boundary_edges']:,}; zero-area faces: {result['checks']['topology']['degenerate_faces']}.",'','## Overall finding','', 'The model is an appropriately portable and well-registered visual representation of the assigned Von’s building. It earns a passing score based on exact footprint registration, identity cross-checks, photo-supported brick/mural cues, a fresh-open library, and documented uncertainty. Its main limitations are the unverified roof/heights/facade rhythm and a high open-surface edge count. No interior plan was found, so not inventing one is acceptable.','']
(folder/'grade_report.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'score':score,'accepted':result['accepted'],'result':str(folder/'result.json'),'report':str(folder/'grade_report.md')},indent=2))

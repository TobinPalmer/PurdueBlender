from pathlib import Path
import hashlib, json, math
ROOT=Path.cwd()
OUT=ROOT/'audit/heine_pharmacy/independent_grade_r1'

def point_segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    t=0.0 if den==0 else max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def distance_to_polygon(p,poly):
    return min(point_segment_distance(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))

def evaluate():
    asset=ROOT/'modular/buildings/heine_pharmacy.blend'
    manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
    entry=next(a for a in manifest['assets'] if a['id']=='heine_pharmacy')
    probe=json.loads((OUT/'probe.json').read_text(encoding='utf-8'))
    gis=json.loads((ROOT/'audit/heine_pharmacy/heine_pharmacy_gis_feature.json').read_text(encoding='utf-8'))
    shell=json.loads((OUT/'shell_mesh.json').read_text(encoding='utf-8'))
    reopen=json.loads((ROOT/'audit/heine_pharmacy/fresh_open_verification.json').read_text(encoding='utf-8'))
    evidence=(ROOT/'audit/heine_pharmacy/evidence.md').read_text(encoding='utf-8')
    digest=hashlib.sha256(asset.read_bytes()).hexdigest()
    ring=gis['geometry']['rings'][0]
    # Convert source WGS84 ring through the project’s stated approximate campus map transform,
    # then center it using the documented original GIS-bounds-center origin.
    campus=[((lon+86.9137)*84810.6041653993,(lat-40.4274)*111040.0) for lon,lat in ring]
    ox=(min(p[0] for p in campus)+max(p[0] for p in campus))/2
    oy=(min(p[1] for p in campus)+max(p[1] for p in campus))/2
    src=[(x-ox,y-oy) for x,y in campus]
    base=[(x,y) for x,y,z in shell['vertices'] if abs(z+1.0)<1e-5]
    gis_to_shell=max(distance_to_polygon(p,base) for p in src)
    shell_to_gis=max(distance_to_polygon(p,src) for p in base)
    bounds=probe['bounds_local_m']
    object_count=probe['collection_objects']
    manifest_origin=entry['placement_origin_xy_m']
    expected_hash='c2dcc0579641f3b6a3b0867ead07da0f789c47f83df1b50434ee77b17a98e017'
    assert digest==expected_hash, (digest,expected_hash)
    assert probe['collection_found'] and probe['collection_name']=='Asset_heine_pharmacy'
    assert reopen['status']=='PASS' and reopen['missing_texture_paths']==[]
    assert gis['attributes']['FID']==606 and gis['attributes']['BUILDING_N']=='Robert E. Heine Pharmacy Building'
    criteria=[
      {'name':'Identity and source-backed footprint','score':1.9,'max_score':2.0,
       'evidence':[f"Official Purdue GIS FeatureServer FID {gis['attributes']['FID']} explicitly names {gis['attributes']['BUILDING_N']} and abbreviation {gis['attributes']['BLDG_ABBR']}.",f"The 44-vertex shell mesh provides a 22-point base ring; comparing it with the 92-point transformed GIS ring gives max GIS-to-shell segment deviation {gis_to_shell:.3f} m and shell-to-GIS {shell_to_gis:.6f} m. The GIS source has no survey date/tolerance and the map transform is approximate."],
       'findings':['Identity and footprint crosswalk are strong; retain the project transform and source-tolerance caveat.']},
      {'name':'Position, orientation, and dimensions','score':1.8,'max_score':2.0,
       'evidence':[f"Asset local bounds are X {bounds[0]}, Y {bounds[1]}, Z {bounds[2]} m; structural shell itself retains the transformed source outline.",f"Manifest campus origin is {manifest_origin} m and is documented unchanged by R1; the master integration audit had previously checked the same marker origin, but this grade did not independently complete a fresh master reopen after the asset update."],
       'findings':['The local origin and plan extent are consistent with the documented GIS frame. A fresh master reopen against the updated linked asset is still needed before final integration sign-off.']},
      {'name':'Height, floors, and roof form','score':1.2,'max_score':2.0,
       'evidence':['Purdue OEP building-plan evidence supports five above-grade floors, a G-floor and basement; the revised facade displays five window rows on the referenced elevation.',f"The modeled shell top is {bounds[2][1]:.2f} m and the roof is modeled flat with a small rooftop penthouse. The official GIS lists 8 levels and a roof elevation attribute of 61 with datum/units uncertainty, while the evidence identifies height as estimated."],
       'findings':['Five above-grade floors have a source, but absolute height, lower-floor exposure, roof elevation and penthouse size remain unresolved. Do not present these dimensions as measured.']},
      {'name':'Facade, entrances, and distinctive architecture','score':1.0,'max_score':2.0,
       'evidence':['The new renderer shows red/orange procedural brick, pale horizontal bands, seven facade bays and an entry/arcade object set. The source image also shows seven narrow dark vertical window strips, wide stone spandrels, a strongly expressed multi-arch entrance and a pale roof parapet.',"Visual comparison of the saved fresh-open render with the cited source image shows the model’s seven bays subdivided into a regular grid of five small window panes per bay; the source photograph instead has tall narrow glazing strips with broad light stone panels within those bays. In the render the arcade reads as a small canopy with thin supports rather than a dominant multi-arch portal. The cited photograph is oblique and partly tree-occluded, so exact dimensions are uncertain, but the broad composition difference is visible."],
       'findings':['The facade revision has not yet achieved the cited facade rhythm. Rework each of the seven bays toward tall, narrow vertically continuous glazing and large stone spandrels; enlarge/raise the multi-arch portal to match its substantial share of the entry elevation. Preserve the evidenced brick palette and horizontal limestone courses.']},
      {'name':'Modular export, portability, and complete evidence','score':1.7,'max_score':2.0,
       'evidence':[f"Blender 5.2.3 fresh-open probe found scene `{probe['scene']}`, stable collection `{probe['collection_name']}`, {object_count} collection objects / {probe['mesh_objects']} meshes, {probe['material_count']} used materials, and no missing external image textures.",f"Saved-file SHA-256 {digest} matches the builder’s reported SHA. Evidence records the GIS source, photo license/date, official emergency-plan source, geometry method, uncertainty, and fresh-open render."],
       'findings':[f"The manifest still advertises object_count={entry['object_count']}, but the current collection contains {object_count} objects; update the shared manifest and synchronization verification after a passing revision is integrated.","No external texture dependency was found; evidence is unusually complete for the available sources."]}
    ]
    return {'score':round(sum(c['score'] for c in criteria),2),'max_score':10.0,'criteria':criteria,'evidence':{'asset_path':'modular/buildings/heine_pharmacy.blend','asset_sha256':digest,'blender_version':probe['scenes'][0] and reopen['blender_version'],'independent_probe_path':'audit/heine_pharmacy/independent_grade_r1/probe.json','gis_comparison':{'source_ring_vertices':len(ring),'shell_base_vertices':len(base),'gis_to_shell_max_point_to_segment_m':gis_to_shell,'shell_to_gis_max_point_to_segment_m':shell_to_gis},'visual_references':['audit/heine_pharmacy/heine_exterior_2023.jpg','audit/heine_pharmacy/heine_pharmacy_fresh_open.png'],'reopen_validation':'PASS'},'findings':['Current grade is below the project pass threshold of 8/10. The next revision should focus on the seven-bay glazing proportions and portal scale, then rerender and request a new independent grade.','Height and room layout must remain explicitly estimated/schematic without stronger source evidence.']}

result=evaluate()
(OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['# Heine Pharmacy R1 independent grade','',f"**Score: {result['score']}/10 — {'PASS' if result['score']>=8 else 'NOT YET PASSING'}**",'',f"Exact SHA-256: `{result['evidence']['asset_sha256']}`",'', '## Criteria','']
for c in result['criteria']:
    lines += [f"### {c['name']} — {c['score']}/{c['max_score']}",'']
    lines += [f"- Evidence: {e}" for e in c['evidence']]
    lines += [f"- Finding: {f}" for f in c['findings']]
    lines += ['']
lines += ['## Overall findings','']+[f'- {f}' for f in result['findings']]
(OUT/'grade_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'score':result['score'],'max_score':10,'result_path':str(OUT/'result.json'),'report_path':str(OUT/'grade_report.md'),'gis_to_shell_m':result['evidence']['gis_comparison']['gis_to_shell_max_point_to_segment_m'],'shell_to_gis_m':result['evidence']['gis_comparison']['shell_to_gis_max_point_to_segment_m']},indent=2))

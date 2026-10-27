from pathlib import Path
import hashlib, json, math
ROOT=Path.cwd()
OUT=ROOT/'audit/heine_pharmacy/independent_grade_r2'

def point_segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    t=0.0 if den==0 else max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def max_poly_deviation(points, polygon):
    return max(min(point_segment_distance(p,polygon[i],polygon[(i+1)%len(polygon)]) for i in range(len(polygon))) for p in points)

def evaluate():
    asset=ROOT/'modular/buildings/heine_pharmacy.blend'
    digest=hashlib.sha256(asset.read_bytes()).hexdigest()
    expected='962fe3572903061e9d590759118ea945b28d32c338a0a5f6b8ce40da18e7d9d7'
    assert digest==expected, f'asset changed while grading: {digest}'
    manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
    entry=next(a for a in manifest['assets'] if a['id']=='heine_pharmacy')
    probe=json.loads((OUT/'probe.json').read_text(encoding='utf-8'))
    gis=json.loads((ROOT/'audit/heine_pharmacy/heine_pharmacy_gis_feature.json').read_text(encoding='utf-8'))
    reopen=json.loads((ROOT/'audit/heine_pharmacy/fresh_open_verification_r2.json').read_text(encoding='utf-8'))
    evidence=(ROOT/'audit/heine_pharmacy/evidence.md').read_text(encoding='utf-8')
    photo=ROOT/'audit/heine_pharmacy/heine_exterior_2023.jpg'
    render=ROOT/'audit/heine_pharmacy/heine_pharmacy_fresh_open_r2.png'
    assert gis['attributes']['FID']==606 and gis['attributes']['BUILDING_N']=='Robert E. Heine Pharmacy Building'
    ring=gis['geometry']['rings'][0]
    campus=[((lon+86.9137)*84810.6041653993,(lat-40.4274)*111040.0) for lon,lat in ring]
    ox=(min(p[0] for p in campus)+max(p[0] for p in campus))/2
    oy=(min(p[1] for p in campus)+max(p[1] for p in campus))/2
    source=[(x-ox,y-oy) for x,y in campus]
    shell=[(x,y) for x,y,z in probe['shell_mesh_vertices'] if abs(z+1.0)<1e-5]
    gis_to_shell=max_poly_deviation(source,shell)
    shell_to_gis=max_poly_deviation(shell,source)
    report_sha=reopen['asset_sha256']
    assert report_sha==digest and reopen['status']=='PASS'
    assert reopen['stable_collection']=='Asset_heine_pharmacy'
    assert reopen['asset_object_count']==probe['object_count']==108
    assert reopen['missing_external_textures']==[] and probe['missing_external_texture_paths']==[]
    assert reopen['r2_glazing_panels']==14 and reopen['r2_broad_stone_faces']==21 and reopen['portal_arch_count']==4
    criteria=[
      {'name':'Identity and source-backed footprint','score':1.9,'max_score':2.0,
       'evidence':[f"Official Purdue GIS layer 0, FID {gis['attributes']['FID']} names {gis['attributes']['BUILDING_N']} / {gis['attributes']['BLDG_ABBR']}.",f"Independent comparison of its 92-point WGS84 ring (using the documented approximate campus transform and bbox-center origin) with the saved shell’s 22-point base ring found maximum point-to-segment deviation {gis_to_shell:.3f} m GIS→shell and {shell_to_gis:.6f} m shell→GIS. The GIS source supplies no survey date/tolerance, so the project CRS approximation remains a limitation."],
       'findings':['Identity and shell footprint are strongly supported. The small remaining deduction reflects the approximate transform and unsurveyed GIS tolerance.']},
      {'name':'Position, orientation, and dimensions','score':1.8,'max_score':2.0,
       'evidence':[f"The current saved asset retains the documented campus placement origin {entry['placement_origin_xy_m']} m and local GIS shell bounds {reopen['shell_bounds_local_m']} m. R2 fresh-open validation confirms `shell_geometry_preserved=true` and no origin/manifest edit.","The prior master-sync record verified this origin on the placement marker. R2 did not alter that origin, but an updated master fresh-open check is still due after coordinator sync."],
       'findings':['Local plan and campus anchor remain consistent with the GIS crosswalk. A fresh master-link check after the shared manifest count is corrected remains a coordinator integration step.']},
      {'name':'Height, floors, and roof form','score':1.25,'max_score':2.0,
       'evidence':['Purdue OEP plan supports five above-grade floors plus a G-floor and basement; the model retains the five-level horizontal facade organization. The cited oblique photo supports a flat parapet and limited rooftop mechanical form.',f"Structural shell bounds retain Z {reopen['shell_bounds_local_m'][2]} m; the asset’s penthouse/roof details raise total collection bounds to {probe['bounds_local_m'][2]} m. Absolute levels remain estimated. GIS attributes list 8 levels and roof value 61 with unresolved datum/units, conflicting with the OEP floor description."],
       'findings':['Five above-grade floors are source-supported, but exact absolute height, lower-level exposure, roof datum and mechanical penthouse dimensions remain unverified. Interior floor/room boundaries are deliberately schematic.']},
      {'name':'Facade, entrances, and distinctive architecture','score':1.8,'max_score':2.0,
       'evidence':['Compared the R2 fresh-open render with the cited 2023-10-18 exterior photo: the selected elevation now has seven tall narrow glazing bays, two long glazed sections per bay, broad pale stone mid-panels, restrained rails, brick fields and horizontal pale courses. The render’s four large stone arches and five substantial piers span a substantial portion of that facade, matching the photo’s defining entrance composition.',f"The fresh-open validation reports {reopen['r2_glazing_panels']} long glazing faces, {reopen['r2_broad_stone_faces']} broad stone faces, {reopen['portal_arch_count']} arches, {reopen['portal_width_m']:.2f} m portal width and {reopen['portal_top_z_m']:.2f} m portal top. No source elevation establishes exact opening sizes or arch dimensions."],
       'findings':['R2 resolves the R1 composition mismatch: window rhythm and arch scale read substantially closer to the one source elevation. Deduct slightly because the photo is oblique/partly occluded, exact dimensions and hidden elevations are unsupported, and the remaining facades are not validated against comparable images.']},
      {'name':'Modular export, portability, and complete evidence','score':1.75,'max_score':2.0,
       'evidence':[f"Independent Blender 5.2.3 reopen found stable collection `{probe['collection']}`, {probe['object_count']} objects / {probe['mesh_count']} meshes and {len(probe['materials'])} used materials. The saved SHA matches the R2 verification record; no missing external texture path was found.","Evidence documents official GIS FID and transform, dated licensed source photo, official OEP floor/use evidence, uncertainties, R2 edits, and exact saved-file hash. Interior cues are explicitly labeled schematic in their object names and evidence."],
       'findings':[f"The shared manifest still has object_count={entry['object_count']} while the current export contains {probe['object_count']} objects. The asset retains the stable collection and is fresh-open portable; update manifest and run master-link verification during integration.","No evidence of room-by-room interior accuracy is claimed; schematic labeling is appropriate."]}
    ]
    total=round(sum(c['score'] for c in criteria),2)
    return {'score':total,'max_score':10.0,'criteria':criteria,'evidence':{'asset_path':'modular/buildings/heine_pharmacy.blend','asset_sha256':digest,'blender_version':reopen['blender_version'],'independent_probe_path':'audit/heine_pharmacy/independent_grade_r2/probe.json','gis_comparison':{'source_ring_vertices':len(source),'shell_base_vertices':len(shell),'gis_to_shell_max_point_to_segment_m':gis_to_shell,'shell_to_gis_max_point_to_segment_m':shell_to_gis,'local_bbox_center_origin_m':[ox,oy]},'source_photo':'audit/heine_pharmacy/heine_exterior_2023.jpg','fresh_open_render':'audit/heine_pharmacy/heine_pharmacy_fresh_open_r2.png','reopen_validation':'PASS'},'findings':['Passes the independent 8/10 threshold for a detailed exterior asset.','The main remaining limits are uncertainty in absolute height and unseen facades/interior. Shared manifest object count and fresh master-link verification remain coordinator-owned integration work.']}

result=evaluate()
(OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['# Heine Pharmacy R2 independent grade','',f"**Score: {result['score']}/10 — {'PASS' if result['score']>=8 else 'NOT YET PASSING'}**",'',f"Exact SHA-256: `{result['evidence']['asset_sha256']}`",'', '## Criteria','']
for c in result['criteria']:
    lines += [f"### {c['name']} — {c['score']}/{c['max_score']}",'']
    lines += [f"- Evidence: {e}" for e in c['evidence']]
    lines += [f"- Finding: {f}" for f in c['findings']]
    lines += ['']
lines += ['## Overall findings','']+[f'- {f}' for f in result['findings']]
(OUT/'grade_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'score':result['score'],'max_score':10,'pass':result['score']>=8,'asset_sha256':result['evidence']['asset_sha256'],'result_path':str(OUT/'result.json'),'report_path':str(OUT/'grade_report.md'),'gis_to_shell_m':result['evidence']['gis_comparison']['gis_to_shell_max_point_to_segment_m'],'shell_to_gis_m':result['evidence']['gis_comparison']['shell_to_gis_max_point_to_segment_m']},indent=2))

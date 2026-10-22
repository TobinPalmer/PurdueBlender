"""Exhaustive evidence ledger. Deliberately does not silently resize geometry."""
import csv,json,math,pathlib,re,collections
BASE=pathlib.Path(__file__).resolve().parent.parent
P=BASE/'audit'
MAP={'walc':'WALC','wiley_hall':'WILY','mechanical_engineering':'ME','potter_engineering':'POTR','electrical_engineering':'EE','south_hall':'SH','beering_hall':'BRNG','tarkington_hall':'TARK','owen_hall':'OWEN','ross_ade':'STDM','winifred_parker_hall':'PKRW','frieda_parker_hall':'PKRF','elliott_hall_of_music':'ELLT','university_hall':'UNIV','neil_armstrong_hall':'ARMS','mackey_arena':'MACK','purdue_memorial_union':'PMU','stewart_center':'STEW','hovde_hall':'HOVD','class_of_1950':'CL50','armory':'AR','math_sciences':'MATH','felix_haas_hall':'HAAS','bell_tower':'BELL'}
def box_score(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    aa=(a[2]-a[0])*(a[3]-a[1]);bb=(b[2]-b[0])*(b[3]-b[1])
    return inter/(aa+bb-inter) if aa+bb-inter else 0
def center(b):return ((b[0]+b[2])/2,(b[1]+b[3])/2)
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
manifest=json.loads((BASE/'modular/manifest.json').read_text())
objects={o['name']:o for o in json.loads((BASE/'building_objects.json').read_text())}
world=json.loads((P/'object_world_bounds.json').read_text()) if (P/'object_world_bounds.json').exists() else {}
selectors={s['group_id']:s for s in json.loads((P/'shell_selectors.json').read_text())['buildings']} if (P/'shell_selectors.json').exists() else {}
if 'ross_ade_stadium' in selectors:selectors['ross_ade']=selectors['ross_ade_stadium']
corrections_path=P/'placement_corrections.json'
corrections=json.loads(corrections_path.read_text()) if corrections_path.exists() else None
duplicate_extents=collections.defaultdict(list)
for asset in manifest['assets']:
    if asset['kind']=='massing' and len(asset['objects'])==1 and asset.get('bounds_world_m'):
        key=tuple(round(v,3) for axis in asset['bounds_world_m'] for v in axis)
        duplicate_extents[key].append(asset['id'])
duplicates=[v for v in duplicate_extents.values() if len(v)>1]
duplicate_by_id={ident:group for group in duplicates for ident in group}
refs=json.loads((P/'official_building_references.json').read_text())['buildings']
bycode=collections.defaultdict(list)
for r in refs:bycode[r['code']].append(r)
rows=[]
for a in manifest['assets']:
    row={'id':a['id'],'file':a['file'],'kind':a['kind'],'object_count':a['object_count'],'status':'unverified','height_status':'unverified','orientation_status':'unverified','position_status':'unverified','plan_dimensions_status':'unverified','action':'reference comparison only; no geometry mutation','match_confidence':'unmatched','source_fid':None,'source_code':None,'source_name':None,'aabb_center_difference_m':None,'aabb_width_difference_m':None,'aabb_depth_difference_m':None,'aabb_overlap_iou':None,'position_error_m':None,'orientation_error_degrees':None,'footprint_method':'not measured; aggregate AABB is screening only','source_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','source_date_retrieved':'2026-10-22'}
    obs=[objects[n] for n in a['objects'] if n in objects]
    shell=[o['name'] for o in obs if o['type']=='MESH' and re.search(r'(MainMass|Wall_(North|South|East|West)|Exterior_Wall|Brick_Wall|Roof_Slab|Roof_Membrane|Envelope|Shell|Wing.*Mass|Foundation)',o['name'],re.I) and not re.search(r'(Interiors|Plaza|Site|Garden)',','.join(o['collections']),re.I)]
    selector=selectors.get(a['id'])
    if selector:
        shell=[n for n in selector['object_names'] if n in a['objects']]
        row['shell_selection_evidence']=selector.get('evidence_script')
        row['shell_selection_limitations']=selector.get('limitations')
    row['shell_candidates']=shell
    row['duplicate_extent_assets']=duplicate_by_id.get(a['id'],[])
    if a['id'] in duplicate_by_id:row['duplicate_status']='same 3D bounds to 1 mm; inspect mesh identity before deletion'
    row['uncertainty']='No measured height/elevations; shell polygon and orientation require geometric review.'
    if a['kind']=='site':
        row.update(status='environment_not_building',height_status='not_applicable',uncertainty='Shared roads, landscape, cameras and other campus objects. Review separately for orphan buildings.')
        rows.append(row);continue
    b=a.get('exterior_bounds_world_m') or a.get('bounds_world_m')
    shell_bounds=[world[n]['world_bounds'] for n in shell if n in world]
    if selector and shell_bounds:
        b=[[min(v[i][0] for v in shell_bounds),max(v[i][1] for v in shell_bounds)] for i in range(3)]
        row['footprint_method']='principal-shell transformed AABB screening; not enclosed footprint polygon or measured wall error'
    if not b:
        row['uncertainty']='No measurable geometry bounds.';rows.append(row);continue
    ab=[b[0][0],b[1][0],b[0][1],b[1][1]];c=center(ab)
    code=MAP.get(a['id']);candidates=bycode.get(code,[])
    if candidates:row['match_confidence']='official_code_by_detailed_group_name'
    if not candidates:
        # Strong name identities only; a nearest polygon remains merely a candidate.
        names=[norm(o['name'].split(' (')[0]) for o in obs]
        candidates=[r for r in refs if norm(r['name']) in names or any('('+r['code']+')' in o['name'] for o in obs)]
        if candidates:row['match_confidence']='official_code_or_exact_name'
    if not candidates:
        ranked=sorted(refs,key=lambda r:math.dist(c,center(r['aabb_xy_m'])))
        if ranked:
            near=ranked[0];distance=math.dist(c,center(near['aabb_xy_m']))
            if distance<100:
                candidates=[near];row['match_confidence']='spatial_candidate_only_identity_unverified'
    if candidates:
        r=max(candidates,key=lambda r:box_score(ab,r['aabb_xy_m']));rb=r['aabb_xy_m'];rc=center(rb)
        row.update(source_fid=r['fid'],source_code=r['code'],source_name=r['name'],aabb_center_difference_m=round(math.dist(c,rc),3),aabb_width_difference_m=round(ab[2]-ab[0]-(rb[2]-rb[0]),3),aabb_depth_difference_m=round(ab[3]-ab[1]-(rb[3]-rb[1]),3),aabb_overlap_iou=round(box_score(ab,rb),4),official_reference_bounds_xy_m=rb,model_bounds_xy_m=ab)
        row['status']='needs_shell_and_height_verification'
        if row['match_confidence']=='spatial_candidate_only_identity_unverified':row['status']='ambiguous_source_match'
        if row['aabb_center_difference_m']>5 or row['aabb_overlap_iou']<.6:row['screening_flag']='large_bounds_discrepancy_review_shell'
        else:row['screening_flag']='bounds_close_not_verified'
    else:row['status']='no_official_match';row['screening_flag']='needs_independent_reference'
    if a['id']=='wiley_hall' and corrections is not None:
        row['action']='Applied documented gross placement translation +4.1889462471 m east, +108.4703903198 m north; no scaling. See placement_corrections.json and preserved before-placement asset.'
        row['position_status']='gross location corrected; precise wall placement unverified'
        row['plan_dimensions_status']='unverified; source shell dimensions differ from official residence envelope'
        row['status']='gross_placement_corrected_precision_and_dimensions_unverified'
        row['correction_evidence']='audit/placement_corrections.json'
        row['uncertainty']='Translation relocates residence-shaped model from dining court anchor to residence envelope. AABB alignment is not exact wall alignment. Shape, orientation, dimensions, and height remain unverified.'
    rows.append(row)
assert len(rows)==len(manifest['assets'])
assert len(set(r['id'] for r in rows))==len(rows)
result={'method':'Exhaustive asset ledger against official Purdue 2D polygon snapshot. Bounding comparisons are review flags, not measured shell errors. No building certified. Explicit placement corrections are recorded separately; this audit does not mutate geometry.','asset_count':len(rows),'building_count':sum(r['kind']!='site' for r in rows),'status_counts':dict(collections.Counter(r['status'] for r in rows)),'records':rows}
result['duplicate_extent_groups']=duplicates
result['duplicate_extent_asset_count']=sum(map(len,duplicates))
(P/'master_building_audit.json').write_text(json.dumps(result,indent=2))
fields=['id','file','kind','object_count','status','match_confidence','source_code','source_fid','source_name','aabb_center_difference_m','aabb_width_difference_m','aabb_depth_difference_m','aabb_overlap_iou','position_status','position_error_m','orientation_status','orientation_error_degrees','plan_dimensions_status','height_status','screening_flag','duplicate_status','duplicate_extent_assets','action','uncertainty','source_url','source_date_retrieved']
with (P/'master_building_audit.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
lines=['# Master building audit','',result['method'],'',f"Assets: {len(rows)}; buildings: {result['building_count']}. One record per asset in JSON and CSV.",'',str(result['status_counts']),'','## Detailed buildings','','| Asset | Official code | Match | Bounds center difference (m) | Screening | Shell candidates |','|---|---|---|---:|---|---:|']
for r in rows:
    if r['kind']=='detailed':lines.append(f"| {r['id']} | {r['source_code'] or 'unmatched'} | {r['match_confidence']} | {r['aabb_center_difference_m']} | {r.get('screening_flag','')} | {len(r['shell_candidates'])} |")
lines+=['','All position, orientation and height criteria remain unverified until a shell-specific measurement and evidence review establishes them. A source match and similar bounds do not establish accuracy. No dimensions were changed from inferred bounding boxes. See GEOSPATIAL_REFERENCE.md for provenance and acceptance method.']
lines+=['',f'Duplicate extent screening: {len(duplicates)} groups containing {sum(map(len,duplicates))} assets have identical 3D bounds rounded to 1 mm. These are collision candidates, not proven duplicate meshes. See JSON groups and CSV per-asset records.']
(P/'MASTER_AUDIT.md').write_text('\n'.join(lines))
print(json.dumps({k:v for k,v in result.items() if k!='records'}))

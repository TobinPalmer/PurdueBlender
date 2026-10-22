"""Supplementary comparison to ORIGINAL imported OSM data; not independent accuracy."""
import collections,csv,json,math,pathlib,re
BASE=pathlib.Path(__file__).resolve().parent.parent
P=BASE/'audit'
manifest=json.loads((BASE/'modular/manifest.json').read_text())
world=json.loads((P/'object_world_bounds.json').read_text())
origin=manifest['origin']; sx=origin['longitude_to_meters'];sy=origin['latitude_to_meters']
raw=[];nodes={};snapshots={}
for filename in ['purdue_campus_buildings.json','ross_ade_stadium.json']:
    d=json.loads((BASE/filename).read_text());snapshots[filename]=d.get('osm3s',{}).get('timestamp_osm_base')
    raw.extend((filename,e) for e in d['elements'])
    nodes.update({e['id']:(e['lat'],e['lon']) for e in d['elements'] if e['type']=='node'})
ways=collections.defaultdict(list);names=collections.defaultdict(list)
for filename,w in raw:
    if w['type']!='way' or 'building' not in w.get('tags',{}):continue
    points=[]
    for nid in w.get('nodes',[]):
        if nid not in nodes:continue
        lat,lon=nodes[nid];point=((lon-origin['lon'])*sx,(lat-origin['lat'])*sy)
        if not points or math.dist(point,points[-1])>.3:points.append(point)
    if len(points)>2 and math.dist(points[0],points[-1])<.5:points.pop()
    if len(points)<3:continue
    b=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(2)]
    rec={'id':w['id'],'bounds':b,'file':filename,'snapshot_timestamp':snapshots[filename],'way_timestamp':w.get('timestamp'),'tags':w['tags']}
    ways[w['id']].append(rec)
    if w['tags'].get('name'):names[w['tags']['name']].append(rec)
rows=[]
for a in manifest['assets']:
    if a['kind']!='massing':continue
    r={'id':a['id'],'file':a['file'],'object_names':a['objects'],'status':'no_exact_input_source_match','match_method':'unmatched','max_xy_bound_difference_m':None,'source_way_id':None,'source_url':None,'source_snapshot_timestamp':None,'source_way_edit_timestamp':None,'source_snapshot_file':None,'height_status':'unverified; may be inferred by importer','independent_accuracy_status':'unverified','method':'original input OSM polygon XY bounds vs current transformed mesh AABB; original importer point filtering reproduced','uncertainty':'Input consistency is not an independent survey or polygon/shape/height certification.'}
    if len(a['objects'])!=1:r['uncertainty']+=' Multi-object massing asset requires review.';rows.append(r);continue
    name=a['objects'][0];base_name=re.sub(r'\.\d{3}$','',name)
    match=re.fullmatch(r'House_(\d+)',base_name)
    candidates=ways.get(int(match.group(1)),[]) if match else names.get(base_name,[])
    r['match_method']='exact_way_id_from_object_name' if match and candidates else ('exact_OSM_name' if candidates else 'unmatched')
    bounds=world.get(name,{}).get('world_bounds')
    if candidates and bounds:
        def error(c):return max(abs(bounds[i][j]-c['bounds'][i][j]) for i in range(2) for j in range(2))
        best=min(candidates,key=error);err=error(best)
        distinct={c['id'] for c in candidates}
        r.update(status='input_source_bounds_consistent_within_1cm' if err<=.01 else 'input_source_bounds_discrepancy',max_xy_bound_difference_m=round(err,6),source_way_id=best['id'],source_url='https://www.openstreetmap.org/way/'+str(best['id']),source_snapshot_timestamp=best['snapshot_timestamp'],source_way_edit_timestamp=best['way_timestamp'],source_snapshot_file=best['file'],source_bounds_xy_m=best['bounds'],model_bounds_xy_m=bounds[:2],candidate_distinct_way_count=len(distinct),original_height_tag=best['tags'].get('height'),original_levels_tag=best['tags'].get('building:levels'))
        if len(distinct)>1:r['uncertainty']+=' Multiple distinct ways share this exact name; best bounds candidate selected and identity remains ambiguous.'
        if best['way_timestamp'] is None:r['uncertainty']+=' Original file contains OSM base snapshot time, not individual way edit timestamp.'
    elif candidates:r['status']='model_world_bounds_missing'
    rows.append(r)
counts=dict(collections.Counter(r['status'] for r in rows))
report={'purpose':'Supplementary input-source consistency, not an independent accuracy audit. Official Purdue master audit statuses are unchanged.','asset_count':len(rows),'tolerance_m':.01,'counts':counts,'source_timestamps':snapshots,'records':rows}
(P/'osm_source_consistency.json').write_text(json.dumps(report,indent=2))
fields=['id','file','status','match_method','max_xy_bound_difference_m','source_way_id','source_url','source_snapshot_file','source_snapshot_timestamp','source_way_edit_timestamp','candidate_distinct_way_count','height_status','independent_accuracy_status','original_height_tag','original_levels_tag','uncertainty']
with (P/'osm_source_consistency.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
text=['# Original OSM source consistency','',report['purpose'],'',f'Checked every massing asset: {len(rows)} records. Threshold: 0.01 m maximum difference across four XY bounding edges.','',str(counts),'','Snapshots: '+str(snapshots),'','Exact House_ID or exact named way matching is required; Blender numeric suffixes are stripped to identify repeated imports. Source coordinate filtering reproduces build_campus_base.py. Multiple ways sharing a name retain an ambiguity flag. Comparison uses the original imported source, so agreement verifies import placement/bounds consistency only. It cannot establish current real-world correctness, exact footprint shape, elevations, or inferred heights. Per-way edit timestamps were not requested in the original OSM snapshots; snapshot base times are preserved without inventing edit dates.','', 'Every massing asset has its own JSON/CSV row, including unmatched assets and discrepancies. Official campus audit statuses were not modified.']
(P/'OSM_SOURCE_CONSISTENCY.md').write_text('\n'.join(text))
print(json.dumps({k:v for k,v in report.items() if k!='records'}))

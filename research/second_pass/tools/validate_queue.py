"""Independent recomputation of the research order, owners, inputs and artifacts.

Run with Python 3: python -X utf8 research/second_pass/tools/validate_queue.py
Uses only the standard library. Does not edit source/model/placement files.
"""
from pathlib import Path
import json,math,hashlib,re,subprocess
D=Path(__file__).resolve().parents[1];R=D.parents[1]
q=json.loads((D/'queue.json').read_text(encoding='utf-8'))
inputs=json.loads((D/'shared/ranking_input_snapshot.json').read_text(encoding='utf-8'))
old={x['asset']:x for x in inputs['old_queue']}
eligible={x['asset']:x for x in inputs['finished_current']}
rows=q['queue'];excluded=q['excluded_already_second_passed_work'];allrows=rows+excluded
assert len(old)==len(eligible)==len(allrows)==232
assert len(rows)==231 and len(excluded)==1 and excluded[0]['building_id']=='felix_haas_hall'
assert set(old)==set(eligible)=={x['asset'] for x in allrows}
assert len({x['building_id'] for x in allrows})==232
assert sum(x['owner']=='Rossen' for x in allrows)==90
assert q['weights']=={'central_campus_location':70,'campus_prominence':20,'current_grade_shortfall':10}
for row in allrows:
    assert row['owner']==old[row['asset']]['owner']
    assert row['importance']==old[row['asset']]['importance']
    assert row['grade']==eligible[row['asset']]['grade']
    assert math.isfinite(row['grade']) and 0<=row['grade']<=10
    cs=[]
    for a in q['anchors']:
        distance=math.hypot(row['location_xy_m'][0]-a['xy_m'][0],row['location_xy_m'][1]-a['xy_m'][1])
        cs.append(a['maximum_centrality']*(1 if distance<=100 else max(0,(1100-distance)/1000)))
    central=max(cs);grade=max(0,min(1,(9.9-row['grade'])/1.9))
    score=70*central+5*(row['importance']-1)+10*grade
    assert math.isclose(central,row['centrality'],abs_tol=1e-10)
    assert math.isclose(score,row['priority'],abs_tol=1e-9)
expected=sorted(rows,key=lambda x:(-x['priority'],-x['centrality'],-x['importance'],x['grade'],x['name'].casefold(),x['asset']))
assert [x['asset'] for x in rows]==[x['asset'] for x in expected]
assert [x['rank'] for x in rows]==list(range(1,232))
prepared=[x for x in rows if x['dossier']]
for x in prepared:
    p=D/x['dossier'];assert p.is_file() and p.stat().st_size>3000
    assert x['research_status']!='Queued'
provenance=json.loads((D/'shared/location_source_provenance.json').read_text())
assert hashlib.sha256((D/'shared/official_purdue_buildings_wgs84_snapshot.json').read_bytes()).hexdigest()==provenance['source_sha256']
for row in json.loads((D/'buildings/walc/sources/lidar_crop_summary.json').read_text()):
    p=D/'buildings/walc'/row['clip_repository_path']
    assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==row['clip_sha256']
current=(R/'README.md').read_text(encoding='utf-8')
base=subprocess.check_output(['git','show','67fedb8:README.md'],cwd=R).decode('utf-8')
def outside(text):
    first,rest=text.split('<!-- second-pass-queue:start -->');_,last=rest.split('<!-- second-pass-queue:end -->');return first,last
assert outside(current)==outside(base),'Existing README content outside ranking must be preserved'
for row in rows:
    line=next(x for x in current.splitlines() if x.startswith('| '+str(row['rank'])+' | ') and row['asset'] in x)
    assert f"| {row['priority']:.2f} |" in line and f"| {row['owner']} |" in line
    if row['location_conflict']:assert '[location conflict]' in line
    elif not row['official_feature_ids']:assert '[location proxy]' in line
changed=subprocess.check_output(['git','diff','--name-only','67fedb8'],cwd=R,text=True).splitlines()
assert not any(x.endswith('.blend') or '/build_' in x or x=='modular/manifest.json' for x in changed)
report={'result':'PASS','eligible':232,'queued_for_research':231,'excluded_prior_model':1,'rossen_assignments_preserved':90,'prepared_dossiers':len(prepared),'unresolved_location_proxies':sum(not x['official_feature_ids'] for x in rows),'location_conflicts':sum(bool(x['location_conflict']) for x in rows),'unavailable_source_assets':sum(not x['asset_available'] for x in rows),'top_five':[x['name'] for x in rows[:5]],'unchanged_models':True,'original_readme_outside_queue_preserved':True}
print(json.dumps(report,indent=2))

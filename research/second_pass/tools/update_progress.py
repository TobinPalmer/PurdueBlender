"""Publish explicitly prepared dossiers into the existing Markdown queue.

Usage: python update_progress.py mechanical_engineering
This changes research status only, never modeling acceptance or assignments.
"""
from pathlib import Path
import json,re,sys
D=Path(__file__).resolve().parents[1];R=D.parents[1]
q=json.loads((D/'queue.json').read_text(encoding='utf-8'))
for stable_id in sys.argv[1:]:
    row=next(x for x in q['queue'] if x['building_id']==stable_id)
    doc=D/'buildings'/stable_id/'README.md'
    assert doc.exists() and doc.stat().st_size>3000,'Publish substantive, inspected research only'
    row.update(research_status='Prepared with gaps',dossier=str(doc.relative_to(D)).replace('\\','/'))
prepared=sum(bool(x['dossier']) for x in q['queue']);nextrow=next((x for x in q['queue'] if not x['dossier']),None)
q['research_progress']={'prepared_with_gaps':prepared,'queued':len(q['queue'])-prepared,'next_rank':nextrow['rank'] if nextrow else None,'model_changes_in_this_phase':0}
(D/'queue.json').write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=D/'README.md';s=p.read_text(encoding='utf-8');nextlabel=f" Next: rank {nextrow['rank']}, {nextrow['name']}." if nextrow else ''
s=re.sub(r'\*\*Research status:.*?\*\*',f"**Research status: {prepared} dossiers prepared with explicit gaps; {len(q['queue'])-prepared} queued.{nextlabel}**",s,count=1)
for row in q['queue']:
    if row['dossier']:
        s=re.sub(r'(?m)^\| '+str(row['rank'])+r' \|.*$',f"| {row['rank']} | {row['name']} | [Research]({row['dossier']}) | {row['research_status']} |",s)
p.write_text(s,encoding='utf-8')
p=R/'README.md';s=p.read_text(encoding='utf-8');lines=s.splitlines()
for row in q['queue']:
    if row['dossier']:
        for i,line in enumerate(lines):
            if line.startswith('| '+str(row['rank'])+' | ') and row['asset'] in line:
                prefix=' | '.join(line.split(' | ')[:6]);lines[i]=prefix+f" | {row['owner']} | [{row['research_status']}](research/second_pass/{row['dossier']}) |"
s='\n'.join(lines)+'\n'
s=re.sub(r'\*\*WALC research is prepared with gaps; next is rank 2, Mechanical Engineering\.\*\*',f"**{prepared} research dossiers prepared with gaps; {len(q['queue'])-prepared} queued.{nextlabel}**",s)
s=re.sub(r'\*\*\d+ research dossiers prepared with gaps;.*?\*\*',f"**{prepared} research dossiers prepared with gaps; {len(q['queue'])-prepared} queued.{nextlabel}**",s,count=1)
p.write_text(s,encoding='utf-8')
print(json.dumps(q['research_progress']))

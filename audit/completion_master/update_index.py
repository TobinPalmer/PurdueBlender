import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
m=json.loads((root/'modular/manifest.json').read_text())
lines=['# Detailed building files','','Edit geometry in its source library; campus placement is controlled by its Placement marker in the master. Reopen the master after source edits.','','| Building | File | Objects |','|---|---|---:|']
for a in m['assets']:
    if a.get('kind')!='detailed':continue
    name=a['id'].replace('_',' ').title();f=a['file'].replace('\\','/')
    lines.append(f"| {name} | [{Path(f).name}]({f}) | {a.get('object_count',0)} |")
(root/'modular/BUILDINGS.md').write_text('\n'.join(lines)+'\n')

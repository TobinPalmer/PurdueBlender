"""Sum independent visual criterion awards; never import first-pass grade."""
import json
from pathlib import Path
from decimal import Decimal
p=Path(__file__).resolve().parent
r=json.loads((p/'assessment.json').read_text())
assert sum(Decimal(str(c['maximum'])) for c in r['criteria'])==Decimal('10')
for c in r['criteria']:
 assert 0<=c['awarded']<=c['maximum'] and c['citations'] and c['deductions']
r['score']=float(sum(Decimal(str(c['awarded'])) for c in r['criteria']))
r['accepted']=r['score']>=r['acceptance_threshold'] and all(g['pass'] for g in r['gates'].values())
(p/'result.json').write_text(json.dumps(r,indent=2))
print(json.dumps({'score':r['score'],'accepted':r['accepted'],'hash':r['asset_sha256']}))

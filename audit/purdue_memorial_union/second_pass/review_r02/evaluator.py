"""Sum independent visual awards and enforce the unmodified second-pass gates."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def evaluate():
    r=json.loads((HERE/'assessment.json').read_text(encoding='utf-8'))
    current=hashlib.sha256((ROOT/r['asset_path']).read_bytes()).hexdigest()
    reopened=json.loads((HERE/'fresh_reopen.json').read_text())
    assert current==r['asset_sha256']==reopened['asset_sha256'],'Asset changed: new independent review required'
    assert [x['maximum'] for x in r['criteria']]==[3,2.5,2,1.5,1]
    assert all(0<=x['awarded']<=x['maximum'] for x in r['criteria'])
    r['score']=sum(x['awarded'] for x in r['criteria'])
    r['reviewed_at']=datetime.now(timezone.utc).isoformat()
    r['accepted']=r['score']>=r['acceptance_threshold'] and all(x['passed'] for k,x in r['gates'].items() if k!='master_integration')
    return r
if __name__=='__main__':
    r=evaluate();(HERE/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({'score':r['score'],'accepted':r['accepted'],'asset_sha256':r['asset_sha256']},indent=2))

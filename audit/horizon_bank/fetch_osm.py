from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path
import json
q='[out:json][timeout:20];way(around:100,40.4477521,-86.9224333)["building"];out body geom;'
req=Request('https://overpass.private.coffee/api/interpreter',data=q.encode(),headers={'User-Agent':'Mozilla/5.0 PurdueMap Research'})
try:
 raw=urlopen(req,timeout=30).read(); Path('audit/horizon_bank/sources/osm_overpass_horizon_2026-10-26.json').write_bytes(raw)
 d=json.loads(raw); print('COUNT',len(d.get('elements',[])))
 for e in d.get('elements',[]): print(json.dumps({'id':e.get('id'),'tags':e.get('tags',{}),'geometry':e.get('geometry')},separators=(',',':')))
except Exception as e: print(type(e).__name__,str(e))

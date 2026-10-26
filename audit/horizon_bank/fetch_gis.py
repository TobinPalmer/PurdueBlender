from urllib.request import urlopen
from urllib.parse import urlencode
from pathlib import Path
import json
base='https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query'
params={'where':'1=1','geometry':'-86.924,40.446,-86.921,40.449','geometryType':'esriGeometryEnvelope','inSR':'4326','geometrySR':'4326','outFields':'FID,BLDG_ABBR,BUILDING_N,OTHER_ABBR,ADDRESS,NUM_LEVELS,CountOfFLO,Shape__Area','returnGeometry':'true','outSR':'4326','f':'pjson'}
url=base+'?'+urlencode(params)
raw=urlopen(url,timeout=30).read()
Path('audit/horizon_bank/sources/purdue_gis_horizon_nearby_2026-10-26.json').write_bytes(raw)
data=json.loads(raw)
print('GIS_QUERY_URL='+url)
print('GIS_QUERY_RESPONSE='+json.dumps({k:v for k,v in data.items() if k!='features'},separators=(',',':')))
for f in data.get('features',[]): print('FEATURE='+json.dumps(f,separators=(',',':')))

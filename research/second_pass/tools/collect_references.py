"""Save explicitly selected public references, retaining access results and hashes.

python collect_references.py BUILDING_ID
Reads buildings/BUILDING_ID/sources/requested_sources.json. Does not infer facts,
count viewpoints, or mark research prepared. Inspect the resulting images.
"""
from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures,re,html,sys,datetime
D=Path(__file__).resolve().parents[1];S=D/'buildings'/sys.argv[1]/'sources'
requests=json.loads((S/'requested_sources.json').read_text(encoding='utf-8'))
def fetch(row):
    result=dict(row,retrieved=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        with urllib.request.urlopen(urllib.request.Request(row['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as r:
            data=r.read();result.update(resolved_url=r.url,content_type=r.headers.get('Content-Type'))
        (S/row['file']).write_bytes(data);result.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='downloaded; inspect before using')
        if row['file'].endswith('.html'):
            text=data.decode('utf-8',errors='replace');result['page_title']=re.findall(r'<title>(.*?)</title>',text,re.I|re.S)[:1]
            result['image_tags']=[html.unescape(t)[:1000] for t in re.findall(r'<img\b[^>]*>',text,re.I)]
            if 'canonical" href="https://www.purdue.edu/home/' in text:result['status']='Redirected homepage, not requested source article'
            if '_Incapsula_Resource' in text and len(data)<2000:result['status']='Anti-bot challenge response, not requested source article'
    except Exception as e:result.update(requested_file=result.pop('file'),file=None,status='unavailable',error=str(e))
    return result
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(fetch,requests))
index=S/'reference_download_index.json';old=json.loads(index.read_text()) if index.exists() else []
replaced={x['url'] for x in rows};index.write_text(json.dumps([x for x in old if x['url'] not in replaced]+rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for r in rows:print(json.dumps({k:v for k,v in r.items() if k not in ('image_tags',)},ensure_ascii=False));print('Image candidates:',r.get('image_tags',[])[:12])

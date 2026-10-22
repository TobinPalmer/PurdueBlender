import urllib.request, urllib.parse, json

q = """[out:json][timeout:30];
(
  way["leisure"="stadium"](40.435,-86.925,40.448,-86.910);
  way["building"](40.440,-86.925,40.448,-86.910);
  relation["leisure"="stadium"](40.435,-86.925,40.448,-86.910);
);
out body;
>;
out skel qt;
"""

data = urllib.parse.urlencode({'data': q}).encode('utf-8')
req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data, headers={'User-Agent': 'PurdueDigitalTwin/1.0'})
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    with open(r'C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin\ross_ade_stadium.json', 'w', encoding='utf-8') as f:
        json.dump(res, f)
    print('Ross-Ade elements fetched:', len(res.get('elements', [])))
    names = set(e.get('tags', {}).get('name') for e in res.get('elements', []) if 'name' in e.get('tags', {}))
    print('Found names:', names)
except Exception as e:
    print('Error:', e)

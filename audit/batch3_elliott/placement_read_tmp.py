import json,pathlib
p=pathlib.Path('modular/BUILDINGS.json')
if p.exists(): d=json.loads(p.read_text())
else: d=json.loads(pathlib.Path('audit/batch3_master/manifest_before.json').read_text())
print(type(d).__name__)
if isinstance(d,dict):
 for k,v in d.items():
  if isinstance(v,list):
   for x in v:
    if isinstance(x,dict) and x.get('id') in ('elliott_hall_of_music','hovde_hall'):print(x)
  elif isinstance(v,dict):
   if k in ('elliott_hall_of_music','hovde_hall'):print(k,v)

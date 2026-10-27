import bpy, json
from pathlib import Path
c=bpy.data.collections['Asset_massing_house_970455277_a3fb72a']
items=[]
for o in c.all_objects:
 n=o.name.lower()
 if any(k in n for k in ('bed','kitchen','dining','lounge','sofa','table','chair','bath','interior','garage','parking','stair','corridor','bedroom')):
  items.append(o.name)
res={'matched_count':len(items),'examples':items[:250]}
Path(bpy.data.filepath).resolve().parents[2].joinpath('audit/alpha_omicron_pi/independent_grade_r2/interior_inventory.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))

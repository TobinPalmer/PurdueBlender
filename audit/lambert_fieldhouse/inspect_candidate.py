import bpy,json,hashlib
from pathlib import Path
c=bpy.data.collections.get('Asset_lambert_fieldhouse')
objs=list(c.all_objects) if c else []
out={'blend':bpy.data.filepath,'collection':c.name if c else None,'objects':len(objs),'meshes':sum(o.type=='MESH' for o in objs),'curves':sum(o.type=='CURVE' for o in objs),'materials':sorted({m.name for o in objs if getattr(o.data,'materials',None) for m in o.data.materials if m}),'cameras':[o.name for o in bpy.data.objects if o.type=='CAMERA'],'lights':[(o.name, o.data.type, o.data.energy) for o in bpy.data.objects if o.type=='LIGHT'],'collection_names':[x.name for x in bpy.data.collections if any(k in x.name.lower() for k in ['interior','context','line','terrain','site','perimeter','exterior'])]}
for o in objs:
 if o.type=='MESH':
  for p in o.data.polygons[:0]: pass
Path('audit/lambert_fieldhouse/inspect_candidate.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))

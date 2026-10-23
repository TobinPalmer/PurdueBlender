import bpy,json
from pathlib import Path
c=bpy.data.collections['Asset_felix_haas_hall']
r={'materials':[], 'objects':[]}
for m in bpy.data.materials:
 r['materials'].append({'name':m.name,'diffuse':list(m.diffuse_color),'nodes':[(n.type,n.name) for n in m.node_tree.nodes] if m.node_tree else []})
for o in c.all_objects:
 r['objects'].append({'name':o.name,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else []})
Path('audit/next_haas/inspect.json').write_text(json.dumps(r,indent=2))

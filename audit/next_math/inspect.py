import bpy,json
from pathlib import Path
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/next_math')
c=bpy.data.collections['Asset_math_sciences']
p.joinpath('inspection.json').write_text(json.dumps({'materials':[{ 'name':m.name,'color':list(m.diffuse_color),'nodes':[(n.type,n.name) for n in m.node_tree.nodes] if m.use_nodes else []} for m in bpy.data.materials], 'objects':[{ 'name':o.name,'materials':[s.material.name if s.material else None for s in o.material_slots]} for o in c.all_objects if o.type=='MESH']},indent=2))

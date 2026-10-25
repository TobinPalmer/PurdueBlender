import bpy,json
from pathlib import Path
asset=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\purdue_memorial_union_independent_grade\materials_inspection.json')
bpy.ops.wm.open_mainfile(filepath=str(asset)); rows=[]
for m in bpy.data.materials:
 if not m.name.startswith('PMU_'): continue
 nodes=[]; links=[]
 if m.use_nodes and m.node_tree:
  nodes=[{'name':n.name,'type':n.type} for n in m.node_tree.nodes]
  links=[{'from':l.from_node.type+':'+l.from_socket.name,'to':l.to_node.type+':'+l.to_socket.name} for l in m.node_tree.links]
 rows.append({'name':m.name,'use_nodes':m.use_nodes,'nodes':nodes,'links':links})
out.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows[:5],indent=2)); print('materials',len(rows),'with image texture nodes',sum(any(n['type']=='TEX_IMAGE' for n in r['nodes']) for r in rows))

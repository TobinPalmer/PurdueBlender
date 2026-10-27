import bpy,json
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_wiley_dining_court_wdct_8a6c669.blend');bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects['Wiley Dining Court (WDCT)'];m=o.data.materials[0]
print(json.dumps({'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'obj_location':list(o.location),'verts':len(o.data.vertices),'faces':len(o.data.polygons),'material':m.name,'diffuse':list(m.diffuse_color),'node_links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links],'nodes':[(n.name,n.bl_idname) for n in m.node_tree.nodes],'mat_indices':list(set(p.material_index for p in o.data.polygons))},indent=2))

import bpy, json
from mathutils import Vector
FILE=r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\black_cultural_center.blend"
bpy.ops.wm.open_mainfile(filepath=FILE)
asset=bpy.data.collections.get("Asset_black_cultural_center")
assert asset, "Missing export collection"
def all_objects(col):
    for o in col.objects: yield o
    for c in col.children: yield from all_objects(c)
objs=list(all_objects(asset))
mesh=[o for o in objs if o.type=="MESH"]
assert mesh, "No geometry in export collection"
deps=bpy.context.evaluated_depsgraph_get()
pts=[]
for o in mesh:
    ev=o.evaluated_get(deps)
    pts.extend([ev.matrix_world @ Vector(corner) for corner in ev.bound_box])
bbox=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
mats={m for o in mesh for m in o.data.materials if m}
def has_connected_texture(mat):
    if not mat.use_nodes: return False
    nt=mat.node_tree
    outputs=[n for n in nt.nodes if n.type=="OUTPUT_MATERIAL"]
    if not outputs: return False
    seen=set(); stack=[l.from_node for o in outputs for l in nt.links if l.to_node==o]
    while stack:
        node=stack.pop()
        if node in seen: continue
        seen.add(node)
        if node.type.startswith("TEX_"): return True
        stack += [l.from_node for l in nt.links if l.to_node==node]
    return False
missing=[m.name for m in mats if not m.use_nodes or not any(l.to_node.type=="OUTPUT_MATERIAL" for l in m.node_tree.links)]
connected=[m.name for m in mats if has_connected_texture(m)]
assert not missing, "materials without connected output: "+repr(missing)
assert len(connected)>=5, "Expected procedural materials are disconnected"
assert bpy.context.scene.camera, "Missing preview camera"
scene=bpy.context.scene
scene.render.filepath=r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\black_cultural_center_preview_verified.png"
scene.render.resolution_percentage=100
bpy.ops.render.render(write_still=True)
result={"file":FILE,"collection":asset.name,"objects":len(objs),"meshes":len(mesh),"bbox_local_m":bbox,"materials":len(mats),"materials_with_connected_texture_nodes":len(connected),"unconnected_materials":missing,"camera":scene.camera.name,"render":scene.render.filepath,"render_width":scene.render.resolution_x,"render_height":scene.render.resolution_y}
with open(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\black_cultural_center_validation.json","w",encoding="utf-8") as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))

import bpy
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular" / "buildings" / "massing_phi_kappa_sigma_fid829.blend"
bpy.ops.wm.open_mainfile(filepath=str(asset))
shell = bpy.data.objects.get("Phi Kappa Sigma | stepped GIS shell")
print("UV layers", [uv.name for uv in shell.data.uv_layers])
for poly in list(shell.data.polygons)[:8]:
    uv = shell.data.uv_layers.active
    print("face", poly.index, len(poly.loop_indices), [tuple(round(v, 3) for v in uv.data[i].uv) for i in poly.loop_indices])
mat = bpy.data.materials.get("White painted brick | procedural")
for node in mat.node_tree.nodes:
    print("node", node.type, node.name, "inputs", [(i.name, getattr(i, "default_value", None)) for i in node.inputs if hasattr(i, "default_value")][:4])
for link in mat.node_tree.links:
    print("link", link.from_node.type, link.from_socket.name, "->", link.to_node.type, link.to_socket.name)

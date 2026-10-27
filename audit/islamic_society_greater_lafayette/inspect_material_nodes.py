import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular" / "buildings" / "massing_islamic_societyof_greater_lafayette_0130012.blend"
bpy.ops.wm.open_mainfile(filepath=str(asset))
collection = bpy.data.collections.get("Asset_massing_islamic_societyof_greater_lafayette_0130012")
mesh_objects = [o for o in collection.all_objects if o.type == "MESH"] if collection else []
result = {"uv_layers": {}, "materials": []}
for obj in mesh_objects:
    uv_summary = []
    for layer in obj.data.uv_layers:
        coords = [loop.uv[:] for loop in layer.data]
        uv_summary.append({"name": layer.name,
                           "bounds": [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(2)],
                           "polygon_sample_by_material": [
                               {"material_index": mi,
                                "uv_bounds": [[min(layer.data[li].uv[i] for li in poly.loop_indices),
                                               max(layer.data[li].uv[i] for li in poly.loop_indices)] for i in range(2)]}
                               for mi in sorted({poly.material_index for poly in obj.data.polygons})
                               for poly in [next(p for p in obj.data.polygons if p.material_index == mi)]
                           ]})
    result["uv_layers"][obj.name] = uv_summary
    for mat in obj.data.materials:
        if mat is None:
            continue
        row = {"name": mat.name, "use_nodes": mat.use_nodes, "node_types": [], "connections": []}
        if mat.use_nodes:
            row["node_types"] = [{"name": n.name, "type": n.type,
                                  "inputs": {s.name: (list(s.default_value) if hasattr(s.default_value, '__len__') else s.default_value)
                                             for s in n.inputs if hasattr(s, 'default_value')}}
                                 for n in mat.node_tree.nodes]
            row["connections"] = [{"from": l.from_node.name + "." + l.from_socket.name,
                                   "to": l.to_node.name + "." + l.to_socket.name}
                                  for l in mat.node_tree.links]
        result["materials"].append(row)
out = root / "audit" / "islamic_society_greater_lafayette" / "material_node_inventory.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))

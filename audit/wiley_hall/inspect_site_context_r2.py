import bpy, json
from pathlib import Path

asset = Path(bpy.data.filepath).resolve()
names = {
    "Lawn | mixed summer grass.001", "Road | aged asphalt.001",
    "Road | faded yellow.001", "Road | parking paint.001", "Walk | warm concrete.001",
    "Mulch.001", "WILEY_IMPORT_FLAG", "AssetRoot_wiley_hall"
}
out = {"asset": str(asset), "objects": []}
site_context = bpy.data.collections.get("Wiley_SiteContext_NotExported")
if site_context:
    site_context.hide_viewport = False
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
for obj in sorted(bpy.data.objects, key=lambda x: x.name):
    if obj.name not in names:
        continue
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh() if obj.type == 'MESH' else None
    item = {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "collections": [c.name for c in obj.users_collection],
        "location": list(obj.location),
        "dimensions": list(ev.dimensions),
        "matrix_world": [list(row) for row in ev.matrix_world],
        "scale": list(obj.scale),
        "data_name": obj.data.name if obj.data else None,
        "modifiers": [m.name + ':' + m.type for m in obj.modifiers],
        "vertex_count_evaluated": len(mesh.vertices) if mesh else None,
        "polygon_count_evaluated": len(mesh.polygons) if mesh else None,
        "hide_render": obj.hide_render,
        "hide_viewport": obj.hide_viewport,
        "hide_get": obj.hide_get(),
    }
    if mesh:
        bounds = [[float('inf')]*3, [float('-inf')]*3]
        for v in mesh.vertices:
            p = ev.matrix_world @ v.co
            for a in range(3):
                bounds[0][a] = min(bounds[0][a], float(p[a]))
                bounds[1][a] = max(bounds[1][a], float(p[a]))
        item['evaluated_bounds_world'] = bounds
        ev.to_mesh_clear()
    out['objects'].append(item)
Path(__file__).with_name('site_context_r2.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf8')
if site_context:
    site_context.hide_viewport = True
print(json.dumps(out, indent=2))

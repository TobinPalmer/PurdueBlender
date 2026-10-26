"""Reopen and render the CQNE asset for evidence and portability checks."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/massing_cary_quadrangle_northeast_cqne_0a76fca.blend"
preview = root / "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/cqne_preview.png"
report = root / "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/reopen_validation.json"
ndhm_report = root / "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/ndhm_measurement.json"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.data.scenes["Building_massing_cary_quadrangle_northeast_cqne_0a76fca"]
collection = bpy.data.collections["Asset_massing_cary_quadrangle_northeast_cqne_0a76fca"]
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in collection.objects:
    ev = obj.evaluated_get(depsgraph)
    if ev.type == "MESH":
        mesh = ev.to_mesh()
        points.extend([ev.matrix_world @ v.co for v in mesh.vertices])
        ev.to_mesh_clear()
mins = [min(p[i] for p in points) for i in range(3)]
maxs = [max(p[i] for p in points) for i in range(3)]
center = Vector([(a+b)/2 for a,b in zip(mins,maxs)])
dimensions = [b-a for a,b in zip(mins,maxs)]

cam_data = bpy.data.cameras.new("CQNE evidence camera")
cam = bpy.data.objects.new("CQNE evidence camera", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = center + Vector((1.35, -1.75, 1.25)) * max(dimensions[:2])
direction = center - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
cam.data.type = "ORTHO"
cam.data.ortho_scale = max(dimensions[:2]) * 1.45

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.36, 0.34, 0.31, 1.0)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.75
light_data = bpy.data.lights.new("CQNE large softbox", type="AREA")
light = bpy.data.objects.new("CQNE large softbox", light_data)
scene.collection.objects.link(light)
light.location = center + Vector((35,-45,70))
light_data.energy = 13000
light_data.size = 45
light.rotation_euler = (center-light.location).to_track_quat("-Z","Y").to_euler()
fill_data = bpy.data.lights.new("CQNE facade fill", type="AREA")
fill = bpy.data.objects.new("CQNE facade fill", fill_data)
scene.collection.objects.link(fill)
fill.location = center + Vector((-10,-35,32))
fill_data.energy = 48000
fill_data.size = 50
fill.rotation_euler = (center-fill.location).to_track_quat("-Z","Y").to_euler()
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y = 1400, 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(preview)
scene.render.film_transparent = False
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"
bpy.ops.render.render(write_still=True)

result = {
  "asset": str(asset),
  "collection": collection.name,
  "scene": scene.name,
  "object_count": len(collection.objects),
  "mesh_count": sum(o.type == "MESH" for o in collection.objects),
  "world_bounds_m": [[round(x,4) for x in mins], [round(x,4) for x in maxs]],
  "world_dimensions_m": [round(x,4) for x in dimensions],
  "collection_instance_transform": "identity (campus-coordinate massing)",
  "modifiers": {o.name: [m.name+":"+m.type for m in o.modifiers] for o in collection.objects if o.modifiers},
  "missing_external_files": [x.filepath for x in bpy.data.images if x.source == "FILE" and x.filepath and not Path(bpy.path.abspath(x.filepath)).exists()],
  "render": str(preview),
  "independent_height_evidence": str(ndhm_report),
  "independent_height_summary": json.loads(ndhm_report.read_text(encoding="utf-8"))["native_height_summary"],
}
report.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))

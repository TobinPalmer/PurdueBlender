"""Fresh-process audit and inspection renders for the Wiley Hall asset."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/wiley_hall.blend"
OUT = ROOT / "audit/wiley_hall"
EXPECTED_COLLECTION = "Asset_wiley_hall"


def safe_path(path: str) -> str:
    return bpy.path.abspath(path) if path else ""


def image_path(image) -> str:
    if not image or not image.filepath:
        return ""
    try:
        return bpy.path.abspath(image.filepath, library=image.library)
    except TypeError:
        if image.library and image.filepath.startswith("//"):
            return str((Path(bpy.path.abspath(image.library.filepath)).parent / image.filepath[2:]).resolve())
        return safe_path(image.filepath)


def material_info(material):
    info = {"name": material.name, "use_nodes": material.use_nodes}
    if not material.use_nodes or not material.node_tree:
        info["diffuse_color"] = list(material.diffuse_color)
        return info
    info["principled"] = []
    for node in material.node_tree.nodes:
        if node.type != "BSDF_PRINCIPLED":
            continue
        p = {"name": node.name}
        for key in ("Base Color", "Roughness", "Metallic", "Alpha", "Transmission Weight", "IOR"):
            socket = node.inputs.get(key)
            if socket is not None:
                value = socket.default_value
                try:
                    value = list(value)
                except TypeError:
                    pass
                p[key] = value
        info["principled"].append(p)
    info["image_nodes"] = [
        {"image": n.image.name if n.image else None,
         "filepath": image_path(n.image) if n.image else None,
         "exists": Path(image_path(n.image)).exists() if n.image and n.image.filepath else None}
        for n in material.node_tree.nodes if n.type == "TEX_IMAGE"
    ]
    return info


def main():
    if Path(bpy.data.filepath).resolve() != ASSET.resolve():
        raise RuntimeError(f"Not opened from the expected asset: {bpy.data.filepath}")
    collection = bpy.data.collections.get(EXPECTED_COLLECTION)
    if collection is None:
        raise RuntimeError(f"Missing export collection {EXPECTED_COLLECTION}")
    objects = list(collection.all_objects)
    types = Counter(obj.type for obj in objects)
    meshes = [obj for obj in objects if obj.type == "MESH"]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mins, maxs = [float("inf")] * 3, [float("-inf")] * 3
    mesh_bounds = {}
    materialless = []
    invalid_slots = []
    material_names = set()
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        bmin, bmax = [float("inf")] * 3, [float("-inf")] * 3
        try:
            for vertex in mesh.vertices:
                p = evaluated.matrix_world @ vertex.co
                for axis in range(3):
                    bmin[axis] = min(bmin[axis], float(p[axis]))
                    bmax[axis] = max(bmax[axis], float(p[axis]))
            if mesh.vertices:
                mesh_bounds[obj.name] = [[round(v, 6) for v in bmin], [round(v, 6) for v in bmax]]
                for axis in range(3):
                    mins[axis] = min(mins[axis], bmin[axis])
                    maxs[axis] = max(maxs[axis], bmax[axis])
        finally:
            evaluated.to_mesh_clear()
        if len(obj.data.materials) == 0:
            materialless.append(obj.name)
        if any(index >= len(obj.data.materials) for poly in obj.data.polygons for index in [poly.material_index]):
            invalid_slots.append(obj.name)
        material_names.update(m.name for m in obj.data.materials if m is not None)
    root = bpy.data.objects.get("AssetRoot_wiley_hall")
    links = [{"filepath": lib.filepath, "resolved": safe_path(lib.filepath),
              "exists": Path(safe_path(lib.filepath)).exists() if lib.filepath else False}
             for lib in bpy.data.libraries]
    missing_images = [img.filepath for img in bpy.data.images if img.source == "FILE" and img.filepath and not Path(image_path(img)).exists()]
    report = {
        "validation": "Independent fresh reopen of saved asset in Blender 5.2.3 LTS",
        "asset": str(ASSET),
        "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "reopened_saved_asset": True,
        "blender_version": bpy.app.version_string,
        "scene": bpy.context.scene.name,
        "export_collection": collection.name,
        "export_collection_object_count": len(objects),
        "object_type_counts": dict(types),
        "mesh_count": len(meshes),
        "evaluated_mesh_bounds_local_axis_major_m": [[mins[i], maxs[i]] for i in range(3)],
        "empty_mesh_objects": [o.name for o in meshes if len(o.data.vertices) == 0],
        "materialless_meshes": materialless,
        "invalid_material_slot_meshes": invalid_slots,
        "material_count": len(material_names),
        "material_names": sorted(material_names),
        "materials": [material_info(m) for m in bpy.data.materials if m.name in material_names],
        "external_images": [
            {"name": img.name, "filepath": img.filepath, "resolved": image_path(img),
             "exists": Path(image_path(img)).exists() if img.filepath else None,
             "packed": bool(img.packed_file)}
            for img in bpy.data.images if img.source == "FILE"
        ],
        "missing_external_images": missing_images,
        "linked_libraries": links,
        "root_transform": {
            "name": root.name if root else None,
            "location": list(root.location) if root else None,
            "rotation": list(root.rotation_euler) if root else None,
            "scale": list(root.scale) if root else None,
        },
        "cameras": [{"name": o.name, "location": list(o.location), "rotation": list(o.rotation_euler),
                     "resolution": [o.data.lens, bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y]}
                    for o in objects if o.type == "CAMERA"],
        "lights": [{"name": o.name, "type": o.data.type, "energy": o.data.energy}
                   for o in objects if o.type == "LIGHT"],
        "object_name_samples": [o.name for o in objects[:100]],
        "materials_missing_texture_nodes": [m.name for m in bpy.data.materials if m.name in material_names and not any(n.type == "TEX_IMAGE" for n in m.node_tree.nodes) if m.use_nodes and m.node_tree],
    }
    (OUT / "independent_reopen.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (OUT / "mesh_bounds.json").write_text(json.dumps(mesh_bounds, indent=2) + "\n", encoding="utf-8")
    # Render every saved camera in the asset's own scene; render settings are in-memory only.
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    target = bpy.data.objects.new("WILEY_GRADE_TEMP_CAMERA", bpy.data.cameras.new("WILEY_GRADE_TEMP_CAMERA"))
    scene.collection.objects.link(target)
    from mathutils import Vector
    look = Vector((-147.5, 0.0, 5.5))
    camera = target.data
    camera.type = "ORTHO"
    camera.ortho_scale = 175.0
    target.location = look + Vector((115.0, -190.0, 135.0))
    target.rotation_euler = (look - target.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = target
    scene.render.filepath = str(OUT / "oblique.png")
    bpy.ops.render.render(write_still=True)
    target.location = look + Vector((0.0, 0.0, 280.0))
    target.rotation_euler = (look - target.location).to_track_quat("-Z", "Y").to_euler()
    camera.type = "ORTHO"
    camera.ortho_scale = 150.0
    scene.render.filepath = str(OUT / "top.png")
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(target, do_unlink=True)
    bpy.data.cameras.remove(camera)
    print(json.dumps({k: report[k] for k in ("sha256", "scene", "export_collection_object_count", "object_type_counts", "evaluated_mesh_bounds_local_axis_major_m", "material_count", "materialless_meshes", "missing_external_images", "linked_libraries", "root_transform", "cameras", "lights")}, indent=2))


main()

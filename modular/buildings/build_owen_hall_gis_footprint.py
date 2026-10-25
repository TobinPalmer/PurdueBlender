"""Rebuild Owen Hall's exterior shell from Purdue's mapped footprint.

Run with Blender in background against modular/buildings/owen_hall.blend.
The GIS polygon supplies horizontal geometry only. Vertical dimensions remain
the existing estimates; this script does not infer or alter them.
"""
import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
BLEND = ROOT / "modular" / "buildings" / "owen_hall.blend"
GIS = ROOT / "audit" / "owen_hall_independent_grade" / "sources" / "purdue_owen_gis_feature_38.json"
MANIFEST = ROOT / "modular" / "manifest.json"


def material(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        raise RuntimeError(f"Expected Owen Hall material not found: {name}")
    return mat


def extrusion(name, outline, z0, z1, mat, collection):
    """Create a watertight polygon extrusion from the source outline."""
    n = len(outline)
    verts = [(x, y, z0) for x, y in outline] + [(x, y, z1) for x, y in outline]
    xy_vectors = [Vector((x, y, 0.0)) for x, y in outline]
    triangles = tessellate_polygon([xy_vectors])
    faces = [tuple(reversed(range(n)))]
    faces.extend(tuple(n + i for i in tri) for tri in triangles)
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def roof_coping(outline, z0, z1, mat, collection):
    """Create narrow coping bars around the polygon perimeter, not a roof slab."""
    verts, faces = [], []
    unit = [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),
            (-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
    face_pattern = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for a, b in zip(outline, outline[1:] + outline[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (z0 + z1) / 2)
        base = len(verts)
        for x, y, z in unit:
            rx = x * max(length, .18) * math.cos(angle) - y * .28 * math.sin(angle)
            ry = x * max(length, .18) * math.sin(angle) + y * .28 * math.cos(angle)
            verts.append((c[0] + rx, c[1] + ry, c[2] + z * (z1-z0)))
        faces.extend(tuple(base+i for i in face) for face in face_pattern)
    mesh = bpy.data.meshes.new("Owen_GIS_Roof_Coping_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new("Owen_GIS_Roof_Coping", mesh)
    collection.objects.link(obj)
    return obj


def run():
    with MANIFEST.open(encoding="utf-8") as f:
        manifest = json.load(f)
    entry = next(a for a in manifest["assets"] if a["id"] == "owen_hall")
    px, py = entry["placement_origin_xy_m"]
    with GIS.open(encoding="utf-8") as f:
        feature = next(x for x in json.load(f)["features"] if x["attributes"]["OBJECTID"] == 38)
    ring = feature["geometry"]["rings"][0]
    x_scale = 111412.84 * math.cos(math.radians(40.4274))
    outline = [((lon + 86.9137) * x_scale - px,
                (lat - 40.4274) * 111040.0 - py) for lon, lat in ring[:-1]]

    asset = bpy.data.collections.get("Asset_owen_hall")
    if asset is None:
        raise RuntimeError("Asset_owen_hall collection is missing")
    shell_terms = (
        "_Limestone_Base", "_Brick_Shaft", "_GF_Wall_", "_Upper_Brick_Shaft",
        "_Ceiling_Slab", "_Limestone_Belt_", "_Roof_Parapet_Coping",
        "_Roof_Membrane", "_Roof_Penthouse_", "_Roof_HVAC_",
    )
    obsolete = [obj for obj in asset.objects
                if obj.name.startswith("Owen_GIS_") or any(term in obj.name for term in shell_terms)]
    for obj in obsolete:
        old_mesh = obj.data if obj.type == "MESH" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if old_mesh is not None and old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)

    brick = material("Beering_Purdue_Red_Brick")
    limestone = material("Indiana_Bedford_Limestone")
    roof = bpy.data.materials.get("Owen_R2_Roof_Membrane") or bpy.data.materials.new("Owen_R2_Roof_Membrane")
    roof.use_nodes = True
    roof_bsdf = next(n for n in roof.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    roof_bsdf.inputs["Base Color"].default_value = (.16,.17,.18,1)
    roof_bsdf.inputs["Roughness"].default_value = .82
    extrusion("Owen_GIS_Limestone_Base", outline, 0.0, 1.5, limestone, asset)
    extrusion("Owen_GIS_Brick_Shell", outline, 1.5, 15.2, brick, asset)
    for z, idx in ((3.8, 1), (7.6, 2), (11.4, 3), (15.2, 4)):
        extrusion(f"Owen_GIS_Limestone_Belt_{idx}", outline, z - 0.11, z + 0.11, limestone, asset)
    extrusion("Owen_GIS_Roof_Membrane", outline, 15.2, 15.35, roof, asset)
    roof_coping(outline, 15.6, 16.0, limestone, asset)

    # Preserve the asset's local frame and expected scene; only save the library.
    bpy.context.scene.camera = bpy.data.objects.get("Cam_27_Owen_Hall_StadiumAve_StreetView")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print(json.dumps({
        "saved": str(BLEND), "source_feature": 38,
        "source_vertices": len(outline), "removed_shell_objects": len(obsolete),
        "new_shell_objects": 8,
        "local_outline_bounds_m": [
            [min(x for x, y in outline), max(x for x, y in outline)],
            [min(y for x, y in outline), max(y for x, y in outline)],
        ],
        "vertical_dimensions_status": "unchanged estimates; no authoritative height source",
    }, indent=2))


if __name__ == "__main__":
    run()

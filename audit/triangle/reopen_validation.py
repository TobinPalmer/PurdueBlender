"""Fresh-open and link-portability checks for the Triangle Blender library."""

import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_triangle_fraternity_8477ad9"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
COLLECTION = f"Asset_{ASSET_ID}"
SCENE = f"Building_{ASSET_ID}"
OBJECT = "Triangle Fraternity"
EVIDENCE = ROOT / "audit" / "triangle"


def bounds_world(obj):
    points = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def main():
    assert Path(bpy.data.filepath).resolve() == ASSET.resolve(), bpy.data.filepath
    scene = bpy.data.scenes.get(SCENE)
    assert scene is not None, f"Missing scene {SCENE}"
    col = bpy.data.collections.get(COLLECTION)
    assert col is not None, f"Missing collection {COLLECTION}"
    assert len(col.objects) == 1, f"Collection object count {len(col.objects)}"
    obj = col.objects[0]
    assert obj.name == OBJECT and obj.type == "MESH"
    assert not obj.modifiers, "Unexpected unapplied modifiers"
    assert all(math.isfinite(v) for axis in bounds_world(obj) for v in axis)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    loose_vertices = sum(not vert.link_edges for vert in bm.verts)
    faces = len(bm.faces)
    verts = len(bm.verts)
    edges = len(bm.edges)
    saved_bounds = bounds_world(obj)
    saved_name = obj.name
    gis = json.loads((EVIDENCE / "sources" / "purdue_gis_fid777_triangle_2026-10-26.json").read_text(encoding="utf-8"))
    ring = gis["features"][0]["geometry"]["rings"][0][:-1]
    expected = [
        ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
         (lat - 40.4274) * 111040.0)
        for lon, lat in ring
    ]
    shell = [(obj.data.vertices[2*i].co.x, obj.data.vertices[2*i].co.y) for i in range(len(expected))]
    footprint_errors = [min(math.hypot(x-gx, y-gy) for gx,gy in expected) for x,y in shell]
    max_footprint_error = max(footprint_errors)
    bm.free()
    images = [image.filepath for image in bpy.data.images if image.source == "FILE"]
    assert not images, f"Unexpected external image dependencies: {images}"

    # Append the same named collection as an external library into a clean scene.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(ASSET), link=True) as (data_from, data_to):
        assert COLLECTION in data_from.collections
        data_to.collections = [COLLECTION]
    linked = next(c for c in bpy.data.collections if c.name.startswith(COLLECTION))
    bpy.context.scene.collection.children.link(linked)
    assert linked.library is not None
    assert len(linked.objects) == 1 and linked.objects[0].name == OBJECT
    probe_path = EVIDENCE / "portable_probe.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(probe_path))
    result = {
        "passed": True,
        "blender_version": bpy.app.version_string,
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "scene": SCENE,
        "collection": COLLECTION,
        "object_count": 1,
        "object_name": saved_name,
        "mesh_vertices": verts,
        "mesh_edges": edges,
        "mesh_faces": faces,
        "nonmanifold_edges": nonmanifold,
        "loose_vertices": loose_vertices,
        "evaluated_world_bounds_m": saved_bounds,
        "source_footprint_vertex_count": len(expected),
        "shell_footprint_vertex_count": len(shell),
        "shell_to_source_vertex_nearest_error_max_m": max_footprint_error,
        "external_file_images": images,
        "linked_collection_library_path": linked.library.filepath,
        "portable_probe": str(probe_path.relative_to(ROOT)).replace("\\", "/"),
        "portable_probe_reopen_check": "run separately with probe_reopen_validation.py",
    }
    (EVIDENCE / "reopen_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

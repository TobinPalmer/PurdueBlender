"""Build the Lilly Hall of Life Sciences modular massing asset.

The GIS shell is preserved from the Purdue BuildingShapesZip4 service (FID 581).
All dimensions are meters in the repository campus frame, X east / Y north.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "massing_lilly_hall_e7fc13e"
SOURCE = EVIDENCE / "sources" / "purdue_gis_fid_581.json"
OUT = ROOT / "modular" / "buildings" / "massing_lilly_hall_e7fc13e.blend"
COLLECTION_NAME = "Asset_massing_lilly_hall_e7fc13e"
SCENE_NAME = "Building_massing_lilly_hall_e7fc13e"

# Purdue GIS gives the roof reference as 82.2, alongside floor level references
# in 12-unit increments. Those values are interpreted as feet based on the
# level increments; retain the uncertainty in the evidence record.
HEIGHT_M = 82.2 * 0.3048
FLOOR_TOPS_M = [12, 24, 36, 48, 60, 72]  # GIS level sequence, converted below
FLOOR_TOPS_M = [ft * 0.3048 for ft in FLOOR_TOPS_M if ft * 0.3048 < HEIGHT_M - 1.2]


def mercator_to_campus(x: float, y: float) -> tuple[float, float]:
    """Convert EPSG:3857 to the project local equirectangular campus frame."""
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2.0 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2.0)
    campus_x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    campus_y = (lat - 40.4274) * 111040.0
    return campus_x, campus_y


def material(name, color, roughness=0.78):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.roughness = roughness
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    return mat


def make_mesh(name, verts, faces, mats, indices=None):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    if indices:
        for poly, idx in zip(mesh.polygons, indices):
            poly.material_index = idx
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def add_quad(verts, faces, a, b, c, d):
    start = len(verts)
    verts.extend((a, b, c, d))
    faces.append((start, start + 1, start + 2, start + 3))


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    feature = data["features"][0]
    ring = feature["geometry"]["rings"][0]
    footprint = [Vector((*mercator_to_campus(float(x), float(y)), 0.0)) for x, y in ring[:-1]]
    if len(footprint) < 3:
        raise RuntimeError("Lilly Hall GIS feature has no usable exterior ring")
    signed_area2 = sum(footprint[i].x * footprint[(i + 1) % len(footprint)].y -
                       footprint[(i + 1) % len(footprint)].x * footprint[i].y
                       for i in range(len(footprint)))
    if signed_area2 < 0:
        footprint.reverse()

    # Start from a clean scene and preserve the manifest's stable scene/collection names.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        if coll.name != "Collection":
            bpy.data.collections.remove(coll)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
    if collection.name not in [c.name for c in scene.collection.children]:
        scene.collection.children.link(collection)
    preview_collection = bpy.data.collections.new("Lilly Hall | preview rig only")
    scene.collection.children.link(preview_collection)

    brick = material("Lilly | masonry shell, archival photo reference", (0.43, 0.38, 0.32))
    stone = material("Lilly | pale stone bands, archival photo reference", (0.70, 0.68, 0.62))
    glass = material("Lilly | recessed dark glazing, schematic", (0.12, 0.20, 0.23), 0.24)
    entry_mat = material("Lilly | entry shadow", (0.08, 0.10, 0.11), 0.35)

    # Build the traced exterior as a single, closed architectural shell.
    verts = [tuple(v) for v in footprint]
    verts.extend((v.x, v.y, HEIGHT_M) for v in footprint)
    n = len(footprint)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    shell = make_mesh("Lilly Hall | official footprint shell", verts, faces, [brick, stone],
                      [0, 1] + [0] * n)
    shell["source_feature"] = "Purdue GIS BuildingShapesZip4 FID 581"
    shell["source_footprint"] = "Exact transformed exterior ring; source CRS EPSG:3857"
    shell["vertical_basis"] = "GIS R=82.2 interpreted as feet; height remains estimated pending units confirmation"

    # The historic Purdue Libraries exterior photograph shows repetitive windows,
    # a pale monumental entrance surround, and long horizontal classroom wings.
    # This simple panel rhythm is an evidence-based representation of that
    # mid-century character; contemporary window registration is not surveyed.
    glazing_verts, glazing_faces = [], []
    entry_verts, entry_faces = [], []
    # Pick a long north-side segment for the address frontage; the exact door bay
    # is explicitly an inference because the historic image lacks orientation.
    north_edges = []
    area2 = sum(footprint[i].x * footprint[(i + 1) % n].y - footprint[(i + 1) % n].x * footprint[i].y for i in range(n))
    winding = 1.0 if area2 > 0 else -1.0
    for i in range(n):
        p0, p1 = footprint[i], footprint[(i + 1) % n]
        edge = p1 - p0
        length = edge.length
        if length < 3.2:
            continue
        # Exterior normal for a ring's winding; coordinate ring may be clockwise.
        outward = Vector((edge.y, -edge.x, 0.0)) * winding
        outward.normalize()
        if (p0.y + p1.y) * 0.5 > max(p.y for p in footprint) - 7.0:
            north_edges.append((length, i, p0, p1, outward))
        bays = max(1, int(length // 6.5))
        for bay in range(bays):
            center = (bay + 0.5) / bays
            width = min(1.45, length / bays * 0.43)
            half = width * 0.5
            center_xy = p0.lerp(p1, center)
            for floor_idx in range(len(FLOOR_TOPS_M) + 1):
                floor_bottom = 0.0 if floor_idx == 0 else FLOOR_TOPS_M[floor_idx - 1]
                floor_top = FLOOR_TOPS_M[floor_idx] if floor_idx < len(FLOOR_TOPS_M) else HEIGHT_M
                if floor_top - floor_bottom < 2.4:
                    continue
                sill = floor_bottom + (0.82 if floor_idx else 1.0)
                head = min(floor_top - 0.55, sill + 1.45)
                if head <= sill:
                    continue
                left = center_xy - edge.normalized() * half + outward * 0.035
                right = center_xy + edge.normalized() * half + outward * 0.035
                add_quad(glazing_verts, glazing_faces,
                         (left.x, left.y, sill), (right.x, right.y, sill),
                         (right.x, right.y, head), (left.x, left.y, head))

    # Mark a modest recessed north-side portal with a light surround and canopy.
    # It is schematic; archival photo proves a monumental entry, but not its current bay.
    if north_edges:
        _, _, p0, p1, outward = max(north_edges, key=lambda item: item[0])
        edge = p1 - p0
        center = (p0 + p1) * 0.5
        halfw = min(1.6, edge.length * 0.12)
        l = center - edge.normalized() * halfw + outward * 0.08
        r = center + edge.normalized() * halfw + outward * 0.08
        add_quad(entry_verts, entry_faces, (l.x,l.y,0.1),(r.x,r.y,0.1),(r.x,r.y,3.4),(l.x,l.y,3.4))
        # canopy above the portal, shallow enough to read as a detail rather than a new wing
        canopy = [((l.x,l.y,3.35),(r.x,r.y,3.35),(r.x+outward.x*1.2,r.y+outward.y*1.2,3.35),(l.x+outward.x*1.2,l.y+outward.y*1.2,3.35))]
    else:
        canopy = []
    if glazing_faces:
        gl = make_mesh("Lilly Hall | schematic window bays", glazing_verts, glazing_faces, [glass])
        gl.parent = shell
        gl["evidence_note"] = "Mid-century repetitive fenestration visible in Purdue Libraries archive exterior; bay locations schematic"
    if entry_faces:
        en = make_mesh("Lilly Hall | schematic entrance", entry_verts, entry_faces, [entry_mat])
        en.parent = shell
        en["evidence_note"] = "Historic photo supports a prominent entry surround; current entry location is inferred from street address"
    if canopy:
        cv = [v for quad in canopy for v in quad]
        cf = [tuple(range(4))]
        co = make_mesh("Lilly Hall | entrance canopy", cv, cf, [stone])
        co.parent = shell

    # Move generated objects into the dedicated library collection.
    for obj in list(scene.objects):
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        collection.objects.link(obj)

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(EVIDENCE / "preview.png")
    scene.world.color = (0.16, 0.16, 0.16)
    scene.world.use_nodes = True
    world_bg = scene.world.node_tree.nodes.get("Background")
    world_bg.inputs["Color"].default_value = (0.34, 0.34, 0.34, 1.0)
    world_bg.inputs["Strength"].default_value = 0.45
    # Camera and lights stay outside the exported building collection.
    center_x = sum(v.x for v in footprint) / n
    center_y = sum(v.y for v in footprint) / n
    bpy.ops.object.camera_add(location=(center_x + 165, center_y - 175, 125))
    camera = bpy.context.object
    camera.name = "Lilly Hall | preview camera"
    direction = Vector((center_x, center_y, 11)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 50
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(center_x + 20, center_y - 50, 100))
    key = bpy.context.object
    key.name = "Lilly Hall | preview key"
    key.data.energy = 350000
    key.data.shape = "DISK"
    key.data.size = 95
    key.rotation_euler = (Vector((center_x, center_y, 9)) - key.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(center_x - 75, center_y + 80, 62))
    fill = bpy.context.object
    fill.name = "Lilly Hall | preview fill"
    fill.data.energy = 190000
    fill.data.size = 80
    fill.rotation_euler = (Vector((center_x, center_y, 9)) - fill.location).to_track_quat("-Z", "Y").to_euler()
    for obj in (camera, key, fill):
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        preview_collection.objects.link(obj)

    scene.render.filepath = str(EVIDENCE / "preview.png")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    bpy.ops.render.render(write_still=True)
    print("LILLY_BUILD", json.dumps({"scene": scene.name, "collection": collection.name,
          "source_ring_vertices": n, "height_m": HEIGHT_M,
          "bounds": [min(v.x for v in footprint), max(v.x for v in footprint),
                     min(v.y for v in footprint), max(v.y for v in footprint)]}))


if __name__ == "__main__":
    main()

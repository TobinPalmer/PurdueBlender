"""Build a source-backed campus-coordinate massing for Purdue Triangle Fraternity.

Footprint geometry comes from Purdue BuildingShapes FID 777 (see audit/triangle).
Facade details are deliberately restrained estimates from the chapter's 2023
exterior photograph; the source does not provide a measured elevation or plan.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_triangle_fraternity_8477ad9"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
OBJECT_NAME = "Triangle Fraternity"
EVIDENCE_DIR = ROOT / "audit" / "triangle"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137

# Purdue BuildingShapes FeatureServer, layer 0, FID 777. EPSG:4326 ring
# retrieved 2026-10-26; raw snapshot: audit/triangle/sources/.
GIS_RING_LON_LAT = [
    (-86.9172366921182, 40.425330489531),
    (-86.9172556564622, 40.4253307912052),
    (-86.9172543525403, 40.4253789912224),
    (-86.9172334846203, 40.4253786868134),
    (-86.9172319668991, 40.4254408036053),
    (-86.9172173484664, 40.4254406179105),
    (-86.9172165778142, 40.4254764662705),
    (-86.9171632044321, 40.4254758130653),
    (-86.9171605849645, 40.4255623586843),
    (-86.9168208115417, 40.4255554190281),
    (-86.9168246779376, 40.4254440881062),
    (-86.9170292241299, 40.4254482255509),
    (-86.9170295749401, 40.4254370814324),
    (-86.9169982192659, 40.4254365147726),
    (-86.9170023586748, 40.4253017146659),
    (-86.9170294759275, 40.4253021927982),
    (-86.9170301810616, 40.4252784771211),
    (-86.9171405538163, 40.4252803926577),
    (-86.917139847116, 40.4253048495321),
    (-86.9172373617497, 40.4253064718938),
]

# Current public chapter photo shows broad brick wings, flat roof/parapet,
# vertically proportioned dark windows, and a raised central entry canopy.
# Heights and exact facade placements are estimates (roughly three visible
# levels, 10.2 m shell); GIS NUM_LEVELS=1 is preserved as a source conflict.
WALL_HEIGHT = 10.2
ROOF_PARAPET = 0.45
TERRACE_Z = 0.85
TERRACE_DEPTH = 2.4


def local_xy(lon: float, lat: float) -> tuple[float, float]:
    """Repository's approximate campus transform; not a surveyed CRS."""
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return x, y


FOOTPRINT = [local_xy(lon, lat) for lon, lat in GIS_RING_LON_LAT]


def signed_area(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1]
               - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) / 2.0


def material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(vertices, faces, materials, center, axes, half_sizes, mat_index):
    """Append an oriented cuboid, with faces using a material slot index."""
    cx, cy, cz = center
    a, b, c = axes
    hx, hy, hz = half_sizes
    start = len(vertices)
    for sx, sy, sz in ((-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
                       (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)):
        p = Vector((cx, cy, cz)) + a * (sx*hx) + b * (sy*hy) + c * (sz*hz)
        vertices.append(tuple(p))
    for face in ((0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5),
                 (2,3,7,6), (3,0,4,7)):
        faces.append(tuple(start+i for i in face))
        materials.append(mat_index)


def build_geometry():
    brick = material("Buff brick, qualitative photo match", (0.50, 0.36, 0.24))
    dark_brick = material("Dark entry and terrace masonry", (0.16, 0.16, 0.15))
    roof_mat = material("Low-slope roof", (0.12, 0.13, 0.13))
    glass = material("Dark blue-gray glazing", (0.045, 0.085, 0.105), roughness=0.22, metallic=0.18)
    trim = material("Dark metal window and canopy trim", (0.07, 0.075, 0.075), roughness=0.45, metallic=0.35)
    concrete = material("Walk and terrace concrete", (0.47, 0.45, 0.40))
    red = material("Triangle red sign accent", (0.55, 0.045, 0.06), roughness=0.55)
    mats = [brick, dark_brick, roof_mat, glass, trim, concrete, red]

    verts, faces, face_mats = [], [], []
    n = len(FOOTPRINT)
    area = signed_area(FOOTPRINT)
    ccw = area > 0

    # Extruded exact GIS perimeter. A single cap intentionally keeps this a
    # simple-envelope massing: roof structure and interior are not inferred.
    for x, y in FOOTPRINT:
        verts.extend(((x, y, 0.0), (x, y, WALL_HEIGHT)))
    for i in range(n):
        j = (i + 1) % n
        lo_i, hi_i = 2*i, 2*i+1
        lo_j, hi_j = 2*j, 2*j+1
        side = (lo_i, lo_j, hi_j, hi_i) if ccw else (lo_j, lo_i, hi_i, hi_j)
        faces.append(side)
        face_mats.append(0)
    bottom = tuple(2*i for i in (reversed(range(n)) if ccw else range(n)))
    faces.append(bottom)
    face_mats.append(2)
    top = tuple(2*i+1 for i in (range(n) if ccw else reversed(range(n))))
    faces.append(top)
    face_mats.append(2)

    # Parapet band around the perimeter (roof line is inferred from the 2023
    # photo and is not a measured roof elevation).
    for i, p in enumerate(FOOTPRINT):
        q = FOOTPRINT[(i+1) % n]
        dx, dy = q[0]-p[0], q[1]-p[1]
        length = math.hypot(dx, dy)
        if length < 1e-6:
            continue
        tangent = Vector((dx/length, dy/length, 0.0))
        # For a CCW outline, the right-hand normal points outward.
        normal = Vector((tangent.y, -tangent.x, 0.0)) if ccw else Vector((-tangent.y, tangent.x, 0.0))
        midpoint = Vector(((p[0]+q[0])/2, (p[1]+q[1])/2, 0.0))
        # Facade glazing: repeated tall dark windows, 3 levels. Short wall
        # fragments remain unadorned rather than inventing tiny window bays.
        if length >= 5.0:
            bays = max(1, min(8, int(length // 3.8)))
            bay_step = length / bays
            win_w = min(1.05, bay_step * 0.38)
            for row in range(3):
                zc = (1.85, 4.95, 8.05)[row]
                for k in range(bays):
                    along = (k + 0.5) * bay_step
                    c = midpoint + tangent * (along - length/2) + normal * 0.035
                    add_box(verts, faces, face_mats, (c.x, c.y, zc),
                            (tangent, normal, Vector((0,0,1))),
                            (win_w/2, 0.10, 1.05), 3)
                    # Narrow vertical frame stiles at both sides.
                    for side in (-1, 1):
                        fc = c + tangent * (side * win_w * 0.51) + normal * 0.10
                        add_box(verts, faces, face_mats, (fc.x, fc.y, zc),
                                (tangent, normal, Vector((0,0,1))),
                                (0.045, 0.06, 1.12), 4)
        # A low parapet with a charcoal cap creates the flat roof silhouette.
        add_box(verts, faces, face_mats,
                (midpoint.x, midpoint.y, WALL_HEIGHT + ROOF_PARAPET/2),
                (tangent, normal, Vector((0,0,1))),
                (length/2, 0.14, ROOF_PARAPET/2), 2)

    # Main entry terrace and short stair on the west side, consistent with
    # address/frontage and the official chapter photo. Exact position is an
    # image-based inference, marked in evidence as approximate.
    west_edges = []
    for i, p in enumerate(FOOTPRINT):
        q = FOOTPRINT[(i+1) % n]
        dx, dy = q[0]-p[0], q[1]-p[1]
        length = math.hypot(dx, dy)
        if length >= 4.0 and abs(dx) < 0.22 * length:
            west_edges.append((p, q, length, (p[0]+q[0])/2))
    # Select the outermost west-facing street wall first; break ties by length.
    p, q, length, _ = sorted(west_edges, key=lambda e: (e[3], -e[2]))[0]
    dx, dy = q[0]-p[0], q[1]-p[1]
    tangent = Vector((dx/length, dy/length, 0.0))
    outward = Vector((tangent.y, -tangent.x, 0.0)) if ccw else Vector((-tangent.y, tangent.x, 0.0))
    mid = Vector(((p[0]+q[0])/2, (p[1]+q[1])/2, 0))
    # Raised entry slab on the street side.
    terrace_center = mid + outward * (TERRACE_DEPTH/2 + 0.12)
    add_box(verts, faces, face_mats, (terrace_center.x, terrace_center.y, TERRACE_Z/2),
            (tangent, outward, Vector((0,0,1))), (min(length*0.28, 5.0), TERRACE_DEPTH/2, TERRACE_Z/2), 1)
    # Steps and dark terrace front retaining fascia.
    stair_w = min(5.6, length*0.56)
    for step in range(3):
        depth = 0.42
        center = mid + outward * (TERRACE_DEPTH + 0.20 + (step+0.5)*depth)
        ztop = TERRACE_Z * (3-step) / 4.0
        add_box(verts, faces, face_mats, (center.x, center.y, ztop/2),
                (tangent, outward, Vector((0,0,1))), (stair_w/2, depth/2, ztop/2), 5)
    # Entry glazing and doorway at the center of the west-side street wall.
    door_center = mid + outward * 0.09
    add_box(verts, faces, face_mats, (door_center.x, door_center.y, 1.35),
            (tangent, outward, Vector((0,0,1))), (0.78, 0.12, 1.35), 3)
    # Entry canopy projects over the raised entrance terrace.
    canopy_center = mid + outward * 0.72
    add_box(verts, faces, face_mats,
            (canopy_center.x, canopy_center.y, 4.25),
            (tangent, outward, Vector((0,0,1))), (min(2.5,length*0.30), 1.15, 0.18), 4)
    # Gabled roof wedge above the dark canopy, evocative of the chapter photo.
    half_w = min(2.5,length*0.30)
    base_z, peak_z = 4.42, 5.15
    gable_depth = 1.05
    gable_start = len(verts)
    for d in (-gable_depth/2, gable_depth/2):
        for along, z in ((-half_w,base_z),(half_w,base_z),(0.0,peak_z)):
            point = canopy_center + tangent*along + outward*d + Vector((0,0,z))
            verts.append(tuple(point))
    gable_faces = ((0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0))
    for face in gable_faces:
        faces.append(tuple(gable_start+i for i in face))
        face_mats.append(4)
    # Entry glazing/sign panel flanks the ground-level doorway.
    for side in (-1, 1):
        c = mid + tangent * (side*0.95) + outward * 0.06
        add_box(verts, faces, face_mats, (c.x,c.y,1.35),
                (tangent,outward,Vector((0,0,1))), (0.47,0.11,1.0), 3)

    mesh = bpy.data.meshes.new(f"{ASSET_ID}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for mat in mats:
        mesh.materials.append(mat)
    for poly, index in zip(mesh.polygons, face_mats):
        poly.material_index = index
    obj = bpy.data.objects.new(OBJECT_NAME, mesh)
    obj["building_id"] = ASSET_ID
    obj["source_feature"] = "Purdue BuildingShapes FID 777"
    obj["coordinate_convention"] = "campus world coordinates; repository approximate lon/lat transform"
    obj["height_status"] = "estimated from current official chapter photo; GIS level field conflicts"
    obj["shell_height_m_estimate"] = WALL_HEIGHT
    obj["roof_parapet_m_estimate"] = ROOF_PARAPET
    obj["frontage_status"] = "west-side entry is an address/map/photo inference"
    return obj


def main():
    # This builder is designed to be run in a clean background Blender session.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    obj = build_geometry()
    collection.objects.link(obj)

    # Neutral material preview render for evidence/review.
    engine_ids = [item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engine_ids else "BLENDER_CYCLES"
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("Triangle preview world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.68,0.72,0.78,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world
    light_data = bpy.data.lights.new("Triangle key", type="AREA")
    light_data.energy = 1800
    light_data.size = 35
    light = bpy.data.objects.new("Triangle key", light_data)
    light.location = (-330, -205, 65)
    scene.collection.objects.link(light)
    # Camera is preview-only and kept outside the exported asset collection.
    cam_data = bpy.data.cameras.new("Triangle preview camera")
    cam = bpy.data.objects.new("Triangle preview camera", cam_data)
    scene.collection.objects.link(cam)
    center = Vector((sum(p[0] for p in FOOTPRINT)/len(FOOTPRINT),
                     sum(p[1] for p in FOOTPRINT)/len(FOOTPRINT), WALL_HEIGHT/2))
    cam.location = center + Vector((-60, -8, 28))
    direction = center - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    scene.camera = cam
    scene.render.filepath = str(EVIDENCE_DIR / "triangle_preview.png")
    bpy.ops.render.render(write_still=True)

    # Store an asset-only library file with one expected collection and scene.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    result = {
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "object_count": len(collection.objects),
        "object_name": obj.name,
        "footprint_vertices": len(FOOTPRINT),
        "footprint_area_local_m2": abs(signed_area(FOOTPRINT)),
        "footprint_bounds_local_m": [
            [min(p[0] for p in FOOTPRINT), max(p[0] for p in FOOTPRINT)],
            [min(p[1] for p in FOOTPRINT), max(p[1] for p in FOOTPRINT)],
            [0.0, WALL_HEIGHT + ROOF_PARAPET],
        ],
        "estimated_wall_height_m": WALL_HEIGHT,
        "estimated_total_height_m": WALL_HEIGHT + ROOF_PARAPET,
        "source_feature_id": 777,
        "source_crs": "EPSG:4326 transformed with repository approximate local campus conversion",
        "external_image_dependencies": [],
    }
    (EVIDENCE_DIR / "build_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

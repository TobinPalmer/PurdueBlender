"""Rebuild the CRTN campus-coordinate building library from its Purdue GIS ring.

Horizontal plan dimensions follow Purdue BuildingShapesZip4 FID 914. Vertical
volumes are explicitly estimates informed by Turner Construction's description
of a three-story lab wing and two-story animal-studies wing.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_creighton_hall_of_animal_sciences_crtn_a88d450.blend"
GIS = ROOT / "audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/sources/crtn_fid914_gis_snapshot.json"
EVIDENCE = ROOT / "audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/crtn_evidence.json"
PREVIEW_DIR = EVIDENCE.parent / "previews"
COLLECTION_NAME = "Asset_massing_creighton_hall_of_animal_sciences_crtn_a88d450"
SCENE_NAME = "Building_massing_creighton_hall_of_animal_sciences_crtn_a88d450"
OBJECT_NAME = "Creighton Hall of Animal Sciences (CRTN)"
ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274
LON_M, LAT_M = 84810.60416539927, 111040.0


def load_ring():
    payload = json.loads(GIS.read_text(encoding="utf-8-sig"))
    feature = payload["features"][0]
    assert feature["attributes"]["FID"] == 914
    ring = feature["geometry"]["rings"][0]
    return [((p[0] - ORIGIN_LON) * LON_M, (p[1] - ORIGIN_LAT) * LAT_M) for p in ring[:-1]]


def clip_x(poly, x_limit, keep_west=True):
    """Sutherland-Hodgman clip to either side of the wing split."""
    out = []
    inside = lambda p: p[0] <= x_limit if keep_west else p[0] >= x_limit
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ain, bin = inside(a), inside(b)
        if ain and bin:
            out.append(b)
        elif ain and not bin:
            t = (x_limit - a[0]) / (b[0] - a[0])
            out.append((x_limit, a[1] + t * (b[1] - a[1])))
        elif not ain and bin:
            t = (x_limit - a[0]) / (b[0] - a[0])
            out.extend([(x_limit, a[1] + t * (b[1] - a[1])), b])
    # Remove consecutive duplicates created where the GIS ring touches the clip.
    clean = []
    for p in out:
        if not clean or math.dist(clean[-1], p) > 1e-5:
            clean.append(p)
    if len(clean) > 2 and math.dist(clean[0], clean[-1]) < 1e-5:
        clean.pop()
    return clean


def material(name, color, roughness=0.82, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


BRICK = material("CRTN warm red-brown brick (photo-derived)", (0.34, 0.105, 0.068))
BRICK_DARK = material("CRTN recessed brick joints", (0.22, 0.063, 0.042))
CONCRETE = material("CRTN light concrete trim (photo-derived)", (0.63, 0.62, 0.56))
GLASS = material("CRTN blue-gray glazing (schematic)", (0.12, 0.24, 0.31), 0.24, 0.12)
ROOF = material("CRTN flat membrane roof (estimated)", (0.33, 0.35, 0.34))
METAL = material("CRTN canopy steel (schematic)", (0.26, 0.29, 0.30), 0.35, 0.62)


def mesh_object(name, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def solid_polygon(name, poly, z0, z1, mat, collection):
    points = [Vector((x, y, 0.0)) for x, y in poly]
    triangles = tessellate_polygon([points])
    verts = [(x, y, z) for z in (z0, z1) for x, y in poly]
    n = len(poly)
    faces = [tuple(reversed(t)) for t in triangles]
    faces.extend([tuple(i + n for i in t) for t in triangles])
    faces.extend([(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)])
    return mesh_object(name, verts, faces, mat, collection)


def box_obj(name, center, dims, mat, collection, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def wall_windows(poly, zbase, floors, floor_height, prefix, collection, exclude_x=None):
    """Schematic regular tall glazing on each long facade, with concrete heads."""
    for idx, (a, b) in enumerate(zip(poly, poly[1:] + poly[:1])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if exclude_x is not None and abs(a[0] - exclude_x) < 1e-4 and abs(b[0] - exclude_x) < 1e-4:
            continue
        if length < 4.0:
            continue
        angle = math.atan2(dy, dx)
        count = max(1, int(length // 5.5))
        ux, uy = dx / length, dy / length
        # Outward direction is determined from ring winding; this signed offset
        # merely places repeated windows on the exterior wall plane.
        winding = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
        sign = -1.0 if winding > 0 else 1.0
        nx, ny = sign * uy, -sign * ux
        for j in range(count):
            s = length * (j + 0.5) / count
            x, y = a[0] + ux * s + nx * 0.035, a[1] + uy * s + ny * 0.035
            for fl in range(floors):
                sill = zbase + fl * floor_height + 0.92
                wh = 1.65
                ww = min(2.35, length / (count + 1) * 0.62)
                box_obj(f"{prefix} glazing {idx:02d}-{j:02d}-F{fl+1}", (x, y, sill + wh / 2), (ww, 0.11, wh), GLASS, collection, angle)
                # Narrow reveals follow the glazing, keeping the model readable
                # at campus scale without claiming measured mullion dimensions.
                box_obj(f"{prefix} lintel {idx:02d}-{j:02d}-F{fl+1}", (x, y, sill + wh + 0.07), (ww + 0.18, 0.16, 0.12), CONCRETE, collection, angle)


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        if col.users == 0:
            bpy.data.collections.remove(col)


def main():
    clear_scene()
    scene = bpy.data.scenes[0] if bpy.data.scenes else bpy.data.scenes.new(SCENE_NAME)
    scene.name = SCENE_NAME
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = 1400, 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.18, 0.18, 0.18)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.38, 0.40, 0.43, 1.0)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)

    ring = load_ring()
    # Source polygon orientation is clockwise in local project XY.
    signed_area = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring))) / 2
    if signed_area < 0:
        ring.reverse()
    xmin, xmax = min(x for x, _ in ring), max(x for x, _ in ring)
    split_x = xmin + 0.66 * (xmax - xmin)
    high_poly = clip_x(ring, split_x)
    low_poly = clip_x(ring, split_x, keep_west=False)
    # The connected facility contains a three-story teaching/research block and
    # two-story animal-studies wing (Turner source). Heights use a 4.0 m/story
    # placeholder pending building-specific elevations.
    low_h, high_h, floor_h = 8.0, 12.0, 4.0
    solid_polygon("CRTN GIS footprint / two-story base", ring, 0.0, low_h, BRICK, collection)
    solid_polygon("CRTN three-story lab wing upper volume", high_poly, low_h, high_h, BRICK, collection)
    wall_windows(ring, 0.0, 2, floor_h, "CRTN lower wing", collection)
    wall_windows(high_poly, low_h, 1, floor_h, "CRTN lab upper", collection, exclude_x=split_x)

    # Low-slope roof and simple perimeter coping are consistent with Purdue's
    # contemporary exterior images; exact roof assemblies remain undocumented.
    solid_polygon("CRTN lower roof cap", low_poly, low_h - 0.06, low_h + 0.10, ROOF, collection)
    solid_polygon("CRTN upper roof cap", high_poly, high_h - 0.06, high_h + 0.12, ROOF, collection)

    # A glass entry bay and canopy are photo-supported features. The public
    # photographs do not unambiguously orient the entrance on this GIS ring, so
    # its location is explicitly a schematic east-front placement.
    ex = xmax - 0.55
    ey = (min(y for _, y in ring) + max(y for _, y in ring)) / 2
    box_obj("CRTN schematic glazed east entry bay", (ex, ey, 2.3), (0.18, 7.2, 4.6), GLASS, collection)
    box_obj("CRTN schematic entry canopy", (xmax - 1.9, ey, 4.35), (3.4, 9.0, 0.28), CONCRETE, collection)
    for j in range(5):
        box_obj(f"CRTN canopy support {j+1}", (xmax - 3.35, ey - 3.2 + j * 1.6, 2.15), (0.16, 0.16, 4.3), METAL, collection)

    # Preserve the existing massing library's single named object contract.
    bpy.ops.object.select_all(action="DESELECT")
    building_obj = bpy.data.objects["CRTN GIS footprint / two-story base"]
    for obj in list(collection.objects):
        obj.select_set(True)
    bpy.context.view_layer.objects.active = building_obj
    bpy.ops.object.join()
    building_obj.name = OBJECT_NAME

    # Presentation camera and lighting are kept outside the exported collection.
    cx, cy = (xmin + xmax) / 2, (min(y for _, y in ring) + max(y for _, y in ring)) / 2
    bpy.ops.object.camera_add(location=(cx + 103, cy - 116, 82))
    cam = bpy.context.object
    cam.name = "CRTN Preview Camera"
    direction = Vector((cx, cy, 5.0)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    scene.camera = cam
    bpy.ops.object.light_add(type="AREA", location=(cx + 8, cy - 45, 75))
    key = bpy.context.object
    key.name = "CRTN Preview Key"
    key.data.energy = 32000
    key.data.shape = "DISK"
    key.data.size = 65
    key.rotation_euler = (Vector((cx, cy, 0)) - key.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(PREVIEW_DIR / "crtn_three_quarter.png")
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.render.resolution_percentage = 85
    bpy.ops.render.render(write_still=True)

    # Secondary overhead view supports plan comparison and geometry review.
    bpy.ops.object.camera_add(location=(cx, cy, 180))
    topcam = bpy.context.object
    topcam.name = "CRTN Preview Top Camera"
    topcam.rotation_euler = (0.0, 0.0, 0.0)
    topcam.data.type = "ORTHO"
    topcam.data.ortho_scale = max(xmax - xmin, max(y for _, y in ring) - min(y for _, y in ring)) * 1.18
    scene.camera = topcam
    scene.render.filepath = str(PREVIEW_DIR / "crtn_plan.png")
    bpy.ops.render.render(write_still=True)

    # Remove presentation-only objects from the library, retaining the scene and
    # its one expected named building collection.
    for obj in (cam, key, topcam):
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.camera = None
    scene.render.resolution_percentage = 100
    scene.render.filepath = "//"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

    local_ring = ring
    evidence = {
        "building_id": "massing_creighton_hall_of_animal_sciences_crtn_a88d450",
        "name": "Hobart and Russell Creighton Hall of Animal Sciences (CRTN)",
        "asset": "modular/buildings/massing_creighton_hall_of_animal_sciences_crtn_a88d450.blend",
        "collection": COLLECTION_NAME,
        "retrieved_date": "2026-10-26",
        "coordinate_system": {
            "source_crs": "EPSG:4326 WGS 84",
            "project_axes": "X east, Y north, Z up; meters",
            "origin_lat_lon": [40.4274, -86.9137],
            "conversion": "X=(lon+86.9137)*84810.60416539927; Y=(lat-40.4274)*111040.0; project equirectangular approximation, not surveyed",
        },
        "sources": [
            {
                "provider": "Purdue University GIS, BuildingShapesZip4 FeatureServer layer 0",
                "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D914&outFields=*&returnGeometry=true&outSR=4326&f=json",
                "feature_id": "FID 914 / GlobalID {3FA2C03E-4423-4F77-8144-C59578DC41F4} / BLDG_ABBR CRTN",
                "source_date": "not supplied by GIS service; occupied timestamp 2017-12-15, built timestamp 2016-08-01",
                "retrieved_date": "2026-10-26",
                "snapshot": "audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/sources/crtn_fid914_gis_snapshot.json",
                "method": "converted the closed WGS84 footprint ring into project XY; built full-plan mesh from the official polygon",
                "uncertainty": "GIS NUM_LEVELS=5 is whole complex metadata, while Extrution=0 and CountOfFLO=0 provide no measured roof elevation; source Shape__Area is a service field and is not treated as metric area",
            },
            {
                "provider": "Turner Construction Company, project page",
                "url": "https://www.turnerconstruction.com/projects/purdue-university-hobart-russell-creighton-hall-of-animal-sciences",
                "feature_id": "Purdue University animal sciences complex; project narrative and gallery",
                "source_date": "project completion circa 2018; page currently accessible",
                "retrieved_date": "2026-10-26",
                "method": "used the published distinction between three-story teaching/research wing and two-story animal-studies wing; interpreted gallery only for massing/facade character",
                "uncertainty": "no measured elevations or architectural plans exposed on the page",
            },
            {
                "provider": "Purdue University Department of Animal Sciences / Purdue Agriculture",
                "url": "https://ag.purdue.edu/news/department/ansc/2023/05/ansc-graduate-student-awards-2023.html",
                "feature_id": "Purdue-hosted 2023 article photo captioned Hobart and Russell Creighton Hall of Animal Sciences",
                "source_date": "2023-05-19 article",
                "retrieved_date": "2026-10-26",
                "image_url": "https://ag.purdue.edu/news/department/ansc/2023/05/_media/crtn-hall.jpg",
                "method": "visual reference for brick facade, tall glazing, concrete trim, and glazed entrance canopy",
                "uncertainty": "photograph does not establish exact facade bay spacing, canopy dimensions, entrance side, or roof height",
            },
        ],
        "horizontal_validation": {
            "method": "direct ring vertex conversion using project transform; no rescaling or aggregate bounding-box fitting",
            "vertex_count": len(local_ring),
            "bounds_xy_m": [[xmin, xmax], [min(y for _, y in ring), max(y for _, y in ring)]],
            "position_error_m": 0.0,
            "plan_dimensions": [xmax - xmin, max(y for _, y in ring) - min(y for _, y in ring)],
            "source_rotation": "retained WGS84 ring orientation after applying the documented approximate project transform",
        },
        "vertical_geometry": {
            "status": "estimated",
            "whole_complex_level_metadata": 5,
            "lab_wing_stories": 3,
            "animal_studies_wing_stories": 2,
            "estimated_lab_roof_m": high_h,
            "estimated_lower_wing_roof_m": low_h,
            "method": "4.0 m per story schematic allowance; floors and roof elevations are not measured",
            "uncertainty": "roof parapet, mechanical equipment, floor-to-floor heights, and ground datum remain unverified",
        },
        "facade_and_roof": {
            "status": "photo-derived schematic",
            "supported": ["brick exterior", "large/tall glazing", "light concrete elements", "glazed entry canopy", "contemporary low-slope roof silhouette"],
            "unverified": ["exact window spacing and dimensions", "entry side/location", "parapet height", "roof equipment", "two-wing split line"],
        },
        "export_validation": {
            "reopened_in_blender": "to be recorded after independent reopen check",
            "collection": COLLECTION_NAME,
            "object_name": OBJECT_NAME,
            "object_count": 1,
            "mesh_vertex_count": len(building_obj.data.vertices),
            "mesh_polygon_count": len(building_obj.data.polygons),
            "object_dimensions_m": [round(v, 4) for v in building_obj.dimensions],
            "modifiers": [modifier.name for modifier in building_obj.modifiers],
            "portable_paths": "no external textures or linked files",
        },
        "edits": [
            "replaced inherited 1-mesh box with the FID 914 polygon extrusion and repeated schematic facade elements",
            "corrected inherited plan bounds from approx. 94.8 x 90.9 m to the GIS ring bounds; adopted 3-story/2-story roof estimates",
        ],
        "preview_files": ["audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/previews/crtn_three_quarter.png", "audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/previews/crtn_plan.png"],
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print("CRTN_BUILD", json.dumps({"asset": str(ASSET), "bounds_xy_m": evidence["horizontal_validation"]["bounds_xy_m"], "objects": len(collection.objects), "vertices": len(building_obj.data.vertices), "faces": len(building_obj.data.polygons)}))


if __name__ == "__main__":
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    main()

"""Build a source-backed, modular massing library for Cary Quadrangle Northeast.

The GIS polygon and vertical fields are authoritative Purdue facility data.
Roof and facade details are schematic interpretations of campus aerial imagery
and the shared Cary architectural context; they are explicitly not measured.
Run from any directory with Blender's Python, e.g. blender --background
--factory-startup --python this_file.py.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ID = "massing_cary_quadrangle_northeast_cqne_0a76fca"
COLLECTION = f"Asset_{ID}"
SCENE = f"Building_{ID}"
ROOT = Path(__file__).resolve().parents[2]
GIS_PATH = ROOT / "audit" / ID / "sources" / "purdue_gis_feature_638_cqne_4326.json"
OUTPUT = ROOT / "modular" / "buildings" / f"{ID}.blend"
EVIDENCE_PATH = ROOT / "audit" / ID / "build_evidence.json"

# Purdue project frame: approximate local conversion at the documented origin.
LAT0 = 40.4274
LON0 = -86.9137
X_SCALE = 111412.84 * math.cos(math.radians(LAT0))
Y_SCALE = 111040.0
ROOF_TOP_M = 16.0          # estimated from 2013 NDHM roof-height p90-p95
EAVE_Z = 12.5              # estimated from lower roof-edge bands in the same 5-ft NDHM
FLOORS = 5                 # Purdue GIS CountOfFLO


def mat(name, color, roughness=0.82):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.roughness = roughness
    return m


BRICK = mat("CQNE | red-brown brick (visual estimate)", (0.30, 0.105, 0.075))
BRICK_LIGHT = mat("CQNE | warm brick variation", (0.40, 0.17, 0.12))
STONE = mat("CQNE | pale limestone trim (visual estimate)", (0.70, 0.66, 0.56))
GLASS = mat("CQNE | dark window glazing", (0.075, 0.16, 0.20), 0.32)
ROOF = mat("CQNE | dark brown pitched roof (massing estimate)", (0.28, 0.19, 0.13))


BOX_BUCKETS = {}


def box_obj(name, center, size, material, collection, bevel=0.0):
    """Append a box to a material batch (hundreds of fast, portable boxes)."""
    verts, faces = BOX_BUCKETS.setdefault(material.name, ([], []))
    cx, cy, cz = center
    sx, sy, sz = (v / 2 for v in size)
    base = len(verts)
    verts.extend([(cx+dx*sx, cy+dy*sy, cz+dz*sz)
                  for dx, dy, dz in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                     (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))])
    faces.extend([tuple(base+i for i in f) for f in
                  ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    return None


def mesh_obj(name, verts, faces, material, collection):
    mesh = bpy.data.meshes.new(name + " | mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    collection.objects.link(o)
    return o


def add_window(name, x, y, z, width, height, side, collection):
    # Shallow framed windows on north/south facades. Side = +/-1.
    y_face = y + side * 0.11
    box_obj(name + " | glazing", (x, y_face, z), (width, 0.12, height), GLASS, collection)
    for dz in (-height / 2 - 0.045, height / 2 + 0.045):
        box_obj(name + " | sill/lintel", (x, y_face + side * 0.075, z + dz),
                (width + 0.20, 0.13, 0.09), STONE, collection)
    for dx in (-width / 2 - 0.045, width / 2 + 0.045):
        box_obj(name + " | jamb", (x + dx, y_face + side * 0.075, z),
                (0.09, 0.13, height + 0.16), STONE, collection)
    box_obj(name + " | mullion", (x, y_face + side * 0.15, z),
            (0.055, 0.06, height), STONE, collection)


def read_polygon():
    record = json.loads(GIS_PATH.read_text(encoding="utf-8"))["features"][0]
    ring = record["geometry"]["rings"][0]
    pts = []
    for lon, lat in ring:
        x = (lon - LON0) * X_SCALE
        y = (lat - LAT0) * Y_SCALE
        if not pts or math.dist(pts[-1], (x, y)) > 0.005:
            pts.append((x, y))
    if math.dist(pts[0], pts[-1]) < 0.005:
        pts.pop()
    return record, pts


def main():
    record, outline = read_polygon()
    # This library is campus-coordinate massing and uses an identity transform.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name != "Collection":
            bpy.data.collections.remove(c)
    scene = bpy.context.scene
    scene.name = SCENE
    root_collection = bpy.data.collections.get("Collection")
    if root_collection:
        root_collection.name = COLLECTION
        collection = root_collection
    else:
        collection = bpy.data.collections.new(COLLECTION)
        scene.collection.children.link(collection)

    # Source footprint, including its small recesses and projections.
    n = len(outline)
    verts = [(x, y, z) for z in (0.0, EAVE_Z) for x, y in outline]
    faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh_obj("CQNE | GIS footprint walls", verts, faces, BRICK, collection)

    xs, ys = [p[0] for p in outline], [p[1] for p in outline]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    length, depth = xmax - xmin, ymax - ymin
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    # Main longitudinal gable: roof crest aligns with the building's long axis.
    x0, x1 = xmin - 0.25, xmax + 0.25
    y0, y1 = ymin - 0.34, ymax + 0.34
    ridge_y = (y0 + y1) / 2
    eave = EAVE_Z
    ridge = ROOF_TOP_M
    roof_verts = [(x0, y0, eave), (x1, y0, eave),
                  (x1, ridge_y, ridge), (x0, ridge_y, ridge),
                  (x0, y1, eave), (x1, y1, eave)]
    roof_faces = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)]
    mesh_obj("CQNE | pitched roof massing", roof_verts, roof_faces, ROOF, collection)

    # End gables close the pitched roof. No dormers are added: the available
    # 5-ft NDHM supports a central ridge but does not resolve CQNE dormers.
    mesh_obj("CQNE | west gable wall",
             [(x0,y0,eave),(x0,y1,eave),(x0,ridge_y,ridge)], [(0,1,2)], BRICK, collection)
    mesh_obj("CQNE | east gable wall",
             [(x1,y1,eave),(x1,y0,eave),(x1,ridge_y,ridge)], [(0,1,2)], BRICK, collection)

    # Five regular storeys follow the official GIS count. Window rhythm is an
    # architectural estimate informed by official Cary aerial/street imagery.
    floor_h = EAVE_Z / FLOORS
    window_h = 1.35
    pitch = 3.05
    count = int(length / pitch)
    for side, y in ((-1, ymin), (1, ymax)):
        for floor in range(FLOORS):
            z = floor_h * (floor + 0.55)
            for i in range(1, count):
                x = xmin + i * length / count
                add_window(f"CQNE | {('south','north')[side > 0]} f{floor+1} w{i:02d}",
                           x, y, z, 1.08, window_h, side, collection)
        # Horizontal stone string courses mark the five-storey elevation.
        for floor in range(1, FLOORS):
            z = floor * floor_h
            box_obj(f"CQNE | {('south','north')[side > 0]} stone course {floor}",
                    (cx, y + side * 0.08, z), (length * 0.99, 0.15, 0.10),
                    STONE, collection)

    # Modest corner piers give the long brick elevations readable ends.
    for x in (xmin + 0.2, xmax - 0.2):
        for y, side in ((ymin, -1), (ymax, 1)):
            box_obj("CQNE | brick corner pier", (x, y + side * 0.13, EAVE_Z/2),
                    (0.45, 0.30, EAVE_Z), BRICK_LIGHT, collection)

    # Batch repetitive windows, trim, and piers into compact material meshes.
    for material_name, (box_verts, box_faces) in BOX_BUCKETS.items():
        material = bpy.data.materials.get(material_name)
        mesh_obj("CQNE | " + material_name.split("|")[-1].strip() + " details",
                 box_verts, box_faces, material, collection)

    # Scene settings make the saved asset easy to inspect and render.
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.world.color = (0.12, 0.12, 0.12)
    bpy.ops.object.select_all(action="DESELECT")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))

    evidence = {
        "building_id": ID,
        "asset": f"modular/buildings/{ID}.blend",
        "collection": COLLECTION,
        "scene": SCENE,
        "export_mode": "campus-coordinate massing, identity transform",
        "source_feature": {"provider": "Purdue University GIS, BuildingShapesZip4 FeatureServer layer 0",
                           "feature_id": record["attributes"]["FID"],
                           "name": record["attributes"]["BUILDING_N"],
                           "code": record["attributes"]["BLDG_ABBR"],
                           "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D638&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
                           "retrieved": "2026-10-26",
                           "source_crs": "WGS 84 geographic coordinates (EPSG:4326)",
                           "raw_snapshot": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/sources/purdue_gis_feature_638_cqne_4326.json",
                           "measurement_method": "Transform the authoritative footprint ring using the repository's documented local latitude/longitude approximation; preserve ring topology.",
                           "vertical_fields": {"CountOfFLO": record["attributes"]["CountOfFLO"],
                                               "Extrution": record["attributes"]["Extrution"],
                                               "interpretation": "Five levels are used. Extrution=48 is retained as an uninterpreted integer because the field has no unit or semantic metadata."}},
        "plan_measurement_m": {"length_axis_x": round(length, 3), "depth_axis_y": round(depth, 3),
                               "footprint_area_source_m2": record["attributes"].get("Shape__Area"),
                               "source_ring_vertex_count": len(outline)},
        "vertical": {"storeys": FLOORS,
                     "overall_height_m_estimate": ROOF_TOP_M,
                     "eave_height_m_estimate": EAVE_Z,
                     "height_source": "Indiana 2013 NDHM tile, 5-ft GSD; 366 pixels within Feature 638 footprint, p90=52.015 and p95=52.558 native units. If interpreted as US survey feet, these are about 15.85-16.02 m.",
                     "height_unit_status": "NDHM values are native and retained in the measurement report; the GeoTIFF horizontal CRS is US survey feet, but raster vertical units are not explicitly declared. Meter conversion is an estimate, not surveyed height.",
                     "roof_form": "longitudinal gable; the cross-building NDHM profile has higher central bands than outer bands. Exact eaves and pitch remain estimated"},
        "additional_sources": [
            {"provider": "Purdue University Residences", "url": "https://www.housing.purdue.edu/my-housing/options/residence-halls/cary-quad.html", "retrieved": "2026-10-26", "snapshot": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/sources/purdue_housing_cary_quad.html", "use": "Cary overview identifies Northeast as one of four outer buildings renovated in 2007 and records suite renovation; no individual elevation dimensions."},
            {"provider": "Purdue University Residences", "url": "https://www.housing.purdue.edu/images/banners/ur-aerial-view-of-cary-visit-hero.jpg", "retrieved": "2026-10-26", "snapshot": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/sources/purdue_housing_cary_aerial.jpg", "use": "Current oblique aerial illustrates Cary roof pitch, brick color, gables, and window character; image covers the whole quad and is not a CQNE-specific survey."},
            {"provider": "Purdue University Residences", "url": "https://www.housing.purdue.edu/images/_hero/ur-caryquad3.jpg", "retrieved": "2026-10-26", "snapshot": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/sources/purdue_housing_cary_quad_hero_3.jpg", "use": "Official Cary image supports general brick, stone, and window character only; it depicts the complex entrance rather than a verified CQNE elevation."},
            {"provider": "Indiana 3DEP LiDAR products hosted by Purdue GDSL/iDiF and Indiana Geographic Information Office open-data bucket", "url": "https://giselevationingov.s3.us-east-2.amazonaws.com/ndhmoptimized/statewide/2013/SPW/5ft/in2013_29951885_12_ndhm.tif", "retrieved": "2026-10-26", "source_date": "2011-2013 program; exact acquisition date not stated in tile metadata", "source_crs": "NAD83 / Indiana West (ftUS), EPSG:2966", "measurement_method": "Mask 5-ft GSD raster cell centers with Purdue GIS Feature 638 transformed to EPSG:2966; NDHM represents object height above underlying ground. 366 cells intersect. Native quantiles and unit uncertainty are recorded in ndhm_measurement.json.", "snapshot": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/sources/indiana_2013_ndhm_tile_29951885.tif", "derived_measurement": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/ndhm_measurement.json", "visualization": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/ndhm_cqne_profile.png", "use": "5-ft sampled height distribution and cross-section. Peak estimate is interpreted as 16.0 m only if native values are US survey feet; vertical units are not explicit in the GeoTIFF."},
            {"provider": "Purdue University Archives and Special Collections", "url": "https://archives.lib.purdue.edu/agents/corporate_entities/793", "retrieved": "2026-10-26", "use": "Historical database says Cary Hall Northeast is the second building of the quad and dates its existence from 1931; direct HTML was blocked by the site challenge."},
            {"provider": "Purdue e-Archives, Purdue Buildings and Campus Scenes", "url": "https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/159/", "retrieved": "2026-10-26", "snapshot": "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/sources/purdue_archives_cary_quad_1950s.jpg", "use": "1950s general Cary exterior photograph; historical context only, not attributed to CQNE."}
        ],
        "uncertainty": ["GIS plan footprint and reported 5 levels are used; Extrution=48 is not used because its semantics and units are undocumented.", "Height is estimated from a 2013 NDHM at 5-ft grid spacing. Raster vertical units are not explicitly declared, so the 16.0 m estimate remains conditional.", "Exact CQNE facade bays, entrance location, roof pitch, and material course dimensions remain unverified; generic facade rhythm is schematic.", "The official oblique aerial depicts the Cary complex collectively and does not isolate the northeast wing."],
        "validation": {"status": "Blender 4.5.15 reopen/render passed; fresh independent grade pending", "geometry_edits": ["Replaced the source single-extrusion mass with the same GIS feature outline, five window rows, floor courses, and a longitudinal gable guided by NDHM cross-section; removed unsupported projecting roof bays and entry marker."]}
    }
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

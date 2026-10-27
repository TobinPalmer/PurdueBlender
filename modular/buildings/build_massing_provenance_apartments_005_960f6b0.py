"""Build the Provenance Apartments Building F (143) massing.

The stable `.005` assignment is crosswalked to Building F / 143 by the county's
approved Phase 1 & 2 construction plan and the current Indiana orthophoto. Its
footprint comes from Purdue GIS FID 506, which still carries a pre-planning layer
label; its close fit to the 2025 roof outline is evidence, not a survey. Geometry
stays in campus world coordinates. Heights and roof segmentation remain
estimates. No exact-block street photo, approved elevation, or section was
found, so facade relief is omitted.
"""

import json
import math
import os
import bpy
from mathutils import Vector


ASSET_ID = "massing_provenance_apartments_005_960f6b0"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
OBJECT_NAME = "Provenance Apartments.005"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SOURCE = os.path.join(ROOT, "audit", ASSET_ID, "sources", "official_purdue_fid506.json")
OUT_BLEND = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
OUT_AUDIT = os.path.join(ROOT, "audit", ASSET_ID)

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
X_M_PER_DEG = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
Y_M_PER_DEG = 111040.0
WALL_HEIGHT_M = 8.9  # estimate: three stories; no measured elevation found
RIDGE_HEIGHT_M = 11.4  # estimate from three-story Provenance project imagery


def web_mercator_to_campus(x, y):
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2.0 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2.0)
    return ((lon - ORIGIN_LON) * X_M_PER_DEG,
            (lat - ORIGIN_LAT) * Y_M_PER_DEG)


def material(name, color, roughness=0.78):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.roughness = roughness
    m.use_nodes = True
    principled = m.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = (*color, 1.0)
        principled.inputs["Roughness"].default_value = roughness
    return m


def add_box(vertices, faces, face_materials, x0, y0, z0, x1, y1, z1, mat_idx):
    start = len(vertices)
    vertices.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                     (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
    faces.extend([(start+0,start+3,start+2,start+1), (start+4,start+5,start+6,start+7),
                  (start+0,start+1,start+5,start+4), (start+1,start+2,start+6,start+5),
                  (start+2,start+3,start+7,start+6), (start+3,start+0,start+4,start+7)])
    face_materials.extend([mat_idx] * 6)


def add_roof_prism(vertices, faces, face_materials, x0, x1, y0, y1, eave, ridge, mat_idx):
    """One approximate townhouse gable, with gable ends facing north/south."""
    xm = (x0 + x1) * 0.5
    section = [(x0,eave),(xm,ridge),(x1,eave)]
    start = len(vertices)
    for y in (y0, y1):
        vertices.extend([(x,y,z) for x,z in section])
    faces.extend([(start,start+1,start+4,start+3),
                  (start+1,start+2,start+5,start+4),
                  (start,start+3,start+4,start+1),
                  (start+1,start+4,start+5,start+2),
                  (start,start+2,start+5,start+3)])
    face_materials.extend([mat_idx] * 5)


def clip_polygon_x(poly, boundary, keep_greater):
    """Clip a simple XY ring to one vertical half-plane."""
    if not poly:
        return []
    out = []
    previous = poly[-1]
    prev_in = previous[0] >= boundary if keep_greater else previous[0] <= boundary
    for current in poly:
        cur_in = current[0] >= boundary if keep_greater else current[0] <= boundary
        if cur_in != prev_in:
            dx = current[0] - previous[0]
            if abs(dx) > 1e-12:
                t = (boundary - previous[0]) / dx
                out.append((boundary, previous[1] + t * (current[1] - previous[1])))
        if cur_in:
            out.append(current)
        previous, prev_in = current, cur_in
    clean = []
    for point in out:
        if not clean or math.dist(point, clean[-1]) > 1e-7:
            clean.append(point)
    if len(clean) > 1 and math.dist(clean[0], clean[-1]) <= 1e-7:
        clean.pop()
    return clean


def vertical_edge_intersections(ring, x):
    """Return exterior boundary y positions at one x station."""
    hits = []
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        if abs(a[0] - b[0]) < 1e-9:
            if abs(x - a[0]) < 1e-7:
                hits.extend((a[1], b[1]))
            continue
        if min(a[0], b[0]) - 1e-7 <= x <= max(a[0], b[0]) + 1e-7:
            t = (x - a[0]) / (b[0] - a[0])
            if -1e-7 <= t <= 1.0 + 1e-7:
                hits.append(a[1] + t * (b[1] - a[1]))
    return sorted(set(round(y, 7) for y in hits))


def main():
    with open(SOURCE, encoding="utf-8") as f:
        feature = json.load(f)["feature"]
    attrs = feature["attributes"]
    assert attrs["FID"] == 506 and attrs["BUILDING_N"] == "Building F"
    assert attrs["BLDG_ABBR"] == "143"
    ring_mercator = feature["geometry"]["rings"][0]
    ring = [web_mercator_to_campus(x, y) for x, y in ring_mercator]
    if ring[0] == ring[-1]:
        ring.pop()

    # Retain this assigned GIS ring verbatim after the documented project transform.
    xs, ys = zip(*ring)
    x_min, x_max, y_min, y_max = min(xs), max(xs), min(ys), max(ys)
    x_span = x_max - x_min
    y_span = y_max - y_min

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        if c.name != "Collection":
            bpy.data.collections.remove(c)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    coll = bpy.data.collections.get(COLLECTION_NAME) or bpy.data.collections.new(COLLECTION_NAME)
    if coll.name not in scene.collection.children:
        scene.collection.children.link(coll)
    preview_coll = bpy.data.collections.new("Preview_" + ASSET_ID)
    scene.collection.children.link(preview_coll)
    old = bpy.data.collections.get("Collection")
    if old and old != coll:
        for o in list(old.objects):
            old.objects.unlink(o)
        try:
            bpy.data.collections.remove(old)
        except RuntimeError:
            pass

    # No exact-block street photo or elevation was found, so the facade stays
    # neutral and undetailed. Roof gray is a neutral display choice from the
    # overhead image, not a measured material/color claim.
    bodymat = material("Provenance 005 unverified facade neutral", (0.43, 0.44, 0.45))
    roofmat = material("Provenance 005 roof neutral from aerial", (0.31, 0.33, 0.35))

    verts, faces, mats = [], [], []
    # A single exact footprint extrusion preserves the full FID 506 ground outline.
    base = len(verts)
    verts.extend([(x,y,0.0) for x,y in ring])
    verts.extend([(x,y,WALL_HEIGHT_M) for x,y in ring])
    n = len(ring)
    faces.append(tuple(base + i for i in range(n)))
    mats.append(0)
    faces.append(tuple(base + n + i for i in reversed(range(n))))
    mats.append(0)
    for i in range(n):
        j = (i + 1) % n
        faces.append((base+i, base+j, base+n+j, base+n+i))
        mats.append(0)

    # Five roof breaks are an estimate inferred from overhead imagery of this
    # exact block. Sections are clipped to the mapped outline; pitch, ridge
    # positions, and height remain unmeasured estimates.
    roof_count = 5
    for i in range(roof_count):
        xa = x_min + x_span * i / roof_count
        xb = x_min + x_span * (i + 1) / roof_count
        xm = (xa + xb) * 0.5
        slab = clip_polygon_x(clip_polygon_x(ring, xa, True), xb, False)
        for left_side in (True, False):
            half = clip_polygon_x(slab, xm, False) if left_side else clip_polygon_x(slab, xm, True)
            if len(half) < 3:
                continue
            start = len(verts)
            for x, y in half:
                t = ((x - xa) / max(xm - xa, 1e-9)) if left_side else ((xb - x) / max(xb - xm, 1e-9))
                z = WALL_HEIGHT_M + max(0.0, min(1.0, t)) * (RIDGE_HEIGHT_M - WALL_HEIGHT_M)
                verts.append((x, y, z))
            faces.append(tuple(start + j for j in range(len(half))))
            mats.append(1)

    mesh = bpy.data.meshes.new(OBJECT_NAME + "_GIS_FID506_massing_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for m in (bodymat, roofmat):
        mesh.materials.append(m)
    mesh.update()
    obj = bpy.data.objects.new(OBJECT_NAME, mesh)
    coll.objects.link(obj)
    for poly, mat_idx in zip(mesh.polygons, mats):
        poly.material_index = mat_idx
    obj["asset_id"] = ASSET_ID
    obj["source_feature"] = "Building F / 143 per approved Tippecanoe County construction-plan sheet C1.4; Purdue Campus Map pre-planning feature FID 506 crosschecked to current 2025 orthophoto"
    obj["footprint_method"] = "FID 506 ring; EPSG:3857 inverse to WGS84 then Purdue local approximation; overlay against current Indiana orthophoto roof outline"
    obj["height_status"] = "estimated: project-level three-story count; eave 8.9 m and ridge 11.4 m are estimates ±1.5 m, no Building F elevation found"
    obj["roof_status"] = "five-break rhythm estimated from exact-block overhead roof imagery; pitch, seams and elevations unmeasured"
    obj["facade_status"] = "undetailed massing: no exact-block street photo or elevation found; facade relief and finish intentionally left unmodeled"

    # Portable, isolated scene and views.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.32, 0.36, 0.42, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
    scene.view_settings.view_transform = "AgX"
    scene.render.film_transparent = False

    def make_camera(name, loc, target, lens=52):
        data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, data)
        preview_coll.objects.link(cam)
        cam.location = loc
        direction = Vector(target) - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        data.lens = lens
        return cam

    center = ((x_min+x_max)*0.5, (y_min+y_max)*0.5, 5.0)
    cam = make_camera("Camera_Provenance005_Southwest", (center[0]-52, center[1]-63, 38), center)
    scene.camera = cam
    light_data = bpy.data.lights.new("Key softbox", "AREA")
    light = bpy.data.objects.new("Key softbox", light_data)
    preview_coll.objects.link(light)
    light.location = (center[0]-25, center[1]-25, 46)
    light_data.energy = 14000
    light_data.shape = "DISK"
    light_data.size = 38
    light.rotation_euler = (math.radians(25), 0, math.radians(-25))

    # Render a preview for the grader/coordinator.
    preview = os.path.join(OUT_AUDIT, "preview_southwest.png")
    scene.render.filepath = preview
    bpy.ops.render.render(write_still=True)

    top_cam = make_camera("Camera_Provenance005_Top", (center[0], center[1], 90), center, 50)
    top_cam.data.type = "ORTHO"
    top_cam.data.ortho_scale = 72
    scene.camera = top_cam
    scene.render.filepath = os.path.join(OUT_AUDIT, "preview_top.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = cam

    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

    # Audit geometry using saved mesh in world coordinates (campus space).
    bpy.context.view_layer.update()
    bb = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    bounds = [[min(v[i] for v in bb), max(v[i] for v in bb)] for i in range(3)]
    record = {
        "asset_id": ASSET_ID,
        "source_feature": {"provider": "Purdue University Campus Map FeatureServer, layer 0", "fid": 506,
                           "name": "Building F", "abbreviation": "143", "layer": "BLDG Building Pre-planning",
                           "BUILDING_1_attribute": "1509", "ADDRESS_attribute": "blank", "retrieved": "2026-10-26",
                           "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/506?f=pjson",
                           "source_crs": "EPSG:3857", "raw_snapshot": "sources/official_purdue_fid506.json",
                           "crosswalk": "County Area Plan Commission construction-plan sheet C1.4 explicitly labels the central target block BLDG F / 143. The transformed GIS polygon closely overlays the matching central roof in Indiana 2025 orthophoto. This resolves the individual-block match, while exact wall registration remains uncertain because the Purdue source layer is pre-planning."},
        "footprint": {"vertex_count": len(ring), "area_source_web_mercator_m2": attrs.get("Shape__Area"),
                      "area_project_ground_approx_m2": abs(sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2),
                      "perimeter_source_web_mercator_m": attrs.get("Shape__Length"),
                      "conversion": "EPSG:3857 inverse Web Mercator -> WGS84 -> Purdue project approximation; origin 40.4274,-86.9137; X east and Y north; not a surveyed CRS",
                      "campus_bounds_xy_m": [[x_min,x_max],[y_min,y_max]], "uncertainty": "cross-checked against the planned BLDG F / 143 site-plan location and current roof outline, but the source feature is pre-planning and not a certified wall-line survey"},
        "dimensions": {"footprint_x_m": x_span, "footprint_y_m": y_span,
                       "wall_height_m": WALL_HEIGHT_M, "ridge_height_m": RIDGE_HEIGHT_M,
                       "vertical_status": "estimated; no measured elevations located",
                       "height_uncertainty_m": {"eave_plus_minus": 1.5, "ridge_plus_minus": 1.5},
                       "story_count": 3,
                       "story_evidence": "Studio M Provenance project description states seven three-story apartment buildings; not individually attributed to Building F."},
        "site_plan_evidence": {"provider": "Tippecanoe County Area Plan Commission",
                                "url": "https://www.tippecanoe.in.gov/AgendaCenter/ViewFile/ArchivedAgenda/_01022020-1597?packet=true",
                                "sheet": "C1.4, construction drawings / post-stormwater pollution prevention plan",
                                "sheet_date": "2019-10-14", "approval": "Final detailed Phase 1 & 2 plan resolution PD-20-01, January 2020",
                                "target_label": "BLDG F / 143, between BLDG E / 144 and BLDG G / 142",
                                "snapshot": "audit/" + ASSET_ID + "/sources/county_provenance_phase1_2_construction_plans.pdf",
                                "method": "explicit plan label + block order/location; drawing not georeferenced and not an elevation"},
        "current_orthophoto_evidence": {"provider": "Indiana Geographic Information Office / Indiana Current Orthophotography ImageServer",
                                        "service_url": "https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer",
                                        "dataset": "Indiana_2025_SPW_2ft_exportraster; identify also returned a 2023 Tippecanoe 6-inch source item",
                                        "retrieved": "2026-10-26", "source_crs": "EPSG:3857",
                                        "overlay": "audit/" + ASSET_ID + "/indiana_current_orthophoto_2025_fid506_overlay.jpg",
                                        "license": "CC0 per ImageServer metadata",
                                        "method": "EPSG:3857 overlay against the transformed Purdue ring; matching central roof outlined without fitting/warping",
                                        "uncertainty": "overhead imagery supports block position and roof outline, not wall-line survey, height, roof pitch or facade layout"},
        "appearance_evidence": {"provider": "Exact-block search and project-wide references", "url": "audit/" + ASSET_ID + "/source_search_r3.json",
                                "source_date": "not stated; project Phase I built / Phase II under construction at retrieval",
                                "retrieved": "2026-10-26", "project_description": "Studio M describes seven three-story buildings; general project photos were reviewed but excluded from Building F facade geometry",
                                "project_wide_reference": "https://www.studiomarchitecture.net/provenance-at-discovery-park",
                                "visible_features": ["current overhead roof outline and roof breaks only"],
                                "uncertainty": "No Building F street-level photo, approved elevation, or section was located; facade openings, finish, entries, balconies, and color stationing remain unknown and are omitted"},
        "geometry": {"object_count": 1, "object_name": OBJECT_NAME, "vertex_count": len(mesh.vertices),
                     "polygon_count": len(mesh.polygons), "world_bounds_m": bounds,
                     "roof_segments_estimated": roof_count, "roof_segment_status": "five-break plan rhythm is an estimate from exact-block overhead imagery; ridge count, placement, pitch, and elevations are not measured",
                     "facade_features_estimated": {"modeled": "none beyond the plain massing shell; exact-block sources do not resolve openings, entries, balconies, or finishes"},
                     "portable_external_dependencies": []},
        "geometry_edit": {"before_bounds_world_m": [[-1627.371337890625,-1489.2232666015625],[-474.5072326660156,-446.1253967285156],[0.0,11.4]],
                          "action": "replaced inherited 138.1m-wide unverified aggregate proxy with the FID 506 ring crosswalked to BLDG F / 143 by county plan C1.4 and corroborated against current 2025 roof imagery; removed unsupported facade details and material stationing; retained only plain shell massing and an estimated roof rhythm",
                          "limits": "FID 506 remains tagged BLDG Building Pre-planning; its ring closely matches the current roof outline but is not a surveyed wall registration. Building-specific street imagery and approved elevations/sections were not found; all vertical dimensions and roof rhythm are estimates"},
        "outputs": {"blend": "modular/buildings/" + ASSET_ID + ".blend", "preview": "audit/" + ASSET_ID + "/preview_southwest.png", "plan_preview": "audit/" + ASSET_ID + "/preview_top.png",
                    "site_plan": "audit/" + ASSET_ID + "/sources/county_plan_sheet_C1_4_apartment_cluster.png",
                    "current_orthophoto_overlay": "audit/" + ASSET_ID + "/indiana_current_orthophoto_2025_fid506_overlay.jpg",
                    "crosswalk_analysis": "audit/" + ASSET_ID + "/crosswalk_analysis.json",
                    "source_register": "audit/" + ASSET_ID + "/source_register.json",
                    "source_search_r3": "audit/" + ASSET_ID + "/source_search_r3.json",
                    "reopen_validation": "audit/" + ASSET_ID + "/reopen_validation.json"}
    }
    with open(os.path.join(OUT_AUDIT, "build_evidence.json"), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    validation_path = os.path.join(OUT_AUDIT, "reopen_validation.json")
    if os.path.exists(validation_path):
        os.remove(validation_path)
    with open(os.path.join(OUT_AUDIT, "build_result.json"), "w", encoding="utf-8") as f:
        json.dump({"status": "built and saved; separate reopen validation required",
                   "scene": SCENE_NAME, "collection": COLLECTION_NAME,
                   "asset_path": "modular/buildings/" + ASSET_ID + ".blend",
                   "expected_object_name": OBJECT_NAME, "world_bounds_m": bounds,
                   "mesh_counts": {"vertices": len(mesh.vertices), "faces": len(mesh.polygons)},
                   "saved_at": "2026-10-26"}, f, indent=2)
        f.write("\n")
    print("PROVENANCE_005_BUILD", json.dumps(record["geometry"], sort_keys=True))


if __name__ == "__main__":
    main()

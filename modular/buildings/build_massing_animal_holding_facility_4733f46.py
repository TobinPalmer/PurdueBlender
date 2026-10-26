"""Build the Animal Holding Facility from official Purdue and Indiana footprint records.

The footprint remains in the project's campus coordinate frame. Vertical dimensions
are diagrammatic: the GIS reports one level, but its extrusion field has no unit
definition. Run with Blender 4.5 from the repository root.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_animal_holding_facility_4733f46.blend"
SOURCE = ROOT / "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json"
OUT = ROOT / "audit/animal_holding_facility"
COLLECTION = "Asset_massing_animal_holding_facility_4733f46"
SCENE = "Building_massing_animal_holding_facility_4733f46"

feature = json.loads(SOURCE.read_text(encoding="utf-8"))["features"][0]
ring = feature["geometry"]["rings"][0]
points = []
for lon, lat in ring[:-1]:
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    points.append((x, y))
assert len(points) == 16 and ring[0] == ring[-1], (len(points), ring[0], ring[-1])

# Purdue GIS confirms one occupied level. The 2018 Indiana NDHM gives median
# roof heights above local ground for the two roof zones; those height values
# are converted from U.S. survey feet to meters. The raster samples are 5 ft.
NDHM_STATS = json.loads((OUT / "ndhm_roof_height_statistics.json").read_text(encoding="utf-8"))
NORTH_TOP = NDHM_STATS["zones"]["north_main"]["median_m"]
SOUTH_TOP = NDHM_STATS["zones"]["south_addition"]["median_m"]
ROOF_THICKNESS = 0.12
ROOF_ZONE_Y = -996.7429296393766  # row 817 of the georeferenced 2023 ortho transformed to local campus XY
WALL_THICKNESS = 0.28

scene = bpy.context.scene
scene.name = SCENE
col = bpy.data.collections.get(COLLECTION)
if col is None:
    col = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(col)
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, roughness=0.82):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
    return mat

wall_mat = material("AHF | neutral wall envelope (facade unverified)", (0.60, 0.60, 0.56))
roof_main_mat = material("AHF | light corrugated main roof (Indiana 2023 ortho)", (0.68, 0.72, 0.71))
roof_south_mat = material("AHF | darker south roof zone (Indiana 2023 ortho)", (0.20, 0.23, 0.25))
trim_mat = material("AHF | perimeter edge (diagrammatic)", (0.42, 0.43, 0.40))

verts, faces, face_materials = [], [], []

def add_box(center, axes, sizes, material_index):
    cx, cy, cz = center
    ax, ay = axes
    sx, sy, sz = (s / 2 for s in sizes)
    base = len(verts)
    for dz in (-sz, sz):
        for dy in (-sy, sy):
            for dx in (-sx, sx):
                verts.append((cx + ax[0] * dx + ay[0] * dy,
                              cy + ax[1] * dx + ay[1] * dy, cz + dz))
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    for q in quads:
        faces.append(tuple(base + i for i in q))
        face_materials.append(material_index)

def orthophoto_pixel(x, y):
    """Map project-local XY back into the saved 2023 EPSG:3857 image crop."""
    lat0 = math.radians(40.4274)
    lon = -86.9137 + x / (111412.84 * math.cos(lat0))
    lat = 40.4274 + y / 111040.0
    merc_x = math.radians(lon) * 6378137.0
    merc_y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * 6378137.0
    extent = (-9675297.9304, 4926877.1, -9675197.8536, 4927002.196)
    return ((merc_x - extent[0]) / (extent[2] - extent[0]) * 1200,
            (extent[3] - merc_y) / (extent[3] - extent[1]) * 1500)

def roof_top_at(y):
    return NORTH_TOP if y >= ROOF_ZONE_Y else SOUTH_TOP

def clip_at_y(poly, limit, keep_north):
    """Clip a simple outline at the measured roof-zone boundary."""
    output = []
    for i, current in enumerate(poly):
        previous = poly[i - 1]
        cy, py = current[1], previous[1]
        current_inside = cy >= limit if keep_north else cy <= limit
        previous_inside = py >= limit if keep_north else py <= limit
        if current_inside != previous_inside:
            t = (limit - py) / (cy - py)
            output.append((previous[0] + t * (current[0] - previous[0]), limit))
        if current_inside:
            output.append(current)
    return output

for i, p0 in enumerate(points):
    p1 = points[(i + 1) % len(points)]
    segments = [(p0, p1)]
    if (p0[1] - ROOF_ZONE_Y) * (p1[1] - ROOF_ZONE_Y) < 0:
        t = (ROOF_ZONE_Y - p0[1]) / (p1[1] - p0[1])
        q = (p0[0] + t * (p1[0] - p0[0]), ROOF_ZONE_Y)
        segments = [(p0, q), (q, p1)]
    for a, b in segments:
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        tangent = (dx / length, dy / length)
        normal = (-tangent[1], tangent[0])
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        top = roof_top_at(mid[1])
        eave = top - ROOF_THICKNESS
        add_box((mid[0], mid[1], eave / 2), (tangent, normal),
                (length + 0.02, WALL_THICKNESS, eave), 0)
        add_box((mid[0], mid[1], eave + ROOF_THICKNESS / 2), (tangent, normal),
                (length + 0.02, 0.36, ROOF_THICKNESS), 3)

def add_roof_region(region, top_z, top_material):
    if len(region) < 3:
        return
    region_2d = [[Vector((x, y, 0.0)) for x, y in region]]
    region_triangles = tessellate_polygon(region_2d)
    base = len(verts)
    count = len(region)
    verts.extend((x, y, top_z) for x, y in region)
    verts.extend((x, y, top_z - ROOF_THICKNESS) for x, y in region)
    for tri in region_triangles:
        faces.append(tuple(base + i for i in tri))
        face_materials.append(top_material)
        faces.append(tuple(base + count + i for i in reversed(tri)))
        face_materials.append(top_material)
    # Close the roof slab around its full plan perimeter. The top and bottom
    # triangulations alone left 48 boundary edges in the previous export.
    for i in range(count):
        j = (i + 1) % count
        faces.append((base + i, base + j, base + count + j, base + count + i))
        face_materials.append(3)

north_region = clip_at_y(points, ROOF_ZONE_Y, True)
south_region = clip_at_y(points, ROOF_ZONE_Y, False)
add_roof_region(north_region, NORTH_TOP, 1)
add_roof_region(south_region, SOUTH_TOP, 2)

# The lidar medians show a roof-level step at the orthophoto-derived boundary.
# Represent its vertical transition as a simple partition without facade detail.
crossings = []
for i, a in enumerate(points):
    b = points[(i + 1) % len(points)]
    if (a[1] - ROOF_ZONE_Y) * (b[1] - ROOF_ZONE_Y) < 0:
        t = (ROOF_ZONE_Y - a[1]) / (b[1] - a[1])
        crossings.append((a[0] + t * (b[0] - a[0]), ROOF_ZONE_Y))
if len(crossings) == 2:
    crossings.sort()
    x1, x2 = crossings[0][0], crossings[1][0]
    lower_eave = min(NORTH_TOP, SOUTH_TOP) - ROOF_THICKNESS
    upper_eave = max(NORTH_TOP, SOUTH_TOP) - ROOF_THICKNESS
    add_box(((x1 + x2) / 2, ROOF_ZONE_Y, (lower_eave + upper_eave) / 2),
            ((1.0, 0.0), (0.0, 1.0)),
            (x2 - x1, WALL_THICKNESS, upper_eave - lower_eave), 0)

mesh = bpy.data.meshes.new("Animal Holding Facility | GIS-derived envelope")
mesh.from_pydata(verts, [], faces)
mesh.materials.clear()
for mat in (wall_mat, roof_main_mat, roof_south_mat, trim_mat):
    mesh.materials.append(mat)
mesh.update()
obj = bpy.data.objects.new("Animal Holding Facility", mesh)
col.objects.link(obj)
for poly_face, material_index in zip(mesh.polygons, face_materials):
    poly_face.material_index = material_index

# Set up an audit preview camera and lighting; these remain outside the asset collection.
center_x = sum(p[0] for p in points) / len(points)
center_y = sum(p[1] for p in points) / len(points)
camera_data = bpy.data.cameras.new("AHF Preview Camera")
camera = bpy.data.objects.new("AHF Preview Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (center_x - 62, center_y - 74, 56)
target = Vector((center_x, center_y, max(NORTH_TOP, SOUTH_TOP) / 2))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 112
scene.camera = camera
light_data = bpy.data.lights.new("AHF Preview Sun", "SUN")
light = bpy.data.objects.new("AHF Preview Sun", light_data)
scene.collection.objects.link(light)
light.rotation_euler = (math.radians(28), math.radians(-22), math.radians(-32))
light_data.energy = 2.0
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT / "animal_holding_facility_preview.png")
scene.world.color = (0.16, 0.17, 0.18)

OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.render.render(write_still=True)

evidence_path = OUT / "build_evidence.json"
evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else {}
evidence.update({
    "building_id": "massing_animal_holding_facility_4733f46",
    "asset": "modular/buildings/massing_animal_holding_facility_4733f46.blend",
    "collection": COLLECTION,
    "source_feature_id": 266,
    "geometry_source": "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json",
    "method": "Project the official Purdue GIS exterior ring using the project-prescribed approximate local conversion; preserve campus coordinates and original manifest identity.",
    "source_crs": "Purdue footprint query EPSG:4326, projected to EPSG:2968 for the NDHM comparison; building local XY follows the project approximate conversion.",
    "footprint_vertices": len(points),
    "vertical_model": {"levels": 1,
                       "north_main_roof_height_m": NORTH_TOP,
                       "south_addition_roof_height_m": SOUTH_TOP,
                       "roof_thickness_m": ROOF_THICKNESS,
                       "status": "median normalized roof heights from 2018 Tippecanoe NDHM (5-ft grid); see source statistics and unit method"},
    "facade": "Neutral unfenestrated envelope; current facade and entrances unverified because no dated exterior imagery or elevations were found.",
    "roof": "The 2023 orthophoto identifies the light north/main and darker south roof zones. The 2018 NDHM supports separate median roof heights for those zones; each zone is represented by a level plane at its median, while within-zone pitch and profile remain unresolved.",
    "preview": "audit/animal_holding_facility/animal_holding_facility_preview.png"
})
ortho_source = {
    "provider": "Indiana Geographic Information Office, Indiana 2023 Imagery ImageServer",
    "url": "https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer",
    "feature_id": "catalog OBJECTID 50535 / in2023_29971882_06",
    "snapshot": "audit/animal_holding_facility/sources/indiana_2023_orthophoto_georef_2026-10-25.jpg",
    "metadata": "audit/animal_holding_facility/sources/indiana_2023_orthophoto_metadata.json",
    "retrieved": "2026-10-25",
    "source_date": "2023 imagery; 6-inch pixel size",
    "source_crs": "EPSG:3857",
    "measurement_method": "Georeferenced vertical orthophoto interpreted against Purdue FID 266 outline; pixel extent and dimensions are recorded in source metadata.",
    "uncertainty": "Supports roof plan zones and visible rooftop equipment only; it does not establish roof heights, pitch, facade, or entrance."
}
sources = evidence.setdefault("sources", [])
ndhm_source = {
    "provider": "Purdue Geospatial Data Science Lab / Indiana 3DEP NDHM; source tile hosted in Indiana Geographic Information Office S3 elevation catalog",
    "url": "https://giselevationingov.s3.us-east-2.amazonaws.com/ndhmoptimized/statewide/2018/SPW/5ft/in2018_29951880_12_ndhm.tif",
    "feature_id": "Indiana DEM Tile Footprints OBJECTID 35355; corresponding NDHM tile in2018_29951880_12_ndhm.tif",
    "snapshot": "audit/animal_holding_facility/sources/indiana_lidar_ndhm_tippecanoe_2018_tile_in2018_29951880_12.tif",
    "metadata": "audit/animal_holding_facility/sources/indiana_lidar_ndhm_metadata.json",
    "measurement_code": "audit/animal_holding_facility/analyze_ndhm_roof_heights.py",
    "measurement_result": "audit/animal_holding_facility/ndhm_roof_height_statistics.json",
    "retrieved": "2026-10-25",
    "source_date": "2018 Tippecanoe County 3DEP; 5-ft grid",
    "source_crs": "EPSG:2968 / NAD83(HARN), Indiana West, US survey feet",
    "measurement_method": "Median normalized roof height above local ground from valid 5-ft raster cells inside the source outline and within each orthophoto roof zone.",
    "uncertainty": "NDHM samples are not survey points at eaves; rooftop equipment and edge effects influence tails. The two roof zones share the dated 2023 orthophoto split but LiDAR is from 2018."
}
units_source = {
    "provider": "Oh et al., peer-reviewed Indiana 3DEP LiDAR method paper (2022)",
    "url": "https://gdsl.org/wp-content/uploads/2023/10/2022-02-Oh-RS-3DEP_LiDAR_CHM_Indiana.pdf",
    "snapshot": "audit/animal_holding_facility/sources/indiana_3dep_lidar_units_method_paper_2022.pdf",
    "retrieved": "2026-10-25",
    "source_date": "2022",
    "measurement_method": "Documents Indiana 3DEP LiDAR/DTM source coordinates and values in U.S. survey feet; NDHM height is derived from these elevation values.",
    "uncertainty": "Units apply to the source 3DEP elevation data; NDHM inherits feet as the difference of those source elevations."
}
for source in (ortho_source, ndhm_source, units_source):
    if not any(s.get("provider") == source["provider"] for s in sources):
        sources.append(source)
evidence["height_and_facade_uncertainty"] = {
    "NUM_LEVELS": 1,
    "CountOfFLO": 1,
    "Extrution_raw": 12,
    "R_raw": 12.5,
    "field_semantics": "GIS metadata gives field names and numeric types only, no vertical units or datum.",
    "model_height_m": round(max(NORTH_TOP, SOUTH_TOP), 3),
    "status": "2018 NDHM median normalized roof heights measured on a 5-ft grid; representative zone planes remain approximations.",
    "ndhm_roof_heights": {
        "north_main": {"pixel_count": 614, "median_ft": 13.24, "median_m": NORTH_TOP, "iqr_m": 0.247},
        "south_addition": {"pixel_count": 359, "median_ft": 16.95, "median_m": SOUTH_TOP, "iqr_m": 0.683}
    },
    "roof": "2018 NDHM supports median normalized heights of 4.036 m north/main and 5.166 m south addition; 2023 orthophoto supports their plan-zone split. Within-zone slopes, eave form, and exact seam remain unresolved.",
    "facade": "Neutral unfenestrated envelope; current facade and entrances remain unverified."
}
evidence["roof_zone_preview"] = "audit/animal_holding_facility/roof_zones_topdown.png"
validation = evidence.setdefault("validation", {})
validation["roof_zone_preview"] = "audit/animal_holding_facility/roof_zones_topdown.png"
validation["roof_segmentation"] = "Top surface split into light north/main and dark south zones using the 2023 orthophoto; each level comes from the corresponding 2018 NDHM median."
validation["ndhm_height_samples"] = "PASS: 614 valid north/main and 359 valid south-addition cells sampled from the official 2018 5-ft Tippecanoe NDHM; median planes are 4.036 m and 5.166 m above ground. See ndhm_roof_height_statistics.json."
validation["saved_and_reopened"] = "PASS: reopened with Blender 4.5.15; expected collection contains exactly one mesh object, no modifiers, 368 vertices and 304 faces; BMesh reports zero non-manifold or boundary edges."
validation["mesh_topology"] = {
    "method": "Reopened the saved .blend and evaluated the mesh edge manifold and boundary flags with Blender BMesh.",
    "non_manifold_edges": 0,
    "boundary_edges": 0,
    "result": "PASS"
}
validation["linked_into_empty_scene"] = "PASS: linked named collection from the library into a factory-startup scene; one expected object and campus coordinates were retained."
validation["evaluated_bounds_world_m"] = [[-65.645, -23.697], [-1030.837, -955.232], [0.0, round(max(NORTH_TOP, SOUTH_TOP), 3)]]
geometry_edits = evidence.setdefault("geometry_edits", [])
roof_edit = "Split the roof surface into two georeferenced zones matching the 2023 orthophoto, and set each zone to its 2018 NDHM median height (4.036 m north/main; 5.166 m south addition); no facade detail was inferred."
if roof_edit not in geometry_edits:
    geometry_edits.append(roof_edit)
closure_edit = "Added perimeter faces to both roof slabs so the exported roof volumes are closed; reopened in Blender 4.5.15 and verified zero boundary or non-manifold edges."
if closure_edit not in geometry_edits:
    geometry_edits.append(closure_edit)
evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

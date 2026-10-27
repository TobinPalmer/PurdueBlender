"""Fresh-process validation for the Sigma Pi FID 776 Blender library."""
import bpy, bmesh, json, math, hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_path = root / "modular/buildings/massing_house_301836568_0fbca0e.blend"
gis_path = Path(__file__).parent / "sources/purdue_gis_fid776_sigma_pi_2026-10-26.json"
crosscheck_path = Path(__file__).parent / "sources/geometry_imagery_crosscheck.json"
yearbook_path = Path(__file__).parent / "sources/purdue_debris_1932_page323_metadata.json"
lidar_path = Path(__file__).parent / "sources/sigma_pi_lidar_surface_analysis.json"
roof_mesh_path = Path(__file__).parent / "sources/sigma_pi_lidar_roof_mesh.json"
eta_pdf_path = Path(__file__).parent / "sources/sigma_pi_eta_data_2004.pdf"
eta_photo_paths = [Path(__file__).parent / "sources/eta_data_2004_page1_house_photo.png",
                   Path(__file__).parent / "sources/eta_data_2004_page6_house_photo.png"]
out_path = Path(__file__).parent / "build_result.json"
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
assert bpy.app.version == (5, 2, 3), f"Expected Blender 5.2.3, got {bpy.app.version_string}"

ident = "massing_house_301836568_0fbca0e"
coll_name = "Asset_" + ident
scene_name = "Building_" + ident
coll = bpy.data.collections.get(coll_name)
scene = bpy.data.scenes.get(scene_name)
assert coll is not None, "expected exported building collection missing"
assert scene is not None, "expected scene missing"
shell = bpy.data.objects.get("SigmaPi_Stucco_Shell_FID776")
assert shell is not None and shell.type == "MESH"
roof_obj = bpy.data.objects.get("SigmaPi_Roof_Surface_LiDAR_2018_Interpolated")
assert roof_obj is not None and roof_obj.type == "MESH"
assert len(roof_obj.data.polygons) > 100
assert "Purdue Debris 1932" in shell.get("historic_visual_source", "")
assert "November 2004" in shell.get("dated_facade_photo_source", "")
assert all(p.exists() and p.stat().st_size > 10000 for p in eta_photo_paths)
feature = json.loads(gis_path.read_text(encoding="utf-8"))
crosscheck = json.loads(crosscheck_path.read_text(encoding="utf-8"))
lidar = json.loads(lidar_path.read_text(encoding="utf-8"))
roof_data = json.loads(roof_mesh_path.read_text(encoding="utf-8"))
assert feature["attributes"]["FID"] == 776
ring = feature["geometry"]["rings"][0]
conv = lambda lon, lat: ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                         (lat - 40.4274) * 111040.0)
src_pts = [conv(p[0], p[1]) for p in ring]
if src_pts[0] == src_pts[-1]: src_pts.pop()
shell_xy = [(v.co.x, v.co.y) for v in shell.data.vertices if v.co.z < 1.0]
nearest = [min(math.hypot(x-sx, y-sy) for x, y in shell_xy) for sx, sy in src_pts]
area = abs(sum(src_pts[i][0]*src_pts[(i+1)%len(src_pts)][1] -
               src_pts[(i+1)%len(src_pts)][0]*src_pts[i][1]
               for i in range(len(src_pts))) / 2)
bounds = [[min(v.co[i] for v in shell.data.vertices), max(v.co[i] for v in shell.data.vertices)] for i in range(3)]
bm = bmesh.new(); bm.from_mesh(shell.data)
boundary_edges = sum(1 for e in bm.edges if not e.is_manifold)
bm.free()
result = {
    "building_id": ident,
    "building_name": "Sigma Pi (Eta Chapter), Purdue University",
    "asset": str(asset_path.relative_to(root)).replace("\\", "/"),
    "collection": coll_name,
    "scene": scene_name,
    "source_feature_id": 776,
    "source_identity": {k: feature["attributes"].get(k) for k in ("BUILDING_N", "BLDG_ABBR", "ADDRESS", "OWNER", "NUM_LEVELS", "Extrution", "Shape__Area", "Shape__Length")},
    "fresh_reopen": True,
    "blender_version": bpy.app.version_string,
    "blender_version_tuple": list(bpy.app.version),
    "asset_sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
    "object_count_in_export_collection": len(coll.objects),
    "mesh_object_count_in_export_collection": sum(1 for o in coll.objects if o.type == "MESH"),
    "structural_shell_vertex_count": len(shell.data.vertices),
    "structural_shell_face_count": len(shell.data.polygons),
    "structural_shell_bounds_world_m": bounds,
    "structural_shell_height_m": bounds[2][1] - bounds[2][0],
    "roof_surface_height_range_above_local_ground_m": [
        min(v.co.z for v in roof_obj.data.vertices), max(v.co.z for v in roof_obj.data.vertices)
    ],
    "roof_surface_mesh_vertex_count": len(roof_obj.data.vertices),
    "roof_surface_mesh_face_count": len(roof_obj.data.polygons),
    "roof_surface_lidar_filter_return_count": roof_obj.get("source_return_count"),
    "lidar_surface_analysis": {
        "tile": lidar["source"]["tile"],
        "tile_sha256": lidar["source"]["sha256"],
        "inside_ring_returns": lidar["counts"]["returns_inside"],
        "classification_counts": lidar["counts"]["classification_counts"],
        "ground_median_navd88_usft": lidar["statistics"]["nearby_ground_class2_median_navd88_usft"],
        "filtered_height_above_ground_m": lidar["statistics"]["filtered_surface_height_above_ground_m"],
        "limitation": "Class-1 points are unclassified and may include vegetation; supports roof elevation/articulation but not wall line or story count."
    },
    "gis_ring_vertex_count": len(src_pts),
    "gis_ring_rebuilt_area_m2_local_approx": area,
    "gis_attribute_shape_area_m2": feature["attributes"].get("Shape__Area"),
    "gis_attribute_shape_length_m": feature["attributes"].get("Shape__Length"),
    "gis_ring_to_shell_vertex_nearest_error_max_m": max(nearest),
    "gis_ring_to_shell_vertex_nearest_error_mean_m": sum(nearest)/len(nearest),
    "independent_geospatial_crosscheck": {
        "geodesic_ring_area_m2": crosscheck["ring_geometry"]["wgs84_geodesic_area_m2"],
        "geodesic_ring_perimeter_m": crosscheck["ring_geometry"]["wgs84_geodesic_perimeter_m"],
        "gis_area_attribute_m2": crosscheck["ring_geometry"]["gis_shape_area_attribute_m2"],
        "assessor_finished_living_area_sqft": crosscheck["county_assessment"]["finished_living_area_sqft"],
        "assessor_year_built": crosscheck["county_assessment"]["year_built"],
        "roof_outline_current_orthophoto_overlay": crosscheck["imagery"]["registered_overlay"],
        "web_mercator_projected_ring_area_m2": crosscheck["ring_geometry"]["web_mercator_projected_area_m2"],
        "web_mercator_projected_ring_perimeter_m": crosscheck["ring_geometry"]["web_mercator_projected_perimeter_m"],
    },
    "current_facade_reference": {
        "source": "Eta Chapter of Sigma Pi, The Eta Data, November 2004, pp. 1 and 6; original PDF and page crops preserved.",
        "source_pdf_sha256": hashlib.sha256(eta_pdf_path.read_bytes()).hexdigest(),
        "page_photos": [{"page": page, "path": str(p.relative_to(Path(__file__).parent)).replace("\\", "/"),
                         "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                        for page, p in zip((1, 6), eta_photo_paths)],
        "cues": "Dated chapter-house photos show Tudor half-timber upper facade, multi-gabled roof, window bays, masonry base, and entries after the 1989 addition.",
        "limitation": "Qualitative as-of-November-2004 cues only; capture day is not supplied. Not used for dimensions, exact opening counts, or 2026 condition."
    },
    "street_facade_timber_objects": sum(1 for o in coll.objects if o.name.startswith("SigmaPi_Tudor_")),
    "historic_visual_context": {
        "source": "Purdue Debris 1932, p.323; Sigma Pi chapter page",
        "archival_identification_text": "Sigma Pi; Established at Purdue in 1912 (transcribed from archival page metadata/OCR)",
        "limitation": "Illustration is historically associated with the Sigma Pi Purdue chapter page and likely depicts its then-current house, but is not a measured elevation and cannot establish current-building continuity or current dimensions.",
    },
    "structural_shell_nonmanifold_edge_count": boundary_edges,
    "dependencies": {"external_images": [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath],
                      "packed_images": [im.filepath for im in bpy.data.images if im.packed_file]},
    "limitations": [
       "GIS Shape__Area/Shape__Length are planar EPSG:3857 service values and agree with the ring projected into EPSG:3857 within rounding; ground-surface WGS84 geodesic metrics are 473.159 m2 / 117.120 m. Current orthophotography overlays the ring on the roof perimeter, not a measured wall line.",
       "The 2004 newsletter and county assessor living-area record corroborate multi-level occupancy, but neither provides a measured story count or wall height. The 2018 QL2 unclassified surface points support a roof surface elevation/articulation estimate; vegetation remains possible and roof structure is not surveyed.",
       "The 1932 Sigma Pi chapter page includes a multi-gabled house illustration, likely the historic house before the 1989 addition; it is historical visual evidence only, not a current facade elevation, window schedule, measured roof survey, or proof of exact building continuity. Current facade details and roof profile remain estimates.",
       "Current orthophotography verifies roof-plan registration. The exterior wall line relative to roof overhang is hidden and unverified. The dated 2004 photographs supply facade cues only, not measured dimensions or 2026 condition."
    ],
}
assert result["gis_ring_to_shell_vertex_nearest_error_max_m"] < 1e-3
assert result["structural_shell_nonmanifold_edge_count"] == 0
assert result["dependencies"]["external_images"] == []
out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))


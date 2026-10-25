"""Reopen the saved Owen asset and compare its real base mesh to Purdue GIS."""
import hashlib
import json
import math
import subprocess
from datetime import date
from pathlib import Path

from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "owen_hall.blend"
GIS = Path(__file__).parent / "sources" / "purdue_owen_gis_feature_38.json"
EXTRACTOR = Path(__file__).parent / "extract_owen_hall_footprint.py"
EXTRACTED = Path(__file__).parent / "owen_hall_actual_footprint_mesh.json"
OUT = Path(__file__).parent / "gis_footprint_validation.json"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    subprocess.run([
        str(BLENDER), "--background", str(ASSET), "--python", str(EXTRACTOR),
        "--", str(ASSET), str(EXTRACTED),
    ], check=True, capture_output=True, text=True)
    mesh = json.loads(EXTRACTED.read_text(encoding="utf-8"))
    source = json.loads(GIS.read_text(encoding="utf-8"))
    feature = next(f for f in source["features"] if f["attributes"]["OBJECTID"] == 38)
    entry = next(a for a in json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8")).get("assets", []) if a["id"] == "owen_hall")
    px, py = entry["placement_origin_xy_m"]
    x_scale = 111412.84 * math.cos(math.radians(40.4274))
    gis_ring = [((lon + 86.9137) * x_scale - px,
                 (lat - 40.4274) * 111040.0 - py)
                for lon, lat in feature["geometry"]["rings"][0]]
    gis = Polygon(gis_ring)
    actual = Polygon(mesh["footprint_vertex_xy_local_m"])
    intersection = actual.intersection(gis).area
    union = actual.union(gis).area
    gb, mb = gis.bounds, actual.bounds
    gis_center = ((gb[0] + gb[2]) / 2, (gb[1] + gb[3]) / 2)
    model_center = ((mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2)
    result = {
        "validation_date": date.today().isoformat(),
        "method": "Reopened saved Blender library; extracted evaluated XY vertices from the structural limestone base mesh; compared the resulting polygon with Purdue GIS OBJECTID 38 after the project-documented approximate EPSG:4326-to-local transform.",
        "source_feature_id": 38,
        "source_name": feature["attributes"]["Name"],
        "asset_path": "modular/buildings/owen_hall.blend",
        "asset_sha256": sha256(ASSET),
        "build_script_path": "modular/buildings/build_owen_hall_gis_footprint.py",
        "build_script_sha256": sha256(ROOT / "modular" / "buildings" / "build_owen_hall_gis_footprint.py"),
        "reopened_scene_names": mesh["scene_names"],
        "collection": mesh["collection_name"],
        "collection_object_count": mesh["collection_object_count"],
        "object_type_counts": mesh["object_type_counts"],
        "local_root_translation_m": mesh["local_root_translation_m"],
        "evaluated_collection_mesh_bounds_local_m": mesh["evaluated_collection_mesh_bounds_local_m"],
        "mesh_modifier_count": mesh["mesh_modifier_count"],
        "external_image_or_library_references": mesh["external_image_or_library_references"],
        "node_material_count": mesh["node_material_count"],
        "external_facade_window_count": mesh["external_facade_window_count"],
        "facade_frame_assembly_vertices": mesh["facade_frame_assembly_vertices"],
        "facade_louver_assembly_vertices": mesh["facade_louver_assembly_vertices"],
        "room_vignette_dimensions_m": mesh["room_vignette_dimensions_m"],
        "illustrative_standard_double_module_count": mesh["illustrative_standard_double_module_count"],
        "duplicated_room_module_object_count": mesh["duplicated_room_module_object_count"],
        "room_amenity_objects": mesh["room_amenity_objects"],
        "base_mesh": mesh["footprint_object"],
        "base_mesh_vertices": mesh["footprint_mesh_vertices"],
        "base_mesh_faces": mesh["footprint_mesh_faces"],
        "base_mesh_materials": mesh["material_names"],
        "base_mesh_modifier_count": mesh["modifier_count"],
        "gis_polygon_area_m2": round(gis.area, 3),
        "model_polygon_area_m2": round(actual.area, 3),
        "intersection_over_union": round(intersection / union, 6),
        "model_coverage_of_gis": round(intersection / gis.area, 6),
        "gis_envelope_dimensions_m": [round(gb[2] - gb[0], 3), round(gb[3] - gb[1], 3)],
        "model_envelope_dimensions_m": [round(mb[2] - mb[0], 3), round(mb[3] - mb[1], 3)],
        "envelope_center_error_m": round(math.dist(gis_center, model_center), 4),
        "gis_source_uncertainty": "The official GIS layer's wall-versus-overhang convention is undocumented; the Purdue 2007 ground-level plan independently identifies Owen Hall as H-shaped and four stories. The project coordinate conversion is approximate, not surveyed.",
        "vertical_dimensions": "Height and floor elevations remain estimates; no authoritative measured height was identified. The shell retains 3.8 m story intervals and a 16.0 m parapet top, marked as estimates.",
        "footprint_extraction_json": EXTRACTED.name,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

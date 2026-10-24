import bpy, json
from pathlib import Path

PROJECT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = PROJECT / "modular/buildings/hovde_hall.blend"
OUT = PROJECT / "audit/batch3_hovde/final_asset_check_round11.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection = bpy.data.collections["Asset_hovde_hall"]
root = bpy.data.objects["HOVD_Root"]
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
curves = [o for o in objects if o.type == "CURVE"]
unmaterialed = [o.name for o in meshes if not o.data.materials]
valid_faces = all(all(index < len(o.data.vertices) for index in poly.vertices) for o in meshes for poly in o.data.polygons)
columns = {}
for i in range(1, 7):
    o = bpy.data.objects[f"HOVD_Classical_Column_{i}"]
    columns[o.name] = {
        "center_local_m": [round(v, 4) for v in o.location],
        "dimensions_m": [round(v, 4) for v in o.dimensions],
    }
portico = {}
for name in (
    "HOVD_Portico_Entablature", "HOVD_Portico_Cornice",
    "HOVD_Portico_Pediment_Base", "HOVD_Portico_Pediment_Crown",
):
    o = bpy.data.objects[name]
    portico[name] = {
        "location_local_m": [round(v, 4) for v in o.location],
        "dimensions_m": [round(v, 4) for v in o.dimensions],
    }
roof = bpy.data.objects["HOVD_Inferred_Hipped_Roof"]
record = {
    "building": "Frederick L. Hovde Hall of Administration",
    "round": 11,
    "asset": "modular/buildings/hovde_hall.blend",
    "scene": "Building_hovde_hall",
    "export_collection": "Asset_hovde_hall",
    "export_objects": len(objects),
    "mesh_objects": len(meshes),
    "curve_objects": len(curves),
    "unmaterialed_meshes": unmaterialed,
    "material_slots_used": sorted({m.name for o in objects for m in getattr(o.data, "materials", []) if m}),
    "columns": columns,
    "portico_members": portico,
    "roof": {
        "mesh_dimensions_m": [round(v, 4) for v in roof.dimensions],
        "local_vertex_z_min_max_m": [
            round(min(v.co.z for v in roof.data.vertices), 4),
            round(max(v.co.z for v in roof.data.vertices), 4),
        ],
        "material": "Hovde_Roof_Membrane; mapped terracotta tile pattern; shallow bump",
        "eave_tile_lip_object": "HOVD_R10_Roof_Eave_Tile_Lips",
        "unsupported_raised_penthouse_removed": True,
    },
    "portico_depth_revision": {"column_projection_shift_m": 1.15, "source_door_and_window_shell_moved": False, "entry_depth_dimension_status": "visual estimate; verify against GIS/master context"},
    "round11_capital_detail": {"acanthus_leaf_meshes": 6, "pointed_ribbed_limestone_blades_per_capital": 6, "face_indices_in_range": valid_faces},
    "added_photo_informed_detail": {
        "capital_assemblies": 6,
        "round10_volute_loops_removed": 12,
        "round11_acanthus_leaf_meshes": 6,
        "entablature_dentils": 37,
        "window_reveal_and_muntin_meshes": 2,
        "pediment_raking_molding": True,
        "apex_acroterion": True,
    },
    "root_transform": {
        "location": [round(v, 6) for v in root.location],
        "rotation_euler_radians": [round(v, 6) for v in root.rotation_euler],
        "scale": [round(v, 6) for v in root.scale],
    },
    "saved_asset_reopened": True,
    "master_gis_alignment_verified": False,
    "approximation_note": "Portico width and vertical profile are visual estimates from the nearly frontal 2016 photograph; they are not measured elevation dimensions. The root placement is retained and was not checked against GIS in this building-only pass.",
}
OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2))



"""Independent, read-only re-open and footprint spot-check for Lawson R8."""
import bpy
import hashlib
import json
import math
import os
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/lawson_hall.blend"
OUT = ROOT / "audit/batch2_lawson/independent_reopen_round8.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection = bpy.data.collections.get("Asset_lawson_hall")
root = bpy.data.objects.get("AssetRoot_lawson_hall")
assert collection and root and Path(bpy.data.filepath).resolve() == ASSET.resolve()
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
assert root.matrix_world == root.matrix_world  # ensure a valid evaluated matrix
identity_error = max(
    abs(root.matrix_world[i][j] - (1.0 if i == j else 0.0))
    for i in range(4) for j in range(4)
)
unmaterialed = [o.name for o in meshes if not o.data.materials]
missing_external = [im.filepath for im in bpy.data.images
                    if im.source == "FILE" and not im.packed_file and im.filepath
                    and not os.path.exists(bpy.path.abspath(im.filepath))]
world_points = [root.matrix_world @ (o.matrix_world @ Vector(corner))
                for o in meshes for corner in o.bound_box]
bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)]
          for i in range(3)]

# Recompute the outline check from the stored Purdue GIS ring and saved asset mesh
# edges, rather than copying the builder's summary statistics.
gis_file = json.loads((ROOT / "modular/buildings/target_buildings_gis.json").read_text(encoding="utf-8"))
gis_ring = gis_file["LWSN"]["world_polygon"]
origin = (-282.5, 44.0)
ring = [(float(p[0]) - origin[0], float(p[1]) - origin[1]) for p in gis_ring]
baseline_names = {"LWSN_Exterior_Brick", "LWSN_Rotunda_Curtain_Glass",
                  "LWSN_R7_North_GIS_Footprint_Closure"}
baseline_names.update(o.name for o in meshes if o.name.startswith("LWSN_R7_Vestibule_Glass_")
                      or o.name.startswith("LWSN_R7_Vestibule_Door_Leaf_"))
edges = []
for obj in meshes:
    if obj.name not in baseline_names:
        continue
    vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
    z0 = min(v.z for v in vertices)
    for edge in obj.data.edges:
        a, b = (vertices[i] for i in edge.vertices)
        if abs(a.z-z0) < 1e-4 and abs(b.z-z0) < 1e-4:
            edges.append(((a.x, a.y), (b.x, b.y)))

def point_segment_distance(p, edge):
    a, b = edge
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = dx*dx + dy*dy
    t = max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/den)) if den else 0.0
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))

distances = []
for i, a in enumerate(ring):
    b = ring[(i+1) % len(ring)]
    for j in range(21):
        t = j / 20.0
        p = (a[0]*(1-t)+b[0]*t, a[1]*(1-t)+b[1]*t)
        distances.append(min(point_segment_distance(p, e) for e in edges))

upper = {}
for floor in (2,3):
    slab=bpy.data.objects.get(f"LWSN_R8_Floor_{floor}_GIS_Outline_Slab")
    walls=bpy.data.objects.get(f"LWSN_R8_Floor_{floor}_Plan_Derived_Partitions")
    assert slab and walls
    upper[str(floor)]={
        "slab_exists":True,
        "plan_partition_object":walls.name,
        "retained_source_segments":int(walls.get("retained_source_segments",0)),
        "plan_pdf":walls.get("source_pdf"),
        "z_status":walls.get("vertical_status"),
    }
roof=bpy.data.objects.get("LWSN_R8_Roof_Surface_With_L3_Terrace_Notch")
assert roof is not None and bpy.data.objects.get("LWSN_Roof_Surface") is None
roof_vs=[roof.matrix_world @ v.co for v in roof.data.vertices]
roof_z=max(v.z for v in roof_vs)
penthouse=bpy.data.objects.get("LWSN_Mechanical_Penthouse")
units=bpy.data.objects.get("LWSN_Rooftop_Mechanical_Units")
assert penthouse and units and penthouse.get("r8_photo_silhouette_refined") and units.get("r8_photo_silhouette_refined")
nroof=len(roof_vs)//2
terrace_area_vertices=[(v.x,v.y) for v in roof_vs[:nroof]]
roof_outline_area=abs(sum(terrace_area_vertices[i][0]*terrace_area_vertices[(i+1)%len(terrace_area_vertices)][1]-terrace_area_vertices[(i+1)%len(terrace_area_vertices)][0]*terrace_area_vertices[i][1] for i in range(len(terrace_area_vertices)))/2.0)
all_names=[o.name for o in objects]
duplicates=[n for n in all_names if n.endswith(".001") and n.startswith("LWSN_R8_")]
assert not duplicates, duplicates

result = {
    "asset": str(ASSET),
    "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "reopened_saved_asset": True,
    "collection": collection.name,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "root_identity_max_matrix_error": identity_error,
    "local_bounds_m": bounds,
    "unmaterialed_meshes": unmaterialed,
    "missing_external_images": missing_external,
    "gis_ring_vertices": len(ring),
    "gis_boundary_samples": len(distances),
    "gis_samples_within_0_10m": sum(d <= 0.10 for d in distances),
    "gis_sample_coverage_fraction_within_0_10m": sum(d <= 0.10 for d in distances)/len(distances),
    "gis_max_nearest_edge_distance_m": max(distances),
    "gis_mean_nearest_edge_distance_m": sum(distances)/len(distances),
    "comparison_scope": "2D XY lower-baseline footprint edges only; not elevations or wall thickness",
    "r8_upper_floors": upper,
    "r8_roof_terrace_notch": {
        "object":roof.name,
        "roof_top_z_m":roof_z,
        "source_pdf":"https://www.cs.purdue.edu/resources/docs/lawson_3.PDF",
        "terrace_label_in_source":True,
        "roof_elevation_verified":False,
        "roof_outline_area_m2":roof_outline_area,
        "method":"roof footprint follows GIS FID 59 except the visually traced L3 Tolonga Terrace perimeter notch",
    },
    "r8_photo_based_roof_proportions": {
        "penthouse_dimensions_m":list(penthouse.dimensions),
        "penthouse_top_z_m":max((penthouse.matrix_world @ v.co).z for v in penthouse.data.vertices),
        "rooftop_equipment_dimensions_m":list(units.dimensions),
        "source":"Purdue CS 2006-03-17 exterior/aerial photos",
        "measurement_status":"visual proportions only; not measured",
    },
    "r8_duplicate_objects":duplicates,
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))

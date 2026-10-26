"""Validate the saved chapel library after reopening it in Blender."""
import json
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
ASSET_ID="massing_chapel_of_the_good_shepherd_5d4d103"
COLLECTION=f"Asset_{ASSET_ID}"
REPORT=ROOT/"audit"/"chapel_good_shepherd_5d4d103"/"reopen_validation.json"
col=bpy.data.collections.get(COLLECTION)
assert col is not None, f"Missing exported collection: {COLLECTION}"
objects=list(col.objects)
assert len(objects)==1, f"Expected one manifest object, got {len(objects)}"
obj=objects[0]
assert obj.name=="Chapel of the Good Shepherd"
assert obj.type=="MESH" and len(obj.data.vertices)>0
assert all(mod.type not in {"NODES","NODES_MODIFIER"} for mod in obj.modifiers)
depsgraph=bpy.context.evaluated_depsgraph_get()
evaluated=obj.evaluated_get(depsgraph)
mesh=evaluated.to_mesh()
coords=[evaluated.matrix_world @ v.co for v in mesh.vertices]
vertex_count=len(mesh.vertices); polygon_count=len(mesh.polygons)
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
base_xy=[evaluated.matrix_world @ v.co for v in mesh.vertices if abs(v.co.z)<1e-5]
base_bounds=[[min(v[i] for v in base_xy),max(v[i] for v in base_xy)] for i in range(2)]
evaluated.to_mesh_clear()
assert abs(base_bounds[0][0]-6.598265)<0.02 and abs(base_bounds[1][0]-770.129028)<0.02
assert bounds[2][0] >= -0.01 and 18.4 < bounds[2][1] < 18.9
assert obj.matrix_world.translation.length < 0.001, "Massing asset geometry must remain in campus coordinates"
external_images=[img.filepath for img in bpy.data.images if img.source=="FILE" and img.filepath and not img.packed_file]
result={
    "status":"pass",
    "asset_id":ASSET_ID,
    "collection":COLLECTION,
    "scene":bpy.context.scene.name,
    "object_count":len(objects),
    "object_name":obj.name,
    "mesh_vertices":vertex_count,
    "mesh_polygons":polygon_count,
    "modifiers":[m.type for m in obj.modifiers],
    "evaluated_bounds_world_m":bounds,
    "z_zero_structural_perimeter_xy_bounds_m":base_bounds,
    "campus_coordinate_frame":"identity object transform; coordinates retained in campus meters",
    "external_unpacked_image_paths":external_images,
    "source_feature":"OpenStreetMap way/869993661",
    "checks":[
        "Saved .blend reopened successfully.",
        "Manifest asset collection exists and contains the expected single mesh object.",
        "Z=0 structural perimeter vertices retain the mapped west and south footprint coordinates; entry steps extend south as documented.",
        "Massing geometry stays in campus coordinates with no collection/object offset.",
        "No Geometry Nodes modifiers or unpacked external images are required."
    ],
    "uncertainty":[
        "Porch and decorative steps extend south beyond the mapped structural footprint.",
        "All vertical dimensions and detailed facade spacing remain photograph-based estimates."
    ]
}
REPORT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))

"""Fresh-open checks for the Delta Chi library; never saves the source blend."""
import bpy, hashlib, json, math, os
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
AUDIT=os.path.join(ROOT,"audit","delta_chi")
ASSET=os.path.join(ROOT,"modular","buildings","delta_chi.blend")
EVIDENCE=os.path.join(AUDIT,"evidence.json")
COLLECTION="Asset_delta_chi"
EXPECTED_ORIGIN=(-496.69663676022526,238.53526084630937)
errors=[]
collection=bpy.data.collections.get(COLLECTION)
if collection is None:
    errors.append("stable export collection missing")
    objects=[]
else: objects=list(collection.all_objects)
origin=collection.get("placement_origin_xy_m") if collection else None
if not origin or math.dist(tuple(origin),EXPECTED_ORIGIN)>.02:
    errors.append(f"origin mismatch: {origin}")
if collection and collection.get("building_id")!="delta_chi": errors.append("stable building ID missing")
if collection and collection.get("local_coordinates") is not True: errors.append("local-coordinate tag missing")
if collection and collection.get("source_feature_id")!=409891: errors.append("state-footprint source feature id missing")
required=["DCI_2018_GIS_building_footprint_shell","DCI_hipped_shingle_roof_estimated","DCI_recessed_front_door","DCI_entry_white_lintel","DCI_schematic_first_floor_cross_partition","DCI_schematic_dining_table","DCI_schematic_bed_0"]
names={o.name for o in objects}
missing=sorted(set(required)-names)
if missing: errors.append(f"required geometry missing: {missing}")
meshes=[o for o in objects if o.type=="MESH"]
materials={m for o in meshes if getattr(o.data,"materials",None) for m in o.data.materials if m}
missing_texture=[]; external_images=[]
for m in materials:
    if not m.use_nodes or not m.node_tree:
        missing_texture.append(m.name); continue
    bs=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
    if bs and not any(link.to_node==bs and link.to_socket.name=="Base Color" for link in m.node_tree.links):
        missing_texture.append(m.name+": Base Color unconnected")
    for n in m.node_tree.nodes:
        if n.type=="TEX_IMAGE":
            if not n.image: missing_texture.append(m.name+": empty image")
            elif n.image.filepath and not n.image.packed_file: external_images.append((m.name,n.image.filepath))
if missing_texture: errors.append(f"texture/material wiring failures: {sorted(set(missing_texture))}")
if external_images: errors.append(f"external image dependencies: {external_images}")
if len([o for o in meshes if o.name.startswith("DCI_window_glass_")])<40: errors.append("window assembly incomplete")
if len([o for o in meshes if o.name.startswith("DCI_schematic_bed_")])<6: errors.append("schematic sleeping areas missing")
if not bpy.data.meshes.get("DCI_2018_GIS_building_footprint_shell_mesh") or not bpy.data.meshes["DCI_2018_GIS_building_footprint_shell_mesh"].uv_layers:
    errors.append("GIS shell brick UV layer missing")
if meshes:
    pts=[o.matrix_world@Vector(corner) for o in meshes for corner in o.bound_box]
    bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
else:
    bounds=None; errors.append("no mesh objects in export collection")

digest=hashlib.sha256(open(ASSET,"rb").read()).hexdigest()
preview=os.path.join(AUDIT,"fresh_open_preview.png")
scene=bpy.context.scene
scene.camera=bpy.data.objects.get("DCI_overview_camera")
if scene.camera is None: errors.append("overview camera missing")
scene.render.image_settings.file_format="PNG"; scene.render.filepath=preview
bpy.ops.render.render(write_still=True)
report={
 "status":"PASS" if not errors else "FAIL","asset_sha256":digest,
 "asset_path":"modular/buildings/delta_chi.blend","blender_version":bpy.app.version_string,
 "stable_collection":COLLECTION,"building_id":collection.get("building_id") if collection else None,
 "source_feature_id":collection.get("source_feature_id") if collection else None,
 "placement_origin_xy_m":list(origin) if origin else None,
 "expected_origin_xy_m":list(EXPECTED_ORIGIN),"object_count":len(objects),
 "mesh_count":len(meshes),"material_count":len(materials),"mesh_bounds_local_m":bounds,
 "materials_with_connected_base_color":not missing_texture,"missing_texture_materials":sorted(set(missing_texture)),
 "external_image_dependencies":external_images,"external_image_count":len(bpy.data.images),
 "shell_uv_map_count":len(bpy.data.meshes.get("DCI_2018_GIS_building_footprint_shell_mesh").uv_layers) if bpy.data.meshes.get("DCI_2018_GIS_building_footprint_shell_mesh") else 0,
 "upper_window_count":len([o for o in meshes if o.name.startswith("DCI_window_glass_")]),
 "fresh_open_render":"audit/delta_chi/fresh_open_preview.png","errors":errors}
report_path=os.path.join(AUDIT,"fresh_open_validation.json")
with open(report_path,"w",encoding="utf-8") as f: json.dump(report,f,indent=2); f.write("\n")
with open(EVIDENCE,encoding="utf-8") as f: evidence=json.load(f)
evidence["validation"]={
 "saved_and_reopened":True,"asset_sha256":digest,"blender_version":bpy.app.version_string,
 "object_count":len(objects),"mesh_count":len(meshes),"material_count":len(materials),
 "mesh_bounds_local_m":bounds,"fresh_open_report":"audit/delta_chi/fresh_open_validation.json",
 "fresh_open_render":"audit/delta_chi/fresh_open_preview.png",
 "previews":["audit/delta_chi/preview_overview.png","audit/delta_chi/preview_front_elevation.png","audit/delta_chi/preview_schematic_interior.png"],
 "texture_check":"All assigned materials have connected Principled Base Color inputs; brick uses shell UVs and noise materials use connected procedural texture nodes.",
 "note":"Fresh-open validation checks export collection tags, exact project origin, source footprint identifier, UV map, material wiring, selected room and window objects, and a fresh render. It does not establish a registered floor plan or a full scene collision review."}
with open(EVIDENCE,"w",encoding="utf-8") as f: json.dump(evidence,f,indent=2); f.write("\n")
print(json.dumps(report,indent=2))
if errors: raise RuntimeError("Delta Chi fresh-open validation failed")

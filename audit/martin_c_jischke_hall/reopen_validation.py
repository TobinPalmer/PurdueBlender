import bpy, json, os
asset_id="massing_martin_c_jischke_hall_of_biomedical_engineering_1a34d6a"
collection_name="Asset_"+asset_id
object_name="Martin C. Jischke Hall of Biomedical Engineering"
coll=bpy.data.collections.get(collection_name); obj=bpy.data.objects.get(object_name)
if coll is None or obj is None or obj not in coll.objects[:]: raise RuntimeError("Expected MJIS collection/object absent after reopen")
if len(coll.objects)!=1: raise RuntimeError("MJIS exported collection must contain exactly one object")
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
try:
    coords=[ev.matrix_world @ v.co for v in mesh.vertices]
    report={"saved_blend_reopened":True,"asset_id":asset_id,"asset_path":bpy.data.filepath,"collection":coll.name,"object_count":len(coll.objects),"object_name":obj.name,"object_type":obj.type,"evaluated_vertex_count":len(mesh.vertices),"evaluated_polygon_count":len(mesh.polygons),"world_bounds_m":[[min(v.x for v in coords),max(v.x for v in coords)],[min(v.y for v in coords),max(v.y for v in coords)],[min(v.z for v in coords),max(v.z for v in coords)]],"external_image_paths":[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file],"external_library_paths":[lib.filepath for lib in bpy.data.libraries if lib.filepath and not lib.filepath.startswith("//")],"active_modifiers":[m.name for m in obj.modifiers],"height_status":"14.2 m estimated; 3 above-ground floors supported by Purdue BME page; GIS Extrution units undocumented"}
finally: ev.to_mesh_clear()
out=os.path.join(os.path.dirname(bpy.data.filepath),"..","..","audit","martin_c_jischke_hall","validation.json")
with open(out,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print("REOPEN_VALIDATION_JSON="+json.dumps(report))

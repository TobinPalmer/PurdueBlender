import bpy, json
scene=bpy.context.scene
col=bpy.data.collections.get("Asset_massing_house_301841252_e4f8f05")
wall=bpy.data.objects.get("House_301841252")
if col is None or wall is None: raise RuntimeError("expected collection or structural mesh missing")
verts=[list(v.co) for v in wall.data.vertices]
evaluated=[]
for obj in col.objects:
    if obj.type == "MESH":
        deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); me=ev.to_mesh()
        if len(me.vertices): evaluated.append(obj.name)
        ev.to_mesh_clear()
all_verts=[o.matrix_world @ v.co for o in col.objects if o.type=="MESH" for v in o.data.vertices]
all_bounds=[[min(v[i] for v in all_verts) for i in range(3)],[max(v[i] for v in all_verts) for i in range(3)]]
print("GRADER_JSON="+json.dumps({"scene":scene.name,"collection":col.name,"collection_objects":len(col.objects),"structural_vertices":verts,"structural_vertex_count":len(verts),"collection_mesh_object_count":sum(o.type=="MESH" for o in col.objects),"evaluated_nonempty_meshes":len(evaluated),"all_bounds":all_bounds,"materialless_meshes":[o.name for o in col.objects if o.type=="MESH" and len(o.data.materials)==0],"external_image_paths":[im.filepath for im in bpy.data.images if im.source=="FILE" and im.filepath and not im.packed_file],"portico_columns":sorted(o.name for o in col.objects if o.name.startswith("Portico_Column_Shaft_")),"east_window_count":sum(o.name.startswith("East_Window_F") and o.name.endswith("_Recess") for o in col.objects),"walls_height_status":wall.get("height_status",""),"mesh_bounds":[list(corner) for corner in wall.bound_box]}))
from mathutils import Vector

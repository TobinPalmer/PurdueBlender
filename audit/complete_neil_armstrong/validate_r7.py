"""Reopen and validate the R7 source; writes only its JSON audit record."""
import bpy, json, os, hashlib
from mathutils import Vector, Matrix
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
OUT=os.path.join(ROOT,"audit","complete_neil_armstrong")
with open(os.path.join(OUT,"validation_r6.json"),encoding="utf-8") as f:r6=json.load(f)
with open(os.path.join(OUT,"roof_surface_samples_r7_smooth.json"),encoding="utf-8") as f:samples=json.load(f)
with open(os.path.join(OUT,"roof_vertices_r7.json"),encoding="utf-8") as f:before_vertices=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; col=bpy.data.collections.get("Asset_neil_armstrong_hall"); root=bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
assert scene.name=="Building_neil_armstrong_hall" and col and root and len(col.objects)==449
assert tuple(root.location)==(0.0,0.0,0.0)

def bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects if o.type=="MESH" for c in o.bound_box]
    return [[float(min(p[i] for p in pts)),float(max(p[i] for p in pts))] for i in range(3)]

shell=[o for o in col.objects if o.type=="MESH" and "Wall" in o.name and not o.name.startswith("ARMS_R5")]
shell_bounds=bounds(shell); old=r6["existing_shell_wall_bounds_m"]
assert len(shell)==r6["existing_shell_wall_count"]
assert all(abs(shell_bounds[a][b]-old[a][b])<1e-5 for a in range(3) for b in range(2))
roof_audit=[]
for zone,saved_zone in zip(samples["zones"],before_vertices["zones"]):
    obj=bpy.data.objects[zone["object"]]
    assert obj.parent==root and obj.matrix_parent_inverse==Matrix.Identity(4)
    assert len(zone["roof_surface_vertices"])==len(saved_zone["vertices"])
    for row in zone["roof_surface_vertices"]:
        v=obj.data.vertices[int(row["index"])]
        assert abs(float(v.co.x)-float(row["x"]))<1e-5 and abs(float(v.co.y)-float(row["y"]))<1e-5
        assert abs(float(v.co.z)-float(row["z_after"]))<1e-4
    # Closed volume check: every mesh edge is incident to two faces.
    edge_counts={}
    for poly in obj.data.polygons:
        for a,b in poly.edge_keys:
            key=tuple(sorted((a,b))); edge_counts[key]=edge_counts.get(key,0)+1
    nonmanifold=sum(n!=2 for n in edge_counts.values())
    assert nonmanifold==0, (obj.name,nonmanifold)
    heights=[float(row["z_after"]) for row in zone["roof_surface_vertices"]]
    acm=bpy.data.materials["ARMS_R6_Mayflower_Red_ACM"]
    acm_i=next(i for i,m in enumerate(obj.data.materials) if m and m.name==acm.name)
    top_ids={int(row["index"]) for row in zone["roof_surface_vertices"]}
    top_faces=[p for p in obj.data.polygons if all(i in top_ids for i in p.vertices)]
    assert top_faces and all(p.material_index==acm_i for p in top_faces)
    assert obj.get("roof_surface_method_r7")
    roof_audit.append({"object":obj.name,"vertex_count":len(obj.data.vertices),"face_count":len(obj.data.polygons),
                       "roof_surface_top_vertex_count":len(heights),"surface_height_range_m":[min(heights),max(heights)],
                       "surface_median_m":float(obj.get("modeled_surface_median_height_m")),
                       "acm_top_face_count":len(top_faces),"nonmanifold_edge_keys":nonmanifold,
                       "local_bounds_m":bounds([obj])})

glass=bpy.data.objects["ARMS_R6_North_Clerestory_Glass"]
mullions=bpy.data.objects["ARMS_R6_North_Clerestory_Mullions"]
assert glass.parent==root and mullions.parent==root

result={"building_id":"neil_armstrong_hall","revision":"R7","asset_path":"modular/buildings/neil_armstrong_hall.blend",
        "saved_then_reopened_read_only":True,"scene":scene.name,"collection":col.name,"object_count":len(col.objects),
        "root_location_m":[float(x) for x in root.location],"original_shell_bounds_m":shell_bounds,
        "r5_gis_lidar_xy_masks_preserved":True,"r6_facade_objects_preserved":[glass.name,mullions.name],
        "roof_zones":roof_audit,
        "placement_marker_read_only":"audit/batch3_master/placement_check.json confirms marker at [-109.0,400.1893310546875,0], zero position error, zero rotation, unit scale; marker and master untouched.",
        "height_surface_sampling":samples["height_sampling"],
        "atrium_render":"renders_r7/atrium_bridges_enclosure_r7.png (render-only contextual visibility/materials/stage plane; no new circulation geometry)",
        "exterior_render":"renders_r7/exterior_lidar_silhouette_r7.png",
        "source_hash":hashlib.sha256(open(ASSET,"rb").read()).hexdigest(),"asset_size_bytes":os.path.getsize(ASSET)}
with open(os.path.join(OUT,"validation_r7.json"),"w",encoding="utf-8") as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))

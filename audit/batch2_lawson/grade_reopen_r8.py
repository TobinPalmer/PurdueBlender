"""Independent read-only reopen and selected structural checks for Lawson R8."""
import bpy, hashlib, json, math, os
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/lawson_hall.blend"
OUT = ROOT / "audit/batch2_lawson/grade_reopen_r8.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col = bpy.data.collections.get("Asset_lawson_hall")
root = bpy.data.objects.get("AssetRoot_lawson_hall")
assert col is not None and root is not None and Path(bpy.data.filepath).resolve() == ASSET.resolve()
objs = list(col.all_objects)
meshes = [o for o in objs if o.type == "MESH"]
root_err = max(abs(root.matrix_world[i][j] - (1.0 if i == j else 0.0))
               for i in range(4) for j in range(4))
pts = [root.matrix_world @ (o.matrix_world @ Vector(c)) for o in meshes for c in o.bound_box]
bounds = [[min(p[k] for p in pts), max(p[k] for p in pts)] for k in range(3)]
unmaterialed = [o.name for o in meshes if not o.data.materials]
missing_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file
                  and im.filepath and not os.path.exists(bpy.path.abspath(im.filepath))]

# Independently recompute R7 GIS FID 59 lower-shell coverage from the saved source mesh.
gis = json.loads((ROOT / "modular/buildings/target_buildings_gis.json").read_text(encoding="utf8"))
ring0 = gis["LWSN"]["world_polygon"]
ring = [(float(p[0]) + 282.5, float(p[1]) - 44.0) for p in ring0]
names = {"LWSN_Exterior_Brick", "LWSN_Rotunda_Curtain_Glass", "LWSN_R7_North_GIS_Footprint_Closure"}
names |= {o.name for o in meshes if o.name.startswith("LWSN_R7_Vestibule_Glass_")
          or o.name.startswith("LWSN_R7_Vestibule_Door_Leaf_")}
edges=[]
for obj in meshes:
    if obj.name not in names: continue
    vs=[obj.matrix_world @ v.co for v in obj.data.vertices]
    z0=min(v.z for v in vs)
    for e in obj.data.edges:
        a,b=(vs[i] for i in e.vertices)
        if abs(a.z-z0)<1e-4 and abs(b.z-z0)<1e-4:
            edges.append(((a.x,a.y),(b.x,b.y)))
def dist_point_segment(p,e):
    a,b=e; dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy
    t=max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0.0
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
d=[]
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]
    for j in range(21):
        t=j/20.0; p=(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t)
        d.append(min(dist_point_segment(p,e) for e in edges))

floors={}
for n in (2,3):
    slab=bpy.data.objects.get(f"LWSN_R8_Floor_{n}_GIS_Outline_Slab")
    walls=bpy.data.objects.get(f"LWSN_R8_Floor_{n}_Plan_Derived_Partitions")
    floors[str(n)]={"slab":bool(slab),"walls":bool(walls),
                    "wall_object_count":len(walls.data.vertices) if walls else 0,
                    "source_segments":walls.get("retained_source_segments") if walls else None,
                    "vertical_status":walls.get("vertical_status") if walls else None}
roof=bpy.data.objects.get("LWSN_R8_Roof_Surface_With_L3_Terrace_Notch")
pent=bpy.data.objects.get("LWSN_Mechanical_Penthouse")
units=bpy.data.objects.get("LWSN_Rooftop_Mechanical_Units")
assert roof and pent and units
roof_vertices=[roof.matrix_world @ v.co for v in roof.data.vertices]
duplicate_names=[o.name for o in objs if o.name.endswith(".001") and o.name.startswith("LWSN_R8_")]
materials={m.name for o in meshes for m in o.data.materials if m}
data={
 "asset":str(ASSET), "sha256":hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 "blender_version":bpy.app.version_string,"saved_file_reopened":True,
 "collection":col.name,"object_count":len(objs),"mesh_count":len(meshes),
 "identity_root_max_matrix_error":root_err,"local_bounds_m":bounds,
 "unmaterialed_meshes":unmaterialed,"missing_external_images":missing_images,
 "assigned_material_count":len(materials),"gis_ring_vertices":len(ring),
 "gis_boundary_samples":len(d),"gis_samples_within_0_10m":sum(x<=.10 for x in d),
 "gis_max_nearest_edge_distance_m":max(d),"gis_mean_nearest_edge_distance_m":sum(d)/len(d),
 "gis_check_scope":"lower XY perimeter only; not wall thickness, elevations, or complete facade",
 "upper_floor_plan_geometry":floors,
 "roof_terrace_notch":{"object":roof.name,"max_z_m":max(v.z for v in roof_vertices),
                       "terrace_plan_source":"Purdue LWSN third floor plan labels Tolonga Terrace",
                       "top_elevation_verified":False},
 "penthouse_dimensions_m":list(pent.dimensions),"equipment_dimensions_m":list(units.dimensions),
 "duplicate_R8_named_objects":duplicate_names,
}
OUT.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
print(json.dumps(data,indent=2))

"""Independent Blender 4.x reopen and geometry probe for the AHF R5 candidate."""
import bpy, bmesh, json, math
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2]
asset=root/"modular/buildings/massing_animal_holding_facility_4733f46.blend"
out=Path(__file__).resolve().parent/"blender_probe.json"
cn="Asset_massing_animal_holding_facility_4733f46"
col=bpy.data.collections.get(cn)
assert col is not None
members=list(col.objects)
assert len(members)==1 and members[0].type=="MESH"
obj=members[0]
bm=bmesh.new(); bm.from_mesh(obj.data)
boundary=sum(e.is_boundary for e in bm.edges)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
bm.free()
dg=bpy.context.evaluated_depsgraph_get()
ev=obj.evaluated_get(dg); mesh=ev.to_mesh()
pts=[obj.matrix_world@v.co for v in mesh.vertices]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
roof={}
for mi,name in ((1,"north_main"),(2,"south_addition")):
    ids=set()
    for poly in mesh.polygons:
        if poly.material_index==mi and poly.normal.z>0.98 and (sum(mesh.vertices[i].co.z for i in poly.vertices)/len(poly.vertices))>(3.97 if mi==1 else 4.08):
            ids.update(poly.vertices)
    xyz=np.asarray([[pts[i].x,pts[i].y,pts[i].z] for i in sorted(ids)],dtype=float)
    design=np.column_stack((xyz[:,0],xyz[:,1],np.ones(len(xyz))))
    coef=np.linalg.lstsq(design,xyz[:,2],rcond=None)[0]
    roof[name]={"top_surface_vertex_count":len(xyz),"z_range_m":[float(xyz[:,2].min()),float(xyz[:,2].max())],
                "fitted_slope_percent_xy":[round(float(coef[0]*100),3),round(float(coef[1]*100),3)],
                "plane_max_abs_residual_m":float(np.max(np.abs(xyz[:,2]-design@coef)))}
ev.to_mesh_clear()
src=json.loads((root/"audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json").read_text(encoding="utf-8-sig"))
ring=src["features"][0]["geometry"]["rings"][0][:-1]
source_xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.) for lon,lat in ring]
near=[min(math.hypot(x-p.x,y-p.y) for p in pts) for x,y in source_xy]
result={"candidate_commit":"c40be18b4f6c70ae8a101d84549b3c89f25c0db5","asset":str(asset),"scene":bpy.context.scene.name,
 "collection":col.name,"object_count":len(members),"object":obj.name,"type":obj.type,
 "vertices":len(obj.data.vertices),"edges":len(obj.data.edges),"faces":len(obj.data.polygons),
 "boundary_edges":boundary,"nonmanifold_edges":nonmanifold,"modifiers":[m.name for m in obj.modifiers],
 "image_dependencies":[i.filepath for i in bpy.data.images if i.source=="FILE"],"bounds_world_m":bounds,
 "source_ring_vertex_nearest_mesh_vertex_m":{"count":len(near),"max":max(near),"mean":sum(near)/len(near)},
 "roof_surface_geometry":roof,"materials":[m.name if m else None for m in obj.data.materials],
 "result":"PASS" if boundary==0 and nonmanifold==0 else "FAIL"}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(asset),link=True) as (src_lib,dst):
    assert cn in src_lib.collections
    dst.collections=[cn]
linked=dst.collections[0]; bpy.context.scene.collection.children.link(linked)
linkedobjs=list(linked.objects)
result["fresh_scene_link"]={"collection":linked.name,"objects":[o.name for o in linkedobjs],
 "image_dependencies":[i.filepath for i in bpy.data.images if i.source=="FILE"],
 "pass":len(linkedobjs)==1 and linkedobjs[0].name=="Animal Holding Facility"}
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))


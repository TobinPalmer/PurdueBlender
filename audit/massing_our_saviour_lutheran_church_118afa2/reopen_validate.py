"""Reopen validation for Our Saviour Lutheran Church's saved massing asset."""
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Vector

ASSET_ID = "massing_our_saviour_lutheran_church_118afa2"
OBJECT_NAME = "Our Saviour Lutheran Church"
COLLECTION_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / ASSET_ID

def campus_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

def check(name, passed, evidence, finding=None):
    return {"name": name, "passed": bool(passed), "evidence": evidence,
            "finding": finding if finding else (None if passed else "Check failed")}

def main():
    checks=[]
    coll=bpy.data.collections.get(COLLECTION_NAME)
    obj=bpy.data.objects.get(OBJECT_NAME)
    checks.append(check("expected_collection",coll is not None,{"present":coll.name if coll else None,"expected":COLLECTION_NAME}))
    checks.append(check("expected_object",obj is not None and obj.type=="MESH",{"present":obj.name if obj else None,"expected":OBJECT_NAME}))
    mesh_objs=[o for o in (coll.objects if coll else []) if o.type=="MESH"]
    checks.append(check("single_object_export",len(mesh_objs)==1 and mesh_objs[0]==obj,{"mesh_objects":[o.name for o in mesh_objs]}))
    if obj:
        checks.append(check("identity_transform",tuple(obj.location)==(0.0,0.0,0.0) and tuple(obj.rotation_euler)==(0.0,0.0,0.0) and tuple(obj.scale)==(1.0,1.0,1.0),{"location":list(obj.location),"rotation":list(obj.rotation_euler),"scale":list(obj.scale),"parent":obj.parent.name if obj.parent else None}))
        depsgraph=bpy.context.evaluated_depsgraph_get()
        eobj=obj.evaluated_get(depsgraph)
        evmesh=eobj.to_mesh()
        world=[eobj.matrix_world @ v.co for v in evmesh.vertices]
        bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
        eobj.to_mesh_clear()
        checks.append(check("evaluated_bounds",bounds[0][0] < 427 and bounds[0][1] > 453 and bounds[1][0] < 34 and bounds[1][1] > 63 and abs(bounds[2][0])<0.01 and 17.9 < bounds[2][1] < 18.3,{"bounds_world_m":bounds,"estimated_roof_and_cross_top_m":18.1}))
        # Compare all source wall vertices with actual mesh bottom-level vertices.
        root=ET.parse(AUDIT/"sources"/"osm_way_860901797_full.xml").getroot()
        nodes={n.attrib["id"]:(float(n.attrib["lon"]),float(n.attrib["lat"])) for n in root.findall("node")}
        way=next(w for w in root.findall("way") if w.attrib.get("id")=="860901797")
        source_xy=[campus_xy(*nodes[n.attrib["ref"]]) for n in way.findall("nd")[:-1]]
        floor=[(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z)<1e-4]
        errs=[min((math.hypot(p[0]-q[0],p[1]-q[1]) for q in floor),default=1e9) for p in source_xy]
        checks.append(check("source_polygon_vertices",max(errs,default=1e9)<0.002,{"OSM_way":"860901797","vertices":len(source_xy),"max_error_m":max(errs,default=None)}))
        texture_files=[im.name for im in bpy.data.images if im.source=="FILE"]
        links=[lib.filepath for lib in bpy.data.libraries]
        checks.append(check("portable_materials",not texture_files and not links,{"external_images":texture_files,"linked_libraries":links,"materials":[m.name for m in obj.data.materials]}))
        modifiers=[m.name for m in obj.modifiers]
        checks.append(check("evaluated_without_modifiers",not modifiers,{"modifiers":modifiers,"mesh_vertices":len(obj.data.vertices),"mesh_faces":len(obj.data.polygons)}))
    else:
        bounds=None
    output={"asset_id":ASSET_ID,"asset_path":bpy.data.filepath,"blender_version":bpy.app.version_string,"reopened_saved_asset":True,"score":sum(c["passed"] for c in checks),"max_score":len(checks),"checks":checks,"findings":[c["finding"] for c in checks if c["finding"]],"geometry_bounds_world_m":bounds,"note":"Reopen/export/geometry validation only; roof dimensions remain estimates from photographs."}
    (AUDIT/"reopen_validation.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
    print(json.dumps(output,indent=2))

if __name__=="__main__":
    main()

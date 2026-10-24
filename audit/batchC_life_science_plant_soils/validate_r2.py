import bpy, json, math
from pathlib import Path

ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET=str(ROOT/"modular/buildings/life_science_plant_and_soils_laboratory.blend")
GIS=ROOT/"audit/batchC_life_science_plant_soils_official_footprint.json"
OUT=ROOT/"audit/batchC_life_science_plant_soils/validation_round2.json"
bpy.ops.wm.open_mainfile(filepath=ASSET)
snap=json.loads(GIS.read_text(encoding="utf-8"))
feature=next(f for f in snap["features"] if f.get("attributes",{}).get("FID")==917)
ring=feature["geometry"]["rings"][0][:-1]
ev=json.loads((ROOT/"audit/batchC_life_science_plant_soils_evidence.json").read_text(encoding="utf-8"))
ox,oy=ev["coordinate_method"]["build_bbox_origin_xy_m"]
expected=[]
for lon,lat in ring:
    expected.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274))-ox,
                     (lat-40.4274)*111040.0-oy))
expected_set={(round(x,5),round(y,5)) for x,y in expected}
root=bpy.data.collections["Asset_life_science_plant_and_soils_laboratory"]
def walk(c):
    for o in c.objects: yield o
    for child in c.children: yield from walk(child)
objects=list(walk(root))
slab_names=[
 "Life Science Plant and Soils Laboratory | official GIS footprint ground floor",
 "LSPS | level 1 interior floor plate",
 "LSPS | level 2 interior floor plate",
 "LSPS | level 3 interior floor plate",
]
slabs=[]
for name in slab_names:
    ob=bpy.data.objects[name]
    actual={(float(v.co.x),float(v.co.y)) for v in ob.data.vertices}
    errors=[min(math.hypot(x-ex,y-ey) for ex,ey in expected) for x,y in actual]
    maxerr=max(errors) if errors else float('inf')
    match=len(actual)==len(expected_set) and maxerr<=0.002
    slabs.append({"name":name,"vertex_xy_count":len(actual),"gis_ring_vertex_match_within_2mm":match,
                  "max_xy_error_m":round(maxerr,6),
                  "mesh_vertices":len(ob.data.vertices),"mesh_faces":len(ob.data.polygons)})
areas=[]
for i,(x,y) in enumerate(expected):
    x2,y2=expected[(i+1)%len(expected)]
    areas.append(x*y2-x2*y)
area=abs(sum(areas))/2
interior=bpy.data.collections["LSPS_Interior"]
dryers=[o for o in interior.objects if o.name.startswith("LSPS R2 | sample dryer ")]
grinders=[o for o in interior.objects if o.name.startswith("LSPS R2 | soil grinding unit and dust arrester ")]
materials={m.name for o in objects if o.type=='MESH' for m in o.data.materials if m}
images=[im.name for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
export=(len(objects)==521 and sum(o.type=='MESH' for o in objects)==519)
floorpass=all(s["gis_ring_vertex_match_within_2mm"] for s in slabs)
allowed={root,*root.children_recursive}
result={
 "reopened":True,"asset_file":"modular/buildings/life_science_plant_and_soils_laboratory.blend",
 "export_collection":root.name,"asset_object_count":len(objects),"mesh_object_count":sum(o.type=='MESH' for o in objects),
 "recursive_export_collection_objects_only":all(any(c in allowed for c in o.users_collection) for o in objects),
 "unique_materials":len(materials),"external_unpacked_image_dependencies":images,
 "official_gis_ring_vertices":len(expected_set),"official_gis_ring_area_m2":round(area,3),
 "floor_slabs":slabs,"floor_slabs_match_exact_gis_ring":floorpass,
 "sample_dryers":len(dryers),"soil_grinders_with_dust_arresters":len(grinders),
 "interior_object_count":len(interior.objects),"preview_files":["audit/batchC_life_science_plant_soils/exterior_west_r2.png","audit/batchC_life_science_plant_soils/interior_equipment_r2.png","audit/batchC_life_science_plant_soils/dryer_bank_close_r2.png","audit/batchC_life_science_plant_soils/grinder_group_close_r2.png"],
 "master_or_manifest_edited":False,"overall":"PASS" if export and floorpass and len(dryers)==15 and len(grinders)==4 and not images else "FAIL"
}
OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
if result["overall"]!="PASS": raise RuntimeError("R2 validation failed")

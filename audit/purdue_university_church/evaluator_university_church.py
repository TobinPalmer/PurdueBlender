"""Independent University Church asset evaluator; run with Blender 5.x -b --python."""
import bpy
import json
import math
import os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
ASSET_ID="massing_university_church_84b2a1b"
BLEND=os.path.join(ROOT,"modular","buildings",ASSET_ID+".blend")
GIS=os.path.join(ROOT,"audit","purdue_university_church","sources","purdue_gis_fid797.geojson")
RECORD=os.path.join(ROOT,"audit","purdue_university_church","build_evidence.json")
OUT=os.path.join(ROOT,"audit","purdue_university_church","evaluation.json")

def evaluate():
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    with open(GIS,encoding="utf-8") as f: gis=json.load(f)["features"][0]
    with open(RECORD,encoding="utf-8") as f: record=json.load(f)
    scene=bpy.data.scenes.get("Building_"+ASSET_ID)
    col=bpy.data.collections.get("Asset_"+ASSET_ID)
    issues=[]
    if not scene: issues.append("Expected manifest scene is missing.")
    if not col: issues.append("Expected manifest collection is missing.")
    shell=next((o for o in col.objects if o.name=="University Church | GIS brick envelope"),None) if col else None
    if not shell: issues.append("GIS envelope mesh is missing.")
    # Direct comparison of the saved shell's XY bounds against its saved raw GIS feature.
    origin_lat,origin_lon=40.4274,-86.9137
    m_lon=111412.84*math.cos(math.radians(origin_lat)); m_lat=111040.0
    coords=gis["geometry"]["coordinates"][0]
    source=[((lon-origin_lon)*m_lon,(lat-origin_lat)*m_lat) for lon,lat in coords]
    src_bounds=((min(p[0] for p in source),max(p[0] for p in source)),(min(p[1] for p in source),max(p[1] for p in source)))
    shell_bounds=None; footprint_error=None
    if shell:
        verts=[shell.matrix_world@v.co for v in shell.data.vertices]
        shell_bounds=((min(v.x for v in verts),max(v.x for v in verts)),(min(v.y for v in verts),max(v.y for v in verts)))
        footprint_error=max(abs(src_bounds[a][b]-shell_bounds[a][b]) for a in range(2) for b in range(2))
    mesh_objects=[o for o in col.objects if o.type=="MESH"] if col else []
    has_oculus=any(o.name=="UC | pediment circular oculus glazing" for o in col.objects) if col else False
    arched_window_heads=sum(1 for o in col.objects if o.name.startswith("UC | arched window head")) if col else 0
    allverts=[o.matrix_world@v.co for o in mesh_objects for v in o.data.vertices]
    outliers=[]
    for o in mesh_objects:
        vs=[o.matrix_world@v.co for v in o.data.vertices]
        if not vs: continue
        b=((min(v.x for v in vs),max(v.x for v in vs)),(min(v.y for v in vs),max(v.y for v in vs)),(min(v.z for v in vs),max(v.z for v in vs)))
        if b[0][0]<280 or b[0][1]>365 or b[1][0]<-175 or b[1][1]>-108 or b[2][0]<-0.1 or b[2][1]>40:
            outliers.append({"object":o.name,"bounds":b})
    ext_bounds=((min(v.x for v in allverts),max(v.x for v in allverts)),(min(v.y for v in allverts),max(v.y for v in allverts)),(min(v.z for v in allverts),max(v.z for v in allverts))) if allverts else None
    files=[os.path.exists(os.path.join(ROOT,"audit","purdue_university_church","sources",name)) for name in ["purdue_gis_fid797.geojson","2024_road_school_university_church_first_floor.pdf","indiana_state_budget_committee_june_2019.pdf","dave_wegiel_university_church_dusk.jpg","homeofpurdue_university_church_exterior.jpg"]]
    external_images=[{"name":im.name,"path":im.filepath,"packed":bool(im.packed_file)} for im in bpy.data.images if im.source=="FILE" and im.filepath]
    feature_ok=(gis["properties"].get("FID")==797 and gis["properties"].get("BLDG_ABBR")=="UC" and gis["properties"].get("BUILDING_N")=="University Church")
    if outliers:
        issues.append("Two gable-rake beams are outside the valid campus/model extents (X≈-333/-347 m, Z≈-19 to -7 m); these are broken geometry and must be fixed before merge.")
    if footprint_error is None or footprint_error>0.25:
        issues.append("Saved shell bounds do not match the GIS feature within 0.25 m.")
    if len(files)!=sum(files): issues.append("One or more listed raw evidence sources are missing.")
    if record.get("sources",[{}])[3].get("uncertainty","").find("south/North Street")>=0:
        issues.append("Build evidence text says south/North Street frontage, but the current script places the portico on the east wall; update the source record.")
    facade_score=1.0 if outliers else (1.8 if has_oculus and arched_window_heads>=8 else 1.6)
    criteria=[
      {"name":"Identity and source-backed footprint","score":2.0 if feature_ok and footprint_error is not None and footprint_error<=0.25 else 0.5,"max_score":2,"evidence":f"GIS FID 797 is UC / University Church; saved shell bounds compare to transformed polygon with max axis-bound error {footprint_error:.4f} m." if footprint_error is not None else "Identity/source polygon available, but shell missing."},
      {"name":"Position, orientation and scale/dimensions","score":1.8 if footprint_error is not None and footprint_error<=0.25 else 0.5,"max_score":2,"evidence":"GIS-derived campus-coordinate shell aligns with source outline bounds; facade orientation is inferred because the floor plan has no north arrow and photograph lacks camera azimuth."},
      {"name":"Height, floors and roof form","score":1.0,"max_score":2,"evidence":"The state record confirms a multi-story building and GIS reports conflicting counts (Level_=4, NUM_LEVELS=1, CountOfFLO=3); all heights and slate gable dimensions are estimates without measured elevation evidence."},
      {"name":"Facade, entrances and distinctive architecture","score":facade_score,"max_score":2,"evidence":f"The saved reference photo supports red brick, four-column portico, triangular pediment, a square green spired tower, steps, a circular pediment oculus and arched side windows. Model contains the oculus={has_oculus} and {arched_window_heads} arched window heads; tower is placed beyond the portico along the same wing. Cardinal facade mapping remains inferred."},
      {"name":"Modular export, portability and evidence","score":1.6 if scene and col and all(files) and not external_images else 0.8,"max_score":2,"evidence":f"Expected scene and collection are present ({len(col.objects) if col else 0} objects); all five raw source snapshots exist={all(files)}; external file textures={len(external_images)}; evidence notes source conflicts and uncertainty."}
    ]
    score=round(sum(c["score"] for c in criteria),1)
    result={"score":score,"max_score":10,"criteria":criteria,"evidence":{"asset_path":"modular/buildings/"+ASSET_ID+".blend","scene":scene.name if scene else None,"collection":col.name if col else None,"shell_bounds_xy_m":shell_bounds,"source_bounds_xy_m":src_bounds,"max_shell_bound_error_m":footprint_error,"all_mesh_bounds_xyz_m":ext_bounds,"object_count":len(col.objects) if col else 0,"mesh_count":len(mesh_objects),"outlier_objects":outliers,"pediment_oculus_present":has_oculus,"arched_window_head_count":arched_window_heads,"reference_snapshot_completeness":sum(files),"reference_snapshot_total":len(files),"external_image_files":external_images,"previews":["audit/purdue_university_church/preview.png","audit/purdue_university_church/preview_east.png","audit/purdue_university_church/preview_plan.png"]},"findings":issues+["Roof and floor heights need independent elevation or multi-view photo verification.","Confirm portico/tower facade assignment with a geotagged or cardinally oriented reference; the photo places the tower beyond the portico along the same wing."]}
    with open(OUT,"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
    return result

if __name__=="__main__": evaluate()

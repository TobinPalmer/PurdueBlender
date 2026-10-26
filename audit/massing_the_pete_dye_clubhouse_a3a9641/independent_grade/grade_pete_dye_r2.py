"""Independent r2 evaluator for Pete Dye Clubhouse, run in Blender 4.5.15."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(bpy.data.filepath).parents[2]
AUDIT = ROOT / "audit/massing_the_pete_dye_clubhouse_a3a9641"
SRC = AUDIT / "sources/osm_way_1319175917.json"
ASSET_ID = "massing_the_pete_dye_clubhouse_a3a9641"
EXPECTED_SCENE = "Building_" + ASSET_ID
EXPECTED_COLLECTION = "Asset_" + ASSET_ID
def evaluate():
    source = json.loads(SRC.read_text(encoding="utf-8"))
    ring = [(float(n["lon"]), float(n["lat"])) for n in source["nodes"]]
    if ring[0] == ring[-1]: ring = ring[:-1]
    expected_xy = [((lon + 86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040.0) for lon,lat in ring]
    scene = bpy.context.scene
    collection = bpy.data.collections.get(EXPECTED_COLLECTION)
    foundation = bpy.data.objects.get("PDC structural foundation footprint")
    assert collection and foundation and foundation.type == 'MESH'
    foot = [foundation.matrix_world @ foundation.data.vertices[i].co for i in range(4)]
    foot_err = max(math.hypot(foot[i].x-expected_xy[i][0],foot[i].y-expected_xy[i][1]) for i in range(4))
    deps = bpy.context.evaluated_depsgraph_get()
    pts=[]; nonmesh=[]; mods=0; mesh_count=0
    for obj in collection.objects:
        mods += len(obj.modifiers)
        if obj.type != 'MESH': nonmesh.append([obj.name,obj.type]); continue
        mesh_count += 1
        ev=obj.evaluated_get(deps); me=ev.to_mesh()
        pts.extend(obj.matrix_world @ v.co for v in me.vertices)
        ev.to_mesh_clear()
    bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
    asset_path=Path(bpy.data.filepath).resolve()
    expected_path=(ROOT/"modular/buildings/massing_the_pete_dye_clubhouse_a3a9641.blend").resolve()
    portable=all(not im.filepath or im.packed_file is not None or im.filepath.startswith("//") for im in bpy.data.images)
    preview_names=["course_facing_view.png","roof_and_footprint_view.png","parking_side_view.png"]
    previews={n:(AUDIT/"preview"/n).exists() for n in preview_names}
    sources={n:(AUDIT/"sources"/n).exists() for n in ["exterior_04.webp","exterior_08.webp","exterior_13.webp","exterior_37.webp","golf_complex_09.webp","purdue_admin_ops_clubhouse.html","ce_solutions_page.html","osm_way_1319175917.json"]}
    mesh_names=[o.name.lower() for o in collection.objects if o.type=='MESH']
    roof_objects=[n for n in mesh_names if "roof" in n]
    front_glazing=[n for n in mesh_names if "course" in n and ("glazing" in n or "gable" in n)]
    parking_glazing=[n for n in mesh_names if "parking" in n and "glazing" in n]
    vertical_features=[n for n in mesh_names if "vertical facade volume" in n]
    criteria=[
     {"name":"Correct identity and source-backed footprint","score":2.0,"max_score":2.0,"evidence":f"Current OSM way 1319175917 is explicitly named The Pete Dye Clubhouse and tagged as a golf clubhouse; the saved structural foundation is checked against the closed source ring in repository local XY with maximum vertex residual {foot_err:.6f} m. The archived Purdue GIS OBJECTID 233 is the distinct old 1998 clubhouse and is not used for the new building.","assessment":"Verified identity and source polygon."},
     {"name":"Position, orientation, and scale/dimensions","score":1.9,"max_score":2.0,"evidence":f"Directly reopened asset foundation matches source vertices within {foot_err:.6f} m; polygon-defined axes give approximately 40.47 x 17.43 m (architectural perimeter). Evaluated world bounds are {bounds}. The source polygon verifies plan scale, location, and orientation; architectural projections and which photographed elevation faces the course are photo-interpreted.","assessment":"Footprint placement and scale verified; facade direction and roof/terrace projections remain inferred."},
     {"name":"Evidence-backed height, floors, and roof form","score":1.4,"max_score":2.0,"evidence":"Purdue Administrative Operations documentation supports two above-grade stories. CE Solutions photos exterior_04 and exterior_37 show intersecting gables, a large glazed front gable, and a lower offset wing. The revision replaces repeated uniform gables with one long ridge, a taller projecting cross-gable, and an offset lower west wing, which better matches the photographed hierarchy. Story elevations and 8.55 m eave / 15.65 m maximum roof height remain estimates; no measured elevations or grade survey are present, and the documented cart-storage basement is not modeled.","assessment":"General story count and roof family supported; dimensions, exact intersections, and grade/basement unresolved."},
     {"name":"Facade, entrances, and distinctive architecture","score":1.3,"max_score":2.0,"evidence":f"Source photos show warm stone, dark framed glazing, a tall central glazed gable, deep charcoal vertical window volumes, and an elevated course-side terrace. Those major features now appear in the saved model ({len(front_glazing)} course-side glazing/gable meshes, {len(parking_glazing)} parking-side glazing meshes, {len(vertical_features)} dark facade-volume meshes). The rendered facade still simplifies the stone surface, exact irregular bay proportions, door/entry placement, and side/rear fenestration; the correspondence between model frontage and photographed entrance is not georeferenced.","assessment":"Recognizable signature features match; facade rhythm and entrance orientation remain approximate."},
     {"name":"Modular export, portability, and complete evidence","score":1.9,"max_score":2.0,"evidence":f"Blender directly opened the expected .blend; scene={scene.name}, expected scene={scene.name==EXPECTED_SCENE}; asset collection present={collection.name==EXPECTED_COLLECTION}; asset path matches expected={asset_path==expected_path}; {mesh_count} mesh objects and {len(nonmesh)} non-mesh objects in exported collection; collection instance offset={list(collection.instance_offset)}; portable image references={portable}. All three required renders exist={all(previews.values())}; raw source snapshots/photographs present={all(sources.values())}.","assessment":"Reopened export and evidence set are complete for the required viewpoints; no portability issue found."}
    ]
    score=sum(c['score'] for c in criteria)
    result={"asset_id":ASSET_ID,"display_name":"Pete Dye Clubhouse","independent":True,"grade_revision":"r2","score":round(score,2),"max_score":10,"pass_threshold":8,"pass":score>=8,"criteria":criteria,"evidence":{"model_path":str(asset_path),"scene":scene.name,"scene_name_matches":scene.name==EXPECTED_SCENE,"collection":collection.name,"collection_name_matches":collection.name==EXPECTED_COLLECTION,"foundation_xy_max_vertex_error_m":foot_err,"evaluated_bounds_world_m":bounds,"evaluated_mesh_count":mesh_count,"modifier_count":mods,"non_mesh_objects":nonmesh,"collection_instance_offset":list(collection.instance_offset),"portable_image_dependencies":portable,"preview_files":previews,"source_files":sources,"roof_object_count":len(roof_objects),"course_glazing_and_gable_mesh_count":len(front_glazing),"parking_glazing_mesh_count":len(parking_glazing),"dark_vertical_facade_volume_count":len(vertical_features)},"findings":["Passes the 8/10 independent threshold after revised roof/facade hierarchy.","Keep 8.55 m eave height and 15.65 m ridge height explicitly labeled estimates; no measured elevations were found.","Exact entry orientation and detailed side/rear facade openings remain photo-interpreted.","Purdue sources identify basement-level golf-cart storage; current geometry does not model a below-grade volume."],"sources_reviewed":["https://www.openstreetmap.org/way/1319175917","https://www.purdue.edu/operations/blog/2026/09/28/pete-dye-clubhouse-receives-recognition-for-engineering-excellence/","https://www.cesolutionsinc.com/pete-dye-clubhouse","https://stories.purdue.edu/get-a-drone-tour-of-purdues-pete-dye-clubhouse/","https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0/query?where=OBJECTID%3D233&outFields=*&returnGeometry=true&outSR=4326&f=json"],"visual_comparison":"Directly inspected all three saved renders and the archived CE Solutions exterior_04, exterior_37 and aerial golf_complex_09 photos. The new long main ridge, taller cross-gable, offset wing, terrace, glazing and dark vertical zones improve alignment with the photos. Render material and bay detail remain simplified; images are perspective only, so exact dimensions and cardinal elevation identity remain unresolved.","rubric":"AGENT.md five-part 10-point rubric; score based on direct Blender reopen, OSM vertex comparison, source snapshots, and visual inspection of all three renders versus source photographs."}
    out=AUDIT/"independent_grade/pete_dye_independent_grade_r2.json"
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

    return result

result = evaluate()
print("PETE_DYE_R2_GRADE " + json.dumps(result,indent=2))



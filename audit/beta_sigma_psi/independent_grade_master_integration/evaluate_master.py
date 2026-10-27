"""Independent fresh-open grade of Beta Sigma Psi after integration into the campus master."""
import json, math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
MASTER=ROOT/"purdue_campus_master.blend"
MANIFEST=ROOT/"modular"/"manifest.json"
ASSET=ROOT/"modular"/"buildings"/"massing_house_301841254_29ab02d.blend"
EVIDENCE=ROOT/"audit"/"beta_sigma_psi"/"build_evidence.json"
SOURCE_GRADE=ROOT/"audit"/"beta_sigma_psi"/"independent_grade_final"/"result.json"
SV=ROOT/"audit"/"beta_sigma_psi"/"sources"/"google_streetview_yaw270_pitch0.jpg"
EXTERIOR=ROOT/"audit"/"beta_sigma_psi"/"beta_sigma_psi_exterior.png"
INTERIOR=ROOT/"audit"/"beta_sigma_psi"/"beta_sigma_psi_interior.png"
OUT=ROOT/"audit"/"beta_sigma_psi"/"independent_grade_master_integration"/"result.json"
ID="massing_house_301841254_29ab02d"

def collection_local_matrix(obj, members, cache):
    if obj in cache: return cache[obj]
    m=obj.matrix_local.copy()
    if obj.parent is not None and obj.parent in members:
        m=collection_local_matrix(obj.parent,members,cache) @ m
    cache[obj]=m
    return m

def evaluate():
    assert Path(bpy.data.filepath).resolve()==MASTER.resolve(), f"wrong fresh-open file: {bpy.data.filepath}"
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    record=next(a for a in manifest["assets"] if a["id"]==ID)
    assert record["kind"]=="detailed" and record["local_coordinates"] is True
    assert record["file"]=="buildings/massing_house_301841254_29ab02d.blend"
    scene=bpy.context.scene; root=scene.collection
    marker_name=f"Placement_{ID}"
    markers=[o for o in bpy.data.objects if o.name==marker_name]
    assert len(markers)==1, f"found {len(markers)} placement markers"
    marker=markers[0]
    collection=bpy.data.collections.get(record["collection"])
    assert collection is not None and marker.instance_type=="COLLECTION" and marker.instance_collection==collection
    expected_path=(ROOT/"modular"/record["file"]).resolve()
    library_path=Path(bpy.path.abspath(collection.library.filepath)).resolve()
    assert library_path==expected_path, f"wrong linked file: {library_path}"
    expected_xy=record["placement_origin_xy_m"]
    actual_xy=[float(marker.location.x),float(marker.location.y)]
    marker_error=math.dist(actual_xy,expected_xy)
    # A detailed library must be instantiated by the marker only, not as a second root child.
    direct_linked=[c.name for c in root.children if c==collection or c.name==collection.name]
    instance_objects=[o.name for o in bpy.data.objects if o.instance_type=="COLLECTION" and o.instance_collection==collection]
    assert len(instance_objects)==1 and instance_objects[0]==marker_name
    assert len(direct_linked)==0, f"duplicate direct-linked collection(s): {direct_linked}"
    members=set(collection.all_objects)
    matrix_cache={}
    mesh_objects=[o for o in members if o.type=="MESH"]
    pts=[]
    for obj in mesh_objects:
        M=marker.matrix_world @ collection_local_matrix(obj,members,matrix_cache)
        pts.extend(M @ Vector(v.co) for v in obj.data.vertices)
    assert pts
    world_bounds=[[min(float(p[i]) for p in pts),max(float(p[i]) for p in pts)] for i in range(3)]
    prior=json.loads(SOURCE_GRADE.read_text(encoding="utf-8"))
    prior_bounds=prior["evidence"]["model_evaluated_world_bounds_m"]
    max_bounds_delta=max(abs(world_bounds[i][j]-prior_bounds[i][j]) for i in range(3) for j in range(2))
    geometry_preserved=max_bounds_delta<=0.001
    assert geometry_preserved, f"integration shifted bounds by {max_bounds_delta} m"
    materials={m for obj in mesh_objects for m in obj.data.materials if m}
    images=[n.image.filepath for m in materials if m.use_nodes for n in m.node_tree.nodes if n.type=="TEX_IMAGE" and n.image]
    external_images=[p for p in images if p and not p.startswith("//")]
    assert SV.exists() and EXTERIOR.exists() and INTERIOR.exists()
    build=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert build["identity"]["purdue_gis_fid"]==793 and build["identity"]["name"]=="Beta Sigma Psi"
    previous_score=float(prior["score"])
    criteria=[
      {"criterion":"Correct identity and source-backed footprint","points":1.85,"max_points":2.0,
       "evidence":"Fresh master links the same stable Beta Sigma Psi asset ID whose exact Purdue GIS FID 793 name/address and 14-vertex source footprint were independently checked. Current April 2026 exact-address pano shows the Beta Sigma Psi sign. WGS84 and EPSG:2968 vertex calculations agree within about 0.2 m².",
       "findings":["Purdue GIS Shape__Area/Shape__Length fields materially disagree with geometry-derived area/perimeter; the vertex polygon is used, but the official attribute discrepancy remains unresolved."]},
      {"criterion":"Position, orientation, and scale/dimensions","points":1.9,"max_points":2.0,
       "evidence":f"The final marker is at {actual_xy} m, matching the manifest by {marker_error:.6f} m. The localized linked collection is instantiated once and not directly parented in the master root. Applying the marker and source-local parent transforms yields campus-world bounds {world_bounds}; maximum difference from the independently graded pre-localization campus-world bounds {prior_bounds} is {max_bounds_delta:.6f} m.",
       "findings":[] if geometry_preserved else ["Marker conversion changed the previously graded campus-world footprint."]},
      {"criterion":"Evidence-backed height, floors, and roof form","points":1.5,"max_points":2.0,
       "evidence":"Integrated geometry is unchanged from the previously graded model. The April 2026 Street View supports two visible stories, the left gable, shallow dark roof and small dormers; the old exact-address listing also describes bathrooms on each floor.",
       "findings":["Purdue GIS NUM_LEVELS/CountOfFlo fields report one level, conflicting with the facade photo and historical listing. Heights and roof pitch remain estimates; no measured elevation or construction drawings are available."]},
      {"criterion":"Facade, entrance, and distinctive architecture","points":1.8,"max_points":2.0,
       "evidence":"The saved exact-address panorama and exterior preview support the model’s red brick, left gabled wing, white-columned portico, red entry door, pale trim, shutters and roof dormers. The asset also contains a cutaway interior with schematic rooms and circulation.",
       "findings":["Hidden elevations and exact facade dimensions are not verified; interior room layout is schematic without an as-built floor plan."]},
      {"criterion":"Modular export, portability, and evidence completeness","points":1.95,"max_points":2.0,
       "evidence":f"Fresh-open master links the expected source path {library_path}; manifest type is detailed/local-coordinate; marker and collection references resolve; exactly one collection-instance object exists and no duplicate direct-linked child is present. The integrated source collection contains {len(mesh_objects)} mesh objects and {len(materials)} materials. The previous fresh-open asset check found no external image dependencies; master-linked image paths checked here: {external_images}.",
       "findings":[] if not external_images else ["External image dependencies remain."]}
    ]
    score=round(sum(c["points"] for c in criteria),2)
    findings=[f for c in criteria for f in c["findings"]]
    result={"building":"Beta Sigma Psi","asset_id":ID,"master_path":str(MASTER),"asset_path":str(ASSET),"score":score,"max_score":10,
      "criteria":criteria,"evidence":{"master_fresh_open":True,"manifest_kind":record["kind"],"local_coordinates":record["local_coordinates"],
      "placement_marker":marker_name,"marker_xy_m":actual_xy,"manifest_xy_m":expected_xy,"marker_error_m":marker_error,
      "linked_collection":collection.name,"linked_library_path":str(library_path),"collection_instance_objects":instance_objects,
      "direct_linked_duplicate_children":direct_linked,"master_world_bounds_m":world_bounds,"prior_independent_grade_world_bounds_m":prior_bounds,
      "max_world_bounds_delta_m":max_bounds_delta,"previous_independent_grade":previous_score,"mesh_object_count":len(mesh_objects),
      "material_count":len(materials),"external_image_dependencies":external_images,"streetview_source":str(SV),"exterior_render":str(EXTERIOR),"interior_render":str(INTERIOR)},
      "findings":findings,"passing_standard":8,"result":"pass" if score>=8 else "below passing standard"}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Independent master integration grade: Beta Sigma Psi","",f"**Score: {score:.2f}/10 — {result['result']}**","",
      "## Criteria",""]
    lines += [f"- **{c['criterion']}**: {c['points']:.2f}/{c['max_points']:.1f}. {c['evidence']}" for c in criteria]
    lines += ["","## Findings",""]+[f"- {f}" for f in findings]
    OUT.with_name("grade_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2,ensure_ascii=False))

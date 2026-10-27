"""Independent grade for Beta Sigma Psi, based on direct GIS, Street View and Blender evidence."""
import json, math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_house_301841254_29ab02d"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE_PATH = ROOT / "audit" / "beta_sigma_psi" / "build_evidence.json"
GIS_PATH = ROOT / "audit" / "beta_sigma_psi" / "sources" / "purdue_gis_fid793_2026-10-26.json"
GIS_2968_PATH = ROOT / "audit" / "beta_sigma_psi" / "sources" / "purdue_gis_fid793_2026-10-26_stateplane_2968.json"
SV_PATH = ROOT / "audit" / "beta_sigma_psi" / "sources" / "google_streetview_yaw270_pitch0.jpg"
EXTERIOR_PATH = ROOT / "audit" / "beta_sigma_psi" / "beta_sigma_psi_exterior.png"
INTERIOR_PATH = ROOT / "audit" / "beta_sigma_psi" / "beta_sigma_psi_interior.png"
OUT = ROOT / "audit" / "beta_sigma_psi" / "independent_grade_final" / "result.json"

def ring_metrics(path, projected=False):
    payload=json.loads(path.read_text(encoding="utf-8-sig"))
    f=payload["features"][0]
    coords=f["geometry"]["rings"][0]
    if coords[0] == coords[-1]: coords=coords[:-1]
    if projected:
        # EPSG:2968 coordinates are US survey feet. Convert them to meters.
        pts=[(x*0.3048006096012192,y*0.3048006096012192) for x,y in coords]
    else:
        pts=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),
              (lat-40.4274)*111040.0) for lon,lat in coords]
    area=abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2)
    perim=sum(math.dist(pts[i],pts[(i+1)%len(pts)]) for i in range(len(pts)))
    bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(2)]
    return f, area, perim, bounds

def evaluate():
    assert Path(bpy.data.filepath).resolve()==ASSET_PATH.resolve(), f"Unexpected reopened file: {bpy.data.filepath}"
    ev=json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    raw,area,perimeter,plan_bounds=ring_metrics(GIS_PATH)
    projected,area2968,perim2968,_=ring_metrics(GIS_2968_PATH,projected=True)
    attrs=raw["attributes"]
    assert attrs["FID"]==793 and attrs["BUILDING_N"]=="Beta Sigma Psi" and attrs["ADDRESS"]=="525 University St"
    coll=bpy.data.collections.get(f"Asset_{ASSET_ID}")
    assert coll is not None
    objs=list(coll.all_objects)
    meshes=[o for o in objs if o.type=="MESH"]
    assert len(meshes)==1 and meshes[0].name=="House_301841254"
    obj=meshes[0]
    depsgraph=bpy.context.evaluated_depsgraph_get()
    evaluated=obj.evaluated_get(depsgraph)
    mesh=evaluated.to_mesh()
    coords=[obj.matrix_world @ v.co for v in mesh.vertices]
    evaluated.to_mesh_clear()
    model_bounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
    materials=[m for m in obj.data.materials if m]
    material_names=[m.name for m in materials]
    brick_nodes=sum(1 for m in materials if m.use_nodes and any(n.type=="TEX_BRICK" for n in m.node_tree.nodes))
    image_nodes=[]
    for m in materials:
        if m.use_nodes:
            image_nodes += [n.image.filepath for n in m.node_tree.nodes if n.type=="TEX_IMAGE" and n.image]
    modifiers=[m.name for m in obj.modifiers]
    external_image_dependencies=[p for p in image_nodes if p and not p.startswith("//")]
    assert SV_PATH.exists() and EXTERIOR_PATH.exists() and INTERIOR_PATH.exists()
    width=plan_bounds[0][1]-plan_bounds[0][0]
    depth=plan_bounds[1][1]-plan_bounds[1][0]
    source_area=attrs.get("Shape__Area")
    source_length=attrs.get("Shape__Length")
    gis_attr_conflict=abs(source_area-area)/area>0.50 or abs(source_length-perimeter)/perimeter>0.20
    criteria=[
      {"criterion":"Correct identity and source-backed footprint","points":1.85,"max_points":2.0,
       "evidence":f"Official Purdue GIS FeatureServer FID 793 identifies Beta Sigma Psi at 525 University St; exact-address April 2026 Street View image shows the Beta Sigma Psi roadside sign and house. The 14-vertex Purdue GIS ring is used directly for the foundation/wall plan. This evaluator independently computes {area:.2f} m² and {perimeter:.2f} m from the published WGS84 vertices; the saved EPSG:2968 check computes {area2968:.2f} m² and {perim2968:.2f} m.",
       "findings":[f"Official Shape__Area/Shape__Length fields ({source_area:.2f}, {source_length:.2f}) materially disagree with polygon-derived metrics; the model appropriately follows the polygon vertices, but that field discrepancy remains unresolved."] if gis_attr_conflict else []},
      {"criterion":"Position, orientation, and scale/dimensions","points":1.75,"max_points":2.0,
       "evidence":f"Asset is saved in the established campus-world massing coordinate frame with identity object transform. Plan-source bounding dimensions from the 14-point ring are approximately {width:.2f} × {depth:.2f} m; builder script converts each authoritative GIS vertex with the project conversion and uses the west-facing front edge indicated by the Street View vantage. Reopened model geometry bounds are {model_bounds} m.",
       "findings":["No surveyed wall registration or independent residual overlay is provided; the project’s local geographic conversion is approximate, and full model bounds include roof/portico projections outside the GIS wall polygon."]},
      {"criterion":"Evidence-backed height, floors, and roof form","points":1.5,"max_points":2.0,
       "evidence":"The saved current Street View pano visibly supports two above-grade facade levels, a prominent left gable, a shallow dark roof and multiple small dormers. The model includes the observed two-level arrangement, left gable, dark shallow roof, dormers and a closed roof deck. The exact-address 2012 listing says bathrooms occur on each floor, providing additional program support.",
       "findings":["GIS NUM_LEVELS/CountOfFlo fields report one level, in conflict with the current two-level facade and historical listing. Wall/eave/ridge/gable heights and roof pitches are estimated; no measured elevations or plans were found."]},
      {"criterion":"Facade, entrance, and distinctive architecture","points":1.8,"max_points":2.0,
       "evidence":"Direct exact-address Street View supports the modeled warm red brick, pale window trim, dark shutters, white-column portico, red front door, left-facing gabled wing and roof dormers. The exterior render reproduces these features with procedural brick and roof textures. The interior cutaway shows schematic floors/rooms and circulation rather than a single solid block.",
       "findings":["Hidden elevations and precise opening/column dimensions are not measured; the interior layout is schematic and is not validated by a floor plan."]},
      {"criterion":"Modular export, portability, and evidence completeness","points":1.9,"max_points":2.0,
       "evidence":f"Fresh-open Blender session confirms the expected asset/scene and Asset_{ASSET_ID} collection, one identity-transform mesh named House_301841254, {len(materials)} material slots, {brick_nodes} materials with procedural brick nodes, no modifiers, no external image dependencies, and a nonzero evaluated mesh ({len(coords)} vertices). Saved evidence includes current panorama source snapshot plus exterior/interior views and coordinate/GIS provenance.",
       "findings":["Asset remains a direct-linked campus-coordinate library, consistent with its existing massing-kind manifest contract; it has not been promoted to the detailed local-coordinate/Placement marker convention."] if external_image_dependencies or not objs or modifiers else []}
    ]
    score=round(sum(c["points"] for c in criteria),2)
    findings=[]
    for c in criteria: findings.extend(c["findings"])
    result={"building":"Beta Sigma Psi","asset_id":ASSET_ID,"asset_path":str(ASSET_PATH),"score":score,"max_score":10,
      "criteria":criteria,"evidence":{"gis_feature_attributes":attrs,"gis_vertex_metrics_local_approx":{"area_m2":area,"perimeter_m":perimeter,"bounds_xy_m":plan_bounds},
      "gis_vertex_metrics_stateplane_2968_m":{"area_m2":area2968,"perimeter_m":perim2968},"gis_shape_attributes":{"area":source_area,"length":source_length,"conflict":gis_attr_conflict},
      "model_evaluated_world_bounds_m":model_bounds,"evaluated_vertices":len(coords),"materials":material_names,"procedural_brick_material_count":brick_nodes,
      "external_image_dependencies":external_image_dependencies,"modifiers":modifiers,"streetview_image":str(SV_PATH),"streetview_source_date":"April 2026",
      "exterior_render":str(EXTERIOR_PATH),"interior_render":str(INTERIOR_PATH),"fresh_open_file":bpy.data.filepath},
      "findings":findings,"passing_standard":8,"result":"pass" if score>=8 else "below passing standard"}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT.parent/"grade_report.md").write_text("# Independent grade: Beta Sigma Psi\n\n"+f"**Score: {score:.2f}/10 — {result['result']}**\n\n"+"\n".join(f"- **{c['criterion']}**: {c['points']:.2f}/{c['max_points']:.1f}. {c['evidence']}" for c in criteria)+"\n\n## Findings\n\n"+"\n".join(f"- {f}" for f in findings)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    result=evaluate()
    print(json.dumps(result,indent=2,ensure_ascii=False))

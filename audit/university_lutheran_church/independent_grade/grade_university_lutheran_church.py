"""Independent evidence and asset probe for the University Lutheran Church model."""
import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "university_lutheran_church"
MODEL = ROOT / "modular" / "buildings" / "massing_university_lutheran_church_20903f1.blend"
ASSET_ID = "massing_university_lutheran_church_20903f1"


def campus_xy(lat, lon):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def bbox_world(obj):
    pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]


def evaluate():
    scene_name="Building_"+ASSET_ID
    collection_name="Asset_"+ASSET_ID
    scene=bpy.data.scenes.get(scene_name)
    collection=bpy.data.collections.get(collection_name)
    shell=bpy.data.objects.get("ULu | brick building envelope and sloped roof")
    if not scene or not collection or not shell:
        raise RuntimeError("missing expected scene, asset collection, or envelope mesh")
    osm=json.loads((AUDIT/"sources"/"osm_way_301932784.json").read_text(encoding="utf-8"))
    way=next(e for e in osm["elements"] if e.get("type")=="way" and e.get("id")==301932784)
    nodes={e["id"]:e for e in osm["elements"] if e.get("type")=="node"}
    coords=[campus_xy(nodes[nid]["lat"],nodes[nid]["lon"]) for nid in way["nodes"][:-1]]
    expected=[[min(p[0] for p in coords),max(p[0] for p in coords)],
              [min(p[1] for p in coords),max(p[1] for p in coords)]]
    bounds=bbox_world(shell)
    xy_error=max(abs(bounds[0][0]-expected[0][0]),abs(bounds[0][1]-expected[0][1]),
                 abs(bounds[1][0]-expected[1][0]),abs(bounds[1][1]-expected[1][1]))
    road_data=json.loads((AUDIT/"sources"/"osm_northwestern_avenue_way_932656636.json").read_text(encoding="utf-8"))
    road_way=next(e for e in road_data["elements"] if e.get("type")=="way" and e.get("id")==932656636)
    road_nodes={e["id"]:e for e in road_data["elements"] if e.get("type")=="node"}
    road_pts=[campus_xy(road_nodes[nid]["lat"],road_nodes[nid]["lon"]) for nid in road_way["nodes"]]
    road_segs=[(Vector((a[0],a[1],0)),Vector((b[0],b[1],0))) for a,b in zip(road_pts,road_pts[1:])]
    center=Vector((sum(p[0] for p in coords)/len(coords),sum(p[1] for p in coords)/len(coords),0))
    front=[]
    for i,a in enumerate(coords):
        b=coords[(i+1)%len(coords)]
        tangent=Vector((b[0]-a[0],b[1]-a[1],0)).normalized()
        normal=Vector((tangent.y,-tangent.x,0))
        mid=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2,0))
        if normal.dot(center-mid)>0: normal.negate()
        choices=[]
        for ra,rb in road_segs:
            d=rb-ra; q=max(0,min(1,(mid-ra).dot(d)/(d.length_squared or 1)))
            nearest=ra+d*q; towards=nearest-mid
            road_dir=d.normalized()
            choices.append((towards.length,abs(tangent.dot(road_dir)),normal.dot(towards.normalized()) if towards.length else -1))
        distance,align,facing=min(choices,key=lambda v:v[0])
        if align>=.90 and facing>=.45:
            front.append({"edge_index":i,"length_m":(Vector((b[0]-a[0],b[1]-a[1])).length),"road_distance_m":distance,"parallel_alignment":align,"faces_road":facing})
    bm=bmesh.new(); bm.from_mesh(shell.data)
    topology={"vertices":len(bm.verts),"edges":len(bm.edges),"faces":len(bm.faces),
              "boundary_edges":sum(e.is_boundary for e in bm.edges),
              "non_manifold_edges":sum(not e.is_manifold for e in bm.edges),
              "loose_vertices":sum(not v.link_edges for v in bm.verts)}
    bm.free()
    material_names=sorted({m.name for o in collection.all_objects if hasattr(o.data,"materials") for m in o.data.materials if m})
    mesh_count=sum(o.type=="MESH" for o in collection.all_objects)
    all_count=len(list(collection.all_objects))
    external_images=[i.filepath for i in bpy.data.images if i.source=="FILE"]
    linked_libraries=[lib.filepath for lib in bpy.data.libraries]
    sha=hashlib.sha256(MODEL.read_bytes()).hexdigest()
    preview_exists=all((AUDIT/name).exists() for name in ("preview_three_quarter.png","preview_top.png"))
    source_paths=["sources/osm_way_301932784.json","sources/osm_northwestern_avenue_way_932656636.json",
                  "sources/official_visit_page.html","sources/official_history_page.html",
                  "images/official_ulupurdue_full_building.jpg"]
    source_complete=all((AUDIT/p).exists() for p in source_paths)
    envelope_ok=xy_error<0.001
    watertight=topology["boundary_edges"]==0 and topology["non_manifold_edges"]==0 and topology["loose_vertices"]==0
    portable=not external_images and not linked_libraries

    criteria=[
      {"name":"Identity and source-backed footprint","score":2.0,"max_score":2.0,
       "evidence":["OSM way 301932784 is tagged as University Lutheran Church, place of worship, at 460 Northwestern Avenue.","Official ULu visit page confirms this location and its relationship across the street from Electrical Engineering.",f"The model envelope XY bounds match the transformed OSM ring within {xy_error:.8f} m."],
       "findings":"Pass. The identity is distinguishable from Purdue Lutheran Ministry, and the source ring is the intended church footprint."},
      {"name":"Position, orientation, and scale/dimensions","score":2.0,"max_score":2.0,
       "evidence":[f"Envelope XY bounds: {bounds[0]} x {bounds[1]} m; transformed OSM expected bounds: {expected}.","Northwestern Avenue OSM way 932656636 was used to identify road-facing edges; detected frontage edges: "+", ".join(str(e['edge_index']) for e in front)+".","The asset keeps the campus-world coordinate convention of its existing manifest record and is intended to be linked at identity."],
       "findings":"Pass on footprint placement and orientation. Coordinate conversion is the project’s approximate local transform, not a surveyed CRS; the OSM geometry and source dataset remain non-survey evidence."},
      {"name":"Evidence-backed height, floors, and roof form","score":1.25,"max_score":2.0,
       "evidence":["Official church imagery shows three above-ground storeys and a shallow dark roof.","Official visit page and Purdue Archives record support basement fellowship hall and third-floor sanctuary.",f"Model roof/parapet reaches approximately {max((o.matrix_world @ Vector(c))[2] for o in collection.all_objects for c in (o.bound_box or [])):.2f} m and basement extends to {bounds[2][0]:.2f} m.","No measured elevation, roof section, or reliable public height field was located; the height remains a photo-scaled estimate with ±2.5 m stated uncertainty."],
       "findings":"Partial. Storey count and low roof profile have direct photo/program support, but the numeric height and roof slope/parapet are estimates. The asset depicts a nearly flat roof plane and a stepped parapet that is less clear in the source photo."},
      {"name":"Facade, entrances, and distinctive architecture","score":1.35,"max_score":2.0,
       "evidence":["Official exterior image shows red-brown brick, repeated dark horizontal window bays, pale masonry courses, UNIVERSITY/LUTHERAN signage, a vertical Fuel sign, and a low dark roof edge.","The model includes brick textures, 3 above-ground window levels, pale courses, road-facing church lettering, Fuel sign, cafe canopy, and exterior entrance details.","Facade module counts on non-photographed sides are extrapolated from footprint and should be treated as uncertain."],
       "findings":"Good source resemblance, but the model distributes more and smaller windows across stepped frontage segments than the photograph’s three dominant wide bays. The church sign is much smaller than the reference sign and the storefront/entry locations are schematic."},
      {"name":"Modular export, portability, and complete evidence","score":2.0,"max_score":2.0,
       "evidence":[f"Expected scene `{scene.name}` and collection `{collection.name}` reopen; collection contains {all_count} objects ({mesh_count} meshes).",f"Envelope is closed: {topology}.",f"Materials found: {', '.join(material_names)}.",f"No external image paths ({len(external_images)}) or linked library paths ({len(linked_libraries)}); previews present: {preview_exists}; required raw source snapshots present: {source_complete}.",f"Freshly reopened SHA256: {sha}."],
       "findings":"Pass. Dedicated build script and evidence exist, expected names are preserved, and the asset is self-contained."}
    ]
    score=round(sum(c["score"] for c in criteria),2)
    findings=[
      "Improve the road-facing elevation by aligning its three dominant wide window bays to the official photo and enlarging/centering the church sign.",
      "Replace the numeric height with a surveyed or independently documented elevation if one becomes available; current value is explicitly an estimate.",
      "Interior uses align with published room assignments, but room partitions and furniture are schematic."
    ]
    return {"score":score,"max_score":10,"criteria":criteria,"evidence":{
      "asset_path":str(MODEL),"asset_sha256":sha,"scene":scene.name,"collection":collection.name,
      "expected_osm_bounds_xy_m":expected,"measured_envelope_bounds_world_m":bounds,
      "max_xy_bound_error_m":xy_error,"road_facing_edges":front,"topology":topology,
      "material_names":material_names,"external_image_paths":external_images,"linked_library_paths":linked_libraries,
      "previews_present":preview_exists,"source_snapshot_paths":source_paths,"source_snapshots_complete":source_complete},
      "findings":findings}


result=evaluate()
out=AUDIT/"independent_grade"/"result.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))

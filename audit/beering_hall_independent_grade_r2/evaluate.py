from pathlib import Path
import json, subprocess
PROJECT = Path(__file__).resolve().parents[2]
GRADE = PROJECT / "audit/beering_hall_independent_grade_r2"
BLENDER = PROJECT.parent / "blender/blender-4.5.15-windows-x64/blender.exe"

def evaluate(run_blender=True):
    if run_blender:
        p = subprocess.run([str(BLENDER), "--background", "--python", str(GRADE/"blender_probe.py")],
                           cwd=PROJECT, capture_output=True, text=True, timeout=240)
        (GRADE/"blender_probe.log").write_text(p.stdout + p.stderr, encoding="utf-8")
        if p.returncode:
            raise RuntimeError("Blender probe failed; see blender_probe.log")
    model=json.loads((GRADE/"blender_probe.json").read_text(encoding="utf-8"))
    export=json.loads((GRADE/"export_probe.json").read_text(encoding="utf-8"))
    src=json.loads((PROJECT/"audit/beering_hall/purdue_gis_feature_251.json").read_text(encoding="utf-8"))
    record=json.loads((PROJECT/"audit/beering_hall/source_record.json").read_text(encoding="utf-8"))
    manifest=json.loads((PROJECT/"modular/manifest.json").read_text(encoding="utf-8"))
    entry=next(x for x in manifest["assets"] if x["id"]=="beering_hall")
    feature=src["features"][0]
    props=feature["properties"]
    assert feature["id"]==251 and props["BLDG_ABBR"]=="BRNG"
    assert props["BUILDING_N"].startswith("Steven C. Beering Hall")
    assert props["ADDRESS"]=="100 N University Street"
    assert model["collection"]==entry["collection"]=="Asset_beering_hall"
    assert model["scene"]=="Building_beering_hall"
    assert export["object_count"]==model["collection_object_count"]
    dims=model["structural_wall_bounds_local_m"][:2]
    source=model["gis_ring_local_bounds_m"]
    ds=[abs((dims[i][1]-dims[i][0])-(source[i][1]-source[i][0])) for i in range(2)]
    room=model["roof_room_xy_center_local_m"]
    previous=json.loads((PROJECT/"audit/beering_hall/reopen_validation.json").read_text(encoding="utf-8"))
    tower=previous["structural_wall_bounds_local_m"]["BRNG_Office_Tower_Masonry"]
    on_tower=tower[0][0] <= room[0] <= tower[0][1] and tower[1][0] <= room[1] <= tower[1][1]
    assert on_tower
    criteria=[
      {"criterion":"Correct identity and source-backed footprint","score":1.4,"max_score":2,
       "evidence":["Purdue GIS feature 251 matches BRNG, the full Beering Hall name, and 100 N University Street.",
         "The 51-point converted GIS envelope and two masonry masses differ by %.2f m and %.2f m in their bounding dimensions." % (ds[0],ds[1]),
         "The GIS ring includes a curved southern frontage that the rectilinear structural wall masses do not represent or verify vertex-by-vertex."],
       "findings":["Identity and overall envelope are supported; the irregular detailed footprint remains approximated."]},
      {"criterion":"Position, orientation, and scale/dimensions","score":1.6,"max_score":2,
       "evidence":["The library preserves its manifest local frame and origin %s m." % entry["placement_origin_xy_m"],
         "The wall-envelope bbox center differs from the GIS bbox center by %.2f m; the greatest bounding dimension delta is %.2f m." % (model["bbox_center_error_m"],max(ds)),
         "The tower and wing follow the cardinal orientation of the GIS footprint; the master Placement marker was not reopened."],
       "findings":["Horizontal registration is close at the envelope level, but exact perimeter fit and master-marker placement are unverified."]},
      {"criterion":"Evidence-backed height, floors, and roof form","score":1.5,"max_score":2,
       "evidence":["Purdue GIS reports NUM_LEVELS=%s and CountOfFLO=%s, but these fields do not establish measured floor elevations." % (props.get("NUM_LEVELS"),props.get("CountOfFLO")),
         "The reopened model is %.2f m tall. GIS R=%s and Extrution=%s have undocumented units/semantics; height remains an estimate." % (model["overall_asset_bounds_local_m"][2][1],props.get("R"),props.get("Extrution")),
         "The source photo supports a white ring-like rooftop room with vertical openings. The current room is centered at %s m on top of the tall office-tower mass; its exact dimensions and elevation are not measured." % room],
       "findings":["The signature roof form and location are now photo-supported; total height, floor datums, current roof construction, and rooftop-room dimensions remain uncertain."]},
      {"criterion":"Facade, entrances, and distinctive architecture","score":1.7,"max_score":2,
       "evidence":["The model has brick masonry, varied glazing, and five photo-interpreted tall glazing bays; the Purdue oblique image supports brick, vertical glazing, and the white rooftop ring.",
         "The overview and close render show the corrected shallow white annular room atop the high tower, matching the photo more closely than the previous green dome on the lower wing.",
         "The west entrance dimensions and most other elevations are not verified by the available oblique photo."],
       "findings":["The distinctive roof form and some glazing now match evidence; the entrance and unseen facades remain qualitative."]},
      {"criterion":"Modular export, portability, and complete evidence","score":1.8,"max_score":2,
       "evidence":["Blender %s reopened the expected scene/collection with %s objects." % (model["blender_version"],model["collection_object_count"]),
         "A collection-only export reopened with %s objects; no cameras/lights, external images, or linked libraries are present." % export["object_count"],
         "The dedicated builder, raw GIS snapshot, Purdue photo, provenance, reopen validation, and renders are saved for this building.",
         "The shared manifest still lists %s objects/names versus %s in the reopened collection." % (model["manifest_object_count"],model["collection_object_count"])],
       "findings":["The asset is portable and reproducible. The coordinator should refresh the shared manifest object list/count before integration."]},
    ]
    score=round(sum(c["score"] for c in criteria),2)
    result={"building_id":"beering_hall","score":score,"max_score":10,"pass_threshold":8,
      "passed":score>=8,"criteria":criteria,
      "evidence":{"asset_path":"modular/buildings/beering_hall.blend",
        "asset_sha256":model["asset_sha256"],"builder_script":"modular/buildings/build_beering_hall.py",
        "source_record":"audit/beering_hall/source_record.json","gis_feature_id":251,
        "gis_attributes":{k:props.get(k) for k in ["BLDG_ABBR","BUILDING_N","ADDRESS","NUM_LEVELS","CountOfFLO","Extrution","R"]},
        "gis_local_bounds_m":source,"structural_wall_bounds_local_m":dims,
        "bounding_dimension_delta_m":ds,"bbox_center_error_m":model["bbox_center_error_m"],
        "overall_asset_bounds_local_m":model["overall_asset_bounds_local_m"],
        "roof_room_bounds_local_m":model["roof_room_bounds_local_m"],
        "roof_room_center_over_tower":on_tower,"asset_object_count":model["collection_object_count"],
        "manifest_object_count":model["manifest_object_count"],"export_object_count":export["object_count"],
        "external_image_dependencies":model["external_image_dependencies"],"linked_libraries":model["linked_libraries"],
        "preview":"audit/beering_hall/beering_hall_repaired_preview.png",
        "roof_detail":"audit/beering_hall/beering_hall_rooftop_room_detail.png",
        "official_photo":"audit/beering_hall/purdue_college_of_education_beering_exterior.jpg"},
      "findings":["The white annular room is now on the high tower and visually supported by the Purdue exterior photo.",
        "The GIS supports identity, plan envelope, cardinal orientation, and a nine-level attribute, but not exact curved walls or measured height.",
        "The coordinator-owned manifest object names/count are stale and need synchronization before integration."]}
    (GRADE/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2,ensure_ascii=False))

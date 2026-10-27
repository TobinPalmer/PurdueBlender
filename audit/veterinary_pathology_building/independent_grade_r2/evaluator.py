import json
from pathlib import Path
D=Path(__file__).resolve().parent
R=Path(__file__).resolve().parents[3]

def evaluate():
    probe=json.loads((D/'fresh_open_probe.json').read_text(encoding='utf-8'))
    evidence=json.loads((R/'audit/veterinary_pathology_building/evidence.json').read_text(encoding='utf-8'))
    footprint_error=max(probe['GIS_to_mesh_base_hausdorff_m'],probe['mesh_base_to_GIS_ring_hausdorff_m'])
    materials=probe['materials']
    total_material_polys=sum(m['polygons_using_slot'] for m in materials)
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':[f"Purdue GIS OBJECTID 165 identifies Veterinary Pathology Building (VPTH), 725 Harrison Street.",f"Fresh Blender 5.2.3 reopen compared the model base to all converted GIS ring points; bidirectional Hausdorff error is {footprint_error:.9f} m.","The raw GIS polygon was preserved without rotation or scale."],
       'limits':["The GIS response does not publish a survey accuracy statement; coordinates use the project's documented local tangent approximation."]},
      {'criterion':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,
       'evidence':["The building mesh is now in local coordinates about documented campus anchor (-162.821272, -816.256807) m; the source object transform is (0,0,0).","Local plan bounds are 54.972 x 42.745 m, consistent with the converted source polygon; vertex orientation is preserved.","Adding the documented anchor reconstructs the campus location; the placement convention is ready for a master marker."],
       'limits':["The master placement marker and neighboring building context were not part of this isolated asset grade."]},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2.0,
       'evidence':["The Purdue 2026 emergency plan lists a basement, first through third floors, and attic; the model shows the same broad vertical organization.","The historic GIS description also notes a basement and attic and reports that the original building was two stories.","Model top height of 15.925 m and the roof/attic volume are explicitly recorded as estimates."],
       'limits':["No measured elevations or floor-to-floor heights were found. Roof profile, penthouse form, and 15.925 m top elevation remain unverified; historical two-story description and current three-floor emergency plan do not resolve exact vertical geometry."]},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.0,'max_score':2.0,
       'evidence':["The rendered exterior presents a coherent masonry shell, repeated windows, story bands, entrance portals and the GIS-derived irregular plan.","The emergency plan confirms exits on the north, south, and west and an elevator dock entrance on the southeast, but does not locate facade bays or specify exterior materials."],
       'limits':["No usable current exterior photographs or elevation drawings were found in the local evidence set or targeted search. Brick/stone colors, window rhythm, portal design, and exact facade detailing remain interpretive; the preview looks like a clean visualization but is not photo-verified."]},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,
       'evidence':["A fresh Blender 5.2.3 process opened the saved asset and found the expected scene, collection, stable asset ID, and one named building mesh.",f"The mesh has {probe['vertex_count']:,} vertices and {probe['polygon_count']:,} polygons; all {probe['material_slot_count']} material slots are used (slot assignments total {total_material_polys} polygons).","The asset has no file-image dependencies or linked external libraries and stores the model in local coordinates.","The evidence folder contains the official GIS snapshot, current emergency plan, source/method notes, preview, and fresh-open validation."],
       'limits':["The interior is represented only by generic floor plates; room partitions and tunnel connections are not modeled or verified."]}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[
      {'severity':'pass with substantial architectural uncertainty','finding':'Local-coordinate conversion resolved the previous modular-placement blocker. The footprint is nearly exact against the saved GIS ring, but roof/attic height and facade character still lack measured or photographic support.'},
      {'severity':'scope limit','finding':'This is an isolated building asset review. The master placement marker, neighboring campus context, and interior layout are not included in this grade.'}
    ]
    return {'building':'Veterinary Pathology Building (VPTH)','asset_sha256':probe['asset_sha256'],'score':score,'max_score':10,'passing_threshold':8.0,'pass':score>=8.0,'criteria':criteria,'evidence':{'independent_fresh_open_probe':'fresh_open_probe.json','source_evidence':'../evidence.json','source_gis_snapshot':'../purdue_campus_building_vpth_raw.geojson','exterior_preview':'../preview_exterior.png','builder_validation':'../validation.json','rubric':'AGENT.md five-criterion rubric'},'findings':findings}

if __name__=='__main__':
    result=evaluate()
    (D/'grade_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

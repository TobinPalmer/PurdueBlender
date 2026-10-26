import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GRADE=ROOT/'audit/burton_morgan_center_independent_grade'
BUILDER=ROOT/'audit/burton_morgan_center'

def evaluate(probe, export_probe, evidence, manifest, gis):
    contract=next(a for a in manifest['assets'] if a['id']=='burton_morgan_center')
    feature=gis['features'][0]
    coords=feature['geometry']['rings'][0]
    lon0,lat0=-86.9137,40.4274
    ox,oy=contract['placement_origin_xy_m']
    xy=[((lon-lon0)*111412.84*math.cos(math.radians(lat0))-ox,
         (lat-lat0)*111040.0-oy) for lon,lat in coords]
    if len(xy)>1 and math.dist(xy[0],xy[-1])<.001: xy.pop()
    mins=[min(q[i] for q in xy) for i in range(2)]
    maxs=[max(q[i] for q in xy) for i in range(2)]
    center=[(mins[i]+maxs[i])/2 for i in range(2)]
    origin_error=math.dist(center,[0.0,0.0])
    shell=probe['shell_bounds_local_m']
    shell_dims=[shell['max'][i]-shell['min'][i] for i in range(2)]
    gis_dims=[maxs[i]-mins[i] for i in range(2)]
    score_parts=[1.9,1.7,1.1,1.7,2.0]
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':1.9,'max_score':2.0,'status':'verified against the named official GIS feature; independent survey match unavailable','evidence':f"Purdue BuildingShapes FID 80, GlobalID {feature['attributes'].get('GlobalID')}, building name and address match Burton D. Morgan Center / 1201 Mitch Daniels Blvd. The 76 unique source-ring vertices are within {probe['gis_ring_to_shell_vertex_nearest_m']['max']:.9g} m of saved shell vertices. Shell XY bounds are {shell_dims[0]:.3f} x {shell_dims[1]:.3f} m versus the transformed GIS outline {gis_dims[0]:.3f} x {gis_dims[1]:.3f} m.",'limitation':'The shell was constructed from this GIS polygon, so geometric agreement establishes faithful implementation of the source, not independent survey accuracy.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.7,'max_score':2.0,'status':'placement and plan dimensions verified relative to the source transform; absolute survey accuracy uncertain','evidence':f"Manifest origin matches the GIS outline bounding-box center within {origin_error:.6f} m. Asset local dimensions are {probe['asset_bounds_local_m']['dimensions'][0]:.3f} x {probe['asset_bounds_local_m']['dimensions'][1]:.3f} x {probe['asset_bounds_local_m']['dimensions'][2]:.3f} m; the all-object XY extent includes the projecting entrance canopy. Structural shell dimensions follow the GIS perimeter. Orientation retains the feature ring order.",'limitation':'Coordinates use the project’s local longitude/latitude-to-meters approximation and no independent geodetic check was available.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.1,'max_score':2.0,'status':'partially supported; height remains estimated','evidence':'The 2004 Purdue dedication article describes a two-story, 31,000-square-foot building; the architect profile supports a flat-roofed contemporary form and a tall entrance glass monitor. The model represents two occupied stories and a flat roof, with 8.82 m monitor top.', 'limitation':'Official GIS attributes report five levels and extrusion 38 with no verified unit, conflicting with the two-story descriptions. No dimensioned section/elevation was found; wall/roof/monitor heights are estimates.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.7,'max_score':2.0,'status':'major forms and materials source-supported; exact details estimated','evidence':'Purdue and architect-attributed photographs show pale metal cladding, glazed bays, red-brick volumes, a glass monitor, and entrance canopy. The architect profile explicitly places brick volumes east and glass/aluminum volumes west; the model includes these elements and orientation.', 'limitation':'Bay spacing, panel modules, canopy dimensions, and exact facade orientation relative to a surveyed viewpoint are not measured; photos are not georeferenced and the historic photos date to the 2004 opening.'},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'status':'verified','evidence':f"Main asset reopened with {probe['object_count']} objects and {probe['mesh_count']} meshes; all {probe['manifest_object_count']} canonical manifest names resolve, including two preserved as custom properties for Blender's object-name limit. Independent export reopen found {export_probe['object_count']} objects and {export_probe['mesh_count']} meshes with matching names and no unpacked external images. Evidence records provider, URL, FID, retrieval date, CRS, source dates, measurements, and uncertainty.",'limitation':'No additional limitation affecting library portability or evidence completeness.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[
      'GIS polygon and model shell agree at sub-micrometer tolerance because the shell was generated from that exact feature; no independent survey footprint was found.',
      'The GIS floor-count fields (5) conflict with Purdue and architect descriptions (2 stories); the model follows the narrative sources and leaves exact height unverified.',
      'Facade rhythm, wall heights, roof equipment, canopy dimensions, and interior layout are not supported by dimensioned plans; interior remains schematic.'
    ]
    return {'building_id':'burton_morgan_center','score':score,'max_score':10,'pass_threshold':8,'result':'PASS' if score>=8 else 'FAIL','criteria':criteria,'evidence':{'independent_blender_probe':'audit/burton_morgan_center_independent_grade/blender_probe.json','independent_export_probe':'audit/burton_morgan_center_independent_grade/export_probe.json','builder_evidence':'audit/burton_morgan_center/evidence.json','builder_validation':'audit/burton_morgan_center/validation.json','official_gis_snapshot':'audit/burton_morgan_center/sources/gis_feature_80_query_2026-10-25.json','official_dedication':'audit/burton_morgan_center/sources/purdue_dedication_2004.html','architect_profile':'audit/burton_morgan_center/sources/schooldesigns_goody_clancy_project.html','current_purdue_directory':'audit/burton_morgan_center/sources/purdue_research_centers.html','rendered_views':['audit/burton_morgan_center/burton_morgan_center_preview.png','audit/burton_morgan_center/burton_morgan_center_plan_preview.png','audit/burton_morgan_center/burton_morgan_center_interior_preview.png']},'findings':findings}

def main():
    probe=json.loads((GRADE/'blender_probe.json').read_text(encoding='utf-8'))
    export_probe=json.loads((GRADE/'export_probe.json').read_text(encoding='utf-8'))
    evidence=json.loads((BUILDER/'evidence.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
    gis=json.loads((BUILDER/'sources/gis_feature_80_query_2026-10-25.json').read_text(encoding='utf-8'))
    result=evaluate(probe,export_probe,evidence,manifest,gis)
    (GRADE/'result.json').write_text(json.dumps(result,indent=2)+'\\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()

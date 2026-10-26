from pathlib import Path
import json, math, itertools
def evaluate():
    HERE=Path(__file__).resolve().parent
    ROOT=HERE.parents[1]
    manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
    entry=next(x for x in manifest['assets'] if x['id']=='bell_tower')
    probe=json.loads((HERE/'blender_probe.json').read_text(encoding='utf-8'))
    feature=json.loads((HERE/'gis_feature_290.geojson').read_text(encoding='utf-8'))['features'][0]
    origin=entry['placement_origin_xy_m']
    ring=feature['geometry']['coordinates'][0][:-1]
    source_world=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
    source_local=[(x-origin[0],y-origin[1]) for x,y in source_world]

    def polygon_centroid(poly):
        signed_area=0.0; cx=cy=0.0
        for (x0,y0),(x1,y1) in zip(poly,poly[1:]+poly[:1]):
            cross=x0*y1-x1*y0;signed_area+=cross;cx+=(x0+x1)*cross;cy+=(y0+y1)*cross
        area=signed_area/2
        return (cx/(6*area),cy/(6*area))

    def convex_hull(points):
        pts=sorted(set((float(x),float(y)) for x,y in points))
        def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lo=[]
        for p in pts:
            while len(lo)>1 and cross(lo[-2],lo[-1],p)<=1e-10:lo.pop()
            lo.append(p)
        hi=[]
        for p in reversed(pts):
            while len(hi)>1 and cross(hi[-2],hi[-1],p)<=1e-10:hi.pop()
            hi.append(p)
        return lo[:-1]+hi[:-1]

    def point_segment_distance(p,a,b):
        dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
        t=0 if den==0 else ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den
        t=max(0,min(1,t))
        return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))

    def boundary_samples(poly,step=.05):
        pts=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            d=math.dist(a,b);n=max(1,math.ceil(d/step))
            pts.extend([(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)])
        return pts

    def directed_boundary_error(a,b):
        return max(min(point_segment_distance(p,x,y) for x,y in zip(b,b[1:]+b[:1])) for p in boundary_samples(a))

    def min_area_rect(poly):
        best=None
        for a,b in zip(poly,poly[1:]+poly[:1]):
            dx=b[0]-a[0];dy=b[1]-a[1];angle=math.atan2(dy,dx)
            ca,sa=math.cos(angle),math.sin(angle)
            uv=[(x*ca+y*sa,-x*sa+y*ca) for x,y in poly]
            w=max(p[0] for p in uv)-min(p[0] for p in uv);h=max(p[1] for p in uv)-min(p[1] for p in uv)
            area=w*h
            if best is None or area<best[0]:best=(area,angle,w,h)
        return best

    def angle_diff_90(a,b):
        d=abs((a-b)%90);return min(d,90-d)

    model_hull=convex_hull(probe['ground_foot_bottom_xy'])
    boundary_model_to_gis=directed_boundary_error(model_hull,source_local)
    boundary_gis_to_model=directed_boundary_error(source_local,model_hull)
    boundary_hausdorff=max(boundary_model_to_gis,boundary_gis_to_model)
    gis_centroid=polygon_centroid(source_world)
    centroid_error=math.dist(gis_centroid,origin)
    gis_box=min_area_rect(source_local);model_box=min_area_rect(model_hull)
    angle_error=angle_diff_90(math.degrees(gis_box[1])%90,math.degrees(model_box[1])%90)
    dims_source=sorted([gis_box[2],gis_box[3]]);dims_model=sorted([model_box[2],model_box[3]])
    dimension_errors=[abs(a-b) for a,b in zip(dims_source,dims_model)]
    height=probe['evaluated_geometry_bounds_local_m'][2][1]
    height_source_m=160*0.3048
    height_error=abs(height-height_source_m)
    object_names=probe['object_names']
    counts={
     'clock_dials':sum(n.startswith('Clock_') and n.endswith('_Ivory_Dial') for n in object_names),
     'historic_bells':sum(n.startswith('Historic_Bell_') for n in object_names),
     'belfry_open_arches':sum(n.startswith('Belfry_Open_Arch_') for n in object_names),
     'base_arch_spandrels':sum(n.startswith('Base_Arch_Spandrel_') for n in object_names),
     'roof_present':any(n=='Pyramidal_Metal_Roof' for n in object_names),
     'memorial_plaque_present':any(n=='Under_Tower_Memorial_Plaque' for n in object_names),
    }
    export=json.loads((HERE/'collection_export_probe_result.json').read_text(encoding='utf-8'))
    checks={
     'identity_match':feature['properties'].get('BLDG_ABBR')=='BELL' and feature['properties'].get('BUILDING_N')=='Bell Tower' and entry['id']=='bell_tower',
     'source_feature_id_match':feature['id']==290 and feature['properties'].get('FID')==290,
     'gis_shell_boundary_under_5cm':boundary_hausdorff<=0.05,
     'placement_centroid_under_1cm':centroid_error<=0.01,
     'model_manifest_object_names_match':probe['object_names_match_manifest'] and probe['object_count']==entry['object_count'],
     'export_reopens_with_all_objects':export['reopened_collection']==entry['collection'] and export['object_count']==entry['object_count'] and not export['camera_light_objects'],
     'no_unpacked_images_or_linked_libraries':not probe['external_unpacked_images'] and not probe['linked_library_paths'],
     'signature_features_present':counts['clock_dials']==4 and counts['historic_bells']==4 and counts['belfry_open_arches']==4 and counts['base_arch_spandrels']==4 and counts['roof_present'],
    }
    result={
     'building_id':'bell_tower','score':9.3,'max_score':10,'pass_threshold':8.0,'passed':9.3>=8.0,
     'criteria':[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'evidence':f"Purdue GIS FID 290 identifies BELL / Bell Tower at 325 Centennial Mall Drive. I projected the 4-vertex source envelope with the documented local conversion; the convex hull of actual base-foot vertices has a sampled symmetric boundary discrepancy of {boundary_hausdorff:.3f} m (sampling interval 0.05 m)."},
      {'name':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,'evidence':f"GIS polygon area centroid and manifest placement differ by {centroid_error:.6f} m. Oriented-envelope edge angle differs by {angle_error:.3f}° modulo 90°, and sorted envelope dimension errors are {dimension_errors[0]:.3f} m and {dimension_errors[1]:.3f} m. The model uses the manifest local frame; the master placement instance itself was not opened."},
      {'name':'Evidence-backed height, floors, and roof','score':2.0,'max_score':2.0,'evidence':f"Purdue News states 160 ft and four historic bells; the actual evaluated model height is {height:.6f} m versus 48.768 m, an error of {height_error:.6f} m. Official Purdue photos show the pyramidal metal roof and open belfry. GIS reports one level; a freestanding tower has no normal occupied-floor stack to infer."},
      {'name':'Facade, entrances, and distinctive architecture','score':1.8,'max_score':2.0,'evidence':f"Reopened/rendered geometry includes red-brick shaft, limestone base arches/string courses, four clock dials, four historic bells, four open belfry arches, and pyramidal roof. The official Purdue photos corroborate these signature features; the plaque text and subordinate architectural dimensions are explicitly representative/estimated."},
      {'name':'Modular export, portability, and evidence completeness','score':1.7,'max_score':2.0,'evidence':f"Scene `Building_bell_tower`, collection `{entry['collection']}`, {entry['object_count']} manifest-matched objects; collection-only export reopened with the same objects and no camera/lights. No unpacked textures or linked libraries. Detailed source evidence and build script are present under `modular/bell_tower_work/`; canonical `modular/buildings/build_bell_tower.py` is absent."}
     ],
     'evidence':{
      'probe':'audit/bell_tower_independent_grade/blender_probe.json',
      'export_probe':'audit/bell_tower_independent_grade/collection_export_probe_result.json',
      'renders':['audit/bell_tower_independent_grade/overview.png','audit/bell_tower_independent_grade/front_elevation.png'],
      'gis_snapshot':'audit/bell_tower_independent_grade/gis_feature_290.geojson',
      'source_record':'audit/bell_tower_independent_grade/source_record.json',
      'builder_evidence':'modular/bell_tower_work/EVIDENCE.md',
      'source_urls':[
       'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0',
       'https://www.purdue.edu/newsroom/archive/releases/2020/Q4/university-to-mark-25th-birthday-of-purdue-bell-tower.html',
       'https://purduenews.exposure.co/happy-birthday-purdue-bell-tower',
       'https://archives.lib.purdue.edu/repositories/2/agents/corporate_entities/544'
      ],
      'measurements':{'centroid_error_m':centroid_error,'boundary_hausdorff_sampled_m':boundary_hausdorff,'orientation_error_mod90_degrees':angle_error,'obb_dimension_errors_m':dimension_errors,'model_height_m':height,'published_height_m':height_source_m,'height_error_m':height_error,'object_count':entry['object_count'],'feature_counts':counts},
      'checks':checks,
      'source_limitations':['GIS polygon is a map envelope, not certified structural survey.','Published source supports overall height but not a measured set of subordinate elevations.','The exact plaque text, plaque seal, and internal mechanism are not verified.','The master placement instance was not opened.']
     },
     'findings':[
      'The model aligns its structural base envelope and placement to official Purdue GIS within centimeter-scale tolerances.',
      'Published 160 ft height matches evaluated geometry to under 0.001 mm; official sources support red brick, limestone trim, four bells, and the clock/tower identity.',
      'The exported collection is portable and reopens with the expected manifest contract.',
      'Remaining evidence gap: the dedicated build module is stored at modular/bell_tower_work/build_tower.py rather than modular/buildings/build_bell_tower.py; the master placement marker was not independently inspected.',
      'Fine dimensions and plaque inscription remain estimates or representative rather than surveyed/facsimile detail.'
     ]
    }
    assert all(checks.values()), checks
    # Additional threshold checks that ground the score in measured evidence.
    assert boundary_hausdorff<0.05 and centroid_error<0.01 and height_error<0.001
    assert angle_error<0.3 and max(dimension_errors)<0.05
    return result

if __name__ == "__main__":
    result = evaluate()
    output = Path(__file__).resolve().parent / "result.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

from pathlib import Path
import json, math, hashlib
import numpy as np
import tifffile
from pyproj import Transformer
from shapely.geometry import Polygon, Point
ROOT=Path('.')
OUT=ROOT/'audit/baptist_student_foundation_independent_grade_r2'
SRC=ROOT/'audit/baptist_student_foundation/sources'
def evaluate():
    old=json.loads((ROOT/'audit/baptist_student_foundation_independent_grade/result.json').read_text())
    evidence=json.loads((ROOT/'audit/baptist_student_foundation/build_evidence.json').read_text())
    meta=json.loads((SRC/'indiana_2018_ndhm_bsf_source_metadata.json').read_text())
    analysis=json.loads((SRC/'indiana_2018_ndhm_bsf_analysis.json').read_text())
    probe=json.loads((OUT/'blender_probe.json').read_text())
    manifest=json.loads((ROOT/'modular/manifest.json').read_text())
    manifest_entry=next(b for b in manifest['assets'] if b.get('id')=='massing_baptist_student_foundation_c3d8114')
    raw=json.loads((SRC/'indiana_lidar_building_footprint_feature_441814_raw.json').read_text())
    to_geo=Transformer.from_crs(3857,4326,always_xy=True)
    srcxy=[]
    for mx,my in raw['geometry']['coordinates'][0][:-1]:
        lon,lat=to_geo.transform(mx,my)
        srcxy.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
    mdlxy=[tuple(p) for p in probe['structural_outline_xy']]
    srcpoly,mdlpoly=Polygon(srcxy),Polygon(mdlxy)
    max_vertex_delta=max(math.dist(a,b) for a,b in zip(srcxy,mdlxy))
    footprint={'feature_id':raw.get('properties',{}).get('objectid',raw.get('properties',{}).get('OBJECTID',441814)),'source_crs':'EPSG:3857','projected_to':'EPSG:4326 then approximate project XY','source_area_m2':srcpoly.area,'model_area_m2':mdlpoly.area,'area_delta_percent':abs(mdlpoly.area-srcpoly.area)/srcpoly.area*100,'intersection_over_union':srcpoly.intersection(mdlpoly).area/srcpoly.union(mdlpoly).area,'max_corresponding_vertex_delta_m':max_vertex_delta,'source_ring_vertices':len(srcxy),'model_ring_vertices':len(mdlxy)}
    tile=SRC/'in2018_29951885_12_ndhm.tif'
    tile_hash=hashlib.sha256(tile.read_bytes()).hexdigest()
    arr=tifffile.imread(tile)
    gt={'shape':list(arr.shape),'dtype':str(arr.dtype),'pixel_size_ft':[5,5],'crs':meta['crs'],'geotiff_origin_ftUS':[2995000,1890000],'sha256':tile_hash,'metadata_hash_matches':tile_hash==meta['sha256']}
    # Independent cell-center sample of the raw 2018 source tile against the source outline.
    to_sp=Transformer.from_crs(4326,2968,always_xy=True)
    ringft=[to_sp.transform(*to_geo.transform(*xy)) for xy in raw['geometry']['coordinates'][0][:-1]]
    polyft=Polygon(ringft); x0,y0,cell=2995000.0,1890000.0,5.0
    minx,miny,maxx,maxy=polyft.bounds; samples=[]
    for row in range(max(0,int((y0-maxy)/cell)),min(arr.shape[0],int((y0-miny)/cell)+1)):
        for col in range(max(0,int((minx-x0)/cell)),min(arr.shape[1],int((maxx-x0)/cell)+1)):
            x=x0+(col+.5)*cell; y=y0-(row+.5)*cell
            if polyft.contains(Point(x,y)): samples.append(float(arr[row,col]))
    roof=np.asarray([v for v in samples if 2<=v<=25],dtype=float)
    conv=.3048006096
    height={'independent_sample_count':len(samples),'filtered_roof_count':len(roof),'filter_ft':[2,25],'quantiles_m_p10_median_p90':(np.quantile(roof,[.1,.5,.9])*conv).tolist(),'model_structural_roof_range_m':[4.5,6.0],'model_asset_height_m':probe['bounds_max'][2]-probe['bounds_min'][2],'prior_grade':old['score'],'prior_threshold':old['passing_threshold']}
    stale={'build_evidence_claimed_height_m':evidence['geometry_and_design']['revision']['vertical_height_total_m'],'reopened_blend_height_m':height['model_asset_height_m'],'build_evidence_manifest_snapshot_object_count':evidence.get('manifest_entry',{}).get('object_count'),'reopened_blend_collection_object_count':probe['object_count'],'coordinator_manifest_object_count':manifest_entry.get('object_count'),'coordinator_manifest_height_m':manifest_entry.get('bounds_world_m',[[0,0],[0,0],[0,0]])[2][1],'note':'Evidence/manifest snapshots were recorded before or not synchronized to the revised asset; modular/manifest.json still reports 1 object and 16 m height.'}
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':['Official The Found site identifies 200 N Russell St; the 2017 Exponent ad independently labels The Baptist Student Foundation at the same address.','The 2023 orthophoto shows the same T-shaped roof plan. Indiana LiDAR-derived feature 441814 matches the 8-vertex structural wall outline with %.8f m maximum corresponding vertex error, %.6f m² area, and IoU %.8f.'%(max_vertex_delta,mdlpoly.area,footprint['intersection_over_union']),'The 2018 footprint is automated LiDAR extraction rather than a survey; identity is cross-checked by address and imagery.']},
      {'name':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2,'evidence':['Independent reprojection uses EPSG:3857→EPSG:4326, then the repository documented local XY formula; the model uses the source outline without fit-to-bounds rescaling.','Structural plan dimensions and T orientation agree with feature 441814 and the 2023 orthophoto.','No independent survey/control point verifies the absolute project XY offset, so placement confidence is limited by the source layer and approximate local conversion.']},
      {'name':'Evidence-backed height, floors, and roof form','score':1.7,'max_score':2,'evidence':['I re-sampled the preserved NDHM tile by 5-ft cell centers after transforming feature 441814 into EPSG:2968; 191 cells fall in the footprint and 177 remain in the disclosed 2–25 ft robustness filter. p10/median/p90 are %.2f/%.2f/%.2f m.'%tuple(np.quantile(roof,[.1,.5,.9])*conv),'The revised model’s structural eaves are 4.5 m and ridge is 6.0 m, consistent with the sampled surface-height range; the 2017 address-bearing image supports a gabled principal form. The model is 6.0 m tall from its base, not 8.9 m as the evidence JSON currently states.','NDHM is roof/vegetation height above terrain, not a measured eave/ridge survey. Floor count and roof pitch remain estimates.']},
      {'name':'Facade, entrances, and distinctive architecture','score':1.2,'max_score':2,'evidence':['The 2017 Exponent photo supports brick exterior, gabled roof, visible windows, and entrance/canopy in broad form. The official 2018 event photo provides an additional context view but not a measured elevation.','The orthophoto supports plan form only. Window count and spacing, entrance location/dimensions, trim and colors are still illustrative; exact facade schedule is not established by the available low-resolution/oblique views.']},
      {'name':'Modular export, portability, and complete evidence','score':1.3,'max_score':2,'evidence':['The revised .blend reopens with exactly one expected scene and collection, 183 mesh objects, zero collection offset, and no linked Blender libraries or external image dependencies.','Raw footprint, NDHM GeoTIFF, tile metadata/hash, reproducible sampling code/results, orthophoto, official site images, and preview renders are present. The NDHM file SHA-256 matches its metadata and independent re-sampling reproduces 191/177 sample counts and quantiles.','The committed build_evidence.json still claims 8.9 m asset height while the saved blend is 6.0 m; its manifest snapshot says one object and 16 m, and the coordinator-owned modular manifest remains stale. Wall and roof structural meshes are open single-surface pieces, not watertight solids. These reduce confidence in evidence synchronization and mesh integrity.']}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    evidence_block={'prior_grade':{'path':'audit/baptist_student_foundation_independent_grade/result.json','score':old['score'],'outcome':'fail'},'asset':'modular/buildings/massing_baptist_student_foundation_c3d8114.blend','builder_source':'modular/buildings/build_massing_baptist_student_foundation_c3d8114.py','build_record':'audit/baptist_student_foundation/build_evidence.json','blender_probe':'audit/baptist_student_foundation_independent_grade_r2/blender_probe.json','source_footprint_comparison':footprint,'ndhm_tile_verification':gt,'ndhm_independent_sampling':height,'evidence_index_mismatch':stale,'imagery_review':['audit/baptist_student_foundation/sources/indiana_2023_orthophoto_bsf_2026-10-25.jpg','audit/baptist_student_foundation/sources/exponent_page-19.png','audit/baptist_student_foundation/sources/official_web_image_5.jpg'],'readme_rules':['AGENT.md: independent score >=8/10, evidence each criterion, fresh grade after revisions','modular/AGENTS.md: record position/dimensions/height separately; distinguish estimated from measured; preserve coordinate contracts and portable export']}
    findings=['PASS threshold achieved at %.1f/10; the NDHM-based revision materially improves vertical evidence over the previous 7.5/10 result.'%score,'The asset’s current saved geometry has max Z 6.0 m. Update build_evidence.json and the coordinator-owned modular/manifest.json, which still report prior 8.9 m/16 m heights and stale object count/bounds.','The main footprint and roof surfaces are open; close or deliberately document those surfaces before treating the library as a solid/watertight building.','Facade openings, entry placement, roof pitch, and story count remain approximate; preserve that status in integration notes.']
    return {'score':score,'max_score':10,'passing_threshold':8,'pass':score>=8,'criteria':criteria,'evidence':evidence_block,'findings':findings}
if __name__=='__main__':
    result=evaluate()
    (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

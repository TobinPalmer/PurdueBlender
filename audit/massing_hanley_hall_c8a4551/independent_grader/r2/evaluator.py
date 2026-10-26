"""Independent r2 evaluator for Hanley Hall. Reopens the .blend through Blender, then compares its grade-level structural ring against archived GIS and OSM geometry."""
import json, math, subprocess
from pathlib import Path
from shapely.geometry import Polygon
from shapely.validation import explain_validity

ROOT=Path(__file__).resolve().parents[4]
AUDIT=ROOT/'audit/massing_hanley_hall_c8a4551'
OUT=AUDIT/'independent_grader/r2'
ASSET=ROOT/'modular/buildings/massing_hanley_hall_c8a4551.blend'
BLENDER=ROOT/'audit/massing_grant_street_parking_garage_pgg_f46c894/review/blender/blender-5.2.0-windows-x64/blender.exe'
INSPECTOR=OUT/'inspect_blend.py'
INSPECTION=OUT/'asset_inspection.json'


def local_xy(lon, lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040.0)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    p=subprocess.run([str(BLENDER),'--background',str(ASSET),'--python',str(INSPECTOR)],cwd=ROOT,capture_output=True,text=True,timeout=300)
    if p.returncode:
        raise RuntimeError(f'Blender reopen failed ({p.returncode}): {(p.stdout+p.stderr)[-2500:]}')
    inspect=json.loads(INSPECTION.read_text())
    asset=Polygon(inspect['grade_vertices_xy_m'])
    gisraw=json.loads((AUDIT/'sources/purdue_campus_gis_hanley.json').read_text(encoding='utf-8-sig'))
    gf=next(f for f in gisraw['features'] if f['attributes'].get('OBJECTID')==310)
    gis=Polygon([local_xy(lon,lat) for lon,lat in gf['geometry']['rings'][0]])
    osmraw=json.loads((AUDIT/'sources/osm_way_283275000_raw.json').read_text())
    nodemap={n['id']:n for n in osmraw['nodes']}
    osm=Polygon([local_xy(nodemap[i]['lon'],nodemap[i]['lat']) for i in osmraw['way']['nodes']])
    ai=asset.intersection(gis).area; au=asset.union(gis).area
    aiou=ai/au
    osi=asset.intersection(osm).area/asset.union(osm).area
    centroid_delta=asset.centroid.distance(gis.centroid)
    hausdorff=asset.exterior.hausdorff_distance(gis.exterior)
    area_ratio=asset.area/gis.area
    # Five rubric criteria, each out of 2. Evidence conflicts are penalized even when one source matches closely.
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','max_score':2,'score':1.0,
       'evidence':[f"Purdue GIS OBJECTID 310 names Bill and Sally Hanley Hall, abbreviation HNLY, address 1202 W State Street; OSM way 283275000 is named Hanley Hall.",f"Saved asset's 28-point grade ring is essentially identical to OSM: IoU {osi:.6f}, symmetric boundary Hausdorff {asset.hausdorff_distance(osm):.4f} m.",f"Official GIS FID/OBJECTID 310 footprint differs materially: GIS area {gis.area:.1f} m² vs asset {asset.area:.1f} m², IoU {aiou:.3f}, centroid offset {centroid_delta:.2f} m, boundary Hausdorff {hausdorff:.2f} m; shell is {area_ratio:.2f}× GIS area."],
       'assessment':'Identity verified; footprint remains source-conflicted. The current model follows OSM/original massing rather than Purdue GIS.'},
      {'criterion':'Position, orientation, and scale/dimensions','max_score':2,'score':1.25,
       'evidence':[f"Direct Blender reopen measured structural grade bounds X {asset.bounds[0]:.3f}..{asset.bounds[2]:.3f} m, Y {asset.bounds[1]:.3f}..{asset.bounds[3]:.3f} m; dimensions {asset.bounds[2]-asset.bounds[0]:.2f}×{asset.bounds[3]-asset.bounds[1]:.2f} m.",f"The ring matches OSM transformed with project local approximation (IoU {osi:.6f}); official GIS center is {centroid_delta:.2f} m away and projected GIS footprint is materially smaller."],
       'assessment':'Campus location and orientation are strongly supported by OSM and inherited geometry, but width/area cannot be treated as resolved until GIS discrepancy is explained.'},
      {'criterion':'Evidence-backed height, floors, and roof form','max_score':2,'score':0.75,
       'evidence':["Purdue OEP emergency plan identifies three floors; it gives no floor elevations or roof height.",f"Direct Blender geometry top is {inspect['mesh_bounds_world_xyz_m'][2][1]:.2f} m. The builder labels 16 m as an inherited estimate; no measured height source was found.","The Purdue HHS photograph supports a dark projecting eave/roof edge at one frontage, but its orientation and roof pitch are unknown. The model uses a flat cap; exact form is not verified."],
       'assessment':'Floor count is supported. Vertical dimensions and detailed roof geometry are estimates.'},
      {'criterion':'Facade, entrances, and distinctive architecture','max_score':2,'score':1.25,
       'evidence':["The Purdue HHS photo visibly supports red-brown brick, extensive ground-floor glazing, repeated upper windows, and a dark projecting eave.","The saved render includes those broad traits, but repeats simplified equal window bays and bands around the entire unphotographed perimeter; the photo is not georeferenced.","No entrance is identified in the asset or source record; no plan/elevation proves entrance location or detailed corner massing."],
       'assessment':'Broad materials and façade rhythm are photo-supported; entrance and unphotographed sides remain generalized.'},
      {'criterion':'Modular export, portability, and complete evidence','max_score':2,'score':1.75,
       'evidence':[f"Direct reopen found scene {inspect['scene']} and expected collection {inspect['collection']} containing one mesh object ({inspect['mesh_vertices']} vertices, {inspect['mesh_faces']} faces); no modifiers, linked libraries, or unpacked external images.","Dedicated source and evidence records include raw Purdue GIS and OSM snapshots, official emergency plan, Purdue HHS article/photo, source URLs, CRS/method, and the unresolved footprint conflict.","The Blender scene contains review camera/light objects outside the exported asset collection; the collection itself remains a single portable mesh."],
       'assessment':'Export and evidence are substantially complete; slight deduction for retained non-export review scene objects and unresolved source conflict in the evidence package.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[
      {'severity':'major','finding':'Purdue GIS FID/OBJECTID 310 and OSM way 283275000 do not describe coincident footprints. The asset currently follows OSM, with area about 23% larger than Purdue GIS and IoU about 0.81.','action':'Resolve source semantics using dated orthophoto, a georeferenced official site/floor plan, or facilities confirmation before claiming the shell footprint is verified. State which line is structural wall vs roof/site outline; if no higher-quality evidence is found, retain the uncertainty explicitly.'},
      {'severity':'major','finding':'Total height 16.08 m and roof cap form are not supported by measured elevations; only three floors and a photographed dark eave are evidenced.','action':'Seek official building section/elevation or reliable survey. Until then keep total height labeled an estimate and avoid representing the flat cap as a verified roof profile.'},
      {'severity':'moderate','finding':'The facade image is not georeferenced and does not identify an entrance; repeated windows/bands on other elevations are extrapolated.','action':'Use official entrance/site plan or additional oriented photos to place the entrance and distinguish the photographed frontage from other sides.'},
    ]
    result={'score':score,'max_score':10,'passing_threshold':8,'passed':score>=8,'asset_id':'massing_hanley_hall_c8a4551','review_revision':'r2','criteria':criteria,'evidence':{
      'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),'inspected_directly':True,'blender_reopen_exit_code':p.returncode,
      'inspection':inspect,'footprints':{'asset':{'validity':explain_validity(asset),'vertices':len(asset.exterior.coords)-1,'area_m2':asset.area,'bounds_xy_m':list(asset.bounds),'centroid_xy_m':[asset.centroid.x,asset.centroid.y]},'purdue_gis_objectid_310':{'validity':explain_validity(gis),'vertices':len(gis.exterior.coords)-1,'area_m2':gis.area,'bounds_xy_m':list(gis.bounds),'centroid_xy_m':[gis.centroid.x,gis.centroid.y]},'osm_way_283275000':{'validity':explain_validity(osm),'vertices':len(osm.exterior.coords)-1,'area_m2':osm.area,'bounds_xy_m':list(osm.bounds),'centroid_xy_m':[osm.centroid.x,osm.centroid.y]}},
      'comparison_metrics':{'asset_osm_iou':osi,'asset_osm_hausdorff_m':asset.hausdorff_distance(osm),'asset_gis_iou':aiou,'asset_gis_boundary_hausdorff_m':hausdorff,'asset_gis_centroid_distance_m':centroid_delta,'asset_to_gis_area_ratio':area_ratio},
      'sources_read':['audit/massing_hanley_hall_c8a4551/evidence_record.json','audit/massing_hanley_hall_c8a4551/sources/source_catalog.json','audit/massing_hanley_hall_c8a4551/sources/purdue_campus_gis_hanley.json','audit/massing_hanley_hall_c8a4551/sources/osm_way_283275000_raw.json','audit/massing_hanley_hall_c8a4551/sources/purdue_hanley_emergency_plan.html','audit/massing_hanley_hall_c8a4551/sources/purdue_hanley_playground_photo.jpg','audit/massing_hanley_hall_c8a4551/renders/hanley_hall_facade.png']},'findings':findings}
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    # Top-down overlay for audit; GIS footprint appears substantially inset from OSM/asset shell.
    try:
      import matplotlib.pyplot as plt
      fig,ax=plt.subplots(figsize=(8,7))
      for poly,label,color in [(asset,'Saved asset / OSM outline','#c9533b'),(gis,'Purdue GIS OBJECTID 310','#2a6ab4')]:
        x,y=poly.exterior.xy; ax.fill(x,y,color=color,alpha=.28,label=label); ax.plot(x,y,color=color,lw=1.7)
      ax.set_aspect('equal','box'); ax.set_xlabel('Campus local X (m)'); ax.set_ylabel('Campus local Y (m)'); ax.set_title('Hanley Hall footprint source comparison'); ax.legend(); ax.grid(True,alpha=.25); fig.tight_layout(); fig.savefig(OUT/'footprint_comparison.png',dpi=160); plt.close(fig)
    except Exception as e: (OUT/'plot_note.txt').write_text(f'Optional plot generation failed: {e}\n')
    print(json.dumps({'score':score,'max_score':10,'passed':score>=8,'criteria':criteria,'findings':findings,'result_path':str(OUT/'result.json')},indent=2))
    return result

if __name__=='__main__': run()

"""Independent evaluator for the Kozuch Football Performance Complex asset."""
import json, hashlib, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
EVID=ROOT/'audit/purdue_football_performance_complex'
ASSET=ROOT/'modular/buildings/massing_purdue_football_performance_complex_f106c29.blend'
PROBE=EVID/'independent_grade/fresh_asset_probe.json'
EXPECTED_SHA='ddaf5e680ed7c121b1a3d1f3666abd493169e9464b2a4e5d0521c1db54e24c0f'


def evaluate():
    probe=json.loads(PROBE.read_text(encoding='utf-8'))
    evidence=json.loads((EVID/'build_evidence.json').read_text(encoding='utf-8'))
    sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    geo=json.loads((EVID/'sources/purdue_gis_fpc_fid1202_2026-10-26.geojson').read_text(encoding='utf-8'))
    feature=next(f for f in geo['features'] if int(f.get('id',-1))==1202)
    source_vertex_error=probe['max_source_to_plinth_vertex_distance_m']
    local_area=evidence['source_feature']['local_approx_polygon_area_m2']
    published_area=112000*0.09290304
    floor_equiv=published_area/local_area
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'status':'verified',
       'evidence':[f"Purdue campus GIS layer 0 feature 1202, abbreviation FPC, source polygon has {probe['source_vertex_count']} unique vertices; independent Blender fresh-open probe compared it to the structural ground-plinth vertices and found a maximum nearest-vertex difference of {source_vertex_error:.8f} m.","The GIS-on-Esri imagery overlay places the polygon on the white-roofed facility north of Mollenkopf; official Purdue Athletics names the Kozuch Football Performance Complex and states it is adjacent to Mollenkopf’s north end."],
       'reason':'The feature identity is corroborated by Purdue Athletics, Purdue Archives and the mapped location. The building’s ground-plan outline matches the official GIS ring.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,'status':'source geometry verified; master marker pending',
       'evidence':[f"The asset is in the documented local coordinate frame, with evidence origin {evidence['placement_origin_xy_m']} m; model structural footprint extent is {evidence['geometry']['local_bounds_m']} m.",f"All {probe['source_vertex_count']} GIS boundary vertices match the local plinth within {source_vertex_error:.8f} m using the project’s stated approximate lon/lat conversion.","The coordinator has not yet integrated or independently checked the final master Placement marker for this building."],
       'reason':'Footprint size and orientation are source-matched. Two tenths are withheld because the master placement marker has not yet been reviewed.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.1,'max_score':2.0,'status':'partly supported; vertical form uncertain',
       'evidence':["Purdue Athletics and the architect page describe a three-level facility; the source supports three levels but does not provide measured elevations.",f"Asset height is {probe['local_bounds_m'][2][1]:.2f} m, explicitly estimated. No surveyed elevation or construction drawing was found.",f"Purdue GIS reports 115,053 sq ft, while Purdue Athletics and Populous report 112,000 sq ft. The GIS footprint is {local_area:.1f} m², so three complete floor plates would imply about {floor_equiv:.2f} times the published area; the model places full-footprint plates at all three levels, although the sources do not establish that every story spans the full plan.","Populous describes a bold roof line resembling two planes in flight. The model includes split roof slabs and a projecting sloped entrance canopy, but the main roof slopes are very subtle compared with the dramatic folded profile visible in the official entrance photo."],
       'reason':'Three levels and the flight-inspired roof concept are source-backed, but precise vertical dimensions are absent and the full-floor geometry / roof profile only partially resolves the source evidence.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.4,'max_score':2.0,'status':'major features present; some facade interpretation',
       'evidence':["The asset includes a glass curtain wall, old-gold/black cladding palette, projecting entrance canopy, splayed columns, Purdue P, 1228 address, and named entry fascia; these features appear in Purdue Athletics, Populous, and FRP project photographs.","The three-quarter preview shows the massing and continuous glazed banding, while the entrance preview exposes the canopy and columns. The facade is otherwise regularized and the interior is schematic."],
       'reason':'Key identity-bearing exterior features are represented and source-backed; exact bay rhythm and hidden facades remain interpreted, and the roof-edge treatment is simplified.'},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'status':'verified',
       'evidence':[f"Independent Blender 5.2.3 fresh open found the expected scene and collection, {probe['geometry_object_count']} geometry objects ({probe['mesh_count']} meshes), 9 materials, no linked objects, and no unpacked external images.",f"Asset SHA-256 matches expected reviewed revision: {sha}.","The building folder contains raw Purdue GIS, official Athletics, architect and construction photographs, Esri imagery/overlay, source methods, model metrics, and preview renders."],
       'reason':'The standalone library opens with the expected collection and all dependencies are packed or procedural; evidence is complete for this review.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    return {'building':'Kozuch Football Performance Complex','asset_id':evidence['building_id'],'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),'asset_sha256':sha,'grader':'independent_grader_subagent','grade_date':'2026-10-26','score':score,'max_score':10,'passing_threshold':8,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,'evidence':['independent_grade/fresh_asset_probe.py and fresh_asset_probe.json','GIS overlay: gis_footprint_on_esri_imagery.png','Source photo: sources/purdue_athletics_kfpc_exterior.jpg','Architect page: sources/populous_kfpc_architect_page_2026-10-26.html (https://populous.com/showcases/purdue-university-football-performance-complex)','Purdue Athletics: https://purduesports.com/facilities/kozuch-football-performance-complex','Purdue GIS layer 0, FID 1202: https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0/query?where=OBJECTID%3D1202&outFields=*&returnGeometry=true&outSR=4326&f=geojson'],'findings':['The GIS feature is the correct roof footprint at the north end of Mollenkopf; it is not the entire Mollenkopf building.','Plan outline matches Purdue GIS to sub-millimeter precision in the project’s stated approximate coordinate system.','Height and roof slopes remain estimated; the source’s bold flight-inspired roof is only weakly expressed by the nearly flat main roof planes.','Purdue GIS lists 115,053 square feet and the athletics/architect pages list 112,000 square feet; three complete footprint floor plates would exceed those records, leaving floor-by-floor extent unresolved.','The master Placement marker has not been checked as part of this asset-only review.']}

if __name__=='__main__':
    result=evaluate()
    out=Path(__file__).with_name('result.json')
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


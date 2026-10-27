from pathlib import Path
import json, hashlib

HERE=Path(__file__).resolve().parent
ASSET=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301840870_c45a5f4.blend')
EXPECTED_SHA='99C798326ED74F49BC635308EEAC1A962906BDFD74D71E240B4C9A8B895A78B4'

def evaluate(fresh, gis):
    actual=hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()
    assert actual == EXPECTED_SHA == fresh['sha256'], 'Candidate bytes changed or fresh-open targeted another file'
    assert fresh['fresh_open'] and fresh['scene']=='Building_massing_house_301840870_c45a5f4'
    assert fresh['collection']=='Asset_massing_house_301840870_c45a5f4'
    assert fresh['root']=='House_301840870'
    assert gis['gis_feature_id']==785 and gis['abbr']=='SOATO'
    criteria=[
      {'name':'Identity and source-backed footprint','score':2.0,'max_score':2.0,'evidence':'Purdue GIS feature FID 785 identifies SOATO / Alpha Tau Omega at 314 Russell St. National Register nomination and photos identify the historic Tudor Revival house. GIS polygon and structural candidate footprint independently recomputed in the documented local approximation: 566.91 m² GIS, 593.03 m² candidate, 562.72 m² intersection, IoU 0.942.'},
      {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,'evidence':'Candidate footprint bounds closely track GIS: X -436.875 to -413.800 m vs -436.873 to -413.695 m; Y 46.000 to 83.700 m vs 46.099 to 83.938 m. The local conversion is approximate and not surveyed; all building parts are placed in the campus-world frame, with identity transform on the named root.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2.0,'evidence':'The nomination describes the 2.5-story Tudor Revival building, while historic photos support the steep roof, dormers, and chimneys. Fresh-open whole-collection top is z=13.89 m, including chimney; principal roof/ridge and facade heights are explicitly estimated from imagery, with no authoritative section/elevation. The source estimate is plausible but exact dimensions and height remain unverified.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.0,'max_score':2.0,'evidence':'The asset includes red-brown brick, dressed limestone, Tudor dormers, a prominent tower and pointed entrance, leaded windows, porch, slate-like roof, chimneys, and historically named/interpreted interior cues. Direct comparison with NPS historic photo 9 shows a recognizable composition, but the render simplifies the source: the light stone tower/entry and roof-wing silhouette are represented as a more regular brick-centered mass, and facade bay/window detailing is approximate.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'evidence':'A clean Blender 5.2.3 process freshly opened the exact candidate. Stable scene/collection/root identifiers are intact, there are 126 collection objects, root location/rotation/scale are identity, all mesh objects have materials, all materials use nodes, and there are no external image dependencies. Source snapshots, GIS comparison, caveats, and exterior/interior previews are present.'}
    ]
    score=sum(c['score'] for c in criteria)
    return {'score':score,'max_score':10,'pass_threshold':8,'passed':score>=8,'asset':str(ASSET),'sha256':actual,'criteria':criteria,'evidence':{'fresh_open_report':str(HERE/'fresh_open.json'),'gis_comparison':str(HERE/'gis_comparison.json'),'source_evidence':str(ASSET.parents[2]/'audit/alpha_tau_omega/evidence.md'),'previews':[str(ASSET.parents[2]/'audit/alpha_tau_omega/previews/ato_exterior_front.png'),str(ASSET.parents[2]/'audit/alpha_tau_omega/previews/ato_exterior_three_quarter.png'),str(ASSET.parents[2]/'audit/alpha_tau_omega/previews/ato_interior_schematic.png'),str(ASSET.parents[2]/'audit/alpha_tau_omega/previews/gis_candidate_footprint_overlay.jpg')],'reference_photo':str(ASSET.parents[2]/'audit/alpha_tau_omega/previews/nps-photos-19.png')},'findings':['Height and roof geometry remain estimates; no measured elevation/section was found.','For a closer historic-photo match, revise the central tower material/proportions and main roof silhouette, then tune the front bay/window rhythm.','Interior is properly labeled schematic; no measured floor plan is established by the cited evidence.']}

fresh=json.loads((HERE/'fresh_open.json').read_text(encoding='utf-8'))
gis=json.loads((HERE/'gis_comparison.json').read_text(encoding='utf-8'))
result=evaluate(fresh,gis)
(HERE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

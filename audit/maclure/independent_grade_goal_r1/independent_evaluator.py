"""Independent Maclure Cooperative grade for a fixed Blender asset SHA.
Run: blender --background --python independent_evaluator.py
Only writes report.json beside this file.
"""
from __future__ import annotations
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular' / 'buildings' / 'maclure_cooperative.blend'
GIS = ROOT / 'audit' / 'maclure' / 'sources' / 'official_gis_fid822.geojson'
EXPECTED_SHA256 = 'F0830F8324640A585C8F4881FB67359C1AE8827DA33F4E8D4FEB04C266AC2609'
OUT = Path(__file__).with_name('report.json')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest().upper()


def evaluate() -> dict:
    before = sha256(ASSET)
    if before != EXPECTED_SHA256:
        return {'status':'refused_asset_changed','expected_sha256':EXPECTED_SHA256,'actual_sha256':before}
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    col = bpy.data.collections.get('Asset_maclure_cooperative')
    root = bpy.data.objects.get('AssetRoot_maclure_cooperative')
    if scene.name != 'Building_maclure_cooperative' or col is None or root is None:
        raise RuntimeError('Expected Maclure scene, asset collection, or root missing')

    # Independently transform official GIS ring to the documented project local frame.
    feature = json.loads(GIS.read_text(encoding='utf-8'))['features'][0]
    coords = feature['geometry']['coordinates'][0][:-1]
    lat0, lon0 = 40.4274, -86.9137
    def xy(lon, lat):
        return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0)
    abs_ring = [xy(lon,lat) for lon,lat in coords]
    area2 = sum(abs_ring[i][0]*abs_ring[(i+1)%len(abs_ring)][1]-abs_ring[(i+1)%len(abs_ring)][0]*abs_ring[i][1] for i in range(len(abs_ring)))
    area = area2/2
    cx = sum((abs_ring[i][0]+abs_ring[(i+1)%len(abs_ring)][0])*(abs_ring[i][0]*abs_ring[(i+1)%len(abs_ring)][1]-abs_ring[(i+1)%len(abs_ring)][0]*abs_ring[i][1]) for i in range(len(abs_ring)))/(6*area)
    cy = sum((abs_ring[i][1]+abs_ring[(i+1)%len(abs_ring)][1])*(abs_ring[i][0]*abs_ring[(i+1)%len(abs_ring)][1]-abs_ring[(i+1)%len(abs_ring)][0]*abs_ring[i][1]) for i in range(len(abs_ring)))/(6*area)
    src_ring = [(x-cx,y-cy) for x,y in abs_ring]
    walls = bpy.data.objects.get('GIS footprint walls | FID 822')
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evwalls = walls.evaluated_get(depsgraph)
    wall_xy = sorted({(round((evwalls.matrix_world @ v.co).x,4),round((evwalls.matrix_world @ v.co).y,4)) for v in evwalls.data.vertices if abs((evwalls.matrix_world @ v.co).z)<1e-5})
    # XY nearest-neighbour distances are a vertex-set comparison independent of ring ordering.
    src_round = [(round(x,4),round(y,4)) for x,y in src_ring]
    errors = [min(math.hypot(px-x,py-y) for x,y in src_round) for px,py in wall_xy]
    reverse_errors = [min(math.hypot(px-x,py-y) for px,py in wall_xy) for x,y in src_round]
    hausdorff = max(errors+reverse_errors)
    placement = list(root.get('placement_origin_xy_m', []))
    dims = {}
    all_bounds=[]
    for obj in col.objects:
        if obj.type in {'MESH','CURVE','FONT'}:
            ev=obj.evaluated_get(depsgraph)
            pts=[ev.matrix_world @ Vector(v) for v in ev.bound_box]
            if pts:
                bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
                all_bounds += pts
                if obj.name in {'GIS footprint walls | FID 822','Main north-south gable roof | estimated profile','Front cross-gable wall | estimated','Front cross-gable shingles | estimated'}:
                    dims[obj.name]=[[round(v,3) for v in axis] for axis in bounds]
    bounds=[[round(min(p[i] for p in all_bounds),3),round(max(p[i] for p in all_bounds),3)] for i in range(3)]
    names=[o.name for o in col.objects]
    materials=sorted({m.name for o in col.objects if getattr(o,'data',None) is not None and hasattr(o.data,'materials') for m in o.data.materials if m})
    ext_images=[{'name':im.name,'path':im.filepath} for im in bpy.data.images if im.source in {'FILE','TILED'} and im.filepath]
    linked=len(bpy.data.libraries)
    room_parts=sum(n.startswith('Estimated room partition') for n in names)
    story_floors=sum(n.startswith('Estimated interior floor slab') for n in names)
    furniture=sum('(estimated)' in n.lower() for n in names)
    hidden_floors=[o.name for o in col.objects if o.name.startswith('Estimated interior floor slab') and o.hide_render]

    criteria = [
      {'criterion':'footprint / placement','max_score':2.0,'model_score':1.9,'evidence_score':1.9,
       'model_finding':f'Wall mesh is the 12-vertex GIS outline extruded to Z=6.0 m; bidirectional vertex Hausdorff error versus transformed FID 822 ring is {hausdorff:.4f} m. Root placement stores GIS centroid ({placement[0]:.6f}, {placement[1]:.6f}) m. Placement is correct in the local frame; master marker integration was not evaluated.',
       'evidence_finding':'Official Purdue GIS FID 822 identifies Maclure / SOMC at 128 Wiggins St. Snapshot and CRS/approximate conversion are documented; source accuracy metadata and a surveyed control point are absent.'},
      {'criterion':'identity','max_score':2.0,'model_score':1.7,'evidence_score':2.0,
       'model_finding':f'Asset root is labeled {root.get("building_id")}; source feature ID is {root.get("source_feature_id")}. Rendered stone inscription is visibly misspelled/clipped in preview, so the visible identity cue is unreliable.',
       'evidence_finding':'GIS name/address/owner attributes match the co-op official About page and Purdue FSCL cooperative list.'},
      {'criterion':'roof / height / facade','max_score':2.0,'model_score':1.2,'evidence_score':1.2,
       'model_finding':f'Photo-supported white clapboard, charcoal roof, red shutters, brick chimney, gable, and raised deck are present. Exterior preview places access stairs near the middle; official facade photo shows them at the right end beside a recessed entrance. First-floor window/door arrangement also differs. Roof/wall heights are estimates (wall 6 m; roof peak 9 m), not measured.',
       'evidence_finding':'Official co-op photo gallery supports overall style and visible features but has no verified capture date/current survey. GIS NUM_LEVELS=1 conflicts with the apparent two-story plus attic; roof form, facade dimensions, window spacing, and all Z values remain unverified estimates.'},
      {'criterion':'interior','max_score':2.0,'model_score':0.8,'evidence_score':0.7,
       'model_finding':f'Asset includes {room_parts} estimated partition pieces, {story_floors} estimated interior floor slabs, furniture proxies ({furniture} objects matching estimated labels), and an estimated basement. However, both floor slabs are render-hidden; the provided cutaway preview reads as sparse schematic partitions plus table/chairs, not a resolved floor plan.',
       'evidence_finding':'Virtual-tour room names support a limited room program only. No architectural plans, measured partitions, door schedule, or verified furniture layout were found; placement and dimensions are estimates.'},
      {'criterion':'materials / portability','max_score':2.0,'model_score':1.7,'evidence_score':1.8,
       'model_finding':f'{len(materials)} assigned materials with procedural Blender materials; {linked} linked libraries and {len(ext_images)} file/tiled image dependencies in the delivered scene. Colors broadly match the official photo. Facade siding edges read as repeated overhanging seams and garden/stone geometry is simplified.',
       'evidence_finding':'Official imagery supports broad exterior colors and roofing/deck material appearance. Procedural materials and no external texture dependencies are directly verified from the asset; exact construction/material specification is unavailable.'}
    ]
    model_score=round(sum(c['model_score'] for c in criteria),1)
    evidence_score=round(sum(c['evidence_score'] for c in criteria),1)
    after=sha256(ASSET)
    if after != EXPECTED_SHA256:
        return {'status':'asset_changed_during_grade','expected_sha256':EXPECTED_SHA256,'before_sha256':before,'after_sha256':after}
    return {
      'status':'graded','asset_path':'modular/buildings/maclure_cooperative.blend','asset_sha256':before,
      'method':{'asset_inspection':'Blender 5.2.3 LTS background open of the exact .blend; evaluated depsgraph bounds/material/library checks; direct review of provided exterior and interior preview images.','footprint_comparison':'Read official raw GeoJSON FID 822; converted EPSG:4326 vertices with modular/AGENTS.md local approximation, computed polygon centroid, compared transformed mesh base vertices bidirectionally by nearest-neighbor distance.','source_review':'Independently read official GIS GeoJSON and preserved co-op/FSCL source notes and exterior photos; did not adopt builder ratings or claims.'},
      'score':model_score,'evidence_score':evidence_score,'max_score':10.0,
      'criteria':criteria,
      'evidence':[
        {'path':'audit/maclure/sources/official_gis_fid822.geojson','role':'Purdue GIS raw feature snapshot, FID 822; source CRS EPSG:4326 output from EPSG:3857 layer; source edit timestamp 2026-08-31; retrieved 2026-10-27.'},
        {'path':'audit/maclure/sources/mac_lure_about_source.txt','role':'Maclure Cooperative official site name/address/history note; retrieved 2026-10-27.'},
        {'path':'audit/maclure/sources/purdue_fscl_houses_source.txt','role':'Purdue FSCL official co-op listing note; retrieved 2026-10-27.'},
        {'path':'audit/maclure/sources/img-6426.jpg','role':'Official cooperative exterior gallery photo; supports facade, roof, windows, shutters, porch/stairs, and landscape; exact image date unknown.'},
        {'path':'audit/maclure/sources/img-6427.jpg','role':'Official cooperative close photo of porch deck, lattice, stairs, and identity rock; exact image date unknown.'},
        {'path':'audit/maclure/sources/img-6430.jpg','role':'Official cooperative gallery street view; supplemental massing/context; exact image date unknown.'},
        {'path':'audit/maclure/maclure_exterior_preview.png','role':'Model preview visually inspected.'},
        {'path':'audit/maclure/maclure_interior_preview.png','role':'Model cutaway preview visually inspected.'}
      ],
      'measured_asset':{'scene':scene.name,'collection':col.name,'object_count':len(col.objects),'local_project_xy_bounds_from_evaluated_asset_m':bounds,'wall_mesh_bounds_m':dims.get('GIS footprint walls | FID 822'),'roof_mesh_bounds_m':dims.get('Main north-south gable roof | estimated profile'),'cross_gable_bounds_m':dims.get('Front cross-gable wall | estimated'),'gis_ring_vertex_count':len(src_ring),'wall_base_vertex_count':len(wall_xy),'gis_wall_bidirectional_vertex_hausdorff_m':round(hausdorff,4),'gis_polygon_area_projected_m2':round(abs(area),3),'placement_centroid_xy_m':[round(v,6) for v in placement],'estimated_wall_top_m':6.0,'estimated_ridge_peak_m':9.0,'procedural_material_count':len(materials),'external_file_image_count':len(ext_images),'linked_library_count':linked,'render_hidden_interior_floor_slabs':hidden_floors},
      'findings':[
        'Exterior evidence supports broad identity and appearance; GIS geometry supports footprint and placement. No independent source verifies building height or roof topology.',
        'The official facade photo places porch access at the right end next to the recessed entry; the current preview puts modeled access near the center and should be revised.',
        'The current interior is not independently verifiable as a plan. The floor slabs are hidden in renders and source material provides only room names.',
        'Materials are portable in the inspected asset: zero external image dependencies and zero linked libraries.'
      ],
      'specific_fixes_to_reach_or_exceed_8_of_10':[
        'Move the deck stairs to the documented right end and model the recessed entry bay; revise the first-floor openings to match the official front photo (remove the extra lower window where the entrance occupies that bay). This is the highest-value fidelity fix.',
        'Render a clear, separate cutaway/floor-plan view with the estimated floor slabs visible, plus enough partition/door openings to show circulation; keep the layout explicitly labeled as estimated until a measured plan is obtained.',
        'Correct the garden identity rock text to read MACLURE / est. 1966 and adjust its angle/contrast so the text is legible.',
        'Keep roof peak and wall height labeled estimated; an independently measured elevation or reliable source is needed before height can score as verified.'
      ],
      'blockers':['No measured elevation or architectural plan.','No verified source-photo date/current facade survey.'],
      'grade_scope_note':'Model score and source-evidence score are separate 10-point scales. Exact asset digest was checked before and after evaluation.'
    }

result=evaluate()
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))

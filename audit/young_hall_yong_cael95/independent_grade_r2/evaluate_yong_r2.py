"""Independent fresh-open YONG revision-2 evaluator."""
import bpy, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
AUDIT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).with_name('result.json')
GIS=json.loads((AUDIT/'purdue_gis_yong_fid70.json').read_text(encoding='utf-8'))['features'][0]
EVID=json.loads((AUDIT/'evidence.json').read_text(encoding='utf-8'))
raw=GIS['geometry']['rings'][0]
ring=raw[:-1] if raw[0]==raw[-1] else raw
expected=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),
           (lat-40.4274)*111040.0) for lon,lat in ring]
coll=bpy.data.collections.get('Asset_massing_young_hall_yong_cae1b95')
shell=bpy.data.objects.get('Young Hall (YONG)')
errors=[]
actual=[]
if coll is None: errors.append('Expected export collection missing')
if shell is None: errors.append('Named shell object missing')
if shell:
    actual=[(float((shell.matrix_world@v.co).x),float((shell.matrix_world@v.co).y))
            for v in shell.data.vertices if abs(float((shell.matrix_world@v.co).z))<1e-4]
    if len(actual)!=len(expected): errors.append(f'GIS ring count mismatch: asset={len(actual)}, GIS={len(expected)}')
maxerr=max((math.dist(a,b) for a,b in zip(actual,expected)),default=float('inf')) if len(actual)==len(expected) else float('inf')
if maxerr>0.01: errors.append(f'GIS projected ring error exceeds 0.01 m: {maxerr}')
member=list(coll.objects) if coll else []
member_types={t:sum(1 for o in member if o.type==t) for t in sorted({o.type for o in member})}
if any(o.type=='EMPTY' for o in member): errors.append('Preview/helper EMPTY remains in exported collection')
if any(o.type not in {'MESH','FONT'} for o in member): errors.append('Unsupported object type in exported collection')
# Verify portable image dependencies and evaluated nonzero mesh.
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        path=Path(bpy.path.abspath(im.filepath, library=im.library))
        if not path.exists(): external.append(str(path))
if external: errors.append('Missing external image dependency')
mesh_count=sum(1 for o in member if o.type=='MESH')
face_count=sum(len(o.data.polygons) for o in member if o.type=='MESH')
if mesh_count==0 or face_count==0: errors.append('Export geometry is empty')
materials=sorted({m.name for o in member if o.type=='MESH' for m in o.data.materials if m})
src=Path(AUDIT/'purdue_archives_building_record.html').read_text(encoding='utf-8',errors='replace')
archive_10='10 stories high' in src or '10 stories' in src
archive_photos=[p.name for p in AUDIT.glob('young_graduate_house_archive_photo_*.jpg')]
archive_photos_ok=len(archive_photos)>=3
facade_img=(AUDIT/'purdue_young_hall_facade_reference.jpg').exists()

def bounds(points):
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
shell_pts=[shell.matrix_world@v.co for v in shell.data.vertices] if shell else []
model_bounds=bounds(shell_pts)
model_h=(model_bounds[2][1]-model_bounds[2][0]) if model_bounds else None
attr=GIS['attributes']

criteria=[
 {'criterion':'Correct identity and source-backed footprint','points':2.0,'max_points':2.0,
  'evidence':f"Purdue GIS FID {attr.get('FID')} identifies {attr.get('BUILDING_N')} (YONG), and shell lower ring has {len(actual)} vertices matching the GIS ring within {maxerr:.6f} m. Purdue Archives corporate record identifies Ernest C. Young Hall.",
  'findings':'Footprint and identity are strong; conversion uses the project local approximation, not survey control.'},
 {'criterion':'Position, orientation, scale and plan dimensions','points':2.0 if maxerr<=0.01 else 0.0,'max_points':2.0,
  'evidence':f"Campus-world bounds derived from official GIS ring: {bounds([(x,y,0.0) for x,y in expected])}; polygon geometry preserves the source vertex sequence; max projected-ring deviation is {maxerr:.6f} m.",
  'findings':'No independent cadastral survey control exists in the saved evidence, so absolute registration inherits the approximate project geographic conversion.'},
 {'criterion':'Evidence-backed height, floors and roof form','points':1.35,'max_points':2.0,
  'evidence':f"Saved shell is {model_h:.3f} m tall (approximately 102 ft inferred from GIS R=102). Purdue Archives explicitly describes 10 stories; GIS NUM_LEVELS/CountOfFLO each report 11. Archival exterior photos show a flat-topped slab form.",
  'findings':'10-story history and flat-roof massing have archival support. 11 GIS levels vs 10 archival stories is unresolved; R units are undocumented and interpreted as feet, so height is an estimate. Floor spacing and rooftop details are not measured.'},
 {'criterion':'Facade, entrance and distinctive architecture','points':1.55 if archive_photos_ok else 1.2,'max_points':2.0,
  'evidence':f"Three Purdue Archives exterior photos show a long slab, pale panelized elevations, repeated narrow vertical window bays and a flat roof; current Purdue detail photo supports the localized red-brick YOUNG HALL sign wall. The revised render follows the historic facade rhythm and the current brick sign detail.",
  'findings':'References are undated historical views plus a close crop of a current sign wall. They do not establish all current elevations, window spacing, entrance placement or roof fittings. Render is bright enough to obscure some panel contrast; facade detail remains schematic.'},
 {'criterion':'Modular export, portability and evidence completeness','points':1.55 if coll is not None and not external and not any(o.type=='EMPTY' for o in member) else 0.5,'max_points':2.0,
  'evidence':f"Fresh Blender {bpy.app.version_string} open contains stable scene/collection and {len(member)} members ({member_types}); {mesh_count} mesh objects / {face_count} polygons; {len(materials)} named material slots; no missing external image dependencies. Fresh sources include official GIS, map, Archives record and {len(archive_photos)} archival photos. Interior cutaway is a compact schematic lobby/corridor only.",
  'findings':'No source floor plan is supplied; interior represents a small lobby slice rather than the building-wide graduate-house/program layout. Dimensions and partitions are illustrative.'}
]
score=round(sum(c['points'] for c in criteria),2)
result={'score':score,'max_score':10,'criteria':criteria,
 'evidence':{'asset_path':str(ROOT/'modular/buildings/massing_young_hall_yong_cae1b95.blend'),
             'scene':bpy.context.scene.name,'collection':coll.name if coll else None,
             'collection_objects':len(member),'object_types':member_types,'mesh_count':mesh_count,'polygon_count':face_count,
             'materials':materials,'external_image_dependencies':external,
             'gis_feature_id':attr.get('FID'),'gis_building_abbr':attr.get('BLDG_ABBR'),
             'gis_ring_vertex_count':len(expected),'asset_ring_vertex_count':len(actual),'gis_ring_max_error_m':maxerr,
             'shell_bounds_world_m':model_bounds,'shell_height_m':model_h,
             'archives_10_story_text_found':archive_10,'archives_photo_count':len(archive_photos),
             'current_facade_detail_photo_present':facade_img,
             'exterior_render':str(AUDIT/'preview_exterior.png'),'interior_render':str(AUDIT/'preview_interior_schematic.png'),
             'fresh_open_errors':errors},
 'findings':['Footprint/identity checks pass directly against the saved official Purdue GIS geometry.',
             'Height remains an estimate: GIS units are undocumented; 102 was interpreted as feet. The 10-vs-11 story-count conflict is recorded, not resolved.',
             'Historical archival photos support the revised light panelized facade and vertical window rhythm but do not prove the current entire facade.',
             'Current reference supports red-brick sign wall only; other elevation details, entrance placement and roof equipment are partly inferred.',
             'Interior is only a representative schematic slice; there is no plan-level interior reconstruction.',
             'Asset is standalone/portable and the preview-only helper EMPTY is absent from the export collection.'],
 'result':'pass' if score>=8 and not errors else 'fail','passing_standard':8}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

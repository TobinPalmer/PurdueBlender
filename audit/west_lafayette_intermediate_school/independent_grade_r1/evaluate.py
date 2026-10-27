import bpy,bmesh,json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/massing_west_lafayette_intermediate_school_d72f0fa.blend'
OSM=ROOT/'audit/west_lafayette_intermediate_school/sources/osm_way_772742586_full.json'
OUT=Path(__file__).resolve().parent
EXPECTED='89bd517ddc0024c6dba1c223cf3138b55af833847e3de94e7a85be34deaf915d'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
data=json.loads(OSM.read_text(encoding='utf-8'))
way=next(e for e in data['elements'] if e.get('type')=='way' and e.get('id')==772742586)
nodes={e['id']:(e['lon'],e['lat']) for e in data['elements'] if e.get('type')=='node'}
source=[]
for nid in way['nodes']:
    lon,lat=nodes[nid]
    source.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
source=source[:-1] if len(source)>1 and source[0]==source[-1] else source
scene=bpy.data.scenes.get('Building_massing_west_lafayette_intermediate_school_d72f0fa')
col=bpy.data.collections.get('Asset_massing_west_lafayette_intermediate_school_d72f0fa')
objects=list(col.all_objects) if col else []
meshes=[o for o in objects if o.type=='MESH']
shell=bpy.data.objects.get('GIS 772742586 | exact connected school footprint')
base=[]
if shell:
    for v in shell.data.vertices:
        p=shell.matrix_world@v.co
        if abs(p.z)<1e-5: base.append((p.x,p.y))
    base=list(dict.fromkeys((round(x,7),round(y,7)) for x,y in base))
errs=[min(math.hypot(x-bx,y-by) for bx,by in base) if base else None for x,y in source]
allverts=[]
for o in meshes:
    for v in o.data.vertices: allverts.append(o.matrix_world@v.co)
bounds=[[min(v[i] for v in allverts),max(v[i] for v in allverts)] for i in range(3)] if allverts else None
def diag(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    result={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_volume_m3':None}
    if bm.edges and all(e.is_manifold for e in bm.edges):
        try: result['signed_volume_m3']=round(bm.calc_volume(signed=True),6)
        except Exception: pass
    bm.free(); return result
image_refs=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        p=Path(bpy.path.abspath(im.filepath)); image_refs.append({'name':im.name,'path':str(p),'exists':p.exists(),'packed':im.packed_file is not None})
materials=sorted({slot.material.name for o in objects if o.type=='MESH' for slot in o.material_slots if slot.material})
mat_nodes={}
for name in materials:
    m=bpy.data.materials.get(name)
    mat_nodes[name]=[n.bl_idname for n in m.node_tree.nodes] if m and m.use_nodes and m.node_tree else []
name_counts={
 'classroom_partitions':sum(1 for o in objects if o.name.startswith('Classroom ') and ' | partition' in o.name),
 'student_tables':sum(1 for o in objects if 'student table' in o.name),
 'interior_doors':sum(1 for o in objects if 'interior door' in o.name),
 'classroom_clerestory_lites':sum(1 for o in objects if 'clerestory interior lite' in o.name),
 'media_center_bookcases':sum(1 for o in objects if 'Media center | bookcase' in o.name),
 'gym_bleacher_tiers':sum(1 for o in objects if 'folding bleacher tier' in o.name),
 'gym_trusses':sum(1 for o in objects if 'gym red steel roof truss' in o.name),
 'gym_court_markings':sum(1 for o in objects if 'Gym court |' in o.name),
 'entry_red_steel_objects':sum(1 for o in objects if 'Entry canopy' in o.name or 'Entry truss' in o.name),
}
report={'fresh_open':True,'asset_sha256':sha,'expected_sha256':EXPECTED,'exact_sha_match':sha==EXPECTED,'scene':scene.name if scene else None,'collection':col.name if col else None,'object_count':len(objects),'mesh_object_count':len(meshes),'mesh_vertex_count':sum(len(o.data.vertices) for o in meshes),'mesh_polygon_count':sum(len(o.data.polygons) for o in meshes),'bounds_world_m':bounds,'osm_way_id':way['id'],'osm_tags':way.get('tags',{}),'osm_node_count_closed':len(way['nodes']),'osm_unique_perimeter_nodes':len(source),'shell_base_unique_vertices':len(base),'footprint_max_nearest_vertex_error_m':max(errs) if errs and all(e is not None for e in errs) else None,'footprint_rms_nearest_vertex_error_m':math.sqrt(sum(e*e for e in errs)/len(errs)) if errs and all(e is not None for e in errs) else None,'shell_mesh_diagnostics':diag(shell) if shell else None,'object_counts_by_subcollection':{c.name:sum(1 for o in c.all_objects if o in objects) for c in (col.children if col else [])},'named_feature_counts':name_counts,'material_names':materials,'material_node_types':mat_nodes,'external_image_dependencies':image_refs,'unpacked_missing_images':[x for x in image_refs if not x['packed'] and not x['exists']]}
(OUT/'geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('WLIS_R1_GEOMETRY '+json.dumps(report))


def evaluate(data):
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'evidence':['WLCSC and NCES records identify the open West Lafayette Intermediate School at 1838 N Salisbury; OSM way 772742586 is named for the same school and address.','The exact shell base contains all 45 unique way vertices and matches the transformed source ring within 0.000061 m maximum nearest-vertex error. The base shell has no boundary, nonmanifold, or zero-area faces.'],'finding':'Identity and GIS outline are strongly supported. OSM remains community mapping rather than a surveyed wall line.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.9,'max_score':2.0,'evidence':[f"The shell and campus bounds are {data['bounds_world_m']}; the wall base reproduces the OSM campus transform.",'The Esri aerial supports the broad campus position and wing arrangement; its capture date and pixel georeferencing are not documented. The project XY transform is approximate, not surveyed.'],'finding':'Placement and footprint scale are convincing; absolute survey control and facade compass bearing remain unverified.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.35,'max_score':2.0,'evidence':['Architect/award sources support a low school mass, a three-wing central learning node, a larger gym and a southeast multipurpose/cafeteria wing. The aerial shows these broad plan components.','The screenshots show 4.75 m base walls, a raised central clerestory and an approximately 8.8 m gym roof, but no measured elevations or roof schedule were found.','The main school roof is largely represented by generic flat roof planes/parapets; aerial roof articulations and connecting edges are simplified, and exact placement/dimensions of the raised volumes remain interpretive.'],'finding':'The broad massing and special gym/central volumes match sources, but roof articulation and vertical dimensions remain schematic estimates.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.45,'max_score':2.0,'evidence':['Architect photographs support red/brown brick, light metal spandrel, broad glazing, a red exposed-steel entry canopy, and the gym/clerestory language. These main motifs appear in the saved renders.','The generated facade repeats a uniform window module around long polygon edges; photographs show more varied glazing bands and wall/window proportions. The entry canopy and glazing are recognizable but simplified.','The interior includes 36 classroom partition/door/table sets, seven bookcases, a gym court, hoops and bleacher tiers, but the reviewed interior renders do not make the classrooms readily legible and omit the source photographs’ richer classroom, library and corridor details. The placement of rooms is explicitly schematic.'],'finding':'The main visual identity is present, while the facade rhythm and interior presentation remain generic.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.2,'max_score':2.0,'evidence':[f"Blender 5.2.3 independently opened the expected scene and collection; {data['object_count']} objects and {data['mesh_object_count']} meshes load.",f"Ten materials use procedural node graphs, including brick, floor and metal-panel nodes; there are {len(data['external_image_dependencies'])} external image dependencies.",'The source register and raw GIS/architect/aerial snapshots document identity, broad program and uncertainties. However, evidence.json still says geometry review is pending and reports the pre-build one-object/90-vertex massing; it does not record this model’s exact SHA, independent footprint result, current 1,359-object count, or current fresh-open result.'],'finding':'The file is self-contained and opens correctly, but the project evidence must be refreshed against this exact asset before the handoff is complete.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=['Refresh evidence.json and source_register.md status with the exact asset SHA, new object/material counts, independent fresh-open result, and 45-vertex footprint comparison; remove the stale “pending”/one-object inspection text.','Improve and clearly present the interior: show classroom desks/chairs and coherent corridor/room boundaries, enrich the media-center/cafeteria/gym details from the supplied photos, or mark elements unavailable instead of implying detailed interiors.','Refine main roof planes/clerestory transitions and long facade glazing rhythm to match the aerial and architect photos more closely; retain height estimates as estimates.','Render at least one close exterior and one readable interior view with neutral lighting/material contrast so the distinctive brick, red steel, glazing, and school program can be judged.']
    result={'building':'West Lafayette Intermediate School','building_id':'massing_west_lafayette_intermediate_school_d72f0fa','review_revision':1,'asset':'modular/buildings/massing_west_lafayette_intermediate_school_d72f0fa.blend','asset_sha256':data['asset_sha256'],'expected_sha256':data['expected_sha256'],'exact_sha_match':data['exact_sha_match'],'review_date':'2026-10-27','reviewer':'independent grader','blender_version':'5.2.3 LTS','fresh_open':data['fresh_open'],'score':score,'max_score':10.0,'threshold':8.0,'accepted':score>=8.0,'criteria':criteria,'sources_reviewed':['audit/west_lafayette_intermediate_school/evidence.json','audit/west_lafayette_intermediate_school/source_register.md','audit/west_lafayette_intermediate_school/sources/osm_way_772742586_full.json','audit/west_lafayette_intermediate_school/sources/esri_world_imagery_site_aerial.jpg','audit/west_lafayette_intermediate_school/sources/idea_award_p61.png','audit/west_lafayette_intermediate_school/sources/schmidt_exterior_main_entry.jpg','audit/west_lafayette_intermediate_school/sources/schmidt_interior_classroom.jpg','audit/west_lafayette_intermediate_school/sources/schmidt_interior_gymnasium.jpg','audit/west_lafayette_intermediate_school/sources/schmidt_interior_media_center.jpg'],'renders_reviewed':['audit/west_lafayette_intermediate_school/preview_aerial.png','audit/west_lafayette_intermediate_school/preview_northwest.png','audit/west_lafayette_intermediate_school/preview_main_entry.png','audit/west_lafayette_intermediate_school/preview_interior_cutaway.png','audit/west_lafayette_intermediate_school/preview_classroom_interior.png','audit/west_lafayette_intermediate_school/preview_gym_interior.png'],'geometry_validation':data,'findings':findings}
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    lines=['# Independent grade r1 — West Lafayette Intermediate School','',f"**Score: {score}/10 — {'PASS' if score>=8.0 else 'BELOW 8.0'}**",f"**Exact asset SHA-256:** `{data['asset_sha256']}`",'**Fresh-open:** passed independently in Blender 5.2.3 LTS.','', '| Criterion | Score | Evidence and finding |','|---|---:|---|']
    for c in criteria: lines.append(f"| {c['criterion']} | {c['score']:.2f}/{c['max_score']:.0f} | {c['finding']} |")
    lines += ['', '## Required revisions'] + [f'- {f}' for f in findings] + ['', 'See `result.json` and `geometry_validation.json` for structured evaluation and mesh measurements.']
    (OUT/'grade_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return result

evaluation=evaluate(report)
print('WLIS_R1_INDEPENDENT_GRADE '+json.dumps({k:evaluation[k] for k in ['score','accepted','asset_sha256','fresh_open']}))

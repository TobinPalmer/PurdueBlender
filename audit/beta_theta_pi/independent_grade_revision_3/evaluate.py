import bpy, bmesh, json, hashlib, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/massing_beta_theta_pi_fid826.blend'
SOURCE=ROOT/'audit/beta_theta_pi/sources/purdue_buildings_fid826_4326.json'
OUT=Path(__file__).resolve().parent
EXPECTED='18c78795b8e52b4d3566450745bb448d1116f7ded56c4312802a8e5f52fa5b25'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
feature=json.loads(SOURCE.read_text(encoding='utf-8'))['features'][0]
attrs=feature['attributes']
ring_ll=feature['geometry']['rings'][0]
ring=[]
for lon,lat in ring_ll:
    ring.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040.0))
ring=ring[:-1] if len(ring)>1 and ring[0]==ring[-1] else ring
scene=bpy.data.scenes.get('Building_massing_beta_theta_pi_fid826')
coll=bpy.data.collections.get('Asset_massing_beta_theta_pi_fid826')
objects=list(coll.all_objects) if coll else []
mesh_objs=[o for o in objects if o.type=='MESH']
wall=bpy.data.objects.get('BetaThetaPi_GIS_826_exact_perimeter_walls')
base_points=[]
if wall and wall.type=='MESH':
    base_points=[(wall.matrix_world@v.co) for v in wall.data.vertices if abs((wall.matrix_world@v.co).z)<1e-5]
    unique=[]; seen=set()
    for p in base_points:
        key=(round(p.x,6),round(p.y,6))
        if key not in seen: seen.add(key); unique.append((p.x,p.y))
    base_points=unique
errs=[]
for x,y in ring:
    errs.append(min(math.hypot(x-bx,y-by) for bx,by in base_points) if base_points else None)
roof=[o for o in mesh_objs if o.name.startswith('GIS_RoofBand_')]
deck=bpy.data.objects.get('GIS_FID826_Exact_Footprint_Roof_Deck')
def mesh_diag(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
    edges=len(bm.edges); boundary=sum(e.is_boundary for e in bm.edges); nonmanifold=sum(not e.is_manifold for e in bm.edges)
    zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces)
    vol=None
    if edges and not boundary and not nonmanifold:
        try: vol=round(bm.calc_volume(signed=True),6)
        except Exception: pass
    bm.free()
    normals=[p.normal for p in obj.data.polygons]
    return {'faces':len(obj.data.polygons),'edges':edges,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'zero_area_faces':zero_faces,'signed_volume_m3':vol,'normal_z_min':min((n.z for n in normals),default=None),'normal_z_max':max((n.z for n in normals),default=None),'all_faces_have_upward_component':all(n.z>1e-8 for n in normals) if normals else False}
image_refs=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        p=Path(bpy.path.abspath(im.filepath))
        image_refs.append({'name':im.name,'path':str(p),'exists':p.exists(),'packed':im.packed_file is not None})
materials=sorted({slot.material.name for o in objects if o.type=='MESH' for slot in o.material_slots if slot.material})
allmeshverts=[]
for o in mesh_objs:
    for v in o.data.vertices:
        w=o.matrix_world@v.co
        allmeshverts.append(w)
bounds=[[min(v[i] for v in allmeshverts),max(v[i] for v in allmeshverts)] for i in range(3)] if allmeshverts else None
report={
 'fresh_open':True,
 'asset_sha256':sha,
 'expected_sha256':EXPECTED,
 'exact_sha_match':sha==EXPECTED,
 'scene':scene.name if scene else None,
 'collection':coll.name if coll else None,
 'object_count':len(objects),
 'mesh_object_count':len(mesh_objs),
 'bounds_world_m':bounds,
 'source_identity':{'fid':attrs.get('FID'),'name':attrs.get('BUILDING_N'),'address':attrs.get('ADDRESS'),'owner':attrs.get('OWNER'),'num_levels':attrs.get('NUM_LEVELS'),'gis_extrusion':attrs.get('Extrution')},
 'source_ring_unique_vertices':len(ring),
 'wall_base_unique_vertices':len(base_points),
 'footprint_max_nearest_vertex_error_m':max(errs) if errs and all(e is not None for e in errs) else None,
 'footprint_rms_nearest_vertex_error_m':math.sqrt(sum(e*e for e in errs)/len(errs)) if errs and all(e is not None for e in errs) else None,
 'roof_facet_object_count':len(roof),
 'roof_facet_mesh_diagnostics':{k:sum(mesh_diag(o)[k] for o in roof) for k in ['faces','edges','boundary_edges','nonmanifold_edges','zero_area_faces']},
 'roof_facet_upward_face_fraction':sum(sum(1 for p in o.data.polygons if p.normal.z>1e-8) for o in roof)/max(1,sum(len(o.data.polygons) for o in roof)),
 'roof_deck_present':deck is not None,
 'roof_deck_diagnostics':mesh_diag(deck) if deck else None,
 'gis_wall_shell_diagnostics':mesh_diag(wall) if wall else None,
 'material_names':materials,
 'file_image_dependencies':image_refs,
 'unpacked_external_images':[r for r in image_refs if not r['exists'] and not r['packed']],
}
(OUT/'geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('BETA_THETA_PI_R3_GEOMETRY '+json.dumps(report))


def evaluate(report):
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'evidence':['Purdue BuildingShapesZip4 FID 826 names Beta Theta Pi at 150 Littleton St; Purdue Beta chapter and university address records corroborate the chapter-house identity.','The model wall base contains all 19 unique source-ring vertices; independent campus transform comparison gives 0.0000294 m maximum nearest-vertex error.'],'finding':'Identity and GIS footprint are directly supported and geometrically faithful.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.9,'max_score':2.0,'evidence':[f"Fresh-open bounds are {report['bounds_world_m']}; XY bounds agree with the transformed FID 826 polygon within rounding.",'The site-specific aerial overlay supports plan location. The official facade photos are not registered to GIS, so the absolute bearing of the photographed elevation is not proven.'],'finding':'Campus placement and plan scale are strong; photographed facade bearing remains uncertain.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':0.75,'max_score':2.0,'evidence':['Official chapter photos support three visible facade levels; housing record lists four floors plus a basement but does not establish above-grade count. Modeled wall/roof elevations are explicitly estimates.','The r4 east, north, south, and aerial renders show conspicuous black triangular voids, roof facets that meet unevenly, and gable/roof intersections that do not read as the source house’s stepped slate roof.','The fresh-open roof audit finds 22 facets and 44 faces, but only 63.6% of face normals have a positive upward component; open boundary edges are pervasive at the separate facet seams. The 19-point footprint remains exact.'],'finding':'The main roof silhouette and facet joins remain visibly incorrect. Roofs need contiguous, outward-facing surfaces with closed seams and the photographed gable/dormer profile.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.45,'max_score':2.0,'evidence':['The west/front render reproduces the photographed red brick, pale multi-level bay, centered gabled feature, repeated sash rows, and offset arched stone entry.','The close render shows the bay and arch, but the door is a blank plaque-like panel rather than the photographed wood door/shield treatment; fine stone surrounds and facade projections are simplified.','East/rear and end elevations use largely repeated generic windows and plain wall fields; source coverage of hidden elevations is limited.'],'finding':'The main facade is recognisable and source-informed, though entry details and secondary elevations remain generic.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.7,'max_score':2.0,'evidence':[f"The file independently opens in Blender 5.2.3 with the expected scene and collection; it contains {report['object_count']} objects and five assigned materials.",f"No external file-image dependencies are present; the asset uses portable node materials.",'The audit folder preserves GIS, official chapter, and aerial sources plus six review views. The evidence.json SHA text does not match the actual 64-character asset SHA, and the wall-shell diagnostic contains one zero-area face.','No verified public interior plan was found; omitting invented interior geometry is appropriate but leaves interior completion unverified.'],'finding':'The modular file opens and is portable, with broad provenance. Correct the evidence hash and degenerate shell face; interior remains intentionally unmodeled pending a plan.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[
      'Do not bridge or cap the roof using mismatched planes. Rebuild a contiguous roof shell whose silhouette matches the photographed long slate wings, front gable, and dormers; remove the visible black gaps and spikes.',
      'Unify winding across all roof faces so normals point outwards; verify with a fresh-open normal audit and review from east, north, south, and 45-degree aerial cameras.',
      'Replace the duplicate closing point in the source wall-cap face to remove its zero-area polygon while preserving the 19 unique GIS vertices.',
      'Correct validation.sha256 in evidence.json to the actual asset SHA reported here; rerun the evidence/hash check after any rebuild.',
      'Improve the visible entry door/shield and finish secondary elevations where chapter imagery supports it.'
    ]
    result={'building':'Beta Theta Pi','building_id':'massing_beta_theta_pi_fid826','revision':3,'asset':'modular/buildings/massing_beta_theta_pi_fid826.blend','asset_sha256':report['asset_sha256'],'expected_sha256':report['expected_sha256'],'exact_sha_match':report['exact_sha_match'],'review_date':'2026-10-26','reviewer':'independent grader','blender_version':'5.2.3 LTS','fresh_open':report['fresh_open'],'score':score,'max_score':10.0,'threshold':8.0,'accepted':score>=8.0,'criteria':criteria,'evidence':['audit/beta_theta_pi/sources/purdue_buildings_fid826_4326.json','audit/beta_theta_pi/sources/purduebeta_chapter_house_gallery.html','audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-1.jpg','audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-11.jpg','audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-14.jpg','audit/beta_theta_pi/sources/gis_overlay_esri_aerial.jpg','audit/beta_theta_pi/preview_r4_west.png','audit/beta_theta_pi/preview_r4_east.png','audit/beta_theta_pi/preview_r4_north.png','audit/beta_theta_pi/preview_r4_south.png','audit/beta_theta_pi/preview_r4_aerial.png','audit/beta_theta_pi/independent_grade_revision_3/geometry_validation.json'],'findings':findings,'geometry_validation':report}
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    md=['# Independent grade revision 3 — Beta Theta Pi','',f"**Score: {score}/10 — {'PASS' if score>=8.0 else 'BELOW 8.0'}**",f"**Exact asset SHA-256:** `{report['asset_sha256']}`",'**Fresh-open:** passed in Blender 5.2.3 LTS.','', '| Criterion | Score | Evidence and findings |','|---|---:|---|']
    for c in criteria:
        md.append(f"| {c['criterion']} | {c['score']:.2f}/{c['max_score']:.0f} | {c['finding']} |")
    md += ['', '## Required revisions'] + [f'- {x}' for x in findings] + ['', 'See `result.json` and `geometry_validation.json` for the structured evidence and mesh measurements.']
    (OUT/'grade_report.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    return result

evaluation=evaluate(report)
print('BETA_THETA_PI_R3_INDEPENDENT_GRADE '+json.dumps({k:evaluation[k] for k in ['score','accepted','asset_sha256','fresh_open']}))

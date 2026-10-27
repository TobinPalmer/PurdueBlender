import bpy, bmesh, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/massing_beta_theta_pi_fid826.blend'
OUT=ROOT/'audit/beta_theta_pi/independent_grade_revision_4/fresh_open_findings.json'
SCENE='Building_massing_beta_theta_pi_fid826'
COLL='Asset_massing_beta_theta_pi_fid826'
assert bpy.data.scenes.get(SCENE) and bpy.data.collections.get(COLL)
scene=bpy.data.scenes[SCENE]; coll=bpy.data.collections[COLL]
objs=list(coll.all_objects); meshes=[o for o in objs if o.type=='MESH']
roof=bpy.data.objects['GIS_FID826_Continuous_Closed_RoofShell']
walls=bpy.data.objects['BetaThetaPi_GIS_826_exact_perimeter_walls']
def diagnostics(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
    out={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),
         'boundary_edges':sum(e.is_boundary for e in bm.edges),
         'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
         'zero_area_faces':sum(f.calc_area()<1e-9 for f in bm.faces),
         'upward_faces':sum(f.normal.z>1e-5 for f in bm.faces),
         'downward_faces':sum(f.normal.z< -1e-5 for f in bm.faces),
         'vertical_faces':sum(abs(f.normal.z)<=1e-5 for f in bm.faces)}
    bm.free(); return out
ring_data=json.loads((ROOT/'audit/beta_theta_pi/sources/purdue_buildings_fid826_4326.json').read_text())
feature=ring_data['features'][0]
ring_ll=feature['geometry']['rings'][0]
src=[((lon-(-86.9137))*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring_ll]
if math.dist(src[0],src[-1])<1e-5:src.pop()
base=[]
for v in walls.data.vertices:
    p=walls.matrix_world@v.co
    if abs(p.z)<1e-5:base.append((round(p.x,7),round(p.y,7)))
base=list(dict.fromkeys(base))
errs=[min(math.dist(p,q) for q in base) for p in src]
all_zero=[]
materials={}
image_dependencies=[]
for obj in meshes:
    for p in obj.data.polygons:
        if p.area < 1e-9: all_zero.append({'object':obj.name,'polygon':p.index,'area':p.area})
    for slot in obj.material_slots:
        m=slot.material
        if m: materials[m.name]=[n.type for n in m.node_tree.nodes] if m.use_nodes and m.node_tree else []
for im in bpy.data.images:
    if im.source=='FILE':
        path=Path(bpy.path.abspath(im.filepath))
        image_dependencies.append({'name':im.name,'path':str(path),'exists':path.exists(),'packed':bool(im.packed_file)})
pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
roofdiag=diagnostics(roof); walldiag=diagnostics(walls)
report={'fresh_open':True,'blender_version':bpy.app.version_string,
 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'asset_size_bytes':ASSET.stat().st_size,
 'scene':scene.name,'collection':coll.name,'collection_objects':len(objs),'mesh_objects':len(meshes),
 'bounds_world_m':bounds,'source_feature_id':feature['attributes'].get('FID'),
 'source_building_name':feature['attributes'].get('BUILDING_N'),'source_address':feature['attributes'].get('ADDRESS'),
 'source_unique_ring_vertices':len(src),'wall_base_unique_vertices':len(base),
 'footprint_max_nearest_vertex_error_m':max(errs),'footprint_rms_nearest_vertex_error_m':math.sqrt(sum(e*e for e in errs)/len(errs)),
 'roof_shell_object':roof.name,'roof_shell_diagnostics':roofdiag,
 'roof_top_facets_upward':roofdiag['upward_faces'],'roof_top_facets_expected':17,
 'wall_shell_diagnostics':walldiag,'all_mesh_zero_area_face_count':len(all_zero),'all_mesh_zero_area_examples':all_zero[:20],
 'materials':materials,'file_image_dependencies':image_dependencies,
 'dormers':[o.name for o in objs if 'dormer' in o.name.lower() and 'gable' in o.name.lower()]}
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('INDEPENDENT_BETA_R4 '+json.dumps(report))

import bpy, bmesh, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/dauch_alumni_center.blend'
OUT=ROOT/'audit/dauch_alumni_center/independent_grade_r3/fresh_open_probe.json'
EXPECTED='de1e3735f6b9f206f53cc1affb13c208ae62e96f1322eea6aeed378af9d37d14'
COLL='Asset_dauch_alumni_center'; SCENE='Scene'
coll=bpy.data.collections.get(COLL); scene=bpy.data.scenes.get(SCENE)
assert coll is not None and scene is not None
objs=list(coll.all_objects); meshes=[o for o in objs if o.type=='MESH']
shell=bpy.data.objects.get('dauch_alumni_center_GIS_outline_primary_shell')
assert shell is not None and shell in objs
geom=json.loads((ROOT/'audit/dauch_alumni_center/dauch_alumni_center_gis_feature_71.json').read_text(encoding='utf-8'))
feature=geom['feature']; attrs=feature['attributes']; ring=feature['geometry']['rings'][0]
if math.dist(ring[0],ring[-1])<1e-12: ring=ring[:-1]
lat0=40.4274; lon0=-86.9137
origin=(241.19898675231826,-618.1852061961912)
projected=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
local=[(x-origin[0],y-origin[1]) for x,y in projected]
cross=sum(projected[i][0]*projected[(i+1)%len(projected)][1]-projected[(i+1)%len(projected)][0]*projected[i][1] for i in range(len(projected)))
area=cross/2
cx=sum((projected[i][0]+projected[(i+1)%len(projected)][0])*(projected[i][0]*projected[(i+1)%len(projected)][1]-projected[(i+1)%len(projected)][0]*projected[i][1]) for i in range(len(projected)))/(6*area)
cy=sum((projected[i][1]+projected[(i+1)%len(projected)][1])*(projected[i][0]*projected[(i+1)%len(projected)][1]-projected[(i+1)%len(projected)][0]*projected[i][1]) for i in range(len(projected)))/(6*area)
# Source-to-shell structural wall vertices, in the unchanged asset-local XY frame.
shell_xy=list(dict.fromkeys((round((shell.matrix_world@v.co).x,6),round((shell.matrix_world@v.co).y,6)) for v in shell.data.vertices))
errors=[min(math.hypot(x-a,y-b) for a,b in shell_xy) for x,y in local]
bm=bmesh.new(); bm.from_mesh(shell.data); bm.normal_update()
side={'outward':0,'inward':0,'ambiguous':0}; min_dot=1.0
for face in bm.faces:
 if abs(face.normal.z)>1e-5: continue
 fx=sum(v.co.x for v in face.verts)/len(face.verts); fy=sum(v.co.y for v in face.verts)/len(face.verts)
 i=min(range(len(local)),key=lambda j: math.hypot((local[j][0]+local[(j+1)%len(local)][0])/2-fx,(local[j][1]+local[(j+1)%len(local)][1])/2-fy))
 ax,ay=local[i]; bx,by=local[(i+1)%len(local)]
 ex,ey=((by-ay),-(bx-ax)) if area>0 else (-(by-ay),(bx-ax))
 d=face.normal.x*ex+face.normal.y*ey; min_dot=min(min_dot,d)
 side['outward' if d>1e-6 else 'inward' if d< -1e-6 else 'ambiguous']+=1
mesh_diag={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'signed_volume_m3':bm.calc_volume(signed=True) if all(e.is_manifold for e in bm.edges) else None,'side_normals':side,'min_outward_dot':min_dot,'caps':[{'mean_z':sum(v.co.z for v in f.verts)/len(f.verts),'normal_z':f.normal.z} for f in bm.faces if abs(f.normal.z)>0.99]}
bm.free()
all_points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
bounds=[[min(p[i] for p in all_points),max(p[i] for p in all_points)] for i in range(3)]
materials={}; image_deps=[]
for o in meshes:
 for slot in o.material_slots:
  m=slot.material
  if m and m.name not in materials: materials[m.name]=bool(m.use_nodes and m.node_tree)
for img in bpy.data.images:
 if img.source=='FILE':
  path=Path(bpy.path.abspath(img.filepath)); image_deps.append({'name':img.name,'filepath':img.filepath,'exists':path.exists(),'packed':bool(img.packed_file)})
roof=[]
for o in meshes:
 if 'roof' in o.name.lower() and ('membrane' in o.name.lower() or 'surface' in o.name.lower()):
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  roof.append({'name':o.name,'vertices':len(o.data.vertices),'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'materials':[s.material.name for s in o.material_slots if s.material]})
report={'fresh_open':True,'blender_version':bpy.app.version_string,'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'expected_sha256':EXPECTED,'sha_match':hashlib.sha256(ASSET.read_bytes()).hexdigest()==EXPECTED,'asset_size_bytes':ASSET.stat().st_size,'scene':scene.name,'collection':coll.name,'collection_is_scene_linked':any(c==coll for c in scene.collection.children),'collection_objects':len(objs),'mesh_objects':len(meshes),'gis_feature_id':attrs.get('FID'),'gis_name':attrs.get('BUILDING_N'),'gis_address':attrs.get('ADDRESS'),'source_ring_vertices':len(local),'shell_unique_xy_vertices':len(shell_xy),'footprint_max_nearest_error_m':max(errors),'footprint_rms_nearest_error_m':math.sqrt(sum(e*e for e in errors)/len(errors)),'gis_polygon_centroid_world_m':[cx,cy],'placement_origin_xy_m':list(origin),'origin_error_m':[origin[0]-cx,origin[1]-cy],'shell_topology':mesh_diag,'all_mesh_bounds_local_m':bounds,'roof_surfaces':roof,'used_material_count':len(materials),'all_used_materials_node_based':all(materials.values()),'external_image_dependencies':image_deps,'zero_area_mesh_faces':sum(p.area<1e-9 for o in meshes for p in o.data.polygons),'preview_images':['audit/dauch_alumni_center/dauch_alumni_center_r3_overview.png','audit/dauch_alumni_center/dauch_alumni_center_r3_roof_profile.png','audit/dauch_alumni_center/dauch_alumni_center_r3_sign_detail.png']}
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('DAUCH_R3_PROBE '+json.dumps(report))

import bpy, bmesh, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/dauch_alumni_center.blend'
OUT=ROOT/'audit/dauch_alumni_center/independent_grade_r2/fresh_open_findings.json'
COLL_NAME='Asset_dauch_alumni_center'
SCENE_NAME='Scene'
coll=bpy.data.collections.get(COLL_NAME); scene=bpy.data.scenes.get(SCENE_NAME)
assert coll is not None and scene is not None
objs=list(coll.all_objects); meshes=[o for o in objs if o.type=='MESH']
shell=bpy.data.objects.get('dauch_alumni_center_GIS_outline_primary_shell')
assert shell is not None and shell in objs
def diag(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
    caps=[{'mean_z':sum(v.co.z for v in f.verts)/len(f.verts),'normal_z':f.normal.z}
          for f in bm.faces if abs(f.normal.z)>0.99]
    d={'verts':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),
       'boundary_edges':sum(e.is_boundary for e in bm.edges),
       'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
       'manifold_edges_with_inconsistent_winding':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),
       'zero_area_faces':sum(f.calc_area()<1e-9 for f in bm.faces),
       'upward_faces':sum(f.normal.z>1e-5 for f in bm.faces),
       'downward_faces':sum(f.normal.z< -1e-5 for f in bm.faces),
       'vertical_faces':sum(abs(f.normal.z)<=1e-5 for f in bm.faces),
       'horizontal_cap_faces':caps,
       'signed_volume_m3':bm.calc_volume(signed=True) if bm.edges and all(e.is_manifold for e in bm.edges) else None}
    bm.free(); return d
geom=json.loads((ROOT/'audit/dauch_alumni_center/dauch_alumni_center_gis_feature_71.json').read_text())
f=geom['feature']; attrs=f['attributes']; ring=f['geometry']['rings'][0]
if math.dist(ring[0],ring[-1])<1e-12:ring=ring[:-1]
lat0=40.4274; lon0=-86.9137
projected=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
origin=(241.19898675231826,-618.1852061961912)
source_local=[(x-origin[0],y-origin[1]) for x,y in projected]
cross=sum(projected[i][0]*projected[(i+1)%len(projected)][1]-projected[(i+1)%len(projected)][0]*projected[i][1] for i in range(len(projected)))
area=cross*0.5
cx=sum((projected[i][0]+projected[(i+1)%len(projected)][0])*(projected[i][0]*projected[(i+1)%len(projected)][1]-projected[(i+1)%len(projected)][0]*projected[i][1]) for i in range(len(projected)))/(6*area)
cy=sum((projected[i][1]+projected[(i+1)%len(projected)][1])*(projected[i][0]*projected[(i+1)%len(projected)][1]-projected[(i+1)%len(projected)][0]*projected[i][1]) for i in range(len(projected)))/(6*area)
shell_pts=[]
for v in shell.data.vertices:
    p=shell.matrix_world@v.co
    shell_pts.append((p.x,p.y,p.z))
source_unique=len(source_local)
shell_xy=list(dict.fromkeys((round(x,6),round(y,6)) for x,y,z in shell_pts))
errors=[min(math.hypot(x-a,y-b) for a,b in shell_xy) for x,y in source_local]
bm_shell=bmesh.new(); bm_shell.from_mesh(shell.data); bm_shell.normal_update()
side_facing={'expected_outward':0,'inward':0,'ambiguous':0,'min_expected_dot':None}
for face in bm_shell.faces:
    if abs(face.normal.z)>1e-5:continue
    cx_face=sum(v.co.x for v in face.verts)/len(face.verts)
    cy_face=sum(v.co.y for v in face.verts)/len(face.verts)
    nearest=min(range(len(source_local)),key=lambda i: math.hypot((source_local[i][0]+source_local[(i+1)%len(source_local)][0])*0.5-cx_face,(source_local[i][1]+source_local[(i+1)%len(source_local)][1])*0.5-cy_face))
    ax,ay=source_local[nearest]; bx,by=source_local[(nearest+1)%len(source_local)]
    # For a CCW ring, the outward edge normal points right; reverse for CW.
    ex,ey=(by-ay,-(bx-ax)) if area>0 else (-(by-ay),bx-ax)
    dot=face.normal.x*ex+face.normal.y*ey
    side_facing['expected_outward' if dot>1e-6 else 'inward' if dot< -1e-6 else 'ambiguous']+=1
    side_facing['min_expected_dot']=dot if side_facing['min_expected_dot'] is None else min(side_facing['min_expected_dot'],dot)
bm_shell.free()
allpts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
bounds=[[min(p[i] for p in allpts),max(p[i] for p in allpts)] for i in range(3)]
materials={}; file_images=[]; zero=[]
for o in meshes:
    for p in o.data.polygons:
        if p.area<1e-9:zero.append({'object':o.name,'polygon':p.index,'area':p.area})
    for s in o.material_slots:
        m=s.material
        if m and m.name not in materials:
            materials[m.name]=[n.type for n in m.node_tree.nodes] if m.use_nodes and m.node_tree else []
for im in bpy.data.images:
    if im.source=='FILE':
        path=Path(bpy.path.abspath(im.filepath))
        file_images.append({'name':im.name,'filepath':im.filepath,'exists':path.exists(),'packed':bool(im.packed_file)})
report={'fresh_open':True,'blender_version':bpy.app.version_string,
 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'asset_size_bytes':ASSET.stat().st_size,
 'scene':scene.name,'collection':coll.name,'collection_objects':len(objs),'mesh_objects':len(meshes),
 'shell_name':shell.name,'shell_local_bounds_m':[[min(p[i] for p in shell_pts),max(p[i] for p in shell_pts)] for i in range(3)],
 'shell_topology':diag(shell),'gis_feature_id':attrs.get('FID'),'gis_building_name':attrs.get('BUILDING_N'),
 'gis_address':attrs.get('ADDRESS'),'gis_unique_outer_ring_vertices':source_unique,
 'gis_projected_signed_area_m2':area,'wall_side_normal_orientation':side_facing,
 'calculated_source_polygon_centroid_world_m':[cx,cy],
 'manifest_origin_minus_source_centroid_m':[origin[0]-cx,origin[1]-cy],
 'shell_unique_xy_vertices':len(shell_xy),'footprint_max_nearest_error_m':max(errors),
 'footprint_rms_nearest_error_m':math.sqrt(sum(e*e for e in errors)/len(errors)),
 'asset_bounds_local_m':bounds,'manifest_placement_origin_xy_m':list(origin),
 'manifest_expected_world_xy_bounds_m':[[210.53023408203018,271.106827481078],[-641.7151057933592,-601.2543227885984]],
 'manifest_world_bounds_from_local_and_origin':[[bounds[0][0]+origin[0],bounds[0][1]+origin[0]],[bounds[1][0]+origin[1],bounds[1][1]+origin[1]]],
 'materials':materials,'file_image_dependencies':file_images,'all_mesh_zero_area_face_count':len(zero),
 'zero_area_examples':zero[:20],
 'feature_object_counts':{'site_sign':sum('site_sign' in o.name.lower() or 'site sign' in o.name.lower() for o in objs),
   'sign_planting':sum(any(t in o.name.lower() for t in ('site_sign_west_evergreen','site_sign_east_evergreen')) for o in objs),
   'schematic_interior':sum('schematic' in o.name.lower() for o in objs),'flagpoles':sum('flagpole' in o.name.lower() for o in objs)}}
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('INDEPENDENT_DAUC_R2 '+json.dumps(report))

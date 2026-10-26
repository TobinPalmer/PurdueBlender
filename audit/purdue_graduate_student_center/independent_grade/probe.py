import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend'
METRICS=json.loads((ROOT/'audit/purdue_graduate_student_center/build_metrics.json').read_text(encoding='utf-8'))
GEO=json.loads((ROOT/'audit/purdue_graduate_student_center/sources/purdue_gis_pgsc_fid526_2026-10-26.geojson').read_text(encoding='utf-8'))
MANIFEST=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
ID='massing_purdue_graduate_student_center_af9c5c7'
GARAGE_ID='massing_northwestern_parking_garage_979f1a2'
COL='Asset_'+ID
GARAGE_COL='Asset_'+GARAGE_ID
anchor=METRICS['placement_origin_xy_m']
source_feature=next(f for f in GEO['features'] if int(f.get('id',-1))==526)
ring=source_feature['geometry']['coordinates'][0][:-1]
lon0,lat0=-86.9137,40.4274
scale_x=111412.84*math.cos(math.radians(lat0)); scale_y=111040.0
source_xy=[((p[0]-lon0)*scale_x,(p[1]-lat0)*scale_y) for p in ring]
scene=bpy.context.scene
col=bpy.data.collections.get(COL)
errors=[]
if col is None: errors.append(f'missing expected collection {COL}')
objs=list(col.all_objects) if col else []
meshes=[o for o in objs if o.type=='MESH']
mesh_names=[o.name for o in meshes]
if bpy.data.scenes.get('Building_'+ID) is None: errors.append('missing expected named scene')
# The named structural shell is the appropriate comparison target; decorative fascia/canopy/furniture are not footprint walls.
shell=next((o for o in meshes if 'source-footprint brick volume' in o.name),None)
if shell is None: errors.append('missing GIS-derived structural shell')
shell_xy=[]
if shell:
    pts=[shell.matrix_world @ v.co for v in shell.data.vertices]
    zmin=min(p.z for p in pts)
    shell_xy=[(p.x+anchor[0],p.y+anchor[1]) for p in pts if abs(p.z-zmin)<1e-4]
# bidirectional nearest vertex estimate for closed polygon vertices, not a sampled edge Hausdorff.
def nearest_dist(p,arr): return min(math.hypot(p[0]-q[0],p[1]-q[1]) for q in arr) if arr else None
source_to_model=[nearest_dist(p,shell_xy) for p in source_xy]
model_to_source=[nearest_dist(p,source_xy) for p in shell_xy]
# asset bbox in world coordinates from mesh local bounds + source placement anchor
world_pts=[]
for o in meshes:
    world_pts.extend((o.matrix_world @ Vector(c)) for c in o.bound_box)
asset_world_bounds=[[min(p[i] for p in world_pts)+ (anchor[i] if i<2 else 0.0),max(p[i] for p in world_pts)+ (anchor[i] if i<2 else 0.0)] for i in range(3)] if world_pts else []
used_mats={m.name for o in objs if getattr(o.data,'materials',None) is not None for m in o.data.materials if m}
external_images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        try: path=Path(bpy.path.abspath(im.filepath)).resolve()
        except Exception: path=Path(im.filepath)
        if not path.exists(): external_images.append({'name':im.name,'path':str(path)})
# Compare actual neighboring garage massing geometry from its saved source library.
garage_rec=next(a for a in MANIFEST['assets'] if a['id']==GARAGE_ID)
garage_path=ROOT/'modular'/garage_rec['file']
garage_probe={'path':str(garage_path),'collection':GARAGE_COL,'mesh_count':None,'bounds_world_m':None,'loads':False}
try:
    with bpy.data.libraries.load(str(garage_path),link=False) as (src,dst):
        if GARAGE_COL in src.collections:
            dst.collections=[GARAGE_COL]
        else:
            garage_probe['error']=f'collection absent; found {src.collections[:10]}'
    garage_col=dst.collections[0] if dst.collections else None
    if garage_col:
        garage_objs=list(garage_col.all_objects)
        garage_meshes=[o for o in garage_objs if o.type=='MESH']
        garage_pts=[o.matrix_world @ Vector(c) for o in garage_meshes for c in o.bound_box]
        garage_probe.update({'loads':True,'object_count':len(garage_objs),'mesh_count':len(garage_meshes),
            'bounds_world_m':[[min(p[i] for p in garage_pts),max(p[i] for p in garage_pts)] for i in range(3)] if garage_pts else [],'mesh_topology':[{ 'object':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in garage_meshes]})
except Exception as e:
    garage_probe['error']=repr(e)
# AABB overlap is only a broad-phase diagnostic; do not treat it as a precise solid-intersection result.
# Compute a planar polygon centroid and test an upward ray through the actual garage mesh.
area2=sum(source_xy[i][0]*source_xy[(i+1)%len(source_xy)][1]-source_xy[(i+1)%len(source_xy)][0]*source_xy[i][1] for i in range(len(source_xy)))
centroid=(sum((source_xy[i][0]+source_xy[(i+1)%len(source_xy)][0])*(source_xy[i][0]*source_xy[(i+1)%len(source_xy)][1]-source_xy[(i+1)%len(source_xy)][0]*source_xy[i][1]) for i in range(len(source_xy)))/(3*area2),sum((source_xy[i][1]+source_xy[(i+1)%len(source_xy)][1])*(source_xy[i][0]*source_xy[(i+1)%len(source_xy)][1]-source_xy[(i+1)%len(source_xy)][0]*source_xy[i][1]) for i in range(len(source_xy)))/(3*area2))
ray_hits=[]
if garage_col and garage_meshes:
    go=garage_meshes[0]
    gverts=[go.matrix_world @ v.co for v in go.data.vertices]
    gpolys=[list(p.vertices) for p in go.data.polygons]
    tree=BVHTree.FromPolygons(gverts,gpolys,all_triangles=False)
    origin=Vector((centroid[0],centroid[1],-1.0)); direction=Vector((0,0,1))
    for _ in range(16):
        hit=tree.ray_cast(origin,direction,25.0)
        if hit[0] is None: break
        hp=hit[0]
        ray_hits.append({'z_m':hp.z,'face_index':hit[2]})
        origin=Vector((hp.x,hp.y,hp.z+0.001))
# AABB overlap is only a broad-phase diagnostic; do not treat it as a precise solid-intersection result.
aabb_overlap=None
if asset_world_bounds and garage_probe.get('bounds_world_m'):
    gb=garage_probe['bounds_world_m']
    lengths=[max(0.0,min(asset_world_bounds[i][1],gb[i][1])-max(asset_world_bounds[i][0],gb[i][0])) for i in range(3)]
    aabb_overlap={'axis_overlap_m':lengths,'aabb_overlap_volume_m3':math.prod(lengths)}
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'asset_id':ID,'asset_path':str(ASSET),'asset_sha256':sha,'expected_sha256':'f3133fc447a1d9cc29db970dd286e417ac08b9ced6cdcb07c031bba1d878b25b','sha_matches_expected':sha=='f3133fc447a1d9cc29db970dd286e417ac08b9ced6cdcb07c031bba1d878b25b',
    'scene_name':bpy.context.scene.name,'collection_name':col.name if col else None,'object_count':len(objs),'mesh_count':len(meshes),'used_material_count':len(used_mats),'used_materials':sorted(used_mats),
    'placement_origin_xy_m':anchor,'structural_shell_name':shell.name if shell else None,'structural_shell_lower_vertices_world_m':shell_xy,
    'source_gis_fid':source_feature['id'],'source_gis_name':source_feature['properties'].get('BUILDING_N'),'source_polygon_vertices_world_m':source_xy,
    'source_to_model_vertex_nearest_max_m':max(source_to_model) if source_to_model else None,'source_to_model_vertex_nearest_mean_m':sum(source_to_model)/len(source_to_model) if source_to_model else None,
    'model_to_source_vertex_nearest_max_m':max(model_to_source) if model_to_source else None,'asset_world_bounds_m':asset_world_bounds,
    'external_unpacked_images':external_images,'garage':garage_probe,'asset_garage_aabb_overlap':aabb_overlap,'source_polygon_centroid_world_m':centroid,'garage_vertical_ray_hits_at_pgsc_centroid':ray_hits,'errors':errors}
OUT=ROOT/'audit/purdue_graduate_student_center/independent_grade/model_probe.json'
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))



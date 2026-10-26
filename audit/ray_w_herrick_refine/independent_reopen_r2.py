import bpy, hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit/ray_w_herrick_refine'
ASSET = AUDIT / 'ray_w_herrick_r2_candidate.blend'
EXPECTED = '5dfe15ad317dad3661fab756b312e2d0ce2de9b64b53bb3ecb0523a93525bbbf'
sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
scene = bpy.context.scene
asset = bpy.data.collections.get('Asset_ray_w_herrick_laboratories')
if asset is None:
    raise RuntimeError('Expected Asset_ray_w_herrick_laboratories collection is missing')
objects = list(asset.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
materialless=[]
invalid_material_refs=[]
materials=set()
for obj in meshes:
    slots=[slot.material for slot in obj.material_slots]
    if not slots or all(m is None for m in slots):
        materialless.append(obj.name)
    if obj.data.polygons and any(p.material_index >= len(slots) or slots[p.material_index] is None for p in obj.data.polygons):
        invalid_material_refs.append(obj.name)
    materials.update(m for m in slots if m is not None)
image_nodes=[]
missing_images=[]
for material in materials:
    if not material.use_nodes:
        continue
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image:
            img=node.image
            path=bpy.path.abspath(img.filepath) if img.source == 'FILE' else None
            image_nodes.append({'material':material.name,'image':img.name,'source':img.source,'path':path,'packed':bool(img.packed_file)})
            if img.source=='FILE' and path and not Path(path).exists() and not img.packed_file:
                missing_images.append(path)
# Evaluated geometry bounds in the candidate's local scene frame.
dg=bpy.context.evaluated_depsgraph_get()
points=[]
for obj in meshes:
    ev=obj.evaluated_get(dg); mesh=ev.to_mesh()
    try:
        points.extend(ev.matrix_world @ v.co for v in mesh.vertices)
    finally:
        ev.to_mesh_clear()
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
# Independently compare the reopened foundation ring to the raw official GIS feature.
gis=json.loads((ROOT/'audit/batch_b_buildings/ray_w_herrick_laboratories_gis_feature.json').read_text(encoding='utf-8'))
evidence=json.loads((ROOT/'audit/batch_b_buildings/ray_w_herrick_laboratories_evidence.json').read_text(encoding='utf-8'))
origin=evidence['official_gis']['campus_placement_origin_xy_m']
ring=gis['geometry']['rings'][0]
source=[]
for lon,lat in ring[:-1]:
    source.append(((lon+86.9137)*84810.60416539927-origin[0],(lat-40.4274)*111040.0-origin[1]))
foundation=bpy.data.objects.get('HLAB raised foundation plinth')
if foundation is None:
    raise RuntimeError('Raised foundation plinth is missing')
verts=[foundation.matrix_world @ v.co for v in foundation.data.vertices]
foundation_ring=[]
seen=set()
for v in verts:
    if abs(v.z) < 1e-5:
        p=(float(v.x),float(v.y))
        key=(round(p[0],6),round(p[1],6))
        if key not in seen:
            seen.add(key); foundation_ring.append(p)
def point_segment_distance(p,a,b):
    dx=b[0]-a[0]; dy=b[1]-a[1]
    den=dx*dx+dy*dy
    if den==0:return math.hypot(p[0]-a[0],p[1]-a[1])
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))
def nearest_to_ring(p,poly):
    return min(point_segment_distance(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))
def hausdorff(A,B):
    return max(max(nearest_to_ring(p,B) for p in A),max(nearest_to_ring(p,A) for p in B))
def area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
source_ring_match={'raw_feature_vertex_count':len(source),'foundation_ring_unique_vertex_count':len(foundation_ring),'max_symmetric_vertex_to_segment_distance_m':hausdorff(source,foundation_ring) if len(foundation_ring)>=3 else None,'raw_transformed_gis_area_m2':area(source),'candidate_foundation_area_m2':area(foundation_ring),'area_difference_m2':abs(area(source)-area(foundation_ring)),'simplification_tolerance_m':0.25,'note':'Feature 878 raw ring transformed using documented project local-meter conversion and placement origin; comparison is against the saved foundation plinth bottom loop. This is the same GIS feature used to author the candidate and is not an independent wall survey.'}
asset_names={o.name for o in objects}
scene_only=sorted(o.name for o in scene.objects if o.name not in asset_names)
root_objects=[o for o in objects if o.name=='AssetRoot_ray_w_herrick_laboratories']
report={'candidate_asset':str(ASSET),'expected_sha256':EXPECTED,'sha256':sha,'hash_matches_expected':sha==EXPECTED,'fresh_reopen':True,'blender_version':bpy.app.version_string,'opened_file':bpy.data.filepath,'scene':scene.name,'scene_object_count':len(scene.objects),'collection':'Asset_ray_w_herrick_laboratories','collection_object_count':len(objects),'mesh_object_count':len(meshes),'unique_materials_used':len(materials),'materialless_meshes':materialless,'meshes_with_invalid_material_indices':invalid_material_refs,'file_backed_image_texture_nodes':image_nodes,'missing_external_images':missing_images,'linked_libraries':[lib.filepath for lib in bpy.data.libraries],'root_object_count':len(root_objects),'root_objects':[{'name':o.name,'matrix_world':[[float(x) for x in row] for row in o.matrix_world]} for o in root_objects],'evaluated_collection_bounds_local_m':bounds,'source_feature_identity':{'source':'Purdue ArcGIS BuildingShapesZip4 layer 0, feature 878','building_abbreviation':'HLAB','address':'177 S Russell Street','distinct_from':'historic HERL / FID 246 Herrick Acoustics'},'footprint_comparison':source_ring_match,'collection_nonbuilding_members':[o.name for o in objects if o.type in {'CAMERA','LIGHT'} or 'Preview ground' in o.name],'scene_objects_outside_asset_collection':scene_only,'collection_hierarchy':{c.name:{'direct_object_count':len(c.objects),'all_object_count':len(c.all_objects)} for c in bpy.data.collections},'limitations':['The model’s footprint is authored from Purdue feature 878; its close match does not constitute an independent survey.','The candidate collection includes preview-stage camera, lights, and a large preview ground object; remove these from the exported building library before master integration.','Campus marker/assembled neighborhood was not reviewed in this standalone candidate grade.']}
(AUDIT/'independent_reopen_r2.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))

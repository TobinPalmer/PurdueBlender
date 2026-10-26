import bpy,json,math
from pathlib import Path
asset=Path(r'modular/buildings/massing_purdue_university_daniel_turf_center_e69b7da.blend').resolve()
source=Path(r'audit/massing_purdue_university_daniel_turf_center_e69b7da/sources/purdue_buildings_fid208_query_2026-10-26.json').resolve()
evidence=Path(r'audit/massing_purdue_university_daniel_turf_center_e69b7da/reopen_validation.json').resolve()
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
cid='massing_purdue_university_daniel_turf_center_e69b7da'
coll=bpy.data.collections.get('Asset_'+cid)
obj=bpy.data.objects.get('Purdue University Daniel Turf Center')
assert scene and scene.name=='Building_'+cid
assert coll is not None and len(coll.objects)==1 and coll.objects[0] is obj
assert obj and obj.type=='MESH'
assert len(obj.modifiers)==0
assert obj.get('raw_gis_extrution_uninterpreted') == 14
assert obj.get('gis_extrution_used_for_height') is False
assert obj.get('photo_facade_orientation') == 'South-facing long elevation (negative Y)'
assert 'window band' in obj.get('facade_detail_method','')
assert len(obj.data.materials) >= 3
with source.open(encoding='utf-8-sig') as f: feature=json.load(f)['features'][0]
ring=feature['geometry']['rings'][0]
pts=[]
for lon,lat,*_ in ring:
    pts.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
if pts[0]==pts[-1]: pts.pop()
mesh_pts=[(v.co.x,v.co.y) for v in obj.data.vertices]
xy_error=max(min(math.hypot(a[0]-b[0],a[1]-b[1]) for b in mesh_pts) for a in pts)
edge_face_counts={e.index:0 for e in obj.data.edges}
for p in obj.data.polygons:
    for i in p.edge_keys:
        e=obj.data.edges.get if False else None
# Count polygon edge use by vertex pair.
uses={tuple(sorted(e.vertices)):0 for e in obj.data.edges}
for p in obj.data.polygons:
    vs=list(p.vertices)
    for i,a in enumerate(vs):
        b=vs[(i+1)%len(vs)]
        uses[tuple(sorted((a,b)))]+=1
nonmanifold=[k for k,v in uses.items() if v!=2]
# Evaluated bounds include object world matrix and any modifiers; compare to source bounds.
coords=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
result={
 'asset_id':cid,'asset_path':str(asset.relative_to(Path.cwd())).replace('\\','/'),
 'reopened_in_blender':bpy.app.version_string,'scene_name':scene.name,'scene_object_count':len(bpy.data.objects),
 'export_collection':coll.name,'collection_object_names':[o.name for o in coll.objects],
 'object_type':obj.type,'mesh_vertices':len(obj.data.vertices),'mesh_edges':len(obj.data.edges),'mesh_faces':len(obj.data.polygons),
 'modifier_count':len(obj.modifiers),'local_bounds_m':bounds,'object_location':list(obj.location),
 'gis_fid':feature['attributes']['FID'],'gis_name':feature['attributes']['BUILDING_N'],'gis_address':feature['attributes']['ADDRESS'],
'gis_extrution_raw_uninterpreted':obj.get('raw_gis_extrution_uninterpreted'),'gis_extrution_used_for_height':obj.get('gis_extrution_used_for_height'),
'height_basis':obj.get('height_basis'),'roof_basis':obj.get('roof_basis'),
'photo_facade_orientation':obj.get('photo_facade_orientation'),'photo_to_facade_mapping':obj.get('photo_to_facade_mapping'),
'facade_detail_method':obj.get('facade_detail_method'),'facade_detail_uncertainty':obj.get('facade_detail_uncertainty'),
'material_names':[m.name for m in obj.data.materials],
 'source_ring_unique_vertex_count':len(pts),'footprint_vertex_max_error_m':xy_error,'nonmanifold_mesh_edges':len(nonmanifold),
 'nonmanifold_edge_details':[{'verts':list(k),'use_count':v,'coords':[[round(obj.data.vertices[i].co.x,5),round(obj.data.vertices[i].co.y,5),round(obj.data.vertices[i].co.z,5)] for i in k]} for k,v in uses.items() if v!=2],
 'unpacked_external_images':external,'render_files':['audit/'+cid+'/renders/daniel_turf_center_top.png','audit/'+cid+'/renders/daniel_turf_center_oblique.png'],
 'max_allowed_footprint_vertex_error_m':0.001,
 'result':'PASS' if xy_error<=0.001 and not nonmanifold and not external and len(coll.objects)==1 and obj.get('gis_extrution_used_for_height') is False else 'FAIL'
}
evidence.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))

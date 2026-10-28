"""Fresh-open structural and source-polygon checks for Slayter's standalone library."""
import bpy, json, math, os, bmesh
from mathutils import Vector
here=os.path.dirname(os.path.abspath(__file__))
feature=json.load(open(os.path.join(here,'source_feature_228_raw.json'),encoding='utf-8'))
assert bpy.data.filepath and bpy.data.filepath.endswith('.blend')
asset='massing_slayter_center_for_performing_arts_f45259b'
name='Slayter Center for Performing Arts'
obj=bpy.data.objects.get(name)
coll=bpy.data.collections.get('Asset_'+asset)
assert obj and obj.type=='MESH' and coll and list(coll.objects)==[obj]
assert obj.get('asset_id')==asset and obj.get('source_feature_id')==228
ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
lat0,lon0=40.4274,-86.9137
poly=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
def contains(x,y):
    inside=False
    for i,(x1,y1) in enumerate(poly):
        x2,y2=poly[(i+1)%len(poly)]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: inside=not inside
    return inside
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps)
verts=[obj.matrix_world@v.co for v in ev.data.vertices]
struct_idx={idx for p in ev.data.polygons if p.material_index!=7 for idx in p.vertices}
outside_all=[i for i,p in enumerate(verts) if not contains(p.x,p.y)]
outside_struct=[i for i in struct_idx if not contains(verts[i].x,verts[i].y)]
bm=bmesh.new(); bm.from_mesh(ev.data)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
loose=sum(not e.link_faces for e in bm.edges)
boundary=sum(e.is_boundary for e in bm.edges)
nonmanifold_samples=[]
for e in bm.edges:
    if not e.is_manifold:
        linked=sorted({f.material_index for f in e.link_faces})
        nonmanifold_samples.append({'edge_midpoint':[round((e.verts[0].co[i]+e.verts[1].co[i])*.5,3) for i in range(3)],'edge_face_count':len(e.link_faces),'linked_material_indices':linked})
        if len(nonmanifold_samples)>=20: break
bm.free()
result={
 'file':bpy.data.filepath,'asset_id':asset,'source_feature_id':228,
 'collection_object_count':len(coll.objects),'vertex_count':len(ev.data.vertices),'face_count':len(ev.data.polygons),
 'material_names':[m.name for m in ev.data.materials],
 'external_image_paths':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file],
 'bounds_m':{'x':[min(v.x for v in verts),max(v.x for v in verts)],'y':[min(v.y for v in verts),max(v.y for v in verts)],'z':[min(v.z for v in verts),max(v.z for v in verts)]},
 'point_in_source_polygon':{'all_mesh_vertices':len(verts),'outside_all':len(outside_all),'structural_vertices':len(struct_idx),'outside_structural':len(outside_struct),'outside_terrain_or_all':len(outside_all)-len(outside_struct)},
 'outside_vertex_samples':[{'index':i,'xyz':[round(verts[i].x,3),round(verts[i].y,3),round(verts[i].z,3)],'materials':sorted({ev.data.materials[p.material_index].name for p in ev.data.polygons if i in p.vertices})} for i in outside_all],
 'topology_counts':{'non_manifold_edges':nonmanifold,'boundary_edges':boundary,'loose_edges':loose,'samples':nonmanifold_samples},
 'source_stage_dimensions_m':{'front_width':56*.3048,'back_width':34*.3048,'depth':46*.3048},
 'height_status':'estimated; tripod apex is modeled at 12.35 m; official sources do not publish building elevations',
 'checks':{'stable_id':obj.get('asset_id')==asset,'one_object_export':len(coll.objects)==1,'within_polygon_structural':len(outside_struct)==0,'within_polygon_all':len(outside_all)==0,'all_materials_portable':not [im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]}
}
out=os.path.join(here,'validation.json')
json.dump(result,open(out,'w',encoding='utf-8'),indent=2)
print('SLAYTER_VALIDATION='+json.dumps(result))

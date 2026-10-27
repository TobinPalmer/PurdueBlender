import bpy, bmesh, json, hashlib, math
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd()
asset=ROOT/'modular/buildings/massing_von_s_d207e41.blend'
expected_sha='4c2715c05d93ec977e878a231355fe465268d7ab32be798ff12262cfb92a0f76'
actual_sha=hashlib.sha256(asset.read_bytes()).hexdigest()
assert actual_sha==expected_sha, (actual_sha,expected_sha)
scene=bpy.context.scene
obj=bpy.data.objects.get("Von's")
coll=bpy.data.collections.get('Asset_massing_von_s_d207e41')
assert obj is not None and obj.type=='MESH'
mesh=obj.data
verts=[obj.matrix_world @ v.co for v in mesh.vertices]
world_bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
src=json.loads((ROOT/'audit/von_s/sources/osm_way_116427236_footprint.json').read_text(encoding='utf-8'))
ring=[Vector((p[0],p[1],0.0)) for p in src['projected_ring_m'][:-1]]
base=[v for v in verts if abs(v.z)<0.03]
dists=[min(math.hypot(v.x-p.x,v.y-p.y) for v in base) for p in ring]
bm=bmesh.new(); bm.from_mesh(mesh); bm.normal_update()
edge_count=len(bm.edges)
boundary=sum(e.is_boundary for e in bm.edges)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
degenerate=sum(f.calc_area()<1e-10 for f in bm.faces)
bm.free()
images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        images.append(im.filepath)
materials=sorted({m.name for m in mesh.materials if m})
uvs=[u.name for u in mesh.uv_layers]
report={
 'status':'PASS' if scene.name=='Building_massing_von_s_d207e41' and coll is not None and obj.name=="Von's" and len(dists)==8 and max(dists)<0.01 and not images and len(uvs)>=1 else 'FAIL',
 'check':'independent fresh Blender 5.2.3 read-only open',
 'blender_version':bpy.app.version_string,
 'asset_path':str(asset), 'asset_sha256':actual_sha,
 'scene':scene.name,'scene_object_count':len(scene.objects),
 'collection':coll.name if coll else None,'collection_object_count':len(coll.all_objects) if coll else None,
 'root_object':obj.name,'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),
 'world_bounds_m':world_bounds,'source_feature':'OSM way 116427236',
 'source_ring_vertex_count':len(ring),'base_vertices_within_3cm':len(base),
 'nearest_base_xy_error_m':dists,'maximum_nearest_base_xy_error_m':max(dists),
 'topology':{'edges':edge_count,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'degenerate_faces':degenerate},
 'uv_layers':uvs,'materials':materials,'unpacked_external_images':images,
 'interior':'not modeled; source record documents no public floor plan found',
 'reviewed_previews':['previews/von_s_three_quarter.png','previews/von_s_state_street_facade.png','previews/von_s_mural_detail.png','previews/von_s_roof_footprint.png']}
out=ROOT/'audit/von_s/independent_grade_r1/fresh_open_validation.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

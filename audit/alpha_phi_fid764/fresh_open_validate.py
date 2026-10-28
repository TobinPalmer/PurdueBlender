import bpy, bmesh, json, os
HERE=os.path.dirname(__file__)
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841331_735e92f.blend')
with open(os.path.join(HERE,'build_config.json'),encoding='utf8') as f: cfg=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
assert obj is not None and coll is not None and obj in coll.objects[:]
assert len(coll.objects)==1 and obj.type=='MESH'
mesh=obj.data
bm=bmesh.new(); bm.from_mesh(mesh)
non_manifold=sum(not e.is_manifold for e in bm.edges)
boundary=sum(e.is_boundary for e in bm.edges)
bm.free()
bounds=[[min(v.co[i] for v in mesh.vertices),max(v.co[i] for v in mesh.vertices)] for i in range(3)]
material_names=[m.name for m in mesh.materials if m]
report={
    'fresh_open':'PASS',
    'asset_id':cfg['asset_id'],
    'file':os.path.relpath(ASSET,ROOT).replace('\\','/'),
    'object_name':obj.name,
    'collection_name':coll.name,
    'collection_object_count':len(coll.objects),
    'object_location':list(obj.location),
    'object_rotation_euler':list(obj.rotation_euler),
    'object_scale':list(obj.scale),
    'mesh_vertex_count':len(mesh.vertices),
    'mesh_polygon_count':len(mesh.polygons),
    'mesh_bounds_xyz_m':bounds,
    'material_count':len(material_names),
    'material_names':material_names,
    'non_manifold_edge_count':non_manifold,
    'boundary_edge_count':boundary,
    'topology_note':'Composite architectural mesh with intersecting and intentionally open decorative/interior parts; not a fabrication-ready watertight solid.',
    'master_integration':'Not checked or performed by this building worker.'
}
with open(os.path.join(HERE,'fresh_open_validation.json'),'w',encoding='utf8') as f: json.dump(report,f,indent=2)
print('FRESH_OPEN_VALIDATION='+json.dumps(report))

import bpy,json,bmesh
from mathutils import Vector
p='modular/buildings/massing_baptist_student_foundation_c3d8114.blend'
bpy.ops.wm.open_mainfile(filepath=p)
coll=bpy.data.collections.get('Asset_massing_baptist_student_foundation_c3d8114')
objs=list(coll.objects) if coll else []
verts=[]; mesh_details=[]
for o in objs:
 if o.type!='MESH': continue
 world=[o.matrix_world@v.co for v in o.data.vertices]
 verts.extend(world)
 if 'wall' in o.name.lower() or 'gable' in o.name.lower() or 'plane' in o.name.lower():
  bm=bmesh.new(); bm.from_mesh(o.data); boundary=sum(e.is_boundary for e in bm.edges); nonmanifold=sum(not e.is_manifold for e in bm.edges); bm.free()
  mesh_details.append({'name':o.name,'vertex_count':len(o.data.vertices),'face_count':len(o.data.polygons),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'bounds':[[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],[max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]]})
wall=bpy.data.objects.get('Red brick exterior walls from LiDAR outline')
outline=[(round((wall.matrix_world@wall.data.vertices[i].co).x,7),round((wall.matrix_world@wall.data.vertices[i].co).y,7)) for i in range(0,len(wall.data.vertices),4)] if wall else []
allmins=[min(v[i] for v in verts) for i in range(3)] if verts else []
allmaxs=[max(v[i] for v in verts) for i in range(3)] if verts else []
bpy_probe={'asset':p,'reopened':True,'scene':bpy.context.scene.name,'collection_count':sum(c.name=='Asset_massing_baptist_student_foundation_c3d8114' for c in bpy.data.collections),'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'bounds_min':allmins,'bounds_max':allmaxs,'structural_outline_xy':outline,'structural_bounds':[[min(x for x,y in outline),min(y for x,y in outline)],[max(x for x,y in outline),max(y for x,y in outline)]],'architectural_meshes':mesh_details,'library_links':[x.filepath for x in bpy.data.libraries if x.filepath],'images':[{'name':i.name,'filepath':i.filepath,'packed':i.packed_file is not None} for i in bpy.data.images]}
open('audit/baptist_student_foundation_independent_grade_r2/blender_probe.json','w').write(json.dumps(bpy_probe,indent=2))
print(json.dumps({k:v for k,v in bpy_probe.items() if k!='architectural_meshes'},indent=2))

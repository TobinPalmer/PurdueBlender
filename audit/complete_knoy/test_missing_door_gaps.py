import bpy, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')

def segment(o):
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    c=sum(pts,Vector())/len(pts)
    xx=sum((p.x-c.x)**2 for p in pts); yy=sum((p.y-c.y)**2 for p in pts)
    xy=sum((p.x-c.x)*(p.y-c.y) for p in pts)
    ang=.5*math.atan2(2*xy,xx-yy); d=Vector((math.cos(ang),math.sin(ang),0))
    proj=[(p-c).dot(d) for p in pts]
    return c+d*min(proj),c+d*max(proj),d

def make_bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(dg); me=ev.to_mesh()
    verts=[o.matrix_world@v.co for v in me.vertices]
    tree=BVHTree.FromPolygons(verts,[p.vertices[:] for p in me.polygons],all_triangles=False)
    ev.to_mesh_clear(); return tree

walls=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('KNOY_Ground_TracePartition_')]
walltrees={o.name:make_bvh(o) for o in walls}
findings={}
for ident in ['09','13','17','18','20','24']:
    wall=bpy.data.objects[f'KNOY_Ground_TracePartition_{ident}']
    side=bpy.data.objects[f'KNOY_Ground_TracePartition_{ident}_AccessSide']
    a0,a1,d=segment(wall); b0,b1,_=segment(side)
    p,q=min(((a,b) for a in (a0,a1) for b in (b0,b1)),key=lambda pq:(pq[0]-pq[1]).length)
    mid=(p+q)*.5; ang=math.atan2(d.y,d.x)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(mid.x,mid.y,1.22))
    door=bpy.context.object; door.name='TEMP_'+ident; door.dimensions=(.90,.045,2.10); door.rotation_euler[2]=ang
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    dbvh=make_bvh(door); hit=[]
    for wn,wt in walltrees.items():
        if f'_{ident}' in wn: continue
        pairs=dbvh.overlap(wt)
        if pairs: hit.append({'wall':wn,'face_pairs':len(pairs)})
    findings[ident]={'candidate_center_local_m':[round(mid.x,3),round(mid.y,3)],'candidate_yaw_deg':round(math.degrees(ang),2),'test_leaf_dimensions_m':[0.90,0.045,2.10],'intersections':hit,'status':'unresolved; low-resolution raster does not clearly distinguish a door leaf/swing at this crossing; test leaf overlaps another traced partition' if hit else 'clear at tested estimate; investigate source before adding'}
    bpy.data.objects.remove(door,do_unlink=True)
report={
  'asset':'modular/buildings/knoy_hall.blend',
  'source_plan':'audit/complete_knoy/Liu.pdf, Figure 3.19(d), thesis raster; not a door schedule or dimensioned construction plan',
  'retrieved':'2026-10-24',
  'method':'Reopened saved blend; centered 0.90 x 0.045 x 2.10 m candidate leaf at each omitted opening; Blender BVH triangle-overlap against traced partition meshes other than its own wall pair. This detects this candidate placement only; it does not prove that a differently located leaf is impossible.',
  'ground_opening_candidate_count':18,
  'modeled_illustrative_leaf_count':12,
  'omitted_candidate_ids':['09','13','17','18','20','24'],
  'status':'Six candidates remain unmodeled as doors pending a clearer plan or as-built schedule. They are not represented as confirmed door locations.',
  'candidates':findings,
}
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\door_gap_collision_audit.json'
with open(out,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))

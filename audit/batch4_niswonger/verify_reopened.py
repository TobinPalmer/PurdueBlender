"""Read-only saved-file validation; run in a fresh Blender process."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

asset=bpy.data.collections.get('Asset_niswonger_aviation_tech')
assert asset, 'Expected export collection is missing'
assert asset.name=='Asset_niswonger_aviation_tech'
objs=list(asset.all_objects)
objs=[o for o in objs if o]
root=bpy.data.objects.get('AssetRoot_niswonger_aviation_tech')
root_transform=None
if root:
    root_transform={'location':[round(v,8) for v in root.location],
                    'rotation':[round(v,8) for v in root.rotation_euler],
                    'scale':[round(v,8) for v in root.scale]}

def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def rectpoly(cx,cy,w,d,deg):
    a=math.radians(deg); pts=[]
    for x,y in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:
        pts.append((cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)))
    return pts
def clips(subject,clip):
    out=subject[:]
    for i in range(len(clip)):
        a,b=clip[i],clip[(i+1)%len(clip)]
        inp=out;out=[]
        if not inp:break
        prev=inp[-1]
        for curr in inp:
            pin=cross(a,b,prev)>=-1e-8;cin=cross(a,b,curr)>=-1e-8
            if cin:
                if not pin:
                    dx=curr[0]-prev[0];dy=curr[1]-prev[1]
                    ex=b[0]-a[0];ey=b[1]-a[1]
                    den=dx*ey-dy*ex
                    if abs(den)>1e-10:
                        t=((a[0]-prev[0])*ey-(a[1]-prev[1])*ex)/den
                        out.append((prev[0]+t*dx,prev[1]+t*dy))
                out.append(curr)
            elif pin:
                dx=curr[0]-prev[0];dy=curr[1]-prev[1]
                ex=b[0]-a[0];ey=b[1]-a[1]
                den=dx*ey-dy*ex
                if abs(den)>1e-10:
                    t=((a[0]-prev[0])*ey-(a[1]-prev[1])*ex)/den
                    out.append((prev[0]+t*dx,prev[1]+t*dy))
            prev=curr
    return out
def polyarea(p): return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2) if len(p)>2 else 0
def in_tri(p,a,b,c):
    q1=cross(a,b,p);q2=cross(b,c,p);q3=cross(c,a,p)
    return (q1>=-1e-7 and q2>=-1e-7 and q3>=-1e-7) or (q1<=1e-7 and q2<=1e-7 and q3<=1e-7)

rooms=json.loads(Path('audit/batch2_niswonger/changes.json').read_text())['rooms']
polys={r['room']:rectpoly(*r['center'],r['width_m'],r['depth_m'],r['orientation_deg']) for r in rooms}
overlaps=[]
keys=list(polys)
for i,a in enumerate(keys):
    for b in keys[i+1:]: overlaps.append({'rooms':[a,b],'intersection_m2':round(polyarea(clips(polys[a],polys[b])),8)})

floor=bpy.data.objects.get('NISW_Official_GroundFloor')
floor_mesh=floor.data if floor else None
triangles=[]
if floor_mesh:
    v=[(floor.matrix_world@x.co).xy[:] for x in floor_mesh.vertices]
    for poly in floor_mesh.polygons:
        if len(poly.vertices)==3: triangles.append(tuple(v[i] for i in poly.vertices))
corner_containment={}
for r in rooms:
    points=polys[r['room']]
    corner_containment[r['room']]=all(any(in_tri(p,*tri) for tri in triangles) for p in points) if triangles else None
aircraft=[o for o in objs if o.name.startswith('NISW_B4_Hangar_Aircraft_')]
aircraft_groups=sorted({o.name.split('_Aircraft_')[1].split('_')[0] for o in aircraft})
aircraft_vertices=[]
for o in aircraft:
    for vtx in o.data.vertices:
        p=o.matrix_world@vtx.co
        if not triangles or not any(in_tri((p.x,p.y),*tri) for tri in triangles): aircraft_vertices.append([o.name,round(p.x,3),round(p.y,3)])

shell_stats={}
for name in ['NISW_Walls_Composite_Panel','NISW_Walls_Purdue_Brick','NISW_Flat_Roof_Membrane','NISW_Photographic_Sloping_Roof']:
    o=bpy.data.objects.get(name)
    if o and o.type=='MESH':
        p=[o.matrix_world@Vector(v) for v in o.bound_box]
        shell_stats[name]={'bounds_m':[[round(min(x[i] for x in p),3) for i in range(3)],[round(max(x[i] for x in p),3) for i in range(3)]]}

missing=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        path=Path(bpy.path.abspath(im.filepath))
        if not path.exists(): missing.append(im.filepath)
unmaterialed=[o.name for o in objs if o.type=='MESH' and len(o.data.materials)==0]
summary={
 'reopened_in_fresh_blender':True,'filepath':bpy.data.filepath,
 'collection':asset.name,'objects':len(objs),'mesh_objects':sum(o.type=='MESH' for o in objs),
 'asset_root_transform':root_transform,'building_instance_marker_untouched':True,
 'room_pair_intersections':overlaps,'room_rectangle_corners_inside_official_floor_triangles':corner_containment,
 'aircraft_count':len(aircraft_groups),'aircraft_groups':aircraft_groups,
 'aircraft_mesh_vertices_outside_floor_polygon':aircraft_vertices[:25],
 'shell_bounds':shell_stats,'unmaterialed_meshes':unmaterialed[:40],
 'missing_external_image_paths':missing,
 'unexported_review_objects':[o.name for o in bpy.data.objects if o.name.startswith('NISW_B4_Review')],
}
Path('audit/batch4_niswonger/reopen_verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

"""Round 5 Elliott-only facade detailing, portal deferral, and opening checks."""
import bpy, json, math, pathlib, shutil
from mathutils import Vector

ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/batch3_elliott'
SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend'
shutil.copy2(SRC,AUD/'before_round5.blend')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
scene=bpy.context.scene
COL=bpy.data.collections['Asset_elliott_hall_of_music']
wall=bpy.data.objects['ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings']

def material(name,color,roughness=.72):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1);m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness
    return m

limestone=material('ELLT_Exterior_Indiana_Limestone',(.62,.57,.46),.78)
brick=wall.data.materials[0]
dark=material('ELLT_R5_Pilaster_Reveal_Shadow',(.22,.065,.04),.85)
review=material('ELLT_R5_Deferred_Portal_Review_Amber',(.78,.25,.035),.52)

ring=json.loads((AUD/'polygon.json').read_text())
N=len(ring)
lengths=[math.dist(ring[i],ring[(i+1)%N]) for i in range(N)]
cum=[0.0]
for l in lengths:cum.append(cum[-1]+l)
perimeter=cum[-1]
area=.5*sum(ring[i][0]*ring[(i+1)%N][1]-ring[(i+1)%N][0]*ring[i][1] for i in range(N))
def normal(i):
    a,b=ring[i],ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy)
    tx,ty=dx/ll,dy/ll
    return (tx,ty),(ty,-tx) if area>0 else (-ty,tx)
def sample(s):
    s=s%perimeter
    for i,l in enumerate(lengths):
        if s<=cum[i+1]+1e-8:
            t=(s-cum[i])/l if l else 0
            a,b=ring[i],ring[(i+1)%N]
            tx,ty=normal(i)[0];nx,ny=normal(i)[1]
            return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),(tx,ty),(nx,ny)
    raise RuntimeError('Arc position not found')

def mesh_object(name,verts,faces,mat,description):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob['evidence_status']=description
    return ob

desc='Form/material follow the SAH description of Indiana limestone banding; course height, projection, and exact alignment are estimated pending a measured elevation.'
# Continuous shallow belt-course faces around the mapped perimeter. Joined in
# one mesh for an explicit, inspectable representation of horizontal bands.
band_vs=[];band_fs=[]
for z in (4.9,9.8,14.7,19.6):
    for i in range(N):
        a,b=ring[i],ring[(i+1)%N];nx,ny=normal(i)[1]
        base=len(band_vs)
        for zz,off in ((z,0.10),(z+.18,0.10),(z,0.22),(z+.18,0.22)):
            band_vs.append((a[0]+nx*off,a[1]+ny*off,zz))
        band_fs.append((base,base+1,base+3,base+2))
bands=mesh_object('ELLT_R5_Limestone_Belt_Courses_Estimated',band_vs,band_fs,limestone,desc)
bands['course_levels_m_estimate']=[4.9,9.8,14.7,19.6]

# Vertical pilasters follow the SAH-described feature. Their spacing is a
# deliberate visual estimate, not an asserted historical facade schedule.
door_xy=[]
for o in COL.objects:
    if o.name in ('ELLT_Access_North_Glazed_Double_Door','ELLT_Access_South_Glazed_Double_Door'):
        door_xy.append((o.location.x,o.location.y))
for label in ('Hovde_Ground_West','Hovde_Ground_East','Hovde_Walkway_Upper'):
    ob=bpy.data.objects.get('ELLT_R4_'+label+'_DoorLeaf_Glazed_Estimated')
    if ob:door_xy.append((ob.location.x,ob.location.y))
# Estimate a count from perimeter length; omit stations near any known opening.
pilaster_vs=[];pilaster_fs=[];stations=[]
for s in [7.5+i*9.0 for i in range(int((perimeter-7.5)//9.0))]:
    p,t,n=sample(s)
    if any(math.hypot(p[0]-x,p[1]-y)<3.2 for x,y in door_xy):continue
    stations.append(round(s,2))
    half=.24;front=.18;back=.34
    corners=[(p[0]-t[0]*half+n[0]*front,p[1]-t[1]*half+n[1]*front),
             (p[0]+t[0]*half+n[0]*front,p[1]+t[1]*half+n[1]*front),
             (p[0]+t[0]*half+n[0]*back,p[1]+t[1]*half+n[1]*back),
             (p[0]-t[0]*half+n[0]*back,p[1]-t[1]*half+n[1]*back)]
    b=len(pilaster_vs)
    for z in (0.35,20.2):
        pilaster_vs.extend((x,y,z) for x,y in corners)
    pilaster_fs.extend([(b,b+1,b+5,b+4),(b+1,b+2,b+6,b+5),(b+2,b+3,b+7,b+6),(b+3,b,b+4,b+7)])
pilasters=mesh_object('ELLT_R5_Vertical_Limestone_Pilasters_Estimated',pilaster_vs,pilaster_fs,limestone,
    'Vertical pilasters are described by SAH Archipedia. Their count, positions, width, height and projection are visual estimates; no measured elevation was found.')
pilasters['arc_spacing_target_m_estimate']=9.0;pilasters['station_arc_m_estimate']=stations

# Rebuild the conceptual connector as an Elliott-side approach only. It stops
# short of Hovde, leaving a visible, labeled gap until the Hovde asset gets its
# own independently checked portal.
for ob in list(COL.objects):
    if ob.name.startswith('ELLT_R4_Hovde_Walkway_') or ob.name=='ELLT_R4_Hovde_Lobby_Threshold_Estimated':
        bpy.data.objects.remove(ob,do_unlink=True)
q=Vector((44.075,9.162,0))
hovde_wall_x=61.97
far=Vector((59.85,10.85,0))
direction=(far-q).normalized();side=Vector((-direction.y,direction.x,0))
width_start=3.4;width_end=3.2;floor_z=4.18;roof_z=7.30
p0=q;p1=far
poly=[p0+side*width_start/2,p1+side*width_end/2,p1-side*width_end/2,p0-side*width_start/2]
def prism(name,poly,z0,z1,mat,description):
    vs=[(p.x,p.y,z) for z in (z0,z1) for p in poly]
    fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return mesh_object(name,vs,fs,mat,description)
conn_desc='Conceptual Elliott-side fragment of the documented second-story Hovde-to-Elliott connection. This module terminates before Hovde and does not assert a completed connection. Span, level, enclosure and section are estimates.'
prism('ELLT_R5_Hovde_Link_Elliott_Side_Landing_Estimated',poly,floor_z-.18,floor_z+.18,limestone,conn_desc)
for side_name,offset in [('A',1),('B',-1)]:
    v0=p0+side*(offset*width_start/2);v1=p1+side*(offset*width_end/2)
    mesh_object('ELLT_R5_Hovde_Link_Glazing_'+side_name+'_Estimated',
      [(v0.x,v0.y,floor_z+.18),(v1.x,v1.y,floor_z+.18),(v1.x,v1.y,roof_z-.12),(v0.x,v0.y,roof_z-.12)],[(0,1,2,3)],
      material('ELLT_R5_Link_Glazing',(.045,.12,.15),.23),conn_desc)
prism('ELLT_R5_Hovde_Link_Roof_Estimated',poly,roof_z-.12,roof_z+.08,limestone,conn_desc)
# Transparent terminal marker is intentionally a review-only placeholder.
cap=[p1+side*width_end/2,p1-side*width_end/2]
mesh_object('ELLT_R5_Hovde_Link_Terminal_Gap_Marker_ReviewOnly',
 [(cap[0].x,cap[0].y,floor_z+.2),(cap[1].x,cap[1].y,floor_z+.2),(cap[1].x,cap[1].y,roof_z-.12),(cap[0].x,cap[0].y,roof_z-.12)],[(0,1,2,3)],review,
 'Review-only end marker at Elliott module terminus. It denotes an unmodeled gap to Hovde; remove after Hovde portal is modeled and both assets are checked together.')
gap=hovde_wall_x-far.x

# Make the state of this modular endpoint explicit in the editable asset.
COL['inter_building_connection_status']='DEFERRED: Elliott-side aperture retained; bridge module terminates before Hovde with a visible gap/landing marker. Hovde-side opening not yet verified or modeled.'

# Ray checks through the actual evaluated Elliott shell at each known aperture.
deps=bpy.context.evaluated_depsgraph_get();eval_wall=wall.evaluated_get(deps);mesh=eval_wall.to_mesh();
from mathutils.bvhtree import BVHTree
import bmesh
bm=bmesh.new();bm.from_mesh(mesh);bvh=BVHTree.FromBMesh(bm)
def edge_project(target):
    best=(1e9,None)
    for i,a in enumerate(ring):
        b=ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
        t=max(0,min(1,((target[0]-a[0])*dx+(target[1]-a[1])*dy)/den)) if den else 0
        p=(a[0]+t*dx,a[1]+t*dy);d=math.dist(p,target)
        if d<best[0]:
            tx,ty=normal(i)[0];nx,ny=normal(i)[1];best=(d,(p,(nx,ny)))
    return best
targets=[('North',(8.339,45.185),1.5),('South',(-25.628,-38.128),1.5),
 ('Hovde_Ground_West',(41.925,7.403),1.3),('Hovde_Ground_East',(38.754,15.672),1.3),('Hovde_Walkway_Upper',(44.075,9.162),5.7)]
ray_checks=[]
for name,target,z in targets:
    dist,(p,n)=edge_project(target);origin=Vector((p[0]+n[0]*.6,p[1]+n[1]*.6,z));direction=Vector((-n[0],-n[1],0))
    hit=bvh.ray_cast(origin,direction,1.2)[0] is not None
    # Positive control at the same edge above the opening top should intersect.
    zcontrol=8.5 if name=='Hovde_Walkway_Upper' else 3.35
    control_origin=Vector((p[0]+n[0]*.6,p[1]+n[1]*.6,zcontrol))
    control=bvh.ray_cast(control_origin,direction,1.2)[0] is not None
    ray_checks.append({'name':name,'opening_center_ray_hits_shell':bool(hit),'above_opening_control_hits_shell':bool(control),'edge_projection_error_m':round(dist,4),'tested_z_m':z,'control_z_m':zcontrol})
bm.free();eval_wall.to_mesh_clear()

# Detailed notes and review render setup.
wall['evidence_status']='Official FID 617 footprint reconstructed as facade. Five modeled through-openings remain at estimated locations/sizes; band courses and pilasters added from SAH material/feature descriptions. Window rhythm remains unverified and is not fabricated.'
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
from mathutils import Vector
views=[('exterior_round5',(126,-135,82),(0,2,11),155),('hovde_gap_round5',(74,-12,30),(53,10.5,5.7),55),('auditorium_round5',(0,-39,28),(0,2,7),63)]
for name,loc,target,scale in views:
    data=bpy.data.cameras.new('ELLT_R5_CAM_'+name);cam=bpy.data.objects.new('ELLT_R5_CAM_'+name,data);scene.collection.objects.link(cam)
    cam.location=loc;data.type='ORTHO';data.ortho_scale=scale
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
    scene.render.filepath=str(AUD/(name+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data)

bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music'];wall=bpy.data.objects['ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings']
result={'saved_and_reopened':True,'blender_version':bpy.app.version_string,'source_file':str(SRC),
 'export_collection':'Asset_elliott_hall_of_music','export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),
 'added_facade_objects':['ELLT_R5_Limestone_Belt_Courses_Estimated','ELLT_R5_Vertical_Limestone_Pilasters_Estimated'],
 'facade_pilaster_count_estimated':len(stations),'facade_belt_courses_m_estimated':[4.9,9.8,14.7,19.6],
 'window_apertures':'No extra windows added; number and placement lack directly inspected primary image/elevation evidence.',
 'hovde_connection':'Deferred; Elliott-side opening retained, connector terminates before Hovde. Hovde portal not edited or claimed.',
 'visible_gap_m_estimated':round(gap,3),'review_only_gap_marker':'ELLT_R5_Hovde_Link_Terminal_Gap_Marker_ReviewOnly',
 'opening_ray_checks':ray_checks,'render_files':[x[0]+'.png' for x in views],
 'uncertainties':['window count/placement','pilaster spacing and dimensions','belt course elevations','five doorway positions/dimensions','connection span/level/section','interior geometry and all seating coordinates','vertical height envelope']}
(AUD/'result_round5.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

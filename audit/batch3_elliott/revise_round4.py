"""Round 4 evidence-led entrance, connection and circulation cleanup for Elliott."""
import bpy, json, math, pathlib, shutil
from mathutils import Vector

ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/batch3_elliott'
SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend'
BACKUP=AUD/'before_round4.blend'
if not BACKUP.exists():shutil.copy2(SRC,BACKUP)
bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music']
for ob in list(COL.objects):
    if ob.name.startswith('ELLT_R4_'):bpy.data.objects.remove(ob,do_unlink=True)
wall=next(o for o in COL.objects if o.name.startswith('ELLT_Official_GIS_Wall_R4_'))
ring=json.loads((AUD/'polygon.json').read_text())
N=len(ring)

def mat(name,color,rough=.75):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1);m.use_nodes=True
    bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bs: bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
    return m
brick=wall.data.materials[0] if wall.data.materials else mat('ELLT_Exterior_Red_Brick_Procedural',(.39,.105,.062),.82)
stone=mat('ELLT_Exterior_Indiana_Limestone',(.69,.65,.55),.82)
bronze=mat('ELLT_Access_Door_Bronze',(.085,.068,.044),.34)
glass=mat('ELLT_Access_Door_Glass',(.025,.08,.10),.2)
walk=mat('ELLT_Connection_Walkway_Indiana_Limestone_Estimated',(.54,.51,.44),.72)
bridge_glass=mat('ELLT_Connection_Bridge_Glazing_Estimated',(.045,.12,.15),.23)
dark=mat('ELLT_Connection_Bridge_Frame_Estimated',(.12,.10,.075),.42)

def edge_len(i): return math.dist(ring[i],ring[(i+1)%N])
seg=[edge_len(i) for i in range(N)]; cum=[0.0]
for L in seg:cum.append(cum[-1]+L)
area=.5*sum(ring[i][0]*ring[(i+1)%N][1]-ring[(i+1)%N][0]*ring[i][1] for i in range(N))
def point(i,t):
    a=ring[i];b=ring[(i+1)%N];return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
def tangent(i):
    dx=ring[(i+1)%N][0]-ring[i][0];dy=ring[(i+1)%N][1]-ring[i][1];ll=math.hypot(dx,dy);return dx/ll,dy/ll
def outward(tx,ty):return (ty,-tx) if area>0 else (-ty,tx)
def project(target):
    best=(1e9,None)
    for i,a in enumerate(ring):
        b=ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
        t=max(0,min(1,((target[0]-a[0])*dx+(target[1]-a[1])*dy)/den)) if den else 0
        q=point(i,t);d=math.dist(target,q)
        if d<best[0]:best=(d,(i,t,q))
    d,(i,t,q)=best
    return {'s':cum[i]+t*seg[i],'p':q,'i':i,'t':t,'tangent':tangent(i),'outward':outward(*tangent(i)),'distance':d}

# North/south doors retained at their currently documented Purdue-facing estimates.
old=json.loads((AUD/'result_round3_accessibility.json').read_text())['doors']
openings=[]
for item in old:
    q=project(item['xy'])
    openings.append(dict(label=item['name'],**q,width=item['width_m_estimate'],z0=0,z1=item['height_m_estimate'],kind='accessible'))
# SAH describes additional ground-level entrances between Elliott and Hovde.
# Candidate locations are inferred along the east-facing GIS edge, close to the
# mapped inter-building gap; neither exact coordinates nor door sizes are sourced.
for label,target in [('Hovde_Ground_West', (41.6,7.8)),('Hovde_Ground_East',(39.4,16.2))]:
    q=project(target); openings.append(dict(label=label,**q,width=1.9,z0=0,z1=2.6,kind='ground_between'))
# SAH and Purdue document the second-story Hovde walkway into Elliott's lobby.
# The Hovde asset's registered adjacent west/south wall is near x=61.97, y=8.84..13.96.
# This portal center is selected on Elliott's closest east GIS edge; vertical and
# width values remain estimates because no measured section/elevation was located.
q=project((44.075,9.162))
openings.append(dict(label='Hovde_Walkway_Upper',**q,width=3.4,z0=4.2,z1=7.2,kind='upper_walkway'))

# Rebuild shell strips with five source-led openings: north/south accessible
# doors, two ground entries between halls, and one upper bridge portal.
verts=[];faces=[]
levels=sorted(set([0.,2.6,3.,4.2,7.2,8.,12.,16.,20.,22.5]))
for i in range(N):
    s0=cum[i];s1=cum[i+1];L=seg[i]
    cuts={s0,s1}
    for o in openings:
        for x in (o['s']-o['width']/2,o['s']+o['width']/2):
            if s0+1e-7<x<s1-1e-7:cuts.add(x)
    cuts=sorted(cuts)
    for a,b in zip(cuts,cuts[1:]):
        if b-a<1e-5:continue
        mid=(a+b)/2; P0=point(i,(a-s0)/L);P1=point(i,(b-s0)/L)
        opening=next((o for o in openings if abs(mid-o['s'])<o['width']/2-1e-6),None)
        for z0,z1 in zip(levels,levels[1:]):
            if opening and z0>=opening['z0']-1e-6 and z1<=opening['z1']+1e-6:continue
            base=len(verts);verts.extend([(P0[0],P0[1],z0),(P1[0],P1[1],z0),(P1[0],P1[1],z1),(P0[0],P0[1],z1)])
            faces.append((base,base+1,base+2,base+3))
me=bpy.data.meshes.new('ELLT_R4_Official_GIS_Wall_Mesh');me.from_pydata(verts,[],faces);me.materials.append(brick);me.update()
oldmesh=wall.data;wall.data=me;bpy.data.meshes.remove(oldmesh)
wall.name='ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings'
wall['evidence_status']='Official 188-point GIS footprint rebuilt with north/south accessible doors, two SAH-described Hovde-side ground-entry openings, and one SAH/Purdue-described second-story bridge portal. Hovde-side locations, dimensions and vertical levels are estimated.'

# Remove round-three unsupported route ribbons and dimensioned clearance pads.
removed=[]
for o in list(COL.objects):
    if o.name.startswith('ELLT_Access_') and ('Estimated_Level_Interior_Route' in o.name or 'Estimated_Wheelchair_Clear_Space' in o.name):
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

def cube(name,loc,dim,ma,rot=0,desc='Estimated geometry; dimensions are not sourced.'):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o);o.dimensions=dim;o.rotation_euler.z=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);o['evidence_status']=desc;return o
def mesh_obj(name,vs,fs,ma,desc):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(vs,[],fs);me.materials.append(ma);me.update()
    o=bpy.data.objects.new(name,me);COL.objects.link(o);o['evidence_status']=desc;return o
def append_door(o):
    p=o['p'];tx,ty=o['tangent'];nx,ny=o['outward'];w=o['width'];z0=o['z0'];z1=o['z1'];th=z1-z0
    # Recessed opaque glazed slab and understated stone jamb/lintel. These are
    # architectural placeholders, not claims about leaf or surround dimensions.
    theta=math.atan2(ty,tx);center=(p[0]-nx*.08,p[1]-ny*.08,(z0+z1)/2)
    cube('ELLT_R4_'+o['label']+'_DoorLeaf_Glazed_Estimated',center,(w-.15,.10,th-.12),glass,theta)
    for side,u in [('L',-w/2),('R',w/2)]:
        cube('ELLT_R4_'+o['label']+'_Jamb_'+side,(p[0]+tx*u-nx*.02,p[1]+ty*u-ny*.02,(z0+z1)/2),(.18,.26,th+.08),stone,theta)
    cube('ELLT_R4_'+o['label']+'_Lintel',(p[0]-nx*.02,p[1]-ny*.02,z1+.07),(w+.36,.26,.16),stone,theta)
for o in openings[2:]:append_door(o)

# Bridge component: registered from Elliott's closest wall point to Hovde's
# modeled wall segment using their local placement metadata. It deliberately
# remains a modular Elliott-only object. No Hovde door geometry is altered.
start=(q['p'][0],q['p'][1]);end=(61.97,11.25);zfloor=4.18;zroof=7.30
dx=end[0]-start[0];dy=end[1]-start[1];L=math.hypot(dx,dy);phi=math.atan2(dy,dx)
nx,ny=-dy/L,dx/L
# The Elliott portal follows its oblique facade tangent while the Hovde target
# follows Hovde's modeled south-west wall. A tapered connector reconciles these
# two registered endpoints without imposing a false parallel rectangle.
tx0,ty0=q['tangent'];hw0=1.7;hw1=1.65
dot=tx0*nx+ty0*ny
nx1,ny1=(nx,ny) if dot>=0 else (-nx,-ny)
S0p=(start[0]+tx0*hw0,start[1]+ty0*hw0);S0m=(start[0]-tx0*hw0,start[1]-ty0*hw0)
S1p=(end[0]+nx1*hw1,end[1]+ny1*hw1);S1m=(end[0]-nx1*hw1,end[1]-ny1*hw1)
quad=[S0p,S1p,S1m,S0m]
def prism(name,poly,z0,z1,ma,desc):
    vs=[(x,y,z) for z in (z0,z1) for x,y in poly]
    fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(vs,[],fs);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o);o['evidence_status']=desc;return o
mesh_obj('ELLT_R4_Hovde_Walkway_Floor_Estimated',[(x,y,z) for x,y in quad for z in (zfloor-.18,zfloor+.18)],[(0,2,4,6),(1,7,5,3),(0,1,3,2),(2,3,7,6),(6,7,5,4),(4,5,1,0)],walk,'Purdue/SAH document a second-story walkway between Hovde and Elliott. Span and level are estimated from registered asset locations; no measured bridge plan/section was found.')
# Faceted glass sides follow the taper. Their framing and glazing are conceptual.
for side,(a0,a1) in [('A',(S0p,S1p)),('B',(S0m,S1m))]:
    vs=[(a0[0],a0[1],zfloor+.18),(a1[0],a1[1],zfloor+.18),(a1[0],a1[1],zroof-.12),(a0[0],a0[1],zroof-.12)]
    mesh_obj('ELLT_R4_Hovde_Walkway_Glazing_'+side+'_Estimated',vs,[(0,1,2,3)],bridge_glass,'Conceptual bridge glazing; presence, module, height and framing require photo/elevation verification.')
prism('ELLT_R4_Hovde_Walkway_Roof_Estimated',quad,zroof-.12,zroof+.08,stone,'The second-story connection is sourced; enclosure/roof form and dimensions are estimated pending a measured drawing or direct photograph review.')
# Slender framing members make the connector read as a glazed bridge instead of a solid duct.
for j,t in enumerate((.08,.32,.56,.80,.98)):
    for label,A0,A1 in [('A',S0p,S1p),('B',S0m,S1m)]:
        x=A0[0]*(1-t)+A1[0]*t;y=A0[1]*(1-t)+A1[1]*t
        cube('ELLT_R4_Hovde_Walkway_Frame_'+label+'_'+str(j),(x,y,(zfloor+zroof)/2),(.16,.16,zroof-zfloor-.05),dark,phi,'Estimated light bridge frame; exact structure is not available in measured sources.')
# Lobby threshold extension within Elliott, matching the portal's oblique axis.
mesh_obj('ELLT_R4_Hovde_Lobby_Threshold_Estimated',[(x-tx0*1.8,y-ty0*1.8,z) for x,y in (S0p,S0m) for z in (zfloor-.10,zfloor+.14)],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)],walk,'Conceptual threshold to Elliott main-floor lobby, supported by Purdue/SAH description of bridge destination; geometry estimated.')

# Tag existing chart-derived wheelchair symbols as indicative seat positions,
# not clearance footprints or a fully measured circulation plan.
if 'ELLT_B3_access' in bpy.data.objects:
    ob=bpy.data.objects['ELLT_B3_access'];ob.name='ELLT_Indicative_Wheelchair_Seat_Markers_Unscaled_Chart'
    ob['evidence_status']='Purdue seating chart indicates accessible seating; marker count/positions are a chart-informed visualization only. The chart is unscaled and does not prove clearance dimensions or routes.'

bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music'];wall=bpy.data.objects['ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings']
route_names=['ELLT_Access_North_Estimated_Wheelchair_Clear_Space','ELLT_Access_North_Estimated_Level_Interior_Route','ELLT_Access_South_Estimated_Wheelchair_Clear_Space','ELLT_Access_South_Estimated_Level_Interior_Route']
report={'saved_and_reopened':True,'source_file':str(SRC),'export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),'opening_count':len(openings),'openings':[{'name':o['label'],'xy':[round(o['p'][0],3),round(o['p'][1],3)],'width_estimate_m':o['width'],'z0_est_m':o['z0'],'z1_est_m':o['z1'],'nearest_edge_distance_m':round(o['distance'],4)} for o in openings],'removed_unsupported_route_and_clearance_meshes_this_execution':removed,'unsupported_route_and_clearance_names_verified_absent':{n:not any(o.name==n for o in COL.objects) for n in route_names},'bridge_estimated_span_m':round(L,3),'bridge_registered_endpoint_xy':list(end),'bridge_estimated_z_m':[zfloor,zroof],'remaining_window_apertures':'0; official photographic references were identified, but their facade pixels were not inspectable through the available web/browser tools, so no window count or spacing is asserted.','uncertainties':['Ground entrance position and dimensions','second-story bridge geometry, section, and exact endpoint','all facade window count/spacing pending image/elevation inspection','interior floor and accessible seating coordinates derived from unscaled chart','all vertical envelope dimensions']}
(AUD/'result_round4.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

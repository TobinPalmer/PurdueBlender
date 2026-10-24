import bpy, bmesh, math, json
from mathutils import Vector

src = bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend'), src
shell = bpy.data.objects['KRCH structural shell | GIS outline']
facade = bpy.data.collections['Facade_Details']

# Match the near southwest outside corner and street-facing facade in the Sasaki view.
base = next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z + 1.0) < 1e-4 for i in p.vertices))
ring = [shell.data.vertices[i].co.copy() for i in base.vertices]
top_z = max(v.co.z for v in shell.data.vertices if v.co.z > 15.0)
N = len(ring)

def box_mesh(name, specs, material, collection, orient=0.0, origin=(0.0,0.0)):
    vv=[]; ff=[]
    c=math.cos(orient); s=math.sin(orient); ox,oy=origin
    for (cx,cy,cz),(sx,sy,sz) in specs:
        k=len(vv)
        for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            lx=cx+x*sx/2; ly=cy+y*sy/2
            vv.append((ox+c*lx-s*ly,oy+s*lx+c*ly,cz+z*sz/2))
        ff.extend([(k,k+3,k+2,k+1),(k+4,k+5,k+6,k+7),(k,k+1,k+5,k+4),(k+1,k+2,k+6,k+5),(k+2,k+3,k+7,k+6),(k+3,k,k+4,k+7)])
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(vv,[],ff); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); ob['building_id']='krach_leadership_center'; return ob

def mat(name,color,rough=.55,metal=0.0,alpha=1.0,trans=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,alpha); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(*color,alpha); bs.inputs['Roughness'].default_value=rough
        bs.inputs['Metallic'].default_value=metal; bs.inputs['Alpha'].default_value=alpha
        if 'Transmission Weight' in bs.inputs: bs.inputs['Transmission Weight'].default_value=trans
        if 'IOR' in bs.inputs: bs.inputs['IOR'].default_value=1.45
    if alpha<1: m.surface_render_method='DITHERED'
    return m

brick=bpy.data.materials['KRACH_LEADERSHIP_CENTER | evidence palette textured masonry']
stone=bpy.data.materials['KRCH | Sasaki photo-backed pale limestone frame']
frame=mat('KRCH | dark bronze-gray facade mullion',(0.13,.15,.15),.35,.45)
glass=mat('KRCH | clear blue-gray lobby glazing',(.23,.38,.41),.1,0,.22,.18)

# Photo-backed opening dimensions and coordinates are interpretations, not surveyed.
# The two westernmost south-wall bays are replaced by the full-height outside-corner
# glazing and must not leave punched windows embedded behind its transparent panes.
west_windows=[-23.1,-18.6]
middle_windows=[-14.1,-9.6,-5.1,-0.6]
east_windows=[4.0,9.3,14.6,19.9,25.2,30.0]
window_levels=[4.88,8.78,12.68]
window_w=1.02; window_h=2.12
# The outer southwest corner is the start of the GIS south wall. The photo shows
# the tall framed bay at this actual end/corner, not at the interior notch.
edge_a=Vector((-35.13066864,-13.89586353)); edge_b=Vector((-16.32078934,-14.05729580))
edge=edge_b-edge_a; bay_t0=0.0; bay_t1=8.66856878/edge.length
bay_a=edge_a+edge*bay_t0; bay_b=edge_a+edge*bay_t1; bay_edge=bay_b-bay_a
bay_angle=math.atan2(bay_edge.y,bay_edge.x); bay_mid=(bay_a+bay_b)*.5
store_x0=bay_b.x-.04; store_x1=31.20
openings=[(bay_a.x-.03,bay_b.x+.03,-.30,15.20),(store_x0,store_x1,.02,2.96)]
for x in west_windows+middle_windows+east_windows:
    for z in window_levels: openings.append((x-(window_w+.18)/2,x+(window_w+.18)/2,z-(window_h+.18)/2,z+(window_h+.18)/2))
end_window_centers=[-12.70,-11.00,-9.20,-7.50]
end_window_openings=[(y-window_w/2,y+window_w/2,z-(window_h+.18)/2,z+(window_h+.18)/2) for y in end_window_centers for z in window_levels]

# Build a clean, aperture-bearing elevation by segmentation. A boolean against this
# GIS-derived zero-thickness shell would cap an opening and leave a false interior
# wall; explicit intervals retain open sightlines through the glazing.
sv=[(v.x,v.y,-1.0) for v in ring]+[(v.x,v.y,top_z) for v in ring]
sf=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
for i in range(N):
    a=ring[i]; b=ring[(i+1)%N]; dx=b.x-a.x
    if max(a.y,b.y)<-13.0 and abs(dx)>2.0:
        breaks=[0.0,1.0]
        for x0,x1,z0,z1 in openings:
            for x in (x0,x1):
                t=(x-a.x)/dx if abs(dx)>1e-8 else -1
                if 1e-6<t<1-1e-6: breaks.append(t)
        breaks=sorted(set(round(t,9) for t in breaks))
        for t0,t1 in zip(breaks[:-1],breaks[1:]):
            xm=a.x+dx*(t0+t1)/2
            cuts=[]
            for x0,x1,z0,z1 in openings:
                if x0-1e-5<=xm<=x1+1e-5 and max(x0,x1)>min(a.x,b.x) and min(x0,x1)<max(a.x,b.x):
                    lo=max(-1.0,z0); hi=min(top_z,z1)
                    if hi>lo+1e-5: cuts.append((lo,hi))
            cuts.sort(); merged=[]
            for lo,hi in cuts:
                if not merged or lo>merged[-1][1]+1e-5: merged.append([lo,hi])
                else: merged[-1][1]=max(merged[-1][1],hi)
            bands=[]; current=-1.0
            for lo,hi in merged:
                if lo>current+1e-5: bands.append((current,lo))
                current=max(current,hi)
            if current<top_z-1e-5: bands.append((current,top_z))
            y0=a.y+(b.y-a.y)*t0; y1=a.y+(b.y-a.y)*t1
            for z0,z1 in bands:
                if z1-z0<.01: continue
                k=len(sv); sv.extend([(a.x+dx*t0,y0,z0),(a.x+dx*t1,y1,z0),(a.x+dx*t1,y1,z1),(a.x+dx*t0,y0,z1)])
                sf.append((k,k+1,k+2,k+3))
    elif max(a.x,b.x)<-34.8 and abs(b.y-a.y)>2.0:
        # Three upper window rows on the short west/end wall. Cut openings using
        # this edge's Y parameter instead of leaving glass laid over solid brick.
        dy=b.y-a.y; breaks=[0.0,1.0]
        for y0,y1,z0,z1 in end_window_openings:
            for y in (y0,y1):
                t=(y-a.y)/dy if abs(dy)>1e-8 else -1
                if 1e-6<t<1-1e-6: breaks.append(t)
        breaks=sorted(set(round(t,9) for t in breaks))
        for t0,t1 in zip(breaks[:-1],breaks[1:]):
            ym=a.y+dy*(t0+t1)/2; cuts=[]
            for y0,y1,z0,z1 in end_window_openings:
                if y0-1e-5<=ym<=y1+1e-5 and max(y0,y1)>min(a.y,b.y) and min(y0,y1)<max(a.y,b.y):
                    lo=max(-1.0,z0); hi=min(top_z,z1)
                    if hi>lo+1e-5: cuts.append((lo,hi))
            cuts.sort(); merged=[]
            for lo,hi in cuts:
                if not merged or lo>merged[-1][1]+1e-5: merged.append([lo,hi])
                else: merged[-1][1]=max(merged[-1][1],hi)
            bands=[]; current=-1.0
            for lo,hi in merged:
                if lo>current+1e-5: bands.append((current,lo))
                current=max(current,hi)
            if current<top_z-1e-5: bands.append((current,top_z))
            y0=a.y+dy*t0; y1=a.y+dy*t1
            for z0,z1 in bands:
                if z1-z0<.01: continue
                k=len(sv); sv.extend([(a.x+dx*t0,y0,z0),(a.x+dx*t1,y1,z0),(a.x+dx*t1,y1,z1),(a.x+dx*t0,y0,z1)])
                sf.append((k,k+1,k+2,k+3))
    else: sf.append((i,(i+1)%N,(i+1)%N+N,i+N))
smesh=bpy.data.meshes.new('KRCH original GIS ring | segmented facade apertures r4')
smesh.from_pydata(sv,[],sf); smesh.update()
bm=bmesh.new(); bm.from_mesh(smesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(smesh); bm.free()
smesh.materials.append(brick)
old=shell.data; shell.data=smesh
if old.users==0: bpy.data.meshes.remove(old)
shell['facade_evidence_round7']='Moved the tall glazed bay from the interior GIS notch to the southwest outside corner shown in the Sasaki reference. Added three upper window rows on the near west/end elevation, removed ground-level punched windows from brick wings, and extended the transparent public storefront from the corner bay along the south frontage. Opening sizes and cadence remain image interpretations.'

# Replace only the Krach facade families changed by this source-only pass.
prefixes=('KRCH | 4-story corner lobby curtainwall panes','KRCH | limestone and bronze corner curtainwall frame','KRCH | corner bay slim metal mullions','KRCH | diagonal lobby storefront continuation','KRCH | diagonal storefront connector mullions','KRCH | transparent Main Street ground-floor storefront','KRCH | Main Street storefront dark mullions and transoms','KRCH | repeated punched window glass','KRCH | limestone punched-window reveals','KRCH | west end facade windows','KRCH | west end facade limestone window surrounds','KRCH | paired transparent lobby entrance leaves','KRCH | entrance door frame and bronze pulls','KRCH | pale stone entrance canopy and supports','KRCH | accessible entry landing','KRCH | entrance name lettering','Krach Leadership | entrance lettering')
for o in list(bpy.data.objects):
    if o.name.startswith(prefixes): bpy.data.objects.remove(o,do_unlink=True)

# Three-story full-height curtainwall bay anchored at the actual outer southwest
# corner; its width and frame details are interpreted from the Sasaki photo.
L=bay_edge.length; cx,cy=bay_mid.x,bay_mid.y; bay_y=-.07
bay_panes=[]; bay_frame=[]
module=L/3
for j in range(3):
    # box_mesh rotates local coordinates around origin, then adds origin. Keep all
    # bay centers relative to bay_mid; the previous 0..L coordinates applied the
    # midpoint twice and displaced the glass east by L/2.
    bay_panes.append(((module*(j+.5)-L/2,bay_y,7.6),(module-.22,.065,15.05)))
    if j: bay_frame.append(((module*j-L/2,bay_y-.10,7.6),(.14,.15,15.25)))
bay_frame += [((-L/2,bay_y-.10,7.6),(.24,.18,15.55)),((L/2,bay_y-.10,7.6),(.24,.18,15.55))]
for z in [.10,3.80,7.70,11.60,15.10]: bay_frame.append(((0,bay_y-.10,z),(L,.15,.14)))
box_mesh('KRCH | 4-story corner lobby curtainwall panes',bay_panes,glass,facade,bay_angle,(cx,cy))
bay_frame_ob=box_mesh('KRCH | limestone and bronze corner curtainwall frame',bay_frame,stone,facade,bay_angle,(cx,cy))
# Guard against repeating the origin-offset regression: mesh is already in local
# source coordinates after box_mesh's rotation/translation. Its extents must stay
# around the measured GIS bay midpoint, which is also where the lobby stair sits.
bay_x=[v.co.x for v in bay_frame_ob.data.vertices]
assert abs((min(bay_x)+max(bay_x))/2-bay_mid.x)<0.1, (min(bay_x),max(bay_x),bay_mid.x)
assert min(bay_x)>bay_a.x-0.3 and max(bay_x)<bay_b.x+0.3, (min(bay_x),max(bay_x))
bay_frame_ob['reference_observation']='Sasaki corner view: narrow full-height pale-stone-framed bay sits at the southwest outside corner, on the first 8.669 m of the 18.811 m south wall. Three vertical glazing modules and floor-height transoms are photo interpretation.'
bay_frame_ob['reference_url']='https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg'

# Keep a continuous public ground-floor storefront along the full south elevation,
# beginning directly after the full-height corner bay. The span bridges the shallow
# GIS notch to match the uninterrupted frontage visible in Sasaki's photograph.
z0=.02; z1=2.96; n=16; pw=(store_x1-store_x0)/n
panes=[]; mullions=[]
for i in range(n):
    x=store_x0+(i+.5)*pw
    panes.append(((x,-13.90,(z0+z1)/2),(pw-.09,.07,z1-z0-.04)))
    if i: mullions.append(((store_x0+i*pw,-14.20,(z0+z1)/2),(.075,.14,z1-z0)))
mullions += [(((store_x0+store_x1)/2,-14.20,.12),(store_x1-store_x0,.14,.10)),(((store_x0+store_x1)/2,-14.20,2.88),(store_x1-store_x0,.14,.12)),(((store_x0+store_x1)/2,-14.20,1.45),(store_x1-store_x0,.14,.075))]
store=box_mesh('KRCH | transparent Main Street ground-floor storefront',panes,glass,facade)
store['reference_observation']='Continuous transparent public/storefront frontage runs from the southwest corner bay across the south street elevation. Sasaki documents transparent first-floor public/social space; the shallow GIS notch is bridged as a photo interpretation.'
store['reference_url']='https://www.sasaki.com/projects/purdue-university-krach-leadership-center/'
box_mesh('KRCH | Main Street storefront dark mullions and transoms',mullions,frame,facade)

# Three photo-supported upper window rows across the near/end west facade. Exact
# bay spacing is estimated. The saved wall mesh receives matching aperture cuts.
end_specs=[]; end_frames=[]; end_y_mid=sum(end_window_centers)/len(end_window_centers)
end_x=-35.19; end_angle=math.pi/2
for y in end_window_centers:
    for z in window_levels:
        lx=y-end_y_mid
        end_specs.append(((lx,.05,z),(.82,.07,1.92)))
        end_frames += [((lx-.45,.13,z),(.12,.18,window_h)),((lx+.45,.13,z),(.12,.18,window_h)),((lx,.13,z-window_h/2+.06),(.92,.18,.12)),((lx,.13,z+window_h/2-.06),(.92,.18,.12))]
end_window_ob=box_mesh('KRCH | west end facade windows',end_specs,glass,facade,end_angle,(end_x,end_y_mid))
end_window_ob['reference_observation']='The Sasaki corner photograph shows three repeated upper window rows across the near/end brick facade. Three bays per level are image interpretation; exact spacing and dimensions are not measured.'
end_window_ob['reference_url']='https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg'
box_mesh('KRCH | west end facade limestone window surrounds',end_frames,stone,facade,end_angle,(end_x,end_y_mid))

# Tall, narrow photo-matched punched windows on three upper levels. Intermediate
# bays fill the blank span in the Sasaki view. Positions remain photo estimates.
window_panes=[]; window_frames=[]
def south_wall_y(x):
    xa,ya=-16.32078934,-14.05729580; xb,yb=.99312007,-13.16014194
    if xa<=x<=xb: return ya+(yb-ya)*(x-xa)/(xb-xa)
    return -13.90
for x in west_windows+middle_windows+east_windows:
    zs=window_levels
    for z in zs:
        w=window_w; h=window_h; wall_y=south_wall_y(x)
        window_panes.append(((x,wall_y-.035,z),(w-.20,.07,h-.20)))
        jamb=.12; depth=.20
        frame_y=wall_y-.24
        window_frames += [((x-w/2+jamb/2,frame_y,z),(jamb,depth,h)),((x+w/2-jamb/2,frame_y,z),(jamb,depth,h)),((x,frame_y,z-h/2+jamb/2),(w,depth,jamb)),((x,frame_y,z+h/2-jamb/2),(w,depth,jamb))]
windows=box_mesh('KRCH | repeated punched window glass',window_panes,glass,facade)
windows['reference_observation']='Sasaki corner image shows a regular, narrow vertical window cadence on the brick frontage over three upper levels. Intermediate bays fill the previous blank span; two bays overlapped by corner glazing are omitted. Exact centers remain photo-estimated.'
windows['reference_url']='https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg'
box_mesh('KRCH | limestone punched-window reveals',window_frames,stone,facade)

# Put the public entrance at the beginning of the photographed Main Street wing.
entry_x=4.4; entry_y=-14.43
doors=box_mesh('KRCH | paired transparent lobby entrance leaves',[
    ((entry_x-.52,entry_y,1.14),(.96,.08,2.18)),((entry_x+.52,entry_y,1.14),(.96,.08,2.18))],glass,facade)
box_mesh('KRCH | entrance door frame and bronze pulls',[
    ((entry_x-1.05,-14.52,1.12),(.12,.16,2.35)),((entry_x+1.05,-14.52,1.12),(.12,.16,2.35)),
    ((entry_x,-14.52,2.29),(2.22,.16,.13)),((entry_x,-14.58,1.12),(.045,.08,.7))],frame,facade)
box_mesh('KRCH | pale stone entrance canopy and supports',[
    ((entry_x,-15.23,3.15),(8.1,2.15,.28)),((entry_x-3.75,-15.95,1.45),(.28,.30,2.9)),((entry_x+3.75,-15.95,1.45),(.28,.30,2.9))],stone,facade)
box_mesh('KRCH | accessible entry landing',[
    ((entry_x,-16.35,-.28),(8.6,2.0,.20)),((entry_x,-17.55,-.47),(8.0,.95,.18)),((entry_x,-18.45,-.66),(7.4,.75,.18))],stone,facade)
# Keep engineering roof information carefully bounded: penthouse form and location
# are unmeasured; building story heights remain estimated.
pent=bpy.data.objects.get('KRCH | schematic mechanical penthouse (location estimated)')
if pent:
    pent['uncertainty']='Mechanical penthouse presence is documented by the project engineer. Its plan dimensions, shape, location and top elevation are not published and remain schematic.'
    pent['source_url']='https://frpinc.com/projects/krach-leadership-center/'
shell['height_status']='GIS footprint verified approximately; four story count documented; story heights and shell top elevation are estimates, not surveyed.'

bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'ring_vertices':N,'bay_endpoints':[list(bay_a),list(bay_b)],'bay_length_m':L,'bay_yaw_deg':math.degrees(bay_angle),'storefront_x_m':[store_x0,store_x1],'south_window_centers_m':west_windows+middle_windows+east_windows,'end_window_centers_m':end_window_centers,'punched_window_clear_m':[window_w-.20,window_h-.20],'penthouse_bounds_m':list(pent.dimensions) if pent else None},indent=2))

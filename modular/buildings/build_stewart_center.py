"""Rebuild Stewart Center exterior shell from Purdue GIS OBJECTID 615.

Run with Blender background against modular/buildings/stewart_center.blend.
Coordinates remain in the library's existing campus-relative source frame.
Only the assigned Stewart Center library is edited.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix

ASSET = Path(__file__).resolve().parents[2] / 'modular' / 'buildings' / 'stewart_center.blend'
GIS = Path(__file__).resolve().parents[2] / 'audit' / 'stewart_center_independent_grade' / 'purdue_gis_feature_615.json'
COL = bpy.data.collections.get('Asset_stewart_center')
assert COL and bpy.data.filepath.lower().endswith('stewart_center.blend')
root = bpy.data.objects.get('AssetRoot_stewart_center')
assert root
feature = json.loads(GIS.read_text(encoding='utf-8'))['features'][0]
attrs = feature['attributes']
assert attrs['OBJECTID'] == 615 and attrs['ABBR'] == 'STEW'
ring = feature['geometry']['rings'][0]
lat0, lon0 = 40.4274, -86.9137
mx_per_lon, my_per_lat = 84810.60416539927, 111040.0
anchor_x, anchor_y = 91.04999828338623, -253.375
pts = [( (lon-lon0)*mx_per_lon-anchor_x, (lat-lat0)*my_per_lat-anchor_y ) for lon,lat in ring]
if (pts[0][0]-pts[-1][0])**2+(pts[0][1]-pts[-1][1])**2 < 1e-10: pts.pop()
# Retain GIS corners while eliminating only sub-decimetre survey noise.
def clean_ring(points, tolerance=0.12):
    out=[]
    for p in points:
        if not out or math.dist(p,out[-1]) > tolerance: out.append(p)
    changed=True
    while changed and len(out)>3:
        changed=False; new=[]
        for i,p in enumerate(out):
            a=out[i-1]; b=out[(i+1)%len(out)]
            ab=Vector((b[0]-a[0],b[1]-a[1])); ap=Vector((p[0]-a[0],p[1]-a[1]))
            d=abs(ab.x*ap.y-ab.y*ap.x)/(ab.length or 1)
            if d < tolerance and ap.dot(ab)>=0 and ap.dot(ab)<=ab.length_squared:
                changed=True
            else: new.append(p)
        out=new
    return out
pts=clean_ring(pts)
area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2
assert area < 0, 'Expected clockwise ring in X east/Y north axes'

# Reuse established materials, with safe fallback for older source copies.
def getmat(name, color, rough=0.65, metallic=0.0):
    m=bpy.data.materials.get(name)
    if m is None:
        m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
        m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Base Color'].default_value=(*color,1)
            bs.inputs['Roughness'].default_value=rough
            bs.inputs['Metallic'].default_value=metallic
    return m
brick=getmat('Stewart_Purdue_Red_Brick',(0.34,0.105,0.07),0.82)
stone=getmat('Stewart_Bedford_Limestone',(0.64,0.59,0.48),0.74)
glass=getmat('Stewart_Solar_Curtain_Glass',(0.045,0.13,0.19),0.22,0.25)
glass_alt=getmat('Stewart_Reflective_Window_Glass',(0.10,0.22,0.24),0.20,0.16)
roofmat=getmat('Stewart_GIS_Roof_Estimated',(0.18,0.19,0.20),0.92)
portico_stone=getmat('Stewart_South_Portico_Limestone',(0.69,0.64,0.53),0.76)
if portico_stone.use_nodes:
    nodes=portico_stone.node_tree.nodes; links=portico_stone.node_tree.links
    bs=nodes.get('Principled BSDF')
    if bs and not any(n.type=='TEX_NOISE' and n.label=='Subtle Bedford limestone grain' for n in nodes):
        noise=nodes.new('ShaderNodeTexNoise'); noise.label='Subtle Bedford limestone grain'
        noise.inputs['Scale'].default_value=7.0; noise.inputs['Detail'].default_value=3.0
        ramp=nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.25
        ramp.color_ramp.elements[0].color=(.47,.43,.35,1)
        ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=(.78,.73,.62,1)
        bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.035
        links.new(noise.outputs['Fac'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal'])

def mesh_obj(name, verts, faces, material, bevel=0):
    mesh=bpy.data.meshes.new(name+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    obj=bpy.data.objects.new(name,mesh); COL.objects.link(obj)
    if root: obj.parent=root
    if bevel:
        mod=obj.modifiers.new('Soft masonry arris','BEVEL'); mod.width=bevel; mod.segments=2
        mod2=obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return obj

def oriented_box(name, center, length, depth, height, angle, material, bevel=0.04):
    hx,hy,hz=length/2,depth/2,height/2
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
           (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    ob=mesh_obj(name,verts,faces,material,bevel)
    ob.location=(center[0],center[1],center[2]); ob.rotation_euler[2]=angle
    return ob

# Remove only obsolete perimeter elements; retain documented entrances, interior,
# public spaces and differentiated roof plant. The wall gap accommodates existing doors.
import re
obsolete=[]
for o in list(COL.all_objects):
    n=o.name
    if (n.startswith('STEW_Ext_Wall_') or n.startswith('STEW_GIS_') or n=='STEW_Roof_GIS_Trace_ESTIMATED' or n.startswith('STEW_Base_Limestone_') or
        n.startswith('STEW_Beltcourse_') or n=='STEW_Roof_Membrane_Main' or
        n=='STEW_Portico_Back_Wall' or
        re.match(r'STEW_(North|South|East|West)_(Win|Sill)_',n) or
        re.match(r'STEW_South_Fin_',n) or n.startswith('STEW_Portico_Pier_') or
        n.startswith('STEW_South_Canopy') or n.startswith('STEW_South_Building_Lettering') or
        n.startswith('STEW_South_Entry_')):
        obsolete.append(o)
for o in obsolete: bpy.data.objects.remove(o,do_unlink=True)

wall_h=16.5 # estimated pending dimensioned elevation; source confirms only the central three-floor organization
thick=.70
# GIS project coordinates are shifted by the fixed manifest placement origin,\n# matching the existing local child-mesh frame and identity AssetRoot.\n# Reposition retained program modules once, using the current Purdue 2024 first-floor map
# for relative room locations and the GIS perimeter for local containment. The map is
# schematic and does not establish metric dimensions, so sizes and exact offsets remain estimates.
layout_moves = [('HSSE_', -45.825, -30.75), ('Loeb_', 68.05, 5.125), ('STEW_FlyLoft_', 68.05, 5.125)]
for prefix, dx, dy in layout_moves:
    for obj in list(COL.all_objects):
        if obj.name.startswith(prefix) and not obj.get('Stewart_GIS_local_layout_adjusted', False):
            wm = obj.matrix_world.copy(); wm.translation += Vector((dx, dy, 0.0)); obj.matrix_world = wm
            obj['Stewart_GIS_local_layout_adjusted'] = True
bpy.context.scene['stewart_local_module_moves'] = json.dumps({p:[dx,dy] for p,dx,dy in layout_moves})
# For clockwise GIS rings, interior lies to the right of each directed edge.
for i,a in enumerate(pts):
    b=pts[(i+1)%len(pts)]; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if length < .28: continue
    ux,uy=dx/length,dy/length; inward=(uy,-ux); outward=(-uy,ux); angle=math.atan2(dy,dx)
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    # Keep openings at the existing documented north/south public entrances.
    # The GIS south-side recess has a 53 m back edge at Y≈-46.6 m. Replace
    # its center section with the documented entrance glazing instead of
    # continuing the generic brick/window rhythm behind the portico.
    entrance_back_wall=(length>50 and abs(mid[1]+46.6)<.45 and -30<mid[0]<26)
    door_gap=entrance_back_wall or (abs(mid[1]+50.0)<1.4 and -25<=mid[0]<=12) or (abs(mid[1]-42.0)<1.4 and -36<=mid[0]<=24)
    if door_gap:
        # split wall either side of the opening, with a small jamb allowance
        gap=34.0 if entrance_back_wall else (36.0 if mid[1]<0 else 59.5)
        if entrance_back_wall:
            portal_center=(-7.65,-46.6)
            center_t=(portal_center[0]-a[0])*ux+(portal_center[1]-a[1])*uy
        else: center_t=length/2
        intervals=[(0,max(0,center_t-gap/2)),(min(length,center_t+gap/2),length)]
    else: intervals=[(0,length)]
    for part,(t0,t1) in enumerate(intervals):
        seg=t1-t0
        if seg<0.35: continue
        c=(a[0]+ux*(t0+t1)/2+inward[0]*thick/2,
           a[1]+uy*(t0+t1)/2+inward[1]*thick/2,wall_h/2)
        oriented_box(f'STEW_Ext_Wall_GIS_{i:02d}_{part}',c,seg,thick,wall_h,angle,brick,.05)
        # Limestone base + restrained floor bands follow each true footprint edge.
        for band,z,h in [('Base',.75,1.5),('L1',4.2,.24),('L2',8.4,.24),('L3',12.6,.24),('Coping',16.45,.35)]:
            bc=(a[0]+ux*(t0+t1)/2+inward[0]*(thick/2-.04),
                a[1]+uy*(t0+t1)/2+inward[1]*(thick/2-.04),z)
            oriented_box(f'STEW_GIS_{band}_{i:02d}_{part}',bc,seg,.16,h,angle,stone,.025)
        # Estimated repeated window rhythm, mounted only on unbroken long facades.
        if seg>=5.5 and not door_gap:
            count=max(1,int(seg//5.0)); spacing=seg/count
            for j in range(count):
                t=t0+(j+.5)*spacing
                wc=(a[0]+ux*t+outward[0]*.025,a[1]+uy*t+outward[1]*.025,0)
                row_specs=((2.85,2.55),(6.3,2.05),(10.5,2.65),(14.5,2.0))
                win_width=min(2.55,spacing*(.51 if (i+j)%3==0 else .62))
                for row,(z,win_height) in enumerate(row_specs,1):
                    # Purdue's photo shows deep stone-framed vertical bays. The
                    # lower and upper lights vary slightly; exact bay dimensions
                    # remain estimates because no elevation was located.
                    winmat=glass_alt if (i+j+row)%4==0 else glass
                    oriented_box(f'STEW_GIS_Window_{i:02d}_{j:02d}_{row}',(wc[0],wc[1],z),win_width,.10,win_height,angle,winmat,.025)
                    sillc=(wc[0]+outward[0]*.03,wc[1]+outward[1]*.03,z-win_height/2-.08)
                    oriented_box(f'STEW_GIS_Sill_{i:02d}_{j:02d}_{row}',sillc,win_width+.26,.22,.14,angle,stone,.018)
                    framec=(wc[0]+outward[0]*.07,wc[1]+outward[1]*.07,z)
                    for side in (-1,1):
                        jamb=(framec[0]+ux*side*(win_width/2+.05),framec[1]+uy*side*(win_width/2+.05),z)
                        oriented_box(f'STEW_GIS_Window_Jamb_{i:02d}_{j:02d}_{row}_{side}',jamb,.10,.18,win_height+.06,angle,stone,.012)
                    head=(framec[0],framec[1],z+win_height/2+.05)
                    oriented_box(f'STEW_GIS_Window_Head_{i:02d}_{j:02d}_{row}',head,win_width+.20,.18,.10,angle,stone,.012)

# Flat roof polygon is kept within the GIS trace. Shape and elevation are estimates.
verts=[(x,y,wall_h-.15) for x,y in pts]+[(x,y,wall_h+.15) for x,y in pts]
n=len(pts); faces=[]
# face n-gons let Blender triangulate concave polygon on evaluation/render.
faces.append(tuple(range(n-1,-1,-1))); faces.append(tuple(range(n,2*n)))
for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
roof=mesh_obj('STEW_Roof_GIS_Trace_ESTIMATED',verts,faces,roofmat,.02)

# Purdue's public south-entrance photo documents a six-column stone portico,
# multi-storey glazing behind it, and a broad stair. Dimensions below are visual
# proportions scaled to the existing portico opening, not surveyed measurements.
landing_z=1.44
for obj in COL.all_objects:
    if obj.name.startswith('STEW_South_Door_Frame_') or obj.name.startswith('STEW_South_Door_Glass_') or obj.name=='STEW_South_Entrance_Glazing':
        if not obj.get('stewart_south_door_raise',False):
            obj.location.z += landing_z; obj.location.y -= .28
            obj['stewart_south_door_raise']=True
        if not obj.get('stewart_south_door_y_adjusted',False):
            obj.location.y -= .24
            obj['stewart_south_door_y_adjusted']=True

# Stone landing and eight broad risers aligned to the source photograph.
oriented_box('STEW_South_Entry_Landing',(-7.05,-48.6,landing_z-.18),31.5,10.2,.36,0,portico_stone,.06)
stair_width=24.0; stair_x=-7.05; riser=.18; tread=.72; stair_start_y=-58.9
for i in range(8):
    ztop=(i+1)*riser
    ycenter=stair_start_y+(i+.5)*tread
    oriented_box(f'STEW_South_Entry_Stair_{i+1:02d}',(stair_x,ycenter,ztop/2),stair_width,tread,ztop,0,portico_stone,.025)

# Six lightly fluted round shafts, bases and restrained capitals. Count and
# silhouette follow Purdue's entrance photograph; dimensions remain estimated.
def column_mesh(name,x,y,z0,z1,radius,material,segments=32,flute=False):
    levels=[(z0,radius*1.48),(z0+.28,radius*1.48),(z0+.52,radius*1.05),
            (z0+.85,radius*.91),(z1-.50,radius*.82),(z1-.30,radius*1.14),
            (z1-.14,radius*1.48),(z1,radius*1.58)]
    vs=[]
    for zi,rad in levels:
        for k in range(segments):
            a=2*math.pi*k/segments
            rr=rad*(1.0+.026*math.cos(12*a) if flute and z0+.85 < zi < z1-.45 else 1.0)
            vs.append((x+rr*math.cos(a),y+rr*math.sin(a),zi))
    fs=[]
    for q in range(len(levels)-1):
        for k in range(segments):
            a=q*segments+k; b=q*segments+(k+1)%segments
            fs.append((a,b,b+segments,a+segments))
    fs.extend([tuple(range(segments-1,-1,-1)),tuple((len(levels)-1)*segments+k for k in range(segments))])
    return mesh_obj(name,vs,fs,material,.025)

col_x=[-22.15,-16.35,-10.55,-4.75,1.05,6.85]
for i,x in enumerate(col_x,1):
    column_mesh(f'STEW_South_Entry_Column_{i:02d}',x,-49.15,landing_z,8.95,.50,portico_stone,32,True)
    oriented_box(f'STEW_South_Entry_Column_Abacus_{i:02d}',(x,-49.15,9.03),1.45,1.32,.20,0,portico_stone,.025)

# Shallow entablature and triangular pediment above the column row.
oriented_box('STEW_South_Entry_Entablature',(-7.65,-49.15,9.15),34.8,1.15,.52,0,portico_stone,.045)
px0,px1=-25.05,9.75; py0,py1=-49.74,-48.56; zbase,ztop=9.41,12.05
pv=[(px0,py0,zbase),(px1,py0,zbase),(-7.65,py0,ztop),
    (px0,py1,zbase),(px1,py1,zbase),(-7.65,py1,ztop)]
pf=[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
mesh_obj('STEW_South_Entry_Pediment',pv,pf,portico_stone,.035)
oriented_box('STEW_South_Entry_Pediment_Baseband',(-7.65,-49.8,9.47),35.5,.18,.16,0,stone,.015)

# Upper glazing behind the foreground columns, divided into source-proportioned bays.
glass_upper=getmat('Stewart_South_Upper_Entrance_Glazing',(0.06,.16,.20),.2,.18)
for row,(z,h) in enumerate(((5.75,1.9),(7.85,1.55)),1):
    for j,x in enumerate((-19.35,-12.35,-5.35,1.65,6.25),1):
        oriented_box(f'STEW_South_Entry_Upper_Glass_{row}_{j}',(x,-44.25,z),5.15,.12,h,0,glass_upper,.025)
        if j<5:
            oriented_box(f'STEW_South_Entry_Upper_Mullion_{row}_{j}',(x+2.92,-44.32,z),.11,.16,h,0,portico_stone,.012)

# Photo-visible metal stair handrails. Continuous rails slope with the stair run,
# and each post starts on a tread and meets the rail underside.
railmat=getmat('Stewart_South_Entry_Rail_Metal',(.24,.25,.24),.34,.72)
for side,x in [('W',stair_x-stair_width/2+.28),('E',stair_x+stair_width/2-.28)]:
    rail_start_y=-58.75; rail_end_y=-52.9
    rail_start_z=.18+1.0; rail_end_z=1.44+1.0
    rail_mid_y=(rail_start_y+rail_end_y)/2; rail_mid_z=(rail_start_z+rail_end_z)/2
    rail_len=math.dist((rail_start_y,rail_start_z),(rail_end_y,rail_end_z))
    rail=oriented_box(f'STEW_South_Entry_Rail_{side}',(x,rail_mid_y,rail_mid_z),.13,rail_len,.13,0,railmat,.025)
    rail.rotation_euler[0]=math.atan2(rail_end_z-rail_start_z,rail_end_y-rail_start_y)
    for k in range(9):
        yy=rail_start_y+(rail_end_y-rail_start_y)*k/8
        tread_index=max(0,min(7,int((yy-stair_start_y)//tread)))
        tread_top=(tread_index+1)*riser
        rail_top=rail_start_z+(rail_end_z-rail_start_z)*(yy-rail_start_y)/(rail_end_y-rail_start_y)
        post_h=rail_top-tread_top
        oriented_box(f'STEW_South_Entry_RailPost_{side}_{k+1}',(x,yy,tread_top+post_h/2),.10,.10,post_h,0,railmat,.018)

# A recessed two-layer glazed vestibule replaces the GIS/legacy brick window
# wall behind the column row. The uncalibrated official photo establishes the
# glazed entrance character; all panel dimensions and returns are estimates.
portal_xmin,portal_xmax=-24.65,9.35
portal_width=portal_xmax-portal_xmin
front_y=-46.78; rear_y=-44.15; glass_bottom=1.62; glass_top=8.55
glass_mat=getmat('Stewart_South_Vestibule_Glass',(.035,.12,.16),.16,.22)
bronze=getmat('Stewart_Bronze_Metal',(.16,.12,.075),.36,.68)
door_centers=(-16.05,-7.05,1.95); door_half=1.72
panel_spans=[]; cursor=portal_xmin
for dc in door_centers:
    left=dc-door_half
    if left>cursor+.08: panel_spans.append((cursor,left))
    cursor=dc+door_half
if portal_xmax>cursor+.08: panel_spans.append((cursor,portal_xmax))
for i,(xa,xb) in enumerate(panel_spans,1):
    oriented_box(f'STEW_South_Entry_Vestibule_Front_Glass_{i}',((xa+xb)/2,front_y,(glass_bottom+glass_top)/2),xb-xa,.15,glass_top-glass_bottom,0,glass_mat,.02)
    mx=xa+3.4; mullion=1
    while mx<xb-.6:
        oriented_box(f'STEW_South_Entry_Vestibule_Front_Mullion_{i}_{mullion}',(mx,front_y-.10,(glass_bottom+glass_top)/2),.075,.12,glass_top-glass_bottom,0,bronze,.012)
        mx+=3.4; mullion+=1
    oriented_box(f'STEW_South_Entry_Vestibule_Front_Rail_{i}',((xa+xb)/2,front_y-.10,5.15),xb-xa,.12,.075,0,bronze,.012)
for i,dc in enumerate(door_centers,1):
    # Tall transom over each visible door opening.
    oriented_box(f'STEW_South_Entry_Vestibule_Transom_{i}',(dc,front_y,(4.42+glass_top)/2),door_half*2,.15,glass_top-4.42,0,glass_mat,.02)
    # Three framed double-leaf entry doors aligned to the original rear doors.
    for side,xx in [('L',dc-.82),('R',dc+.82)]:
        oriented_box(f'STEW_South_Entry_Vestibule_DoorGlass_{i}_{side}',(xx,front_y-.11,3.02),1.55,.10,2.8,0,glass_mat,.02)
    for xx in (dc-1.72,dc,dc+1.72):
        oriented_box(f'STEW_South_Entry_Vestibule_DoorMullion_{i}_{xx:.2f}',(xx,front_y-.16,3.02),.075,.12,2.95,0,bronze,.012)
    oriented_box(f'STEW_South_Entry_Vestibule_DoorHead_{i}',(dc,front_y-.16,4.50),3.5,.12,.10,0,bronze,.012)
    # Full-height limestone surrounds break the portal into three legible bays,
    # following Purdue's deep stone-framed glazed openings. Bay width/depth is
    # estimated from unscaled campus photography.
    bay_half=3.55; bay_y=front_y-.20; bay_mid_z=(glass_bottom+glass_top)/2
    for side in (-1,1):
        oriented_box(f'STEW_South_Entry_GlassBay_Pier_{i}_{side}',(dc+side*bay_half,bay_y,bay_mid_z),.58,.72,glass_top-glass_bottom,0,portico_stone,.035)
    oriented_box(f'STEW_South_Entry_GlassBay_Lintel_{i}',(dc,bay_y,8.28),bay_half*2+.58,.72,.54,0,portico_stone,.045)
    oriented_box(f'STEW_South_Entry_GlassBay_Base_{i}',(dc,bay_y,1.70),bay_half*2+.58,.72,.16,0,portico_stone,.025)
for i,x in enumerate((portal_xmin+.08,portal_xmax-.08),1):
    oriented_box(f'STEW_South_Entry_Vestibule_SideGlass_{i}',(x,(front_y+rear_y)/2,(glass_bottom+glass_top)/2),.14,front_y-rear_y,glass_top-glass_bottom,0,glass_mat,.015)
    oriented_box(f'STEW_South_Entry_Vestibule_SideRail_{i}',(x,(front_y+rear_y)/2,glass_top),.22,front_y-rear_y,.18,0,portico_stone,.025)

# The clear portal replaces only the ground-to-portico portion of the recessed
# facade. Restore the upper masonry mass above it so the GIS notch does not read
# as an open hole through the building; the window rhythm above is an estimate.
upper_h=max(.1,wall_h-glass_top)
oriented_box('STEW_South_Entry_Upper_Brick_Backdrop',((portal_xmin+portal_xmax)/2,-46.23,(wall_h+glass_top)/2),portal_width,.70,upper_h,0,brick,.03)
upper_window_x=[portal_xmin+2.5+i*4.15 for i in range(8)]
for j,x in enumerate(upper_window_x,1):
    for row,z in enumerate((10.4,14.25),1):
        oriented_box(f'STEW_South_Entry_Upper_Window_{j:02d}_{row}',(x,-46.70,z),2.25,.12,1.9,0,glass,.025)
        oriented_box(f'STEW_South_Entry_Upper_Window_Sill_{j:02d}_{row}',(x,-46.73,z-1.03),2.42,.18,.12,0,stone,.015)
# Material and collection validation before saving.
for o in COL.all_objects:
    if o.type=='MESH' and not o.data.materials:
        o.data.materials.append(brick)
bpy.context.scene['stewart_gis_footprint_vertices']=len(pts)
bpy.context.scene['stewart_gis_area_m2']=abs(area)
bpy.context.scene['stewart_height_status']='Estimated: no authoritative elevation located; central three-floor organization documented by Purdue Archives.'
bpy.context.scene['stewart_south_entry_status']='Purdue photo supports six-column stone portico, upper entrance glazing and broad stair. Local dimensions are photo-scaled estimates, not surveyed.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'saved':str(ASSET),'gis_feature':615,'vertices_after_noise_cleanup':len(pts),'gis_area_m2':abs(area),'wall_height_m_estimate':wall_h,'deleted_obsolete_shell_objects':len(obsolete),'placement_origin_xy_m':[anchor_x,anchor_y],'asset_objects':len(list(COL.all_objects))},indent=2))







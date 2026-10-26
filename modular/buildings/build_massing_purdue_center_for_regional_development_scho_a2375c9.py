"""Rebuild the Schowe House library from Purdue GIS and photo evidence.
Run with Blender 5.2: blender -b --python build_massing_purdue_center_for_regional_development_scho_a2375c9.py
"""
from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular/buildings/massing_purdue_center_for_regional_development_scho_a2375c9.blend'
GIS = ROOT / 'audit/schowe_house/sources/purdue_gis_fid295_schowe_house_2026-10-26.json'
AUDIT = ROOT / 'audit/schowe_house'
COLL_NAME = 'Asset_massing_purdue_center_for_regional_development_scho_a2375c9'
SCENE_NAME = 'Building_massing_purdue_center_for_regional_development_scho_a2375c9'
OBJ_NAME = 'Purdue Center for Regional Development (SCHO)'

# Project CRS: documented local approximation, X east/Y north in meters.
origin_lon, origin_lat = -86.9137, 40.4274
coslat = math.cos(math.radians(origin_lat))
angle = math.radians(20.0)  # dominant 20/110 degree GIS wall axes
ca, sa = math.cos(angle), math.sin(angle)
def ll_to_xy(lon, lat):
    return ((lon-origin_lon)*111412.84*coslat, (lat-origin_lat)*111040.0)
def xy_to_uv(x,y): return (x*ca+y*sa, -x*sa+y*ca)
def uv_to_xy(u,v): return (u*ca-v*sa, u*sa+v*ca)
def uv_world(u,v,z=0):
    x,y=uv_to_xy(u,v); return (x,y,z)

def clear_objects(coll):
    for ob in list(coll.objects): bpy.data.objects.remove(ob, do_unlink=True)

def material(name, c1, c2=None, rough=0.75, pattern=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*c1,1.0); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); bs.location=(430,0); bs.inputs['Roughness'].default_value=rough
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if pattern in {'brick','slate','shingle'}:
        # Use a deterministic packed image tile. UVs are generated per face from measured
        # world coordinates, so brick courses do not collapse into stripes on rotated walls.
        import random
        random.seed({'brick':295,'slate':296,'shingle':297}[pattern])
        image_name='SCHO_'+pattern+'_tile'
        img=bpy.data.images.get(image_name)
        if img is None:
            w=h=256; img=bpy.data.images.new(image_name,width=w,height=h,alpha=False)
            pixels=[]
            if pattern=='brick':
                base=(0.20,0.075,0.042); var=(0.16,0.07,0.042); mortar=(0.18,0.16,0.135)
                row_h=32; cell_w=64; gap=4
            elif pattern=='slate':
                base=(0.13,0.15,0.17); var=(0.10,0.11,0.12); mortar=(0.075,0.08,0.09)
                row_h=32; cell_w=64; gap=3
            else:
                base=(0.17,0.075,0.038); var=(0.12,0.07,0.045); mortar=(0.09,0.055,0.035)
                row_h=32; cell_w=64; gap=3
            for py in range(h):
                row=py//row_h; ry=py%row_h; shift=(cell_w//2 if row%2 else 0)
                for px in range(w):
                    xx=(px+shift)%cell_w; rx=py%row_h
                    is_gap=(xx<gap or rx<gap)
                    if is_gap: col=mortar
                    else:
                        n=random.uniform(-0.035,0.035)
                        col=tuple(max(0,min(1,base[k]+var[k]*random.random()+n)) for k in range(3))
                    pixels.extend((*col,1.0))
            img.pixels.foreach_set(pixels)
            img.filepath_raw=str(AUDIT/'sources'/f'schowe_{pattern}_tile.png'); img.file_format='PNG'; img.save(); img.pack()
        tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=img; tex.extension='REPEAT'; tex.location=(-260,100)
        tc=nt.nodes.new('ShaderNodeTexCoord'); tc.location=(-480,100)
        nt.links.new(tc.outputs['UV'],tex.inputs['Vector']); nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        noise=nt.nodes.new('ShaderNodeTexNoise'); noise.location=(-250,-140); noise.inputs['Scale'].default_value=38; noise.inputs['Detail'].default_value=2
        nt.links.new(tc.outputs['UV'],noise.inputs['Vector'])
        bump=nt.nodes.new('ShaderNodeBump'); bump.location=(190,-120); bump.inputs['Strength'].default_value=0.12 if pattern=='brick' else 0.08; bump.inputs['Distance'].default_value=0.018
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    else:
        bs.inputs['Base Color'].default_value=(*c1,1)
    return m

def mesh_obj(name, verts, faces, mat, coll, smooth=False):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.update()
    if mat and mat.name.startswith('SCHO •') and ('brick' in mat.name or 'slate' in mat.name or 'shingle' in mat.name):
        uv=me.uv_layers.new(name='SourceScaleUV')
        tile='brick' if 'brick' in mat.name else ('shingle' if 'shingle' in mat.name else 'slate')
        for poly in me.polygons:
            nz=abs(poly.normal.z)
            for li in poly.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co
                if tile=='brick':
                    if nz>0.7: uv.data[li].uv=(co.x/2.0,co.y/1.28)
                    elif abs(poly.normal.x)>=abs(poly.normal.y): uv.data[li].uv=(co.y/2.0,co.z/1.28)
                    else: uv.data[li].uv=(co.x/2.0,co.z/1.28)
                else:
                    if nz>0.25: uv.data[li].uv=(co.x/3.2,co.y/2.24)
                    elif abs(poly.normal.x)>=abs(poly.normal.y): uv.data[li].uv=(co.y/3.2,co.z/2.24)
                    else: uv.data[li].uv=(co.x/3.2,co.z/2.24)
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob)
    if mat: ob.data.materials.append(mat)
    if smooth:
        for p in me.polygons:p.use_smooth=True
    return ob

def append_prism(verts,faces,center,tangent,normal,width,depth,z0,z1):
    cx,cy=center; tx,ty=tangent; nx,ny=normal; start=len(verts)
    for z in (z0,z1):
        for s,n in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:
            verts.append((cx+tx*s+nx*n,cy+ty*s+ny*n,z))
    faces.extend([(start+0,start+1,start+2,start+3),(start+4,start+7,start+6,start+5),
                  (start+0,start+4,start+5,start+1),(start+1,start+5,start+6,start+2),
                  (start+2,start+6,start+7,start+3),(start+3,start+7,start+4,start+0)])

def add_box(name, center, tangent, normal, width, depth, z0, z1, mat, coll):
    v=[];f=[];append_prism(v,f,center,tangent,normal,width,depth,z0,z1)
    return mesh_obj(name,v,f,mat,coll)

def gable_wall(verts,faces,uend,v0,v1,eaves,ridge):
    # At an end of a ridge-along-u volume, triangular wall under the roof.
    p0=uv_world(uend,v0,eaves); p1=uv_world(uend,v1,eaves); p2=uv_world(uend,(v0+v1)/2,ridge)
    i=len(verts); verts.extend([p0,p1,p2]); faces.append((i,i+1,i+2))

def roof_mass(name,u0,u1,v0,v1,eaves,ridge,mat,coll,overhang=0.30,gable0=True,gable1=True):
    # Intersecting gable masses match the visible multi-wing slate/shingle roof.
    u0-=overhang;u1+=overhang;v0-=overhang;v1+=overhang
    vm=(v0+v1)/2
    def P(u,v,z):return uv_world(u,v,z)
    verts=[P(u0,v0,eaves),P(u1,v0,eaves),P(u1,vm,ridge),P(u0,vm,ridge),
           P(u0,v1,eaves),P(u1,v1,eaves)]
    faces=[(0,1,2,3),(3,2,5,4)]
    ob=mesh_obj(name,verts,faces,mat,coll)
    sol=ob.modifiers.new('Slate thickness and eaves','SOLIDIFY');sol.thickness=0.10;sol.offset=-0.1
    bevel=ob.modifiers.new('Soft roof edges','BEVEL');bevel.width=0.035;bevel.segments=2
    # brick gable end geometry.
    gv=[];gf=[]
    if gable0: gable_wall(gv,gf,u0,v0,v1,eaves,ridge)
    if gable1: gable_wall(gv,gf,u1,v0,v1,eaves,ridge)
    mesh_obj(name+'_GableEnds',gv,gf,brick,coll)
    # Eave fascia boards along both long sides and both gable rakes.
    evec=[];ef=[]
    def fascia(uA,vA,uB,vB,zA,zB,width=0.16,depth=0.13):
        dx=uB-uA;dy=vB-vA;ln=math.hypot(dx,dy);t=(dx/ln,dy/ln);n=(-t[1],t[0])
        miduv=((uA+uB)/2,(vA+vB)/2);mid=uv_to_xy(*miduv)
        append_prism(evec,ef,mid,t,n,ln,depth,min(zA,zB)-width/2,max(zA,zB)+width/2)
    for v in (v0,v1): fascia(u0,v,u1,v,eaves,eaves)
    mesh_obj(name+'_Fascia',evec,ef,trim,coll)
    return ob

# Load the official source geometry and the one-building source scene.
src=json.loads(GIS.read_text(encoding='utf-8'))
feature=next(f for f in src['features'] if f['attributes']['OBJECTID']==295)
ring=feature['geometry']['rings'][0]
xy=[ll_to_xy(lon,lat) for lon,lat in ring]
uv=[xy_to_uv(x,y) for x,y in xy]
area=sum(uv[i][0]*uv[i+1][1]-uv[i+1][0]*uv[i][1] for i in range(len(uv)-1))/2
ccw=area>0
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
bpy.context.window.scene=scene
coll=bpy.data.collections.get(COLL_NAME)
if not coll: raise RuntimeError('Required export collection missing: '+COLL_NAME)
clear_objects(coll)
# Source-based material palette: red-brown brick and steep gray slate, with brown shingle wing/garage.
brick=material('SCHO • Purdue red-brown brick',(.42,.19,.12),(.27,.105,.065),.82,'brick')
slate=material('SCHO • weathered gray slate',(.28,.30,.32),(.42,.43,.43),.78,'slate')
shingle=material('SCHO • aged cedar shingles',(.25,.12,.065),(.38,.20,.11),.86,'shingle')
trim=material('SCHO • dark painted timber',(.11,.075,.055),None,.65)
stone=material('SCHO • limestone sills',(.56,.51,.43),(.43,.39,.33),.78)
glass=material('SCHO • shaded glass',(.035,.085,.105),(.07,.14,.17),.22)
door=material('SCHO • stained oak doors',(.19,.085,.035),(.30,.14,.055),.62)
metal=material('SCHO • dark metal',(.08,.085,.09),(.16,.17,.18),.42)
floor_mat=material('SCHO • interior oak floor',(.28,.16,.08),(.38,.24,.12),.72)

# Floor slab exactly follows the mapped wall footprint.  ArcGIS repeats its first
# vertex at the end of the ring; omit that duplicate for a valid non-degenerate cap.
ring_xy=xy[:-1]
base=[(x,y,0.0) for x,y in ring_xy]
mesh_obj(OBJ_NAME+'_GIS_Footprint_Floor',base,[tuple(range(len(base)-1,-1,-1))],stone,coll)
# Extruded brick shell with real door/window voids on long surveyed facade segments.
wall_v=[];wall_f=[];trim_v=[];trim_f=[];glass_v=[];glass_f=[];door_v=[];door_f=[]
first_height=3.35
opening_records=[]
for ei,(a,b) in enumerate(zip(ring_xy,ring_xy[1:]+ring_xy[:1])):
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    if L<0.02: continue
    t=(dx/L,dy/L)
    inward=(-dy/L,dx/L) if ccw else (dy/L,-dx/L)
    outward=(-inward[0],-inward[1])
    door_open=(ei==0 and L>7.0)
    garage_open=(ei==10 and L>6.5)
    door_center=L*0.62
    opens=[]
    if door_open: opens.append((door_center-0.63,door_center+0.63,0.0,2.30,'entry'))
    if garage_open:
        for gc in (L*0.34,L*0.70): opens.append((gc-1.18,gc+1.18,0.08,2.42,'garage'))
    if L>=3.15 and not garage_open:
        nwin=max(1,min(3,int(L//3.25)))
        for j in range(nwin):
            c=L*(j+1)/(nwin+1)
            if door_open and abs(c-door_center)<1.30: continue
            w=1.18;z0=0.88;z1=2.32
            opens.append((c-w/2,c+w/2,z0,z1,'window'))
    # Generate continuous masonry panels around each rectangular opening.
    sb=sorted({0.0,L,*[max(0,min(L,o[0])) for o in opens],*[max(0,min(L,o[1])) for o in opens]})
    zb=sorted({0.0,first_height,*[max(0,min(first_height,o[2])) for o in opens],*[max(0,min(first_height,o[3])) for o in opens]})
    # Each run has a true GIS-aligned exterior face (the center is offset half
    # the wall thickness inward). Extend solid masonry slightly at corners so
    # adjacent runs overlap instead of leaving hairline daylight gaps.
    centerline=(a[0]+t[0]*L/2+inward[0]*0.14,
                a[1]+t[1]*L/2+inward[1]*0.14)
    for si in range(len(sb)-1):
        s0,s1=sb[si],sb[si+1]
        if s1-s0<0.02:continue
        for zi in range(len(zb)-1):
            z0,z1=zb[zi],zb[zi+1]
            if z1-z0<0.02:continue
            sm=(s0+s1)/2;zm=(z0+z1)/2
            ishole=any(o[0]+1e-3<sm<o[1]-1e-3 and o[2]+1e-3<zm<o[3]-1e-3 for o in opens)
            if not ishole:
                cen=(centerline[0]+t[0]*(sm-L/2),centerline[1]+t[1]*(sm-L/2))
                pad=0.15 if s0<=1e-5 or s1>=L-1e-5 else 0.0
                append_prism(wall_v,wall_f,cen,t,inward,s1-s0+pad,0.28,z0,z1)
    for oi,o in enumerate(opens):
        s0,s1,z0,z1,typ=o; c=(s0+s1)/2;w=s1-s0;h=z1-z0
        wallxy=(a[0]+t[0]*c+outward[0]*0.04,a[1]+t[1]*c+outward[1]*0.04)
        if typ=='window':
            # Recess-like dark glass plus four timber mullions, an operable center rail and a pale sill.
            append_prism(glass_v,glass_f,wallxy,t,outward,w-0.20,0.065,z0+0.12,z1-0.12)
            frame=0.085
            for sgn in (-1,1):
                cen=(wallxy[0]+t[0]*(sgn*(w/2-frame/2)),wallxy[1]+t[1]*(sgn*(w/2-frame/2)))
                append_prism(trim_v,trim_f,cen,t,outward,frame,0.12,z0,z1)
            for zz in (z0+frame/2,z1-frame/2,(z0+z1)/2):
                append_prism(trim_v,trim_f,wallxy,t,outward,w,0.12,zz-frame/2,zz+frame/2)
            # Projecting masonry sill below glazing.
            sillc=(wallxy[0]+outward[0]*0.05,wallxy[1]+outward[1]*0.05)
            append_prism(trim_v,trim_f,sillc,t,outward,w+0.18,0.18,z0-0.10,z0+0.01)
            opening_records.append({'edge':ei,'type':'window','center_m':c,'width_m':w,'sill_m':z0,'head_m':z1})
        elif typ=='garage':
            append_prism(door_v,door_f,wallxy,t,outward,w-0.08,0.09,z0+0.02,z1-0.02)
            frame=0.10
            for sgn in (-1,1):
                fc=(wallxy[0]+t[0]*(sgn*(w/2-frame/2)),wallxy[1]+t[1]*(sgn*(w/2-frame/2)))
                append_prism(trim_v,trim_f,fc,t,outward,frame,0.15,z0,z1)
            for k in range(1,5):
                zz=z0+(z1-z0)*k/5
                append_prism(trim_v,trim_f,wallxy,t,outward,w,0.08,zz-0.035,zz+0.035)
            opening_records.append({'edge':ei,'type':'double_garage_doors','center_m':c,'width_m':w,'head_m':z1})
        else:
            append_prism(door_v,door_f,wallxy,t,outward,w-0.08,0.08,z0+0.03,z1-0.02)
            # dark frame, split door leaves, small upper glazing and handles.
            for sgn in (-1,1):
                cen=(wallxy[0]+t[0]*(sgn*(w/2-0.035)),wallxy[1]+t[1]*(sgn*(w/2-0.035)))
                append_prism(trim_v,trim_f,cen,t,outward,0.07,0.12,z0,z1)
            append_prism(trim_v,trim_f,wallxy,t,outward,w,0.12,z1-0.06,z1+0.04)
            for sgn in (-1,1):
                cen=(wallxy[0]+t[0]*(sgn*w*0.25),wallxy[1]+t[1]*(sgn*w*0.25))
                append_prism(trim_v,trim_f,cen,t,outward,0.028,0.10,0.95,1.02)
            opening_records.append({'edge':ei,'type':'main_entry','center_m':c,'width_m':w,'head_m':z1})

mesh_obj(OBJ_NAME+'_Perimeter_Brickwork',wall_v,wall_f,brick,coll)
mesh_obj(OBJ_NAME+'_Window_Glass',glass_v,glass_f,glass,coll)
mesh_obj(OBJ_NAME+'_Window_Trim_and_Entry_Frames',trim_v,trim_f,trim,coll)
mesh_obj(OBJ_NAME+'_Main_Entry_Doors',door_v,door_f,door,coll)

# The source photo shows intersecting cross-gables. The roof volumes below use
# rectangular runs read from the orthogonal GIS footprint, with short overlaps
# at junctions. They are single-sided slate planes (no pale underside/deck is
# exposed at intersections). Wall placement remains tied to the original GIS ring.
def clip_v(poly,cut,keep_lower):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ina=(a[1]<=cut) if keep_lower else (a[1]>=cut)
        inb=(b[1]<=cut) if keep_lower else (b[1]>=cut)
        if ina and inb: result.append(b)
        elif ina and not inb:
            t=(cut-a[1])/(b[1]-a[1]);result.append((a[0]+t*(b[0]-a[0]),cut))
        elif not ina and inb:
            t=(cut-a[1])/(b[1]-a[1]);result.append((a[0]+t*(b[0]-a[0]),cut));result.append(b)
    # Remove adjacent duplicate points introduced where the cut meets a vertex.
    clean=[]
    for p in result:
        if not clean or math.dist(p,clean[-1])>1e-5:clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-5:clean.pop()
    return clean

def footprint_roof(poly, coll, mat):
    # Two triangulated slopes meet at a modest central ridge.  Each slope is
    # clipped against the actual concave GIS polygon, so there are no roof
    # overhang bounds or unsupported wing masses.  Ridge orientation remains
    # an explicitly documented estimate pending an elevation survey.
    vmin=min(p[1] for p in poly); vmax=max(p[1] for p in poly)
    vm=(vmin+vmax)/2; half=max((vmax-vmin)/2,0.01)
    eaves=3.35; ridge=5.85; verts=[]; faces=[]
    for lower in (True,False):
        part=clip_v(poly,vm,lower)
        if len(part)<3: continue
        tri=tessellate_polygon([[Vector((u,v,0)) for u,v in part]])
        off=len(verts)
        for u,v in part:
            z=eaves+(ridge-eaves)*(1.0-min(1.0,abs(v-vm)/half))
            verts.append(uv_world(u,v,z))
        faces.extend([tuple(off+i for i in face) for face in tri])
    ob=mesh_obj(OBJ_NAME+'_GIS_Clipped_Continuous_Roof',verts,faces,mat,coll)
    sol=ob.modifiers.new('Thin roof deck','SOLIDIFY'); sol.thickness=0.12; sol.offset=-1.0
    return ob

def cross_gable_roof(name,u0,u1,v0,v1,ridge_axis='u',eaves=3.38,ridge=6.25,
                     end_material=None):
    """Build two slate planes and matching triangular gable-end infill."""
    if ridge_axis=='u':
        vm=(v0+v1)/2
        points=[(u0,v0,eaves),(u1,v0,eaves),(u1,vm,ridge),
                (u0,vm,ridge),(u0,v1,eaves),(u1,v1,eaves)]
        faces=[(0,1,2,3),(3,2,5,4)]
        end_faces=[[(u0,v0,eaves),(u0,v1,eaves),(u0,vm,ridge)],
                   [(u1,v0,eaves),(u1,vm,ridge),(u1,v1,eaves)]]
    else:
        um=(u0+u1)/2
        points=[(u0,v0,eaves),(um,v0,ridge),(um,v1,ridge),
                (u0,v1,eaves),(u1,v0,eaves),(u1,v1,eaves)]
        faces=[(0,1,2,3),(1,4,5,2)]
        end_faces=[[(u0,v0,eaves),(um,v0,ridge),(u1,v0,eaves)],
                   [(u0,v1,eaves),(u1,v1,eaves),(um,v1,ridge)]]
    roof=mesh_obj(name+'_Slate_Planes',[uv_world(u,v,z) for u,v,z in points],faces,slate,coll)
    # fascia rails hide small seams where the gable planes meet, without creating
    # an exposed light-colored solid roof intersection.
    # Fascia only along the horizontal eaves. Sloped rake boards require tilted
    # 3D beams; making them as vertical prisms creates unsupported wall-like slabs.
    if ridge_axis=='u': eaves_edges=[((u0,v0),(u1,v0)),((u0,v1),(u1,v1))]
    else: eaves_edges=[((u0,v0),(u0,v1)),((u1,v0),(u1,v1))]
    for k,((a0,b0),(a1,b1)) in enumerate(eaves_edges):
        ca0=uv_to_xy(a0,b0);ca1=uv_to_xy(a1,b1);dx=ca1[0]-ca0[0];dy=ca1[1]-ca0[1];ln=math.hypot(dx,dy)
        if ln>0.1:
            tangent=(dx/ln,dy/ln);normal=(-tangent[1],tangent[0]);mid=((ca0[0]+ca1[0])/2,(ca0[1]+ca1[1])/2);vv=[];ff=[]
            append_prism(vv,ff,mid,tangent,normal,ln,0.12,eaves-0.10,eaves+0.10)
            mesh_obj(name+f'_Eave_Fascia_{k+1}',vv,ff,trim,coll)
    if end_material:
        vv=[];ff=[]
        for tri in end_faces:
            off=len(vv);vv.extend(uv_world(u,v,z) for u,v,z in tri);ff.append((off,off+1,off+2))
        mesh_obj(name+'_Dark_Wood_Gable_Cladding',vv,ff,end_material,coll)

dark_wood=material('SCHO • dark wood upper gable cladding',(.028,.009,.003),None,.88)
# Three footprint-derived wings form the principal and cross-gabled roof mass.
# Coordinates follow GIS-aligned UV bounds; only the roof eaves overlap at the
# junctions, while the surveyed perimeter wall path is unchanged.
cross_gable_roof(OBJ_NAME+'_West_Historic_Gable',72.55,82.86,1374.82,1383.87,'u',3.38,6.05,dark_wood)
cross_gable_roof(OBJ_NAME+'_East_Main_Cross_Gable',80.90,93.84,1367.38,1382.73,'u',3.38,6.55,dark_wood)
cross_gable_roof(OBJ_NAME+'_South_Wing_Cross_Gable',80.90,90.28,1363.68,1375.15,'v',3.38,5.95,dark_wood)

# Two brick chimney stacks emerge from the photo-visible roof ridges. Their
# exact survey positions are unavailable, so centers/heights remain estimates.
for i,(u,v,base_z,top_z) in enumerate([(77.72,1379.34,5.65,7.18),(87.45,1375.07,6.18,7.62)]):
    center=uv_to_xy(u,v);bt=[];bf=[];append_prism(bt,bf,center,(ca,sa),(-sa,ca),0.58,0.50,base_z,top_z)
    mesh_obj(OBJ_NAME+f'_Photo_Derived_Brick_Chimney_{i+1}',bt,bf,brick,coll)
    cap=[];cf=[];append_prism(cap,cf,center,(ca,sa),(-sa,ca),0.72,0.64,top_z,top_z+0.16)
    mesh_obj(OBJ_NAME+f'_Chimney_Cap_{i+1}',cap,cf,stone,coll)

# A projecting timber entry porch and two shallow masonry steps sit at the source-photo-facing long edge.
# Entry edge is GIS ring edge 0; porch placement follows its tangent, not an assumed campus north orientation.
a,b=xy[0],xy[1];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);t=(dx/L,dy/L);inward=(-dy/L,dx/L) if ccw else (dy/L,-dx/L);out=(-inward[0],-inward[1]); c=L*0.62
porch_center=(a[0]+t[0]*c+out[0]*1.0,a[1]+t[1]*c+out[1]*1.0)
pv=[];pf=[];append_prism(pv,pf,porch_center,t,out,2.7,1.7,2.42,2.58);mesh_obj(OBJ_NAME+'_Entry_Porch_Canopy',pv,pf,slate,coll)
for sgn in (-1,1):
    pp=(porch_center[0]+t[0]*sgn*1.12-out[0]*0.56,porch_center[1]+t[1]*sgn*1.12-out[1]*0.56)
    vv=[];ff=[];append_prism(vv,ff,pp,t,out,0.12,0.12,0.0,2.55);mesh_obj(OBJ_NAME+f'_Porch_Post_{sgn}',vv,ff,trim,coll)
for k in range(2):
    center=(porch_center[0]+out[0]*(1.35+k*0.30),porch_center[1]+out[1]*(1.35+k*0.30)); vv=[];ff=[]
    append_prism(vv,ff,center,t,out,1.55,0.45-k*0.08,0.12-k*0.1,0.28+k*0.12);mesh_obj(OBJ_NAME+f'_Entry_Step_{k+1}',vv,ff,stone,coll)

# Minimal schematic interior: one floorplate, vestibule and a few partitions; layout is explicitly not source-verified.
fv=[];ff=[]
for i in range(len(ring_xy)):
    fv.append((ring_xy[i][0],ring_xy[i][1],0.18))
ff=[tuple(range(len(fv)))]
mesh_obj(OBJ_NAME+'_Interior_Ground_Floorplate',fv,ff,floor_mat,coll)
# Partitions are contained in the two large footprint rectangles and use plaster, not exterior brick.
plaster=material('SCHO • warm interior plaster',(.66,.60,.49),None,.9)
parts_v=[];parts_f=[]
for u0,u1,v0,v1 in [(81.4,92.0,1368.05,1377.65),(73.45,80.98,1375.6,1383.1)]:
    for u,v,w in [((u0+u1)/2,v0+(v1-v0)*0.38,u1-u0-0.8),((u0+u1)/2,v0+(v1-v0)*0.72,u1-u0-0.8)]:
        center=uv_to_xy(u,v);append_prism(parts_v,parts_f,center,(ca,sa),(-sa,ca),w,0.13,0.18,2.75)
mesh_obj(OBJ_NAME+'_Schematic_Interior_Partitions',parts_v,parts_f,plaster,coll)
# Warm ceiling fixtures visible through the glazing; placement is schematic.
light_mat=material('SCHO • warm interior light',(1.0,.65,.30),None,.4)
light_bs=next(n for n in light_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');light_bs.inputs['Emission Color'].default_value=(1.0,.45,.12,1);light_bs.inputs['Emission Strength'].default_value=0.35
for u,v in [(84,1370),(88,1370),(76,1378),(79,1381)]:
    cxy=uv_to_xy(u,v); vv=[];ff=[];append_prism(vv,ff,cxy,(ca,sa),(-sa,ca),0.28,0.28,2.92,2.98);mesh_obj(OBJ_NAME+'_Interior_Ceiling_Light',vv,ff,light_mat,coll)

# Set active collection metadata and scene settings.
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world.color=(0.08,0.08,0.08)
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
# Remove any stale cameras/lights left in the source file, then create a neutral review setup.
for ob in list(scene.objects):
    if ob.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(ob,do_unlink=True)
cam_data=bpy.data.cameras.new('SCHO Review Camera');cam=bpy.data.objects.new('SCHO Review Camera',cam_data);scene.collection.objects.link(cam)
center_uv=(83.5,1373.5);cx,cy=uv_to_xy(*center_uv)
# Set the preview view toward the measured entry facade, at a pedestrian eye-level angle.
a,b=xy[0],xy[1]; edx=b[0]-a[0];edy=b[1]-a[1];elen=math.hypot(edx,edy);et=(edx/elen,edy/elen);ein=(-edy/elen,edx/elen) if ccw else (edy/elen,-edx/elen);eout=(-ein[0],-ein[1]);
cam.location=(cx+eout[0]*43,cy+eout[1]*43,14.5);target=Vector((cx,cy,3.1));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cam_data.type='ORTHO';cam_data.ortho_scale=39;scene.camera=cam
ld=bpy.data.lights.new('SCHO soft key','AREA');lo=bpy.data.objects.new('SCHO soft key',ld);scene.collection.objects.link(lo);lo.location=(cx-20,cy-25,30);ld.energy=1800;ld.shape='DISK';ld.size=26
ld2=bpy.data.lights.new('SCHO fill','AREA');lo2=bpy.data.objects.new('SCHO fill',ld2);scene.collection.objects.link(lo2);lo2.location=(cx+25,cy+18,18);ld2.energy=800;ld2.size=20
scene.render.filepath=str(AUDIT/'preview_three_quarter.png')
bpy.ops.render.render(write_still=True)
# A roof-forward secondary view documents the connected gables and measured footprint extents.
cam.location=(cx+43,cy-55,31.0);target=Vector((cx,cy,3.2));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cam_data.ortho_scale=43
scene.render.filepath=str(AUDIT/'preview_roof.png');bpy.ops.render.render(write_still=True)
# Return the source scene to a single-building, no-external-dependency package and save.
scene.camera=None
for ob in list(scene.objects):
    if ob.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# Record model metrics from the source-ring and built objects. The height is an estimate from the dated photograph.
allverts=[]
for ob in coll.objects:
    if ob.type=='MESH':
        dg=bpy.context.evaluated_depsgraph_get(); ev=ob.evaluated_get(dg); me=ev.to_mesh(); allverts.extend([ev.matrix_world@v.co for v in me.vertices]);ev.to_mesh_clear()
wall_ob=next(o for o in coll.objects if o.name.endswith('_Perimeter_Brickwork'))
deps=bpy.context.evaluated_depsgraph_get(); ev=wall_ob.evaluated_get(deps); wme=ev.to_mesh()
wall_xy=[( (ev.matrix_world@v.co).x, (ev.matrix_world@v.co).y) for v in wme.vertices]; ev.to_mesh_clear()
vertex_distances=[min(math.dist((x,y),p) for p in wall_xy) for x,y in ring_xy]
wall_bounds={'x':[min(p[0] for p in wall_xy),max(p[0] for p in wall_xy)],'y':[min(p[1] for p in wall_xy),max(p[1] for p in wall_xy)]}
metrics={'building_id':ASSET.stem,'source_feature_id':295,'source_area_m2':feature['attributes']['Shape.STArea()'],'gis_vertex_count':len(ring)-1,
 'gis_bounds_project_m':{'x':[min(x for x,y in xy),max(x for x,y in xy)],'y':[min(y for x,y in xy),max(y for x,y in xy)]},
 'model_evaluated_bounds_m':{'x':[min(v.x for v in allverts),max(v.x for v in allverts)],'y':[min(v.y for v in allverts),max(v.y for v in allverts)],'z':[min(v.z for v in allverts),max(v.z for v in allverts)]},
 'approximate_wall_footprint_error_m':0.14,'footprint_error_method':'wall exterior face is offset inward by 0.14 m for 0.28 m thick masonry; segment ends overlap at corners by 0.15 m to close seams','max_source_vertex_to_nearest_wall_mesh_vertex_m':max(vertex_distances),'mean_source_vertex_to_nearest_wall_mesh_vertex_m':sum(vertex_distances)/len(vertex_distances),'perimeter_wall_bounds_m':wall_bounds,'estimated_height_m':7.78,'height_status':'chimney cap tops; roof ridge and chimney heights inferred from photo, no surveyed height source found',
 'main_entry_and_window_openings':opening_records,'interior_status':'schematic partitions and floorplate; no interior source available',
 'material_summary':['procedural red-brown brick with mortar and bump','gray slate cross-gable roof planes','dark wood upper gable cladding','dark glass and timber frames','limestone sills/steps','schematic oak floor and plaster'],
 'validation':{'saved':True,'collection':COLL_NAME,'scene':SCENE_NAME,'object_count':len(coll.objects),'mesh_object_count':sum(o.type=='MESH' for o in coll.objects),'generated_texture_images':['SCHO_brick_tile','SCHO_slate_tile','SCHO_shingle_tile'],'textures_packed_into_blend':True,'external_absolute_texture_dependencies':[]}}
(AUDIT/'model_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
(AUDIT/'asset_sha256.txt').write_text(sha+'  '+ASSET.name+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2));print('SHA256',sha)

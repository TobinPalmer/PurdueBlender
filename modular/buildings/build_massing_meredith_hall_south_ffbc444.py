"""Rebuild Meredith Hall South from Purdue FID 410 and primary references.

Run from the repository root with Blender 5.2:
  blender --background modular/buildings/massing_meredith_hall_south_ffbc444.blend \
    --python modular/buildings/build_massing_meredith_hall_south_ffbc444.py

GIS walls use the source footprint in the project's local campus approximation.
The section heights come from Purdue's 2026-10-16 emergency plan; room layout,
facade bay sizing, and stair-bay positions are explicitly schematic estimates.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_meredith_hall_south_ffbc444"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
GIS_PATH = ROOT / "audit" / "official_purdue_buildings_wgs84.json"
OUT = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
LAT0 = 40.4274
LON0 = -86.9137
FLOOR_H = 3.30
BASE_FLOORS = 6
BASE_ROOF = FLOOR_H * BASE_FLOORS
WEST_ROOF = FLOOR_H * 8


def distance_to_segment(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = dx*dx+dy*dy
    t = 0.0 if den == 0 else max(0.0, min(1.0, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))


def simplify_ring(points, tolerance=0.2):
    pts = list(points[:-1] if points[0] == points[-1] else points)
    changed = True
    while changed and len(pts) > 8:
        changed = False
        for i in range(len(pts)):
            if distance_to_segment(pts[i], pts[i-1], pts[(i+1) % len(pts)]) <= tolerance:
                pts.pop(i)
                changed = True
                break
    return pts


def area(poly):
    return 0.5 * sum(poly[i][0]*poly[(i+1)%len(poly)][1] -
                     poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))


def clip_x(poly, limit, keep_less=True):
    """Sutherland-Hodgman clip of one ring against a vertical x plane."""
    if not poly:
        return []
    def inside(p): return p[0] <= limit + 1e-6 if keep_less else p[0] >= limit - 1e-6
    out=[]
    prev=poly[-1]
    for cur in poly:
        pin, cin=inside(prev),inside(cur)
        if cin != pin:
            den=cur[0]-prev[0]
            t=0.0 if abs(den)<1e-9 else (limit-prev[0])/den
            out.append((limit,prev[1]+t*(cur[1]-prev[1])))
        if cin: out.append(cur)
        prev=cur
    cleaned=[]
    for p in out:
        if not cleaned or math.dist(cleaned[-1],p)>1e-4: cleaned.append(p)
    if len(cleaned)>1 and math.dist(cleaned[0],cleaned[-1])<1e-4: cleaned.pop()
    return cleaned if len(cleaned)>=3 else []


def fresh_material(name, color, roughness=0.75, brick=False, transmission=0.0, metallic=0.0):
    old=bpy.data.materials.get(name)
    if old: bpy.data.materials.remove(old, do_unlink=True)
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial")
    shader=nt.nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value=(*color,1)
    shader.inputs["Roughness"].default_value=roughness
    shader.inputs["Metallic"].default_value=metallic
    if "Transmission Weight" in shader.inputs:
        shader.inputs["Transmission Weight"].default_value=transmission
    nt.links.new(shader.outputs["BSDF"],out.inputs["Surface"])
    if brick:
        tc=nt.nodes.new("ShaderNodeTexCoord")
        tex=nt.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Color1"].default_value=(0.15,0.024,0.016,1)
        tex.inputs["Color2"].default_value=(0.235,0.043,0.025,1)
        tex.inputs["Mortar"].default_value=(0.13,0.10,0.085,1)
        tex.inputs["Scale"].default_value=1.0
        tex.inputs["Mortar Size"].default_value=0.012
        tex.inputs["Brick Width"].default_value=0.48
        tex.inputs["Row Height"].default_value=0.14
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=0.22
        bump.inputs["Distance"].default_value=0.02
        nt.links.new(tc.outputs["Object"],tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"],shader.inputs["Base Color"])
        nt.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"],shader.inputs["Normal"])
    return m


def mesh_object(name, verts, faces, mat, collection):
    mesh=bpy.data.meshes.new(name+"Mesh")
    mesh.from_pydata(verts,[],faces)
    if mat: mesh.materials.append(mat)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    return obj


def prism(name, poly, z0, z1, mat, collection):
    if len(poly)<3: return None
    verts=[(x,y,z) for z in (z0,z1) for x,y in poly]
    n=len(poly)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    return mesh_object(name,verts,faces,mat,collection)


def append_box(verts,faces,center,tangent,normal,width,depth,z0,z1):
    tx,ty=tangent; nx,ny=normal; cx,cy=center; base=len(verts)
    for z in (z0,z1):
        for n in (-depth/2,depth/2):
            for t in (-width/2,width/2):
                verts.append((cx+tx*t+nx*n,cy+ty*t+ny*n,z))
    faces.extend([(base,base+1,base+3,base+2),(base+4,base+6,base+7,base+5),
      (base,base+4,base+5,base+1),(base+2,base+3,base+7,base+6),
      (base,base+2,base+6,base+4),(base+1,base+5,base+7,base+3)])


def append_axis_box(verts,faces,x,y,z,sx,sy,sz):
    b=len(verts); x0,x1=x-sx/2,x+sx/2; y0,y1=y-sy/2,y+sy/2; z0,z1=z-sz/2,z+sz/2
    verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                  (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
    faces.extend([(b,b+1,b+2,b+3),(b+4,b+7,b+6,b+5),(b,b+4,b+5,b+1),
                  (b+1,b+5,b+6,b+2),(b+2,b+6,b+7,b+3),(b+3,b+7,b+4,b)])


def y_span_at_x(poly,x):
    ys=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        if (a[0]<=x<b[0]) or (b[0]<=x<a[0]):
            t=(x-a[0])/(b[0]-a[0])
            ys.append(a[1]+t*(b[1]-a[1]))
    return (min(ys),max(ys)) if len(ys)>=2 else None


def add_text(name,body,location,size,collection,mat):
    data=bpy.data.curves.new(name,"FONT"); data.body=body; data.size=size; data.extrude=0.008
    obj=bpy.data.objects.new(name,data); collection.objects.link(obj)
    obj.location=location; obj.rotation_euler=(math.radians(90),0,0)
    if mat: data.materials.append(mat)
    return obj


def main():
    data=json.loads(GIS_PATH.read_text(encoding="utf-8"))
    feature=next(f for f in data["features"] if int(f["attributes"]["FID"])==410)
    attrs=feature["attributes"]
    assert attrs["BUILDING_N"]=="Virginia C. Meredith Residence Hall South"
    raw=feature["geometry"]["rings"][0]
    ll=raw[:-1] if raw[0]==raw[-1] else raw
    xy=[((lon+86.9137)*111412.84*math.cos(math.radians(LAT0)),(lat-LAT0)*111040.0) for lon,lat in ll]
    ring=simplify_ring(xy)
    minx,maxx=min(p[0] for p in ring),max(p[0] for p in ring)
    miny,maxy=min(p[1] for p in ring),max(p[1] for p in ring)
    building_span=maxx-minx
    cut_a=minx+building_span/3.0
    cut_b=minx+building_span*2.0/3.0
    west=clip_x(ring,cut_a,True)
    middle=clip_x(clip_x(ring,cut_a,False),cut_b,True)

    col=bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col=bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    for obj in list(col.objects): bpy.data.objects.remove(obj,do_unlink=True)
    for m in list(bpy.data.materials):
        if m.users==0: bpy.data.materials.remove(m,do_unlink=True)
    for im in list(bpy.data.images):
        if im.users==0: bpy.data.images.remove(im)

    brick=fresh_material("MRDS_Red_Brown_Brick_PBR",(0.16,0.026,0.018),brick=True)
    glass=fresh_material("MRDS_Reflective_BlueGray_Glazing",(0.018,0.055,0.072),roughness=0.18,transmission=0.04,metallic=0.22)
    frame=fresh_material("MRDS_Dark_Metal_Frames",(0.075,0.083,0.082),roughness=0.34,metallic=0.55)
    stone=fresh_material("MRDS_Warm_Light_Stone",(0.66,0.59,0.48),roughness=0.72)
    roof=fresh_material("MRDS_Gray_Roof_Membrane",(0.20,0.215,0.21),roughness=0.9)
    floor=fresh_material("MRDS_Interior_Light_Concrete",(0.53,0.51,0.47),roughness=0.86)
    partition=fresh_material("MRDS_Interior_Partition_Warm_White",(0.76,0.73,0.66),roughness=0.84)
    bedding=fresh_material("MRDS_Interior_Bedding",(0.46,0.58,0.62),roughness=0.94)
    furniture=fresh_material("MRDS_Interior_Furniture_Wood",(0.37,0.24,0.13),roughness=0.72)
    retail=fresh_material("MRDS_Retail_Sign_Panel",(0.13,0.095,0.065),roughness=0.55,metallic=0.15)
    white=fresh_material("MRDS_Retail_Lettering",(0.92,0.82,0.63),roughness=0.55)
    concrete=fresh_material("MRDS_Concrete_and_Mechanical_Screens",(0.42,0.43,0.41),roughness=0.88)

    # Purdue BEP: west A is eight floors; middle B and east C are six.
    prism("MRDS_Exterior_Base_B_C_and_A_Floors_1_to_6",ring,0,BASE_ROOF,brick,col)
    prism("MRDS_West_A_Section_Floors_7_to_8",west,BASE_ROOF,WEST_ROOF,brick,col)
    prism("MRDS_Roof_B_C",ring,BASE_ROOF-0.26,BASE_ROOF,roof,col)
    prism("MRDS_Roof_West_A",west,WEST_ROOF-0.26,WEST_ROOF,roof,col)
    prism("MRDS_Basement_B_Maintenance_and_Mechanical",middle,-3.3,0.0,concrete,col)

    # Add light stone coping strips around the section rooflines.
    sign_area=area(ring)
    normals=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        t=(dx/length,dy/length)
        normals.append((t[1],-t[0]) if sign_area>0 else (-t[1],t[0]))

    win_v,win_f,frame_v,frame_f=[],[],[],[]
    canopy_v,canopy_f,column_v,column_f=[],[],[],[]
    def add_window_on_edge(a,b,n,z0,width=0.82,height=1.96):
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length<4.0:return
        t=(dx/length,dy/length); count=max(1,int(length//3.35))
        for j in range(count):
            along=(j+0.5)*length/count
            c=(a[0]+t[0]*along+n[0]*0.075,a[1]+t[1]*along+n[1]*0.075)
            append_box(win_v,win_f,c,t,n,width,0.12,z0,z0+height)
            fw=0.045
            for ccw,dd,lo,hi in [(width+fw*2,fw,z0-fw/2,z0+fw/2),
                (width+fw*2,fw,z0+height-fw/2,z0+height+fw/2),
                (fw,height,-width/2-fw/2+0,z0+height/2),
                (fw,height,width/2+fw/2,z0+height/2)]:
                if dd==fw:
                    center=c; boxw=ccw; zz0=lo;zz1=hi
                else:
                    shift=lo
                    center=(c[0]+t[0]*shift,c[1]+t[1]*shift); boxw=ccw;zz0=hi-height/2;zz1=hi+height/2
                append_box(frame_v,frame_f,center,t,n,boxw,0.17,zz0,zz1)

    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length<5.0: continue
        n=normals[i]; centerx=(a[0]+b[0])/2
        south=n[1] < -0.45
        for level in range(BASE_FLOORS):
            z0=0.92+level*FLOOR_H
            if level==0 and south: continue
            add_window_on_edge(a,b,n,z0)
        if centerx < cut_a-0.4:
            for level in (6,7):
                add_window_on_edge(a,b,n,0.92+level*FLOOR_H)
        # Glazed public ground floor along 1st Street facing south.
        if south and length>7.0:
            t=(dx/length,dy/length); count=max(1,int(length//8.0)); panel_w=length/count
            for j in range(count):
                along=(j+0.5)*panel_w
                c=(a[0]+t[0]*along+n[0]*0.10,a[1]+t[1]*along+n[1]*0.10)
                append_box(win_v,win_f,c,t,n,panel_w-0.32,0.16,0.30,3.55)
                append_box(frame_v,frame_f,c,t,n,0.085,0.2,0.3,3.55)
                append_box(frame_v,frame_f,c,t,n,panel_w-0.32,0.2,3.48,3.58)
            # Purdue's opening photograph shows a light canopy and slender
            # columns along the transparent first-floor public frontage.
            if length>20.0:
                canopy_center=((a[0]+b[0])/2+n[0]*0.85,(a[1]+b[1])/2+n[1]*0.85)
                append_box(canopy_v,canopy_f,canopy_center,t,n,length-0.6,2.2,3.58,3.98)
                columns=max(2,int(length//7.5))
                for k in range(columns+1):
                    sh=-length/2+length*k/columns
                    cc=(canopy_center[0]+t[0]*sh+n[0]*0.9,canopy_center[1]+t[1]*sh+n[1]*0.9)
                    append_box(column_v,column_f,cc,t,n,0.24,0.24,0.05,3.58)

    mesh_object("MRDS_Punched_Window_Bays_and_Ground_Floor_Glazing",win_v,win_f,glass,col)
    mesh_object("MRDS_Window_Frames_and_Curtainwall_Mullions",frame_v,frame_f,frame,col)
    mesh_object("MRDS_First_Street_Ground_Floor_Canopy",canopy_v,canopy_f,stone,col)
    mesh_object("MRDS_First_Street_Slender_Canopy_Columns",column_v,column_f,frame,col)

    # Two prominent multi-storey glazed study/stair volumes on long public facades.
    candidates=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        n=normals[i]
        if length>12 and n[1]<-0.45 and abs(dx)>abs(dy)*1.5:
            candidates.append((i,a,b,length,n))
    if not candidates:
        candidates=[(i,ring[i],ring[(i+1)%len(ring)],math.dist(ring[i],ring[(i+1)%len(ring)]),normals[i]) for i in range(len(ring)) if math.dist(ring[i],ring[(i+1)%len(ring)])>18]
    candidates.sort(key=lambda q:(q[1][0]+q[2][0])/2)
    bays=[]
    if candidates:
        # The 2020 Purdue opening photograph shows a smaller west-junction
        # glazed stair and one broad east study/stair bay; the central run is
        # predominantly punched brick. Select the outer public runs.
        bays=[candidates[0],candidates[-1]] if len(candidates)>1 else [candidates[0]]
    tower_v,tower_f,mullion_v,mullion_f=[],[],[],[]
    for idx,(edge,a,b,length,n) in enumerate(bays):
        dx,dy=b[0]-a[0],b[1]-a[1];t=(dx/length,dy/length)
        w=min(5.8 if idx==0 else 11.8,length*0.52)
        along=length*(0.18 if idx==0 else 0.72)
        c=(a[0]+t[0]*along+n[0]*0.12,a[1]+t[1]*along+n[1]*0.12)
        z0=0.18 if idx==1 else 3.25
        z1=BASE_ROOF-0.22 if idx==1 else 13.2
        append_box(tower_v,tower_f,c,t,n,w,0.18,z0,z1)
        verticals=max(2,int(w//1.9))
        for k in range(1,verticals):
            sh=-w/2+k*w/verticals
            cc=(c[0]+t[0]*sh,c[1]+t[1]*sh)
            append_box(mullion_v,mullion_f,cc,t,n,0.085,0.23,z0,z1)
        first=math.ceil((z0+0.15)/FLOOR_H)
        last=math.floor((z1-0.15)/FLOOR_H)
        for k in range(first,last+1):
            z=FLOOR_H*k
            append_box(mullion_v,mullion_f,c,t,n,w,0.23,z-0.10,z+0.10)
    mesh_object("MRDS_Multistory_Glass_Stair_and_Study_Bays_Estimated",tower_v,tower_f,glass,col)
    mesh_object("MRDS_Glass_Bay_Floor_and_Vertical_Frames",mullion_v,mullion_f,frame,col)

    # Purdue BEP places Panera and QDOBA retail in east/C first-floor area.
    east_edges=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)];cx=(a[0]+b[0])/2
        if cx>cut_b and normals[i][1]<-0.35 and math.dist(a,b)>5: east_edges.append((i,a,b,math.dist(a,b),normals[i]))
    if not east_edges: east_edges=[q for q in candidates if (q[1][0]+q[2][0])/2>cut_b]
    retail_panels_v,retail_panels_f=[],[]
    sign_candidates=[]
    if east_edges:
        i,a,b,length,n=east_edges[0]
        dx,dy=b[0]-a[0],b[1]-a[1];t=(dx/length,dy/length)
        for label,ratio in [("PANERA",0.37),("QDOBA",0.66)]:
            along=length*ratio
            c=(a[0]+t[0]*along+n[0]*0.24,a[1]+t[1]*along+n[1]*0.24)
            width=min(6.0,length*0.24)
            append_box(retail_panels_v,retail_panels_f,c,t,n,width,0.2,0.32,3.65)
            sign_candidates.append((c,t,n,width,label))
    mesh_object("MRDS_East_C_Retail_Curtainwall_Estimate",retail_panels_v,retail_panels_f,glass,col)
    for c,t,n,w,label in sign_candidates:
        add_text("MRDS_Retail_Sign_"+label,label,(c[0]-w*0.34,c[1]-0.28,3.82),0.52,col,white)

    # Schematic interior floors, central corridor, double-room modules and
    # representative furniture; these are source-informed use cues, not a plan.
    interior_data={}
    ymid=(miny+maxy)/2
    for level in range(1,9):
        room_floor_v,room_floor_f=[],[]
        bed_v,bed_f,desk_v,desk_f=[],[],[],[]
        wall_v,wall_f=[],[]
        interior_data[level]=(room_floor_v,room_floor_f,wall_v,wall_f,bed_v,bed_f,desk_v,desk_f)
        z=level*FLOOR_H
        # Floor plate follows the GIS plan on levels 1-6 and west A on levels 7-8.
        plate=ring if level<=6 else west
        if not plate: continue
        prism("MRDS_Interior_Floor_Plate_L%02d"%level,plate,z-0.12,z,floor,col)
        x0,x1=(minx+4,maxx-4) if level<=6 else (minx+4,cut_a-3)
        # Corridor is inset by the source footprint's local section width.
        corridor_len=max(0.0,x1-x0)
        if corridor_len>3:
            append_axis_box(room_floor_v,room_floor_f,(x0+x1)/2,ymid,z-FLOOR_H-0.1,corridor_len,1.8,0.12)
        start=x0;step=4.98;stop=x1
        x=start
        while x<stop:
            span=y_span_at_x(plate,x)
            if not span:
                x+=step
                continue
            # Keep the schematic rooms in a conservative central band. The
            # mapped footprint has stepped wings, so a min/max cross-section
            # across a concave notch can otherwise bridge outdoor space.
            south_y=max(span[0],ymid-4.65)
            north_y=min(span[1],ymid+4.65)
            local_mid=(south_y+north_y)/2
            depth=north_y-south_y
            if depth<8:
                x+=step
                continue
            for side in (-1,1):
                corridor_edge=local_mid+side*0.9
                outer_edge=north_y-0.2 if side>0 else south_y+0.2
                room_depth=abs(outer_edge-corridor_edge)
                if room_depth<2: continue
                room_center=(outer_edge+corridor_edge)/2
                # Schematic double-room divider and furniture stay inside the local GIS cross-section.
                floor_base=z-FLOOR_H
                append_axis_box(wall_v,wall_f,x,room_center,floor_base+1.30,0.12,room_depth,2.6)
                bed_y=room_center+side*min(0.9,room_depth*0.18)
                append_axis_box(bed_v,bed_f,x+1.35,bed_y,floor_base+0.34,1.9,0.88,0.68)
                append_axis_box(bed_v,bed_f,x-1.0,bed_y,floor_base+0.34,1.9,0.88,0.68)
                desk_y=outer_edge-side*0.8
                append_axis_box(desk_v,desk_f,x+2.1,desk_y,floor_base+0.39,1.0,0.52,0.78)
            x+=step
    for level,items in interior_data.items():
        rv,rf,wv,wf,bv,bf,dv,df=items
        mesh_object("MRDS_Interior_Corridor_Floor_L%02d"%level,rv,rf,floor,col)
        mesh_object("MRDS_Interior_Room_Partitions_L%02d"%level,wv,wf,partition,col)
        mesh_object("MRDS_Interior_Double_Room_Beds_L%02d"%level,bv,bf,bedding,col)
        mesh_object("MRDS_Interior_Desks_L%02d"%level,dv,df,furniture,col)

    # Interior commons / kitchen-lounge cues in B and ground-floor retail/office zones.
    amenity_v,amenity_f=[],[]
    for x in [minx+building_span*0.43,minx+building_span*0.60]:
        for yy in (ymid-4.0,ymid+4.0):
            append_axis_box(amenity_v,amenity_f,x,yy,1.65,2.4,0.95,0.75)
            append_axis_box(amenity_v,amenity_f,x+1.7,yy,1.65,0.45,0.45,0.9)
    mesh_object("MRDS_Schematic_Lobby_Lounge_and_Common_Furniture",amenity_v,amenity_f,furniture,col)

    # Compact roof mechanical screens sit below the highest west roofline.
    mech_v,mech_f=[],[]
    for x,y,w,d,h in [(maxx-14,miny+8,2.6,1.9,0.75),(maxx-22,maxy-8,2.2,1.7,0.65),
                      (minx+building_span*0.49,miny+8,2.5,1.8,0.7)]:
        append_axis_box(mech_v,mech_f,x,y,BASE_ROOF+h/2,w,d,h)
    mesh_object("MRDS_Compact_Rooftop_Mechanical_Screens",mech_v,mech_f,concrete,col)

    # Drop unused legacy images/materials so this library carries only the new
    # procedural materials and has no stale external image references.
    for m in list(bpy.data.materials):
        if m.users==0: bpy.data.materials.remove(m,do_unlink=True)
    for im in list(bpy.data.images):
        if im.users==0: bpy.data.images.remove(im)

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(json.dumps({"asset":str(OUT),"source_fid":410,"name":attrs["BUILDING_N"],
      "footprint_vertices":len(ring),"floor_counts":{"west_A":8,"middle_B":6,"east_C":6},
      "section_bounds_x_m":{"west_A":[minx,cut_a],"middle_B":[cut_a,cut_b],"east_C":[cut_b,maxx]},
      "basement_B_m":-3.3,"roof_heights_m":{"B_C":BASE_ROOF,"A":WEST_ROOF},
      "object_count":len(col.objects),"interior":"schematic corridor, doubles, beds, desks, lounge; not dimensioned plan"},indent=2))


if __name__=="__main__":
    main()

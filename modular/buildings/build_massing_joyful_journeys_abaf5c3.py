"""Build Joyful Journey (massing_joyful_journeys_abaf5c3) as a sourced low-rise home/day-service massing.
The XY outline comes from OSM way 869182111 and is checked against Esri aerial. Height and facade details are estimates.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ID='massing_joyful_journeys_abaf5c3'
ASSET=ROOT/'modular'/'buildings'/(ID+'.blend')
REVIEW=ROOT/'audit'/ID/'review'
COL='Asset_'+ID
SCENE='Building_'+ID
# Exact transformed OSM roof-perimeter coordinates (WGS84 to project documented local approximation).
RING=[(-104.04564919,2066.010240),(-99.73727050,2067.398240),(-101.18753183,2071.862048),(-91.06962675,2075.126624),(-89.90772147,2071.562240),(-69.69735450,2078.080288),(-65.91480156,2066.432192),(-74.04813850,2063.811648),(-73.31876730,2061.568640),(-89.84835405,2056.238720),(-91.06114569,2059.980768),(-101.03487274,2056.760608)]
EAVE=5.40
PEAK=8.70
RIDGE_Y=2066.8224
RIDGE_X0=-101.5247
RIDGE_X1=-66.0415

# Clean a standalone simple-massing library.
if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c,do_unlink=True)
sc=bpy.context.scene; sc.name=SCENE; sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1.0
col=bpy.data.collections.new(COL); sc.collection.children.link(col)

def mat(name,color,rough=.82,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
# Exterior finish is kept neutral because no reliable elevation/material schedule was located.
mats=[mat('Muted green-gray lap siding from 2019 facade photo',(.37,.49,.42)),mat('Warm white trim and porch',(.88,.86,.78)),mat('Dark window glass',(.09,.16,.18),.35,.05),mat('Weathered charcoal roof',(.22,.23,.22)),mat('Dark entry door',(.12,.18,.16)),mat('Foundation masonry',(.47,.46,.42)),mat('Deep red shutters',(.31,.12,.13))]
verts=[]; faces=[]; mids=[]
def face(points,mi):
    inds=[]
    for p in points: inds.append(len(verts)); verts.append(tuple(p))
    faces.append(tuple(inds)); mids.append(mi)
def quad(a,b,c,d,mi): face([a,b,c,d],mi)

def box(center,tangent,normal,width,depth,z0,z1,mi):
    cx,cy=center; tx,ty=tangent; nx,ny=normal; w=width/2; d=depth/2
    poly=[(cx-tx*w-nx*d,cy-ty*w-ny*d),(cx+tx*w-nx*d,cy+ty*w-ny*d),(cx+tx*w+nx*d,cy+ty*w+ny*d),(cx-tx*w+nx*d,cy-ty*w+ny*d)]
    face([(x,y,z0) for x,y in poly],mi); face([(x,y,z1) for x,y in poly],mi)
    for i in range(4):
        a=poly[i];b=poly[(i+1)%4];quad((a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1),mi)

def wall_panel(a,b,t0,t1,z0,z1,offset,mi):
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);tx,ty=dx/L,dy/L
    nx,ny=(dy/L,-dx/L) if ccw else (-dy/L,dx/L)
    p0=(a[0]+dx*t0+nx*offset,a[1]+dy*t0+ny*offset,z0)
    p1=(a[0]+dx*t1+nx*offset,a[1]+dy*t1+ny*offset,z0)
    p2=(p1[0],p1[1],z1);p3=(p0[0],p0[1],z1)
    face([p0,p1,p2,p3],mi)
    return (tx,ty,nx,ny,L)

# Low single-level residential/day-service shell; the source describes a home but does not establish floor count.
area=sum(RING[i][0]*RING[(i+1)%len(RING)][1]-RING[(i+1)%len(RING)][0]*RING[i][1] for i in range(len(RING)))
ccw=area>0
face([(x,y,0) for x,y in RING],5)
face([(x,y,EAVE) for x,y in RING],0)
for i,a in enumerate(RING):
    b=RING[(i+1)%len(RING)]
    quad((a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],EAVE),(a[0],a[1],EAVE),0)
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    if L<3.6: continue
    tx,ty=dx/L,dy/L; nx,ny=(dy/L,-dx/L) if ccw else (-dy/L,dx/L)
    # Schematic house-scale window rhythm; openings are representational, not measured.
    count=max(1,min(7,int(L/5.0)))
    step=L/(count+1)
    for j in range(count):
        mid=(j+1)*step; width=min(1.35,step*.47)
        for z0,z1 in ([(1.0,2.55),(3.25,4.75)] if (a[1]+b[1])/2 < 2063.0 else [(1.0,2.55)]):
            w=width; t0=(mid-w/2)/L;t1=(mid+w/2)/L
            wall_panel(a,b,t0,t1,z0,z1,.075,2)
            trim=.075
            wall_panel(a,b,t0-.035,t1+.035,z0-.06,z0+.02,.09,1)
            wall_panel(a,b,t0-.035,t1+.035,z1-.02,z1+.06,.09,1)
            wall_panel(a,b,t0-.035,t0+.015,z0,z1,.09,1)
            wall_panel(a,b,t1-.015,t1+.035,z0,z1,.09,1)
            if z0 > 3.0:
                # Shutters flank upper front-gable windows, matching the 2019 address photo.
                sw=.20; sh0=max(z0+.12,.35); sh1=z1-.12
                wall_panel(a,b,max(0,t0-sw/L),t0-.035,sh0,sh1,.10,6)
                wall_panel(a,b,t1+.035,min(1,t1+sw/L),sh0,sh1,.10,6)
            # center mullion
            wall_panel(a,b,(t0+t1)/2-.006,(t0+t1)/2+.006,z0,z1,.095,1)

# Main continuous gabled roof. Aerial supports a multi-faceted pitched residential roof;
# exact ridge breaks and roof heights are not documented, so this silhouette is explicitly approximate.
R=[(x,y) for x,y in RING]
for i,a in enumerate(R):
    b=R[(i+1)%len(R)]
    za=(EAVE if abs(a[1]-RIDGE_Y)<.06 else EAVE)
    zb=EAVE
    e0=(a[0],a[1],za);e1=(b[0],b[1],zb)
    if a[1]>=RIDGE_Y and b[1]>=RIDGE_Y:
        r0=(max(RIDGE_X0,min(RIDGE_X1,a[0])),RIDGE_Y,PEAK)
        r1=(max(RIDGE_X0,min(RIDGE_X1,b[0])),RIDGE_Y,PEAK)
        face([e0,e1,r1,r0],3)
    elif a[1]<=RIDGE_Y and b[1]<=RIDGE_Y:
        r0=(max(RIDGE_X0,min(RIDGE_X1,a[0])),RIDGE_Y,PEAK)
        r1=(max(RIDGE_X0,min(RIDGE_X1,b[0])),RIDGE_Y,PEAK)
        face([e0,r0,r1,e1],3)
    else:
        # End/transition edge: connect to closest ridge end as an approximate hip plane.
        r=(RIDGE_X0 if (a[0]+b[0])/2<RIDGE_X0 else RIDGE_X1,RIDGE_Y,PEAK)
        face([e0,e1,r],3)
# Ridge cap, subtle and centered along the long axis.
box(((RIDGE_X0+RIDGE_X1)/2,RIDGE_Y),(1,0),(0,1),RIDGE_X1-RIDGE_X0,.20,PEAK-.05,PEAK+.06,3)

# One schematic entrance canopy on the Lindberg-facing (south) edge; exact door position is not documented.
# use the longest southern facade segment (edge 8->9).
a=RING[8];b=RING[9];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);tx,ty=dx/L,dy/L
nx,ny=(dy/L,-dx/L) if ccw else (-dy/L,dx/L)
mid=.53*L; doorw=1.25; t0=(mid-doorw/2)/L;t1=(mid+doorw/2)/L
wall_panel(a,b,t0,t1,.05,2.25,.095,4)
wall_panel(a,b,t0-.05,t0,t0*0+0.05,2.27,.105,1)
wall_panel(a,b,t1,t1+.05,.05,2.27,.105,1)
# A simple canopy is represented by a slim light roof plane and two supports.
cx=a[0]+tx*mid+nx*.72;cy=a[1]+ty*mid+ny*.72
face([(cx-tx*1.25,cy-ty*1.25,2.55),(cx+tx*1.25,cy+ty*1.25,2.55),(cx+tx*1.25+nx*.65,cy+ty*1.25+ny*.65,2.55),(cx-tx*1.25+nx*.65,cy-ty*1.25+ny*.65,2.55)],1)
for s in [-.95,.95]:
    x=cx+tx*s+nx*.62;y=cy+ty*s+ny*.62
    box((x,y),(1,0),(0,1),.10,.10,0,2.52,1)

mesh=bpy.data.meshes.new('JoyfulJourney_shell_and_gabled_roof');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('Joyful Journeys',mesh);col.objects.link(obj)
for m in mats:mesh.materials.append(m)
for p,mi in zip(mesh.polygons,mids):p.material_index=mi
obj['stable_id']=ID
obj['use']='Joyful Journey adult day service; former single-family home per 2014 county zoning staff report'
obj['source_footprint']='OSM way 869182111 (name/address match), visually checked against Esri World Imagery export; roof perimeter proxy, not surveyed wall line'
obj['height_m_estimate']=PEAK
obj['height_evidence']='Approximate 8.7 m total: scaled visually from the second-level gable windows and entry in the 2019 community-guide photo; no surveyed or published elevation. Eave 5.4 m also estimated.'
obj['storey_count_estimate']='2 above-grade levels estimated from upper-level windows visible in the 2019 photo; exact floor count and floor heights unverified'
obj['roof_form']='approximate multi-facet gable from aerial; exact ridge layout unverified'
obj['facade']='Photo-informed schematic: muted green-gray siding, light trim, dark shutters, upper gable windows, and covered entrance; locations and colors interpreted from the 2019 photo, remaining openings schematic'
sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100
# Save clean portable collection before creating temporary review camera/lights.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# Review camera and lights are temporary and are removed after rendering.
world=bpy.data.worlds.new('Joyful Journey Review World') if not bpy.data.worlds else bpy.data.worlds[0];sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.74,.80,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.72
center=Vector((-84.98,2066.82,4.8))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('review_camera');cam=bpy.data.objects.new('review_camera',camd);sc.collection.objects.link(cam);camd.type='ORTHO';camd.ortho_scale=54;cam.location=(center.x-34,center.y-42,center.z+24);aim(cam,center);sc.camera=cam
ld=bpy.data.lights.new('review_area','AREA');lo=bpy.data.objects.new('review_area',ld);sc.collection.objects.link(lo);lo.location=(center.x-16,center.y-24,center.z+35);ld.energy=9000;ld.shape='DISK';ld.size=28;aim(lo,center)
sc.render.image_settings.file_format='PNG';sc.render.filepath=str(REVIEW/'joyful_journeys_hero_r2.png');bpy.ops.render.render(write_still=True)
cam.location=(center.x-10,center.y-8,center.z+70);aim(cam,center);camd.ortho_scale=56;sc.render.filepath=str(REVIEW/'joyful_journeys_aerial_r2.png');bpy.ops.render.render(write_still=True)


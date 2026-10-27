"""Build the evidence-backed Gamma Phi Beta / Delta Iota chapter-house asset.

Run from the repository root:
  blender -b --python modular/buildings/build_gamma_phi_beta.py

The original campus-coordinate massing library is read only and remains unchanged.
This detailed asset uses a local frame centered on the transformed official GIS bounds.
"""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
GIS_PATH = ROOT / 'audit' / 'gamma_phi_beta' / 'gis_feature_fid_759.json'
ASSET_PATH = ROOT / 'modular' / 'buildings' / 'gamma_phi_beta.blend'
AUDIT = ROOT / 'audit' / 'gamma_phi_beta'
assert GIS_PATH.exists()
feature_set = json.loads(GIS_PATH.read_text(encoding='utf-8-sig'))
feature = next(f for f in feature_set['features'] if f['attributes']['FID'] == 759)
attrs, ring_ll = feature['attributes'], feature['geometry']['rings'][0]
assert attrs['BUILDING_N'] == 'Gamma Phi Beta' and attrs['ADDRESS'] == '810 David Ross Rd'
ring_ll = ring_ll[:-1] if ring_ll[0] == ring_ll[-1] else ring_ll
LAT0, LON0 = 40.4274, -86.9137
def campus_xy(lon, lat):
    return ((lon-LON0)*111412.84*math.cos(math.radians(LAT0)), (lat-LAT0)*111040.0)
ring_world = [campus_xy(lon, lat) for lon,lat in ring_ll]
origin = ((min(p[0] for p in ring_world)+max(p[0] for p in ring_world))/2,
          (min(p[1] for p in ring_world)+max(p[1] for p in ring_world))/2)
ring = [(x-origin[0],y-origin[1]) for x,y in ring_world]
assert len(ring) == 12
signed_area = sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
assert abs(signed_area) > 500
# Use counter-clockwise ring order so extruded shell normals face outward. Retain
# the identified small projection segment as the tentative entry edge after reversal.
entry_hint = (Vector(ring[3]) + Vector(ring[4])) / 2
if signed_area < 0:
    ring.reverse()
    ring_ll.reverse()
    signed_area = -signed_area
ccw = True

# The export collection is the only geometry that the master should instance.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'Building_gamma_phi_beta'
asset = bpy.data.collections.new('Asset_gamma_phi_beta')
scene.collection.children.link(asset)
stage = bpy.data.collections.new('Render_stage_gamma_phi_beta')
scene.collection.children.link(stage)

def material(name, color, roughness=0.6, metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nodes=m.node_tree.nodes; nodes.clear(); links=m.node_tree.links
    out=nodes.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    bsdf=nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location=(360,0)
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Roughness'].default_value=roughness
    bsdf.inputs['Metallic'].default_value=metallic
    links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return m,bsdf

skin,skin_bsdf=material('GPB | muted charcoal coated steel skin',(0.27,0.30,0.31),0.68,0.22)
nodes=skin.node_tree.nodes; links=skin.node_tree.links
geo=nodes.new('ShaderNodeNewGeometry'); geo.location=(-700,120)
noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-490,130); noise.inputs['Scale'].default_value=42; noise.inputs['Detail'].default_value=2
ramp=nodes.new('ShaderNodeValToRGB'); ramp.location=(-240,130)
ramp.color_ramp.elements[0].position=0.23; ramp.color_ramp.elements[0].color=(0.19,0.22,0.23,1)
ramp.color_ramp.elements[1].position=0.78; ramp.color_ramp.elements[1].color=(0.36,0.40,0.41,1)
bump=nodes.new('ShaderNodeBump'); bump.location=(120,-120); bump.inputs['Strength'].default_value=0.12; bump.inputs['Distance'].default_value=0.018
links.new(geo.outputs['Position'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
links.new(ramp.outputs['Color'],skin_bsdf.inputs['Base Color']); links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],skin_bsdf.inputs['Normal'])
rib_mat,_=material('GPB | standing rib highlights',(0.36,0.39,0.39),0.52,0.34)
roof_mat,_=material('GPB | aluminized steel roof',(0.45,0.48,0.48),0.38,0.58)
dark_metal,_=material('GPB | dark bronze window and canopy metal',(0.065,0.085,0.092),0.32,0.62)
glass,glass_bsdf=material('GPB | tinted blue charcoal glazing',(0.055,0.11,0.145),0.16,0.32)
glass_bsdf.inputs['Transmission Weight'].default_value=0.18
wood,_=material('GPB | carved entry door wood',(0.30,0.15,0.075),0.44,0.05)
concrete,_=material('GPB | foundation and entry concrete',(0.36,0.37,0.36),0.78,0.0)
interior,_=material('GPB | schematic interior warm neutral',(0.62,0.58,0.50),0.82,0.0)
furniture,_=material('GPB | schematic interior furniture',(0.35,0.22,0.14),0.67,0.0)
stage_mat,_=material('GPB render stage | grass-muted earth',(0.15,0.20,0.15),0.93,0.0)

def obj_mesh(name, verts, faces, mat, collection=asset):
    mesh=bpy.data.meshes.new(name+' Mesh'); mesh.from_pydata(verts,[],faces); mesh.validate(); mesh.update()
    if mat: mesh.materials.append(mat)
    ob=bpy.data.objects.new(name,mesh); collection.objects.link(ob)
    return ob

def add_faces(name, faces, mat):
    verts=[]; polys=[]
    for f in faces:
        i=len(verts); verts.extend(f); polys.append(tuple(range(i,i+len(f))))
    return obj_mesh(name,verts,polys,mat)

def prism(name, poly, z0, z1, mat, collection=asset):
    n=len(poly); verts=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return obj_mesh(name,verts,faces,mat,collection)

def scaled_poly(poly, amount):
    # Small radial roof/foundation eaves; this is a visual offset, not a GIS shift.
    cx=sum(p[0] for p in poly)/len(poly); cy=sum(p[1] for p in poly)/len(poly)
    factor=1+amount/(max(math.hypot(x-cx,y-cy) for x,y in poly))
    return [(cx+(x-cx)*factor,cy+(y-cy)*factor) for x,y in poly]

def box(name, center, dims, mat, angle=0.0, collection=asset):
    cx,cy,cz=center; dx,dy,dz=(d/2 for d in dims); ca,sa=math.cos(angle),math.sin(angle)
    local=[(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),(-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]
    verts=[(cx+x*ca-y*sa,cy+x*sa+y*ca,cz+z) for x,y,z in local]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return obj_mesh(name,verts,faces,mat,collection)

def point_on_edge(a,u,n,t,offset,z):
    q=Vector(a)+u*t+n*offset
    return (q.x,q.y,z)

# GIS-derived exterior wall grid with explicit door/window openings.
floor_levels=[0.0,3.72,7.44,11.16,12.0]
base_z, roof_z=0.0,12.0
entry_edge_idx=min(range(len(ring)), key=lambda i: ((Vector(ring[i])+Vector(ring[(i+1)%len(ring)]))*0.5-entry_hint).length) # tentative door edge at the mapped footprint step.
edge_records=[]
windows_by_edge={}
for i,a0 in enumerate(ring):
    b0=ring[(i+1)%len(ring)]
    delta=Vector((b0[0]-a0[0],b0[1]-a0[1])); length=delta.length; u=delta.normalized()
    n=Vector((u.y,-u.x)) if ccw else Vector((-u.y,u.x))
    edge_records.append((a0,b0,u,n,length))
    wins=[]
    if i != entry_edge_idx and length >= 9.5:
        # Even groups of narrow vertical sash windows across photo-observed flat steel walls.
        group_count=4 if length>27 else (2 if length>18 else 1)
        margin=max(1.65,length*0.075)
        centers=[margin+(length-2*margin)*(k+0.5)/group_count for k in range(group_count)]
        for c in centers:
            for du in (-0.57,0.57):
                wc=c+du
                for f in range(3):
                    z0=floor_levels[f]+0.88
                    z1=min(floor_levels[f+1]-0.28,z0+2.02)
                    wins.append((wc-0.43,wc+0.43,z0,z1,'window'))
    if i == entry_edge_idx:
        door_t=length*0.5
        wins.append((door_t-0.82,door_t+0.82,base_z+0.02,base_z+2.55,'door'))
    windows_by_edge[i]=wins


wall_faces_by_edge=[]; all_rib_faces=[]; all_band_faces=[]
for i,(a,b,u,n,length) in enumerate(edge_records):
    a=Vector(a)
    openings=windows_by_edge[i]
    ts=sorted(set([0.0,length]+[max(0.0,min(length,t)) for w in openings for t in w[:2]]))
    zs=sorted(set([base_z,roof_z]+floor_levels+[z for w in openings for z in w[2:4]]))
    quads=[]
    for j in range(len(ts)-1):
        tm=(ts[j]+ts[j+1])/2
        for k in range(len(zs)-1):
            zm=(zs[k]+zs[k+1])/2
            if any(t0<tm<t1 and z0<zm<z1 for t0,t1,z0,z1,_ in openings):
                continue
            p0=point_on_edge(a,u,n,ts[j],0.0,zs[k]); p1=point_on_edge(a,u,n,ts[j+1],0.0,zs[k])
            p2=point_on_edge(a,u,n,ts[j+1],0.0,zs[k+1]); p3=point_on_edge(a,u,n,ts[j],0.0,zs[k+1])
            quads.append((p0,p1,p2,p3))
    wall_faces_by_edge.append((i,quads))

    # Vertical standing ribs are interrupted at all openings, in keeping with the 1979 image.
    rib_pitch=0.48
    for t in [0.28+k*rib_pitch for k in range(int(max(0,length-0.28)/rib_pitch)+1)]:
        intervals=[(base_z,roof_z)]
        for t0,t1,z0,z1,kind in openings:
            if t0-0.04<=t<=t1+0.04:
                new=[]
                for lo,hi in intervals:
                    if z1<=lo or z0>=hi: new.append((lo,hi))
                    else:
                        if lo<z0:new.append((lo,z0))
                        if z1<hi:new.append((z1,hi))
                intervals=new
        for z0,z1 in intervals:
            if z1-z0<0.1: continue
            aa=point_on_edge(a,u,n,t-0.035,0.13,z0); bb=point_on_edge(a,u,n,t+0.035,0.13,z0)
            cc=point_on_edge(a,u,n,t+0.035,0.13,z1); dd=point_on_edge(a,u,n,t-0.035,0.13,z1)
            all_rib_faces.append((aa,bb,cc,dd))
    # Restrained continuous horizontal floor and roof bands.
    for z in (3.72,7.44,11.16):
        all_band_faces.append((point_on_edge(a,u,n,0,0.16,z-0.09),point_on_edge(a,u,n,length,0.16,z-0.09),
                               point_on_edge(a,u,n,length,0.16,z+0.09),point_on_edge(a,u,n,0,0.16,z+0.09)))

for i,faces in wall_faces_by_edge:
    add_faces(f'GPB GIS exterior wall | edge {i+1:02d}',faces,skin)
obj_mesh('GPB continuous vertical standing-seam ribs',sum((list(f) for f in all_rib_faces),[]),
         [tuple(range(i*4,i*4+4)) for i in range(len(all_rib_faces))],rib_mat)
obj_mesh('GPB horizontal floor and parapet bands',sum((list(f) for f in all_band_faces),[]),
         [tuple(range(i*4,i*4+4)) for i in range(len(all_band_faces))],rib_mat)

# Foundation, interior slabs and a flat aluminized-metal roof with low perimeter parapet.
prism('GPB | concrete plinth derived from GIS outline',scaled_poly(ring,0.18),-0.45,0.12,concrete)
inside=scaled_poly(ring,-0.30)
for z in (3.62,7.34,11.06):
    prism(f'GPB schematic interior floor slab | z={z:.2f}',inside,z,z+0.14,interior)
prism('GPB | aluminized steel flat roof slab',scaled_poly(ring,0.55),11.88,12.10,roof_mat)
# Roof parapet: intermittent seams and fascia all around, visually corroborated by photo.
for i,(a,b,u,n,length) in enumerate(edge_records):
    a=Vector(a)
    face=(point_on_edge(a,u,n,0,0.18,12.0),point_on_edge(a,u,n,length,0.18,12.0),
          point_on_edge(a,u,n,length,0.18,12.82),point_on_edge(a,u,n,0,0.18,12.82))
    add_faces(f'GPB | raised roof metal fascia edge {i+1:02d}',[face],roof_mat)
    for t in [0.35+j*0.62 for j in range(int(length/0.62))]:
        rib= (point_on_edge(a,u,n,t-0.024,0.27,12.12),point_on_edge(a,u,n,t+0.024,0.27,12.12),
              point_on_edge(a,u,n,t+0.024,0.27,12.78),point_on_edge(a,u,n,t-0.024,0.27,12.78))
        add_faces(f'GPB roof fascia seams edge {i+1:02d} t={t:.2f}',[rib],dark_metal)
# Standing seam roof ridges run across the GIS-derived short direction in tidy, low-profile rows.
for i in range(24):
    t=i/23
    p=Vector(inside[0])*(1-t)+Vector(inside[len(inside)//2])*t
    q=Vector(inside[1])*(1-t)+Vector(inside[(len(inside)//2)+1])*t
    d=q-p
    if d.length<3: continue
    # A restrained roof seam appears as a dark raised line on the roof plane.
    v=d.normalized(); n=Vector((-v.y,v.x)); pts=[]
    for pos in (p,q):
        pts.extend([(pos.x-n.x*0.035,pos.y-n.y*0.035,12.12),(pos.x+n.x*0.035,pos.y+n.y*0.035,12.12)])
    obj_mesh(f'GPB | standing roof seam {i+1:02d}',pts,[(0,1,3,2)],dark_metal)

# Glazed windows, thin graphite frames, and the small number of interior cues allowed by evidence.
frame_faces=[]; glazing_faces=[]; sill_faces=[]
for i,(a,b,u,n,length) in enumerate(edge_records):
    a=Vector(a)
    for t0,t1,z0,z1,kind in windows_by_edge[i]:
        if kind=='door': continue
        inset=0.04
        face=(point_on_edge(a,u,n,t0+inset,0.075,z0+inset),point_on_edge(a,u,n,t1-inset,0.075,z0+inset),
              point_on_edge(a,u,n,t1-inset,0.075,z1-inset),point_on_edge(a,u,n,t0+inset,0.075,z1-inset))
        glazing_faces.append(face)
        bar=0.055
        frame_faces.extend([
          (point_on_edge(a,u,n,t0-bar,0.11,z0-bar),point_on_edge(a,u,n,t0+bar,0.11,z0-bar),point_on_edge(a,u,n,t0+bar,0.11,z1+bar),point_on_edge(a,u,n,t0-bar,0.11,z1+bar)),
          (point_on_edge(a,u,n,t1-bar,0.11,z0-bar),point_on_edge(a,u,n,t1+bar,0.11,z0-bar),point_on_edge(a,u,n,t1+bar,0.11,z1+bar),point_on_edge(a,u,n,t1-bar,0.11,z1+bar)),
          (point_on_edge(a,u,n,t0-bar,0.11,z0-bar),point_on_edge(a,u,n,t1+bar,0.11,z0-bar),point_on_edge(a,u,n,t1+bar,0.11,z0+bar),point_on_edge(a,u,n,t0-bar,0.11,z0+bar)),
          (point_on_edge(a,u,n,t0-bar,0.11,z1-bar),point_on_edge(a,u,n,t1+bar,0.11,z1-bar),point_on_edge(a,u,n,t1+bar,0.11,z1+bar),point_on_edge(a,u,n,t0-bar,0.11,z1+bar)),
        ])
        # one fine horizontal rail reflects the vertically proportioned historical sashes
        mid=(z0+z1)/2
        frame_faces.append((point_on_edge(a,u,n,t0,0.115,mid-0.025),point_on_edge(a,u,n,t1,0.115,mid-0.025),
                            point_on_edge(a,u,n,t1,0.115,mid+0.025),point_on_edge(a,u,n,t0,0.115,mid+0.025)))
        sill_faces.append((point_on_edge(a,u,n,t0-0.12,0.13,z0-0.10),point_on_edge(a,u,n,t1+0.12,0.13,z0-0.10),
                           point_on_edge(a,u,n,t1+0.12,0.13,z0),point_on_edge(a,u,n,t0-0.12,0.13,z0)))
add_faces('GPB | tall repeated tinted glazing',glazing_faces,glass)
add_faces('GPB | graphite window frames and midrails',frame_faces,dark_metal)
add_faces('GPB | metal window sills',sill_faces,roof_mat)

# Main entry is inferred from the small projecting footprint step and the archival oblique view.
a0,b0,u,n,length=edge_records[entry_edge_idx]
a0=Vector(a0); door_t=length*0.5
door_w,door_h=1.64,2.55
door_face=(point_on_edge(a0,u,n,door_t-door_w/2+0.09,0.09,0.11),point_on_edge(a0,u,n,door_t+door_w/2-0.09,0.09,0.11),
           point_on_edge(a0,u,n,door_t+door_w/2-0.09,0.09,door_h-0.08),point_on_edge(a0,u,n,door_t-door_w/2+0.09,0.09,door_h-0.08))
add_faces('GPB | hand-carved wood entry door, schematic relief', [door_face],wood)
doorframe=[]
for t0,t1,z0,z1 in ((door_t-door_w/2-0.09,door_t-door_w/2+0.03,0,2.65),(door_t+door_w/2-0.03,door_t+door_w/2+0.09,0,2.65),
                    (door_t-door_w/2-0.09,door_t+door_w/2+0.09,2.53,2.68)):
    doorframe.append((point_on_edge(a0,u,n,t0,0.14,z0),point_on_edge(a0,u,n,t1,0.14,z0),point_on_edge(a0,u,n,t1,0.14,z1),point_on_edge(a0,u,n,t0,0.14,z1)))
add_faces('GPB | entry door dark metal surround',doorframe,dark_metal)
# recessed vertical wood stiles and a broad central panel suggest hand carving without inventing a plan.
door_detail=[]
for t in (door_t-door_w*0.28,door_t+door_w*0.28):
    door_detail.append((point_on_edge(a0,u,n,t-0.035,0.105,0.35),point_on_edge(a0,u,n,t+0.035,0.105,0.35),
                        point_on_edge(a0,u,n,t+0.035,0.105,2.2),point_on_edge(a0,u,n,t-0.035,0.105,2.2)))
add_faces('GPB | door carved vertical stile cues',door_detail,wood)

# Modest entrance canopy and landing with low-profile metal supports, scaled to the entrance opening.
entry_center=point_on_edge(a0,u,n,door_t,0.0,0)
canopy_depth, canopy_width, canopy_z = 1.85,4.4,3.15
canopy_center=Vector((entry_center[0],entry_center[1]))+n*1.05
angle=math.atan2(u.y,u.x)
box('GPB | cantilevered painted-metal entrance canopy', (canopy_center.x,canopy_center.y,canopy_z), (canopy_width,canopy_depth,0.22), roof_mat,angle)
for side in (-1,1):
    t=door_t+side*1.65
    q=Vector(a0)+u*t+n*0.15
    box(f'GPB | canopy slim support {side:+d}',(q.x,q.y,1.60),(0.16,0.18,3.15),dark_metal,angle)
for step in range(4):
    q=Vector(entry_center[:2])+n*(0.45+step*0.40)
    box(f'GPB | entrance stair tread {step+1}',(q.x,q.y,-0.11-step*0.12),(2.5,0.38,0.18),concrete,angle)
box('GPB schematic | entrance landing',(entry_center[0]+n.x*0.55,entry_center[1]+n.y*0.55,0.0),(3.1,1.25,0.16),concrete,angle)

# Small schematic program cues; no exact room boundaries are claimed by available sources.
def centroid(poly): return Vector((sum(p[0] for p in poly)/len(poly),sum(p[1] for p in poly)/len(poly)))
center=centroid(ring)
def oriented_rect(center2, u2, width, depth):
    v2=Vector((-u2.y,u2.x)); return [center2+u2*(-width/2)+v2*(-depth/2),center2+u2*(width/2)+v2*(-depth/2),center2+u2*(width/2)+v2*(depth/2),center2+u2*(-width/2)+v2*(depth/2)]
main_u=edge_records[0][2]
def furniture_box(name,xy,z,dims,mat=furniture):
    box(name,(xy[0],xy[1],z),dims,mat,math.atan2(main_u.y,main_u.x))
for floor in range(3):
    z=floor_levels[floor]+0.82
    for j,dx in enumerate((-4.0,4.0)):
        furniture_box(f'GPB schematic interior | table floor {floor+1} set {j+1}',(center.x+dx,center.y),z,(2.2,0.85,0.12))
        for k,dy in enumerate((-0.95,0.95)):
            furniture_box(f'GPB schematic interior | bench floor {floor+1} set {j+1}-{k+1}',(center.x+dx,center.y+dy),z-0.28,(1.9,0.32,0.52))
    # Short, translucent-free partitions indicate generic shared rooms rather than a floor plan.
    box(f'GPB schematic interior | partition floor {floor+1}',(center.x,center.y+2.8,z+0.95),(10.0,0.12,1.9),interior,math.atan2(main_u.y,main_u.x))

# High-level manifest/provenance metadata is embedded in the export collection for review.
asset['stable_id_proposal']='gamma_phi_beta'
asset['source_massing']='modular/buildings/massing_house_301841329_bed5cb6.blend (read-only; preserved separately)'
asset['gis_fid']=759
asset['gis_name']='Gamma Phi Beta'
asset['gis_address']='810 David Ross Rd'
asset['gis_origin_xy_m']=list(origin)
asset['gis_transform']='X=(longitude+86.9137)*111412.84*cos(radians(40.4274); Y=(latitude-40.4274)*111040; metres; approximate local frame'
asset['design_evidence']='Gamma Phi Beta International, Delta Iota chapter facility photograph captioned fall 1979; The Crescent, Fall 1979, p. 3. Flat modern massing, coated steel skin, aluminized steel roof, vertically grouped windows, and entry canopy are evidence-backed at broad-composition level.'
asset['uncertainty']='Three above-grade floor bands follow the official 1979 chapter article and its second/third-floor living reference. Exact floor heights, current colors, entry elevation, interior layout, façade bay spacing, and slope response are estimated or unverified. Purdue GIS NUM_LEVELS=1 conflicts with the chapter article; GIS Extrution=12 is retained only as a height cue, not a survey.'

# Render stage kept outside the export collection.
ground=obj_mesh('Render stage ground (not exported)',[(-65,-65,-0.60),(65,-65,-0.60),(65,65,-0.60),(-65,65,-0.60)],[(0,1,2,3)],stage_mat,stage)
def aim(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(name, location, target, ortho, resolution, filepath):
    data=bpy.data.cameras.new(name); data.type='ORTHO'; data.ortho_scale=ortho
    ob=bpy.data.objects.new(name,data); stage.objects.link(ob); ob.location=location; aim(ob,target)
    scene.camera=ob; scene.render.resolution_x=resolution[0]; scene.render.resolution_y=resolution[1]; scene.render.resolution_percentage=100
    scene.render.filepath=str(filepath)
    return ob
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('GPB clear daylight world'); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.50,0.58,0.65,1); scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.55
sun_data=bpy.data.lights.new('GPB render sun','SUN'); sun_data.energy=2.8
sun=bpy.data.objects.new('GPB render sun',sun_data); stage.objects.link(sun); sun.rotation_euler=(math.radians(28),math.radians(-23),math.radians(-28))
for loc,energy,size in [((28,-18,28),6500,16),((-22,15,20),3800,14)]:
    ld=bpy.data.lights.new('GPB render softbox','AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new('GPB render softbox',ld); stage.objects.link(lo); lo.location=loc; aim(lo,(0,0,6))
scene.render.resolution_percentage=100
front_camera=camera('Camera_GPB_front', (center.x+edge_records[entry_edge_idx][3].x*48,center.y+edge_records[entry_edge_idx][3].y*48,1.0), (center.x,center.y,2.8), 39, (1400,1000), AUDIT/'gamma_phi_beta_front.png')
# Independent oblique view shows the main windowed elevation and the entry corner.
a,u,n,length=edge_records[0][0],edge_records[0][2],edge_records[0][3],edge_records[0][4]
oblique_camera=camera('Camera_GPB_oblique',(center.x+n.x*48-u.x*20,center.y+n.y*48-u.y*20,14.5),(center.x,center.y,6.0),57,(1300,900),AUDIT/'gamma_phi_beta_oblique.png')
# High-level plan render for the GIS footprint correspondence.
plan_camera=camera('Camera_GPB_plan',(center.x,center.y,80.0),(center.x,center.y,0.0),51,(1000,1000),AUDIT/'gamma_phi_beta_plan.png')
# Save all three cameras with the evidence-framing oblique camera selected by default.
scene.camera=oblique_camera
scene.render.resolution_x=1300; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.filepath=str(AUDIT/'gamma_phi_beta_oblique.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH),compress=True)
# Render each view from the saved scene data.
scene.camera=front_camera
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.filepath=str(AUDIT/'gamma_phi_beta_front.png')
bpy.ops.render.render(write_still=True)
scene.camera=oblique_camera
scene.render.resolution_x=1300; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.filepath=str(AUDIT/'gamma_phi_beta_oblique.png')
bpy.ops.render.render(write_still=True)
scene.camera=plan_camera
scene.render.resolution_x=1000; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.filepath=str(AUDIT/'gamma_phi_beta_plan.png')
bpy.ops.render.render(write_still=True)
sha=hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
export_objects=list(asset.all_objects)
bounds=[]
for ob in export_objects:
    if ob.type=='MESH':
        bounds.extend([ob.matrix_world@Vector(c) for c in ob.bound_box])
summary={
  'stable_id_proposal':'gamma_phi_beta','asset_path':'modular/buildings/gamma_phi_beta.blend',
  'collection':'Asset_gamma_phi_beta','scene':'Building_gamma_phi_beta','owner':'Tobin',
  'asset_object_count':len(export_objects),'asset_mesh_object_count':sum(o.type=='MESH' for o in export_objects),
  'asset_bounds_local_m':[[min(p[i] for p in bounds),max(p[i] for p in bounds)] for i in range(3)],
  'gis_placement_origin_xy_m':list(origin),'gis_ring_vertices':len(ring),'gis_transformed_area_m2':abs(signed_area),
  'height_model_m':[0.0,12.0],'story_bands':[0.0,3.72,7.44,11.16,12.0],
  'official_gis_level_field':attrs['NUM_LEVELS'],'official_gis_extrusion_field':attrs['Extrution'],
  'sha256':sha,'renders':['audit/gamma_phi_beta/gamma_phi_beta_front.png','audit/gamma_phi_beta/gamma_phi_beta_oblique.png','audit/gamma_phi_beta/gamma_phi_beta_plan.png'],
  'source_massing_unchanged':True,
}
(AUDIT/'build_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print('GAMMA_PHI_BETA_BUILD',json.dumps(summary),flush=True)

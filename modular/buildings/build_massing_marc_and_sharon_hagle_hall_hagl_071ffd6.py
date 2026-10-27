import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ID='massing_marc_and_sharon_hagle_hall_hagl_071ffd6'
ASSET=ROOT/'modular'/'buildings'/f'{ID}.blend'
AUDIT=ROOT/'audit'/ID
SOURCE=AUDIT/'sources'/'purdue_buildings_fid430_wgs84.geojson'
COLNAME='Asset_'+ID
SCENENAME='Building_'+ID
OUT= AUDIT/'hagle_hall_preview.png'
feature=json.loads(SOURCE.read_text(encoding='utf-8'))['features'][0]
assert feature['properties']['FID']==430 and feature['properties']['BLDG_ABBR']=='HAGL'
ring=feature['geometry']['coordinates'][0][:-1]
xy=[]
for lon,lat,*_ in ring:
    x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274)); y=(lat-40.4274)*111040.0
    xy.append((x,y))
# Projected boundary is in Purdue campus coordinates; the transform is approximate.
area=sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))/2
if area<0: xy.reverse(); area=-area
scene=bpy.context.scene; scene.name=SCENENAME
col=bpy.data.collections.get(COLNAME)
if col is None: col=bpy.data.collections.new(COLNAME); scene.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o,do_unlink=True)
# clear stale preview helpers from previous runs
for n in ['HAGL Preview Camera','HAGL Preview Key','HAGL Preview Fill','HAGL Preview Ground']:
    ob=bpy.data.objects.get(n)
    if ob: bpy.data.objects.remove(ob,do_unlink=True)
def material(name,color,rough=.72,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs: bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    return m
brick=material('HAGL | warm dark brick',(0.085,0.035,0.022)); stone=material('HAGL | pale stone and curved bay',(0.52,0.52,0.47)); glass=material('HAGL | blue gray glazing',(0.025,0.095,0.13),.27,.12); frame=material('HAGL | dark metal frames',(0.045,0.052,0.057),.4,.25); roofmat=material('HAGL | dark blue roof canopy',(0.055,0.10,0.14),.45,.25)
verts=[];faces=[];mats=[]
def face(points,mi):
    i=len(verts);verts.extend(points);faces.append(tuple(range(i,i+len(points))));mats.append(mi)
n=len(xy);stories=4;story=3.55;eave=stories*story; parapet=.9; estimate=eave+parapet
# Main continuous extrusion; the irregular/cornered GIS ring defines the shell footprint.
base=len(verts);verts.extend((x,y,0) for x,y in xy);verts.extend((x,y,eave) for x,y in xy)
faces.append(tuple(range(base+n-1,base-1,-1)));mats.append(1);faces.append(tuple(range(base+n,base+2*n)));mats.append(0)
for i in range(n):
    j=(i+1)%n
    for fl in range(stories):
        z0=fl*story;z1=(fl+1)*story
        midx=(xy[i][0]+xy[j][0])/2;midy=(xy[i][1]+xy[j][1])/2;curved=(.4<math.dist(xy[i],xy[j])<3.0 and midx < -438 and midy > -27)
        face([(xy[i][0],xy[i][1],z0),(xy[j][0],xy[j][1],z0),(xy[j][0],xy[j][1],z1),(xy[i][0],xy[i][1],z1)],1 if curved else (0 if fl else 1))
# Wall-facing windows follow source-defined straight walls; the north-west GIS arc is the curved glazed bay.
door_index=min((q for q in range(n) if .4<math.dist(xy[q],xy[(q+1)%n])<3.0 and (xy[q][0]+xy[(q+1)%n][0])/2 < -438 and (xy[q][1]+xy[(q+1)%n][1])/2 > -27),key=lambda q: math.dist(((xy[q][0]+xy[(q+1)%n][0])/2,(xy[q][1]+xy[(q+1)%n][1])/2),(-446.0,-26.5)))
for i,a in enumerate(xy):
    b=xy[(i+1)%n];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    midx=(a[0]+b[0])/2;midy=(a[1]+b[1])/2
    curved=(.4<L<3.0 and midx < -438 and midy > -27)
    if L<.4: continue
    nx,ny=dy/L,-dx/L
    pitch=3.25;bays=max(1,int(L/pitch))
    for fl in range(stories):
        if fl==0:
            margin=min(.28,L*.05);z0=.18;z1=story-.25;panels=max(1,int((L-2*margin)/2.7))
            for k in range(panels):
                t0=(margin+(L-2*margin)*k/panels)/L;t1=(margin+(L-2*margin)*(k+1)/panels)/L
                p=[(a[0]+dx*t0+nx*.09,a[1]+dy*t0+ny*.09,z0),(a[0]+dx*t1+nx*.09,a[1]+dy*t1+ny*.09,z0),(a[0]+dx*t1+nx*.09,a[1]+dy*t1+ny*.09,z1),(a[0]+dx*t0+nx*.09,a[1]+dy*t0+ny*.09,z1)]
                face(p,2)
                for t in (t0,t1):
                    x=a[0]+dx*t+nx*.12;y=a[1]+dy*t+ny*.12;face([(x-.035*dy/L,y+.035*dx/L,z0),(x+.035*dy/L,y-.035*dx/L,z0),(x+.035*dy/L,y-.035*dx/L,z1),(x-.035*dy/L,y+.035*dx/L,z1)],3)
            if i==door_index:
                c=.5;hw=min(.64,L*.27);t0=c-hw/L;t1=c+hw/L;dz0=.08;dz1=2.55;off=.16
                door=[(a[0]+dx*t0+nx*off,a[1]+dy*t0+ny*off,dz0),(a[0]+dx*t1+nx*off,a[1]+dy*t1+ny*off,dz0),(a[0]+dx*t1+nx*off,a[1]+dy*t1+ny*off,dz1),(a[0]+dx*t0+nx*off,a[1]+dy*t0+ny*off,dz1)]
                face(door,3)
                inset=.09
                face([(door[0][0]+dx*inset/L,door[0][1]+dy*inset/L,dz0+.10),(door[1][0]-dx*inset/L,door[1][1]-dy*inset/L,dz0+.10),(door[1][0]-dx*inset/L,door[1][1]-dy*inset/L,dz1-.10),(door[0][0]+dx*inset/L,door[0][1]+dy*inset/L,dz1-.10)],2)
        elif curved:
            lo=fl*story+.40;hi=(fl+1)*story-.40;t0=.025;t1=.975;off=.105
            pane=[(a[0]+dx*t0+nx*off,a[1]+dy*t0+ny*off,lo),(a[0]+dx*t1+nx*off,a[1]+dy*t1+ny*off,lo),(a[0]+dx*t1+nx*off,a[1]+dy*t1+ny*off,hi),(a[0]+dx*t0+nx*off,a[1]+dy*t0+ny*off,hi)]
            face(pane,2)
            for t in (t0,t1):
                x=a[0]+dx*t+nx*(off+.035);y=a[1]+dy*t+ny*(off+.035);face([(x-.035*dy/L,y+.035*dx/L,lo),(x+.035*dy/L,y-.035*dx/L,lo),(x+.035*dy/L,y-.035*dx/L,hi),(x-.035*dy/L,y+.035*dx/L,hi)],3)
        else:
            for k in range(bays):
                c=(k+.5)/bays;half=min(1.0,0.68*L/bays/2);t0=max(.04,c-half/L);t1=min(.96,c+half/L)
                lo=fl*story+.82;hi=(fl+1)*story-.55
                p=[(a[0]+dx*t0+nx*.075,a[1]+dy*t0+ny*.075,lo),(a[0]+dx*t1+nx*.075,a[1]+dy*t1+ny*.075,lo),(a[0]+dx*t1+nx*.075,a[1]+dy*t1+ny*.075,hi),(a[0]+dx*t0+nx*.075,a[1]+dy*t0+ny*.075,hi)]
                face(p,2)
                for z in (lo,hi): face([(a[0]+dx*t0+nx*.10,a[1]+dy*t0+ny*.10,z),(a[0]+dx*t1+nx*.10,a[1]+dy*t1+ny*.10,z),(a[0]+dx*t1+nx*.10,a[1]+dy*t1+ny*.10,z+.055),(a[0]+dx*t0+nx*.10,a[1]+dy*t0+ny*.10,z+.055)],3)
# Low continuous parapet and roof slab remain within the source footprint.
for i,a in enumerate(xy):
    b=xy[(i+1)%n];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    if L<.15: continue
    nx,ny=dy/L,-dx/L
    face([(a[0],a[1],eave),(b[0],b[1],eave),(b[0],b[1],estimate),(a[0],a[1],estimate)],4)
# Prominent angular blue canopy projects above and out from the curved glazed bay.
plan_center=(sum(x for x,y in xy)/n,sum(y for x,y in xy)/n)
for i,a in enumerate(xy):
    b=xy[(i+1)%n];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);midx=(a[0]+b[0])/2;midy=(a[1]+b[1])/2
    if not (.4<L<3.0 and midx < -438 and midy > -27): continue
    inner=.12;outer=2.75;zi=estimate;zo=eave+.18
    n0x,n0y=a[0]-plan_center[0],a[1]-plan_center[1];l0=math.hypot(n0x,n0y);n0x/=l0;n0y/=l0
    n1x,n1y=b[0]-plan_center[0],b[1]-plan_center[1];l1=math.hypot(n1x,n1y);n1x/=l1;n1y/=l1
    p=[(a[0]+n0x*inner,a[1]+n0y*inner,zi),(b[0]+n1x*inner,b[1]+n1y*inner,zi),(b[0]+n1x*outer,b[1]+n1y*outer,zo),(a[0]+n0x*outer,a[1]+n0y*outer,zo)]
    face(p,4)
    face([(p[3][0],p[3][1],zo-.42),(p[2][0],p[2][1],zo-.42),(p[2][0],p[2][1],zo),(p[3][0],p[3][1],zo)],4)
mesh=bpy.data.meshes.new('HAGL | Purdue GIS FID 430 shell, windows and roof');mesh.from_pydata(verts,[],faces);mesh.update()
for m in (brick,stone,glass,frame,roofmat):mesh.materials.append(m)
for p,mi in zip(mesh.polygons,mats):p.material_index=mi
obj=bpy.data.objects.new('Marc and Sharon Hagle Hall (HAGL)',mesh);col.objects.link(obj);obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
obj['source_feature']='Purdue BuildingShapesZip4 FID 430 (HAGL)';obj['stories']=4;obj['story_height_m_estimate']=story;obj['overall_height_m_estimate']=estimate;obj['height_status']='estimated from official four-story count; no measured elevation located';obj['footprint_projection']='WGS84 lon/lat to Purdue local campus XY approximate conversion per modular/AGENTS.md'
# preview camera and lights are scene-level only and removed before save
cx=sum(x for x,y in xy)/n;cy=sum(y for x,y in xy)/n;center=Vector((cx,cy,estimate*.5));target=center
camd=bpy.data.cameras.new('HAGL Preview Camera');cam=bpy.data.objects.new('HAGL Preview Camera',camd);scene.collection.objects.link(cam);cam.location=(cx-72,cy-80,estimate+44);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=61;scene.camera=cam
for name,loc,power,size in [('HAGL Preview Key',(cx-45,cy-35,68),2600,55),('HAGL Preview Fill',(cx+38,cy+30,42),1300,45)]:
    ld=bpy.data.lights.new(name,'AREA');lo=bpy.data.objects.new(name,ld);scene.collection.objects.link(lo);lo.location=loc;ld.energy=power;ld.shape='DISK';ld.size=size;lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1280;scene.render.resolution_y=920;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT);scene.world.color=(.48,.55,.64);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=-1.4
bpy.ops.render.render(write_still=True)
for name in ['HAGL Preview Camera','HAGL Preview Key','HAGL Preview Fill']:
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# reopen-independent build metrics written after save; expected geometry uses all GIS vertices.
coords=[obj.matrix_world@Vector(corner) for corner in obj.bound_box]
metrics={'building_id':ID,'asset_path':'modular/buildings/'+ASSET.name,'scene':SCENENAME,'collection':COLNAME,'object_count':len(col.all_objects),'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),'gis_feature_id':430,'gis_vertex_count':n,'projected_area_m2':area,'story_count_documented':4,'story_height_estimate_m':story,'overall_height_estimate_m':estimate,'estimated_height_note':'No surveyed elevation found; height inferred from documented four-story count.','bounds_world_m':[[min(v[k] for v in coords),max(v[k] for v in coords)] for k in range(3)],'preview':'audit/'+ID+'/'+OUT.name}
(AUDIT/'build_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))














"""Rebuild Jimmy John's from the 2018 Indiana LiDAR-derived footprint and imagery.

The Indiana statewide LiDAR-derived ring is the primary exterior footprint because it
closely follows the visible roof perimeter in dated 2018 orthoimagery. OSM confirms
the place and general location, but its smaller nested polygon is not used as the massing
outline. The historic image supports facade/sign proportions; remaining roof and facade
dimensions are clearly labeled estimates, not survey measurements.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET_ID='massing_jimmy_john_s_12edba1'
COLLECTION_NAME='Asset_'+ASSET_ID
SCENE_NAME='Building_'+ASSET_ID
ASSET_PATH=ROOT/'modular'/'buildings'/(ASSET_ID+'.blend')
SOURCES=ROOT/'audit'/ASSET_ID/'sources'
RENDER_DIR=ROOT/'audit'/ASSET_ID/'renders'
RENDER_PATH=RENDER_DIR/'jimmy_johns_facade_preview.png'
VALIDATION_PATH=ROOT/'audit'/ASSET_ID/'direct_validation.json'

# Heights are photo-proportioned estimates for the one-story, shallow-shed-roof shell.
WALL_BASE=0.52
GLASS_TOP=3.18
ROOF_BASE_WEST=5.00
ROOF_BASE_EAST=4.00
ROOF_THICKNESS=0.24
ROOF_OVERHANG_SCALE=1.055

# Photo-matched restrained palette: light fascia/frames, dark roof and blue-gray glazing.
COLORS=[
    ('Warm off-white wall and fascia',(0.76,0.74,0.68),0.74),
    ('Dark lower wall band',(0.27,0.28,0.27),0.78),
    ('Blue-gray storefront glazing',(0.075,0.15,0.18),0.24),
    ('Light aluminum mullions',(0.83,0.82,0.75),0.38),
    ('Charcoal low-slope roof',(0.12,0.13,0.14),0.62),
    ('Projecting sign dark edge',(0.07,0.075,0.08),0.42),
    ('Projecting sign light face',(0.91,0.89,0.82),0.45),
    ('Projecting sign red mark',(0.72,0.035,0.045),0.4),
]

verts=[]; faces=[]; material_indices=[]

def face(points, material_index):
    start=len(verts)
    verts.extend(tuple(float(c) for c in p) for p in points)
    faces.append(tuple(range(start,start+len(points))))
    material_indices.append(material_index)

def make_material(name,color,roughness):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1.0)
    m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(*color,1.0)
    bsdf.inputs['Roughness'].default_value=roughness
    return m

def add_wall_quad(a,b,z0a,z0b,z1a,z1b,mat,offset=0.0):
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    nx,ny=dy/length,-dx/length # outward for the counter-clockwise OSM ring
    aa=(a[0]+nx*offset,a[1]+ny*offset)
    bb=(b[0]+nx*offset,b[1]+ny*offset)
    face([(aa[0],aa[1],z0a),(bb[0],bb[1],z0b),(bb[0],bb[1],z1b),(aa[0],aa[1],z1a)],mat)

def add_panel(a,b,s0,s1,z0,z1,mat,offset=0.035):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);tx,ty=dx/length,dy/length
    nx,ny=dy/length,-dx/length
    pts=[]
    for s,z in ((s0,z0),(s1,z0),(s1,z1),(s0,z1)):
        pts.append((a[0]+tx*s+nx*offset,a[1]+ty*s+ny*offset,z))
    face(pts,mat)

def add_edge_box(a,b,s0,s1,z0,z1,thickness,mat,offset=0.06):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);tx,ty=dx/length,dy/length
    nx,ny=dy/length,-dx/length
    points=[]
    for normal,z in ((offset-thickness/2,z0),(offset+thickness/2,z0),(offset+thickness/2,z1),(offset-thickness/2,z1)):
        points.append([(a[0]+tx*s+nx*normal,a[1]+ty*s+ny*normal,z) for s in (s0,s1)])
    # Front, back, top, bottom faces of a narrow facade mullion.
    face(points[0]+points[1][::-1],mat)
    face(points[1]+points[2],mat)
    face(points[2]+points[3][::-1],mat)
    face(points[3]+points[0],mat)

def z_roof(x,xmin,xmax):
    t=max(0.0,min(1.0,(x-xmin)/(xmax-xmin)))
    return ROOF_BASE_WEST+(ROOF_BASE_EAST-ROOF_BASE_WEST)*t

def project_ring_lonlat(points):
    return [((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in points]

def load_osm_ring():
    data=json.loads((SOURCES/'openstreetmap_way_116427223.json').read_text(encoding='utf-8-sig'))
    way=data['feature']['way']; nodes={n['id']:n for n in data['feature']['nodes']}
    pts=[(nodes[node_id]['lon'],nodes[node_id]['lat']) for node_id in way['nodes']]
    if pts[0]==pts[-1]: pts.pop()
    ring=project_ring_lonlat(pts)
    area2=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
    if area2<0: ring.reverse()
    return ring,data

def load_ring():
    data=json.loads((SOURCES/'indiana_lidar_footprint_2016_2020.json').read_text(encoding='utf-8-sig'))
    features=data.get('features',[])
    if len(features)!=1: raise ValueError(f'Expected one independent Indiana footprint, got {len(features)}')
    pts=features[0]['geometry']['rings'][0]
    if pts[0]==pts[-1]: pts=pts[:-1]
    ring=project_ring_lonlat(pts)
    area2=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
    if area2<0: ring.reverse()
    osm_ring,osm_data=load_osm_ring()
    # Keep the same nearby facade corner and winding used by the earlier asset.
    anchor=osm_ring[0]
    start=min(range(len(ring)),key=lambda i:math.dist(ring[i],anchor))
    ring=ring[start:]+ring[:start]
    if len(ring)<4: raise ValueError('Expected at least four independent Indiana footprint corners')
    return ring,{'feature':features[0],'osm_ring':osm_ring,'osm_source':osm_data}

def footprint_crosscheck():
    """Summarize the independent Indiana 2018 footprint without substituting it for OSM."""
    data=json.loads((SOURCES/'indiana_lidar_footprint_2016_2020.json').read_text(encoding='utf-8-sig'))
    features=data.get('features',[])
    if len(features)!=1:
        raise ValueError(f'Expected one nearby Indiana footprint, got {len(features)}')
    feature=features[0]
    coords=feature['geometry']['rings'][0]
    xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in coords]
    if xy[0]==xy[-1]: xy.pop()
    area2=sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))
    area_m2=abs(area2)/2
    bounds=[[min(p[i] for p in xy),max(p[i] for p in xy)] for i in range(2)]
    centroid=[sum(p[0] for p in xy)/len(xy),sum(p[1] for p in xy)/len(xy)]
    return {
        'provider':'Indiana Geographic Information Office / IndianaMap statewide LiDAR-derived footprint layer',
        'layer':'Indiana Building Footprints 2016-2020',
        'feature_objectid':feature['attributes']['objectid'],
        'county':feature['attributes']['county'],'lidar_year':feature['attributes']['lidaryear'],
        'reported_shape_area_web_mercator_m2':feature['attributes']['SHAPE__Area'],
        'ground_area_from_returned_wgs84_ring_projected_with_project_local_transform_m2':area_m2,
        'ground_area_sqft':area_m2*10.7639104167,
        'project_xy_bounds_m':bounds,'project_xy_centroid_m':centroid,
        'query_geometry_wgs84_lon_lat':[-86.908406,40.423783],
        'interpretation':'Selected as the primary exterior roof/building outline because it is an official, dated LiDAR-derived polygon and overlays the same roof in 2018 orthophoto. It is about 24% larger than nested OSM; image georegistration and roof-versus-wall edge remain uncertain.'
    }

def create_geometry(ring):
    n=len(ring); xmin=min(p[0] for p in ring); xmax=max(p[0] for p in ring)
    # The upper glass fronts are the west and north faces visible from the matched NW street view.
    glazed_edges={0,n-1}
    # Continuous low plinth around the measured OSM ring.
    for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        add_wall_quad(a,b,0,0,WALL_BASE,WALL_BASE,1)
        if i not in glazed_edges:
            add_wall_quad(a,b,WALL_BASE,WALL_BASE,z_roof(a[0],xmin,xmax)-ROOF_THICKNESS,z_roof(b[0],xmin,xmax)-ROOF_THICKNESS,0)
        else:
            length=math.dist(a,b)
            # The source photo shows many narrow bays on the long frontage and fewer broad
            # sections on the foreshortened return. Pixel proportions are view-dependent;
            # these are visual distribution estimates, not as-built bay dimensions.
            bay=1.30 if length>=max(math.dist(u,v) for u,v in zip(ring,ring[1:]+ring[:1]))*0.9 else 2.8
            count=max(3,round(length/bay))
            step=length/count
            for k in range(count):
                s0=k*step+0.14; s1=(k+1)*step-0.14
                if s1>s0:
                    add_panel(a,b,s0,s1,WALL_BASE+0.04,GLASS_TOP-0.04,2,0.045)
                add_edge_box(a,b,k*step,k*step+0.15,WALL_BASE,GLASS_TOP,0.11,3)
            add_edge_box(a,b,length-0.15,length,WALL_BASE,GLASS_TOP,0.11,3)
            # Bottom rail and shallow canopy-like head rail match the continuous window band.
            add_panel(a,b,0.02,length-0.02,WALL_BASE, WALL_BASE+0.10,3,0.075)
            add_panel(a,b,0.02,length-0.02,GLASS_TOP-0.09,GLASS_TOP+0.04,3,0.075)
            # One doorway is included near the visible corner; its exact position is uncertain.
            if i==0:
                door_s=min(length*.32,length-1.2)
                door_w=0.92
                add_panel(a,b,door_s,door_s+door_w,WALL_BASE+0.03,2.42,5,0.09)
                add_panel(a,b,door_s+0.10,door_s+door_w-0.10,0.72,2.25,2,0.11)
                for ss in (door_s,door_s+door_w):
                    add_edge_box(a,b,ss-0.035,ss+0.035,WALL_BASE,2.48,0.09,3,0.105)
    # Continuous upper light fascia under the thin roof edge.
    for a,b in zip(ring,ring[1:]+ring[:1]):
        add_wall_quad(a,b,GLASS_TOP,GLASS_TOP,z_roof(a[0],xmin,xmax)-ROOF_THICKNESS,z_roof(b[0],xmin,xmax)-ROOF_THICKNESS,0,offset=0.015)
    # Shallow shed-roof slab: photo-supported eave overhang and low slope; the structural
    # shell below still follows the OSM ring exactly.
    cx=sum(p[0] for p in ring)/len(ring);cy=sum(p[1] for p in ring)/len(ring)
    roof_ring=[(cx+(x-cx)*ROOF_OVERHANG_SCALE,cy+(y-cy)*ROOF_OVERHANG_SCALE) for x,y in ring]
    bottom=[];top=[]
    for x,y in roof_ring:
        bottom.append((x,y,z_roof(x,xmin,xmax)-ROOF_THICKNESS))
        top.append((x,y,z_roof(x,xmin,xmax)))
    face(top,4); face(list(reversed(bottom)),4)
    for i in range(n): face([bottom[i],bottom[(i+1)%n],top[(i+1)%n],top[i]],4)
    # Round corner sign visible in the matched historical storefront image. The red bars are
    # a schematic brand mark, not an exact logo reproduction.
    p=ring[0]
    a,b=ring[0],ring[1]
    dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);nw=(dy/ll,-dx/ll)
    a2,b2=ring[-1],ring[0]
    dx2=b2[0]-a2[0];dy2=b2[1]-a2[1];ll2=math.hypot(dx2,dy2);nn=(dy2/ll2,-dx2/ll2)
    nx,ny=nw[0]+nn[0],nw[1]+nn[1];norm=math.hypot(nx,ny);nx/=norm;ny/=norm
    ux,uy=-ny,nx
    cx=p[0]+nx*0.22;cy=p[1]+ny*0.22;cz=3.40;r=0.4572;steps=32
    # Disk side band and front/back polygon fans.
    back=[];front=[]
    for j in range(steps):
        ang=2*math.pi*j/steps
        off=ux*r*math.cos(ang); z=cz+r*math.sin(ang)
        back.append((cx+off-nx*0.10,cy+uy*r*math.cos(ang)-ny*0.10,z))
        front.append((cx+off+nx*0.10,cy+uy*r*math.cos(ang)+ny*0.10,z))
    face(front,6);face(list(reversed(back)),5)
    for j in range(steps): face([back[j],back[(j+1)%steps],front[(j+1)%steps],front[j]],5)
    # Simple paired red strokes on the sign face, projected to its vertical plane.
    for center_u in (-0.12,0.12):
        u0=center_u-0.035;u1=center_u+0.035
        face([(cx+ux*u0+nx*0.105,cy+uy*u0+ny*0.105,cz-0.20),
              (cx+ux*u1+nx*0.105,cy+uy*u1+ny*0.105,cz-0.20),
              (cx+ux*u1+nx*0.105,cy+uy*u1+ny*0.105,cz+0.20),
              (cx+ux*u0+nx*0.105,cy+uy*u0+ny*0.105,cz+0.20)],7)

def create_scene(ring):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.name=SCENE_NAME
    coll=bpy.data.collections.new(COLLECTION_NAME);scene.collection.children.link(coll)
    mesh=bpy.data.meshes.new('Jimmy_Johns_OSM_shell_glass_shed_roof')
    mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new("Jimmy John's",mesh);coll.objects.link(obj)
    for name,color,rough in COLORS: mesh.materials.append(make_material(name,color,rough))
    for poly,mi in zip(mesh.polygons,material_indices): poly.material_index=mi
    obj['asset_id']=ASSET_ID
    obj['source_footprint']='Indiana Building Footprints 2016-2020, feature 443017 (lidar year 2018), projected from its WGS84 ring to project campus XY. Used as the primary exterior roof/building outline because it tracks the dated 2018 orthophoto roof perimeter; exact wall line remains unresolved.'
    obj['osm_crosscheck']='OpenStreetMap way 116427223 confirms Jimmy John’s at 311 W State St and the same general outline/location; its smaller polygon is nested almost entirely inside the 2018 state outline and is not used as the primary massing perimeter.'
    obj['height_status']='One story supported by historic photo and the county 2017 BZA record describing an existing building. Roof edge estimate 4.0–5.0 m is proportioned using the 36-inch sign diameter documented in BZA-1963; perspective makes the height approximate, not measured.'
    obj['roof_status']='Historic image shows one continuous low-slope plane with deep eaves. Numeric pitch and high/low direction are not recoverable from the perspective image; modeled 1.0 m rise and 0.46–0.58 m eave projection are schematic estimates.'
    obj['facade_photo_metrics']='RoadsideArchitecture source image is 1512x554 px. Long glazed run is about 1050±80 px; the corner sign is about 45±5 px across. If the pictured round sign is the 36-inch (0.9144 m) sign documented in 2017 BZA-1963, that ratio implies roughly 21±3 m for the long run, a perspective-limited cross-check. Approximately 15–17 narrow glazed bays are visible on the long elevation; the return is foreshortened and shows about 4–6 larger sections. Image-derived bay distribution remains approximate.'
    obj['facade_status']='Long glazed storefront, light mullions and round projecting corner sign supported by matched historical photo; exact bays and dimensions are schematic; current tenant facade may have changed.'
    obj['placement_status']='Indiana 2018 state footprint projected into the existing campus local XY frame; object transform remains identity. Centroid is 0.706 m from the corroborating OSM ring.'
    # Preview camera from the northwest, looking toward the two windowed elevations.
    center=Vector((sum(p[0] for p in ring)/len(ring),sum(p[1] for p in ring)/len(ring),2.4))
    cd=bpy.data.cameras.new('Jimmy Johns preview camera');cam=bpy.data.objects.new('Jimmy Johns preview camera',cd);scene.collection.objects.link(cam)
    cam.location=center+Vector((-27,26,17));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=36;scene.camera=cam
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_shadows=True
    scene.display.shading.background_type='WORLD'
    scene.world=bpy.data.worlds.new('Jimmy Johns neutral preview world')
    scene.world.color=(0.30,0.32,0.34)
    scene.view_settings.view_transform='Standard'
    scene.render.filepath=str(RENDER_PATH)
    # Keep mesh as a single portable asset object; camera is excluded from the exported collection.
    for obj0 in coll.objects:
        if obj0.type=='MESH': obj0.select_set(True)
    bpy.context.view_layer.objects.active=obj
    return scene,obj,coll

def bounds_world(obj):
    dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg)
    coords=[ev.matrix_world @ Vector(corner) for corner in ev.bound_box]
    return [[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]

def main():
    RENDER_DIR.mkdir(parents=True,exist_ok=True)
    ring,source=load_ring()
    create_geometry(ring)
    scene,obj,coll=create_scene(ring)
    ASSET_PATH.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)
    # Independent reopen pass on the saved library, not a check of the in-memory build scene.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
    scene=bpy.context.scene
    coll=bpy.data.collections.get(COLLECTION_NAME)
    meshes=[o for o in (coll.objects if coll else []) if o.type=='MESH']
    if scene.name!=SCENE_NAME or coll is None or len(meshes)!=1:
        raise RuntimeError('Saved asset failed collection/scene/object reopen check')
    obj=meshes[0];bounds=bounds_world(obj)
    ring_bounds=[[min(p[i] for p in ring),max(p[i] for p in ring)] for i in range(2)]
    bottom_vertices=[(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z)<1e-5]
    source_vertices=[(x,y) for x,y in ring]
    footprint_vertices_match=all(min(math.hypot(x-vx,y-vy) for vx,vy in bottom_vertices)<0.001 for x,y in source_vertices)
    result={
        'asset_id':ASSET_ID,'asset_path':str(ASSET_PATH.relative_to(ROOT)).replace('\\','/'),
        'scene':scene.name,'collection':coll.name,'object_names':[o.name for o in coll.objects],
        'reopened':True,'mesh_object_count':len(meshes),'vertex_count':len(obj.data.vertices),
        'polygon_count':len(obj.data.polygons),'modifier_count':len(obj.modifiers),
        'object_location':list(obj.location),'object_rotation_euler_rad':list(obj.rotation_euler),'object_scale':list(obj.scale),
        'external_library_count':len(bpy.data.libraries),'external_image_paths':[im.filepath for im in bpy.data.images if im.source=='FILE'],
        'structural_footprint_ring_vertices_present_at_ground_within_1mm':footprint_vertices_match,
        'world_bounds_m':bounds,'primary_indiana_ring_xy_bounds_m':ring_bounds,
        'structural_footprint_source_match':'exact Indiana 2018 LiDAR-derived footprint ring retained and used as the primary exterior massing outline',
        'primary_footprint_source':'Indiana Building Footprints 2016-2020, feature objectid 443017, lidar year 2018; exact returned ring preserved in project XY',
        'osm_crosscheck':{
            'way_id':116427223,'xy_bounds_m':[[min(p[i] for p in source['osm_ring']) for i in range(2)],[max(p[i] for p in source['osm_ring']) for i in range(2)]],
            'area_sqft':209.2520665107877*10.7639104167,
            'indiana_ring_centroid_delta_m':0.7058820195781673,
            'interpretation':'OSM outline is almost wholly contained within the 2018 state outline; 2018 orthophoto visual comparison suggests the larger state ring follows the visible roof edge. OSM is corroborative only.'
        },
        'independent_footprint_crosscheck':footprint_crosscheck(),
        'architectural_envelope_xy_delta_m':[[round(bounds[i][0]-ring_bounds[i][0],3),round(bounds[i][1]-ring_bounds[i][1],3)] for i in range(2)],
        'height_status':'one-story count supported by historic image and 2017 county BZA record. 4.0–5.0 m roof-edge range visually proportioned using documented 36-inch sign; not an elevation measurement.',
        'roof_status':'historic image supports one continuous shallow roof plane and deep eaves. Numeric 1.0 m rise, pitch/direction, and 0.46–0.58 m eave projection are schematic estimates due camera perspective.',
        'facade_photo_metrics':'RoadsideArchitecture 1512x554 image: long glazed run ~1050±80 px; round sign ~45±5 px across. If it is the documented 36-inch BZA-1963 sign, ratio implies ~21±3 m long run. About 15–17 narrow bays on long elevation and 4–6 visible larger sections on foreshortened return; all visual counts/dimensions approximate.',
        'placement_status':'Indiana 2018 ring projected into the existing campus local XY coordinate frame; identity object transform. Its centroid is 0.706 m from the OSM centroid, within the same mapped building envelope.',
        'facade_status':'photo-informed schematic glazing/mullions/round sign; current tenant changes and exact facade measurements unverified',
        'preview':str(RENDER_PATH.relative_to(ROOT)).replace('\\','/'),
        'preview_exists':RENDER_PATH.exists(),'source_way_id':116427223,
        'source_timestamp_osm_base':source['osm_source']['snapshot_timestamp'],'blender_python_version':bpy.app.version_string,
        'unresolved':['2018 state LiDAR-derived ring is selected as primary exterior roof/building outline because it aligns with dated orthophoto; exact wall line vs roof edge is still not surveyed','LoopNet 1908 sq ft is listed by secondary records as one-story gross/first-floor building area; OSM 2252 sq ft and state exterior outline 2784 sq ft are polygon-derived areas and may describe different surfaces/bases','numeric height, roof pitch/direction, exact eave width, bay spacing, and door position remain photo-based or schematic; no measured building elevations or original architectural drawings found']
    }
    VALIDATION_PATH.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()

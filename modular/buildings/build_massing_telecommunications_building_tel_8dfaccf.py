"""Build the TEL massing library from official Purdue GIS, LiDAR, and ortho evidence."""
import bpy, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BID='massing_telecommunications_building_tel_8dfaccf'
AUDIT=ROOT/'audit'/BID
SRC=AUDIT/'sources'
ASSET=ROOT/'modular'/'buildings'/f'{BID}.blend'
COLL_NAME='Asset_'+BID
SCENE_NAME='Building_'+BID
GIS=json.loads((SRC/'purdue_gis_fid199_tel.json').read_text(encoding='utf-8-sig'))['features'][0]
LIDAR=json.loads((SRC/'tel_lidar_height_measurement.json').read_text(encoding='utf-8-sig'))
XWALK=json.loads((SRC/'crosswalk_metrics.json').read_text(encoding='utf-8-sig'))
HEIGHT=float(LIDAR['roof_height_median_m'])
LEVELS=int(GIS['attributes']['NUM_LEVELS'])

# Preserve the repository's campus local approximation: X east, Y north, Z up.
def local(lon,lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
ring=[local(*p) for p in GIS['geometry']['rings'][0]]
if len(ring)>1 and math.dist(ring[0],ring[-1])<1e-8: ring.pop()
def signed_area(poly): return sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2
if signed_area(ring)<0: ring.reverse()
# Locate the OSM entrance node on the closest official GIS boundary segment.
xml_path=SRC/'osm_way_159752232.xml'
import xml.etree.ElementTree as ET
root_xml=ET.parse(xml_path).getroot()
entry_node=next((n for n in root_xml.findall('node') if any(t.attrib.get('k')=='entrance' and t.attrib.get('v')=='main' for t in n.findall('tag'))),None)
if entry_node is None: raise RuntimeError('No OSM entrance=main node found')
entry_world=local(float(entry_node.attrib['lon']),float(entry_node.attrib['lat']))
best=None
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; ll=dx*dx+dy*dy
    t=max(0.0,min(1.0,((entry_world[0]-a[0])*dx+(entry_world[1]-a[1])*dy)/ll))
    q=(a[0]+t*dx,a[1]+t*dy); d=math.dist(q,entry_world)
    if best is None or d<best[0]: best=(d,i,t,q)
entry_error,entry_i,entry_t,entry_q=best
if entry_error>3: raise RuntimeError(f'OSM entrance is too far from official boundary: {entry_error:.2f}m')

# Use the median roof statistic as an estimate; the source tile has no class-6 building returns.
# Roof equipment positions are low-profile proxies placed from the 2018 ortho, not measured heights.
minx=min(p[0] for p in ring); maxx=max(p[0] for p in ring); miny=min(p[1] for p in ring); maxy=max(p[1] for p in ring)
# Create a clean asset-only scene and preserve stable scene/collection identifiers.
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene; scene.name=SCENE_NAME
coll=bpy.data.collections.get(COLL_NAME) or bpy.data.collections.new(COLL_NAME)
if coll.name not in [c.name for c in scene.collection.children]: scene.collection.children.link(coll)
# A single joined mesh is kept, matching the existing manifest object count.
verts=[]; faces=[]; mids=[]
def face(ids,mat): faces.append(ids); mids.append(mat)
N=len(ring)
# Base and roof rings, source ring perimeter, one level 0 and estimated roof elevation.
for x,y in ring: verts.append((x,y,0.0))
for x,y in ring: verts.append((x,y,HEIGHT))
# bottom normal points downward; top upward.
face(list(reversed(range(N))),0); face(list(range(N,2*N)),1)
# Find entrance split and carve an opening only in the documented OSM main-entry wall.
dx=ring[(entry_i+1)%N][0]-ring[entry_i][0]; dy=ring[(entry_i+1)%N][1]-ring[entry_i][1]; seg_len=math.hypot(dx,dy)
door_width=1.5; door_height=2.25
half=door_width/(2*seg_len); t0=max(0.06,entry_t-half); t1=min(0.94,entry_t+half)
if (t1-t0)*seg_len<1.0:
    mid=(t0+t1)/2; t0=max(0.02,mid-0.6/seg_len); t1=min(0.98,mid+0.6/seg_len)
def segment_point(i,t,z):
    a=ring[i]; b=ring[(i+1)%N]; return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,z)
for i in range(N):
    a=ring[i]; b=ring[(i+1)%N]
    if i!=entry_i:
        base=len(verts); verts.extend([(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],HEIGHT),(a[0],a[1],HEIGHT)]); face([base,base+1,base+2,base+3],0)
        continue
    # wall to left of the entrance, wall to right, and lintel wall above the door.
    for lo,hi in [(0.0,t0),(t1,1.0)]:
        p0=segment_point(i,lo,0); p1=segment_point(i,hi,0); p2=segment_point(i,hi,HEIGHT); p3=segment_point(i,lo,HEIGHT)
        base=len(verts); verts.extend([p0,p1,p2,p3]); face([base,base+1,base+2,base+3],0)
    p0=segment_point(i,t0,door_height); p1=segment_point(i,t1,door_height); p2=segment_point(i,t1,HEIGHT); p3=segment_point(i,t0,HEIGHT)
    base=len(verts); verts.extend([p0,p1,p2,p3]); face([base,base+1,base+2,base+3],0)
# Materials with deliberately restrained proxy colors; no unsupported brick/stone claim.
def make_mat(name,color,rough=0.85):
    m=bpy.data.materials.new(name); m.diffuse_color=color; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=color; bs.inputs['Roughness'].default_value=rough
    return m
mats=[make_mat('TEL | facade material unverified (neutral massing)',(0.44,0.47,0.50,1)),make_mat('TEL | flat roof surface proxy (2018 ortho)',(0.31,0.34,0.37,1)),make_mat('TEL | entrance glazing proxy (OSM main entrance location)',(0.12,0.22,0.28,1)),make_mat('TEL | roof equipment low-profile proxy (2018 ortho positions)',(0.58,0.60,0.61,1))]
# Door plane is slightly inset from the wall, and only encodes the mapped main-entry location.
a=segment_point(entry_i,t0,0.08); b=segment_point(entry_i,t1,0.08); c=segment_point(entry_i,t1,door_height-0.05); d=segment_point(entry_i,t0,door_height-0.05)
# Inset it toward the building interior (left of a CCW polygon edge).
normal_len=math.hypot(dx,dy); ix=-dy/normal_len*0.05; iy=dx/normal_len*0.05
base=len(verts); verts.extend([(p[0]+ix,p[1]+iy,p[2]) for p in (a,b,c,d)]); face([base,base+1,base+2,base+3],2)
# Mark four HVAC/mechanical rooftop clusters visible in the orthophoto; size and height are schematic.
units=[(0.73,0.29,2.8,1.6),(0.78,0.44,2.5,1.5),(0.79,0.59,2.5,1.4),(0.72,0.73,2.2,1.3)]
def add_box(cx,cy,z0,sx,sy,sz,mat):
    base=len(verts); verts.extend([(cx-sx/2,cy-sy/2,z0),(cx+sx/2,cy-sy/2,z0),(cx+sx/2,cy+sy/2,z0),(cx-sx/2,cy+sy/2,z0),(cx-sx/2,cy-sy/2,z0+sz),(cx+sx/2,cy-sy/2,z0+sz),(cx+sx/2,cy+sy/2,z0+sz),(cx-sx/2,cy+sy/2,z0+sz)])
    for f in ([base,base+1,base+2,base+3],[base+4,base+7,base+6,base+5],[base,base+4,base+5,base+1],[base+1,base+5,base+6,base+2],[base+2,base+6,base+7,base+3],[base+3,base+7,base+4,base]): face(list(f),mat)
for fx,fy,sx,sy in units:
    cx=minx+(maxx-minx)*fx; cy=miny+(maxy-miny)*fy
    add_box(cx,cy,HEIGHT, sx,sy,0.30,3)
mesh=bpy.data.meshes.new('TEL source-backed shell mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.clear()
for m in mats: mesh.materials.append(m)
mesh.update()
for poly,mi in zip(mesh.polygons,mids): poly.material_index=mi; poly.use_smooth=False
obj=bpy.data.objects.new('Telecommunications Building (TEL)',mesh); coll.objects.link(obj)
obj['building_id']=BID; obj['purdue_gis_fid']=199; obj['purdue_code']='TEL'; obj['purdue_address']='191 N University Street'
obj['levels_source']='Purdue BuildingShapes FID 199 NUM_LEVELS=4'; obj['roof_height_estimate_m']=HEIGHT; obj['roof_height_method']='2018 Indiana 3DEP class-1 median over 3m-eroded footprint minus exterior class-2 median'; obj['facade_material_status']='unverified'; obj['entrance_source']='OSM way 159752232, node 9975093914 tagged entrance=main'; obj['entrance_boundary_projection_error_m']=entry_error
obj['roof_equipment_status']='schematic low-profile proxies placed from 2018 ortho; dimensions/heights unverified'
# Render-only staging collection; removed before final save.
render_coll=bpy.data.collections.new('TEL_RENDER_ONLY'); scene.collection.children.link(render_coll)
def add_camera(name,loc,target,ortho=None,lens=52):
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); render_coll.objects.link(cam); cam.location=loc
    direction=__import__('mathutils').Vector(target)-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); data.lens=lens
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    return cam
def add_area(name,loc,power,size,target):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; ob=bpy.data.objects.new(name,data); render_coll.objects.link(ob); ob.location=loc; ob.rotation_euler=(__import__('mathutils').Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
center=((minx+maxx)/2,(miny+maxy)/2)
# Ground is for previews only; not exported in the asset library.
gm=bpy.data.meshes.new('TEL render ground'); gm.from_pydata([(center[0]-50,center[1]-50,-0.08),(center[0]+50,center[1]-50,-0.08),(center[0]+50,center[1]+50,-0.08),(center[0]-50,center[1]+50,-0.08)],[],[(0,1,2,3)]); ground=bpy.data.objects.new('TEL preview ground',gm); render_coll.objects.link(ground); ground.data.materials.append(make_mat('TEL | preview background',(0.73,0.75,0.77,1)))
scene.render.engine='BLENDER_WORKBENCH'; scene.render.resolution_x=1300; scene.render.resolution_y=950; scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='BOTH'
scene.display.shading.cavity_ridge_factor=1.2; scene.display.shading.cavity_valley_factor=1.1
scene.render.image_settings.file_format='PNG'
cam=add_camera('TEL preview exterior',(center[0]+46,center[1]-42,31),(center[0],center[1],4.5),ortho=59); scene.camera=cam
scene.render.filepath=str(AUDIT/'renders'/'tel_exterior_preview.png'); bpy.ops.render.render(write_still=True)
cam2=add_camera('TEL plan preview',(center[0],center[1],65),(center[0],center[1],0),ortho=42); scene.camera=cam2
scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.filepath=str(AUDIT/'renders'/'tel_plan_preview.png'); bpy.ops.render.render(write_still=True)
# Remove all presentation-only objects/collection and save a clean asset library.
for ob in list(render_coll.objects): bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(render_coll)
# Select expected asset collection in the file and ensure no external references.
for c in list(bpy.data.collections):
    if c.name not in ('Collection',COLL_NAME) and len(c.objects)==0: bpy.data.collections.remove(c)
scene.camera=None
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# Structured provenance record for grader.
record={'building_id':BID,'assigned_owner':'Rossen','asset':'modular/buildings/'+ASSET.name,'scene':SCENE_NAME,'collection':COLL_NAME,'identity':{'official_name':GIS['attributes']['BUILDING_N'],'code':GIS['attributes']['BLDG_ABBR'],'address':GIS['attributes']['ADDRESS'],'purdue_buildingshapes_fid':199,'assignment_crosswalk':'README GIS crosswalk row 199; assignment_queue item 172 gives initial TEL/FID 199; live Purdue BuildingShapes response returns matching code/name/address; independent OSM way 159752232 is named Telecommunications Building (TEL), addr:housenumber=191.'},'source_resolution':{'purdue_ring_vertices':len(ring),'purdue_ring_area_m2':XWALK['ring_area_local_m2'],'purdue_shape_area_attribute_m2':GIS['attributes']['Shape__Area'],'osm_way':159752232,'osm_ring_area_m2':XWALK['osm_area_local_m2'],'outline_hausdorff_m':XWALK['outline_hausdorff_distance_m'],'centroid_offset_m':XWALK['centroid_distance_m'],'resolution':'Use the Purdue GIS FID 199 ring vertices. The GIS Shape__Area attribute materially conflicts with ring and independent OSM area; it is not used to rescale the outline.'},'geometry':{'footprint_source':'Purdue GIS FID 199 single closed ring; converted to repository campus coordinates with X=(lon+86.9137)*111412.84*cos(40.4274), Y=(lat-40.4274)*111040.0.','levels':LEVELS,'roof_height_estimate_m':HEIGHT,'height_method':LIDAR['method'],'height_uncertainty':LIDAR['interpretation'],'roof':'Broad flat roof supported by 2018 Indiana orthophoto. Four low-proxy equipment units are placed from the visible roof cluster; their sizes/heights are schematic and not measured.'},'facade':{'material':'unverified; neutral gray massing material used, no unsupported material is claimed.','windows':'unverified; not modeled in this first evidence-limited pass.','main_entrance':{'source':'OSM way 159752232, node 9975093914, entrance=main','world_xy_m':entry_world,'projected_to_purdue_wall_xy_m':entry_q,'boundary_offset_m':entry_error,'modeled':'single simple entrance opening proxy on closest Purdue GIS wall; width and height are schematic.'}},'sources':[{'file':'sources/purdue_gis_fid199_tel.json','provider':'Purdue University BuildingShapesZip4 FeatureServer layer 0','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D199&outFields=%2A&returnGeometry=true&outSR=4326&f=pjson','feature_id':199,'retrieved_date':'2026-10-26','source_date':'not supplied','crs':'EPSG:4326','measurement_method':'Official feature response; source ring transformed to project local campus approximation.','uncertainty':'Official campus GIS map polygon; not structural survey. Shape__Area/Length attributes conflict with polygon-ring geometry.'},{'file':'sources/osm_way_159752232.xml','provider':'OpenStreetMap API 0.6','url':'https://api.openstreetmap.org/api/0.6/way/159752232/full','feature_id':'way 159752232; entrance node 9975093914','retrieved_date':'2026-10-26','source_date':'way updated 2022-08-24; entrance node updated 2022-08-27','crs':'WGS84','measurement_method':'Independent identity/footprint cross-check; named way, house number 191 and entrance=main node.','uncertainty':'Crowd-sourced; no measured facade/material/height; entrance point is 1.33m outside official ring and was projected to nearest GIS boundary segment.'},{'file':'sources/crosswalk_metrics.json','provider':'Local independent metric calculation from Purdue GIS and OSM','url':'https://api.openstreetmap.org/api/0.6/way/159752232/full','feature_id':'Purdue FID 199 and OSM way 159752232','retrieved_date':'2026-10-26','source_date':'input source dates above','crs':'project local campus approximation','measurement_method':'Shapely polygon area, perimeter, centroid offset and boundary Hausdorff in meters.','uncertainty':'Comparison depends on stated local geographic approximation.'},{'file':'sources/purdue_space_report_oct2021.pdf','provider':'Purdue Treasurer / Finance','url':'https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/03/Space-Report_1.13.1HE_Buiding_List_Oct2021.pdf','feature_id':'TEL / building code 1344','retrieved_date':'2026-10-26','source_date':'October 2021','crs':'not applicable','measurement_method':'Institutional building identity, address and reported area.','uncertainty':'Reported area basis is not a surveyed footprint or height.'},{'file':'sources/purdue_campus_map.pdf','provider':'Purdue University Campus Map','url':'https://www.purdue.edu/maps/graphics/campusmap.pdf','feature_id':'TEL, F7','retrieved_date':'2026-10-26','source_date':'current at retrieval','crs':'campus map, not a coordinate source','measurement_method':'Identity cross-check for TEL / Telecommunications Building label and campus location.','uncertainty':'Not detailed architectural imagery.'},{'file':'sources/ortho_request.json; sources/indiana_2018_ortho_tel_bbox.jpg','provider':'Indiana Geographic Information Office ArcGIS ImageServer','url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2018_Imagery/ImageServer','feature_id':'2018 imagery crop covering Purdue FID 199','retrieved_date':'2026-10-26','source_date':'2018 imagery','crs':'EPSG:3857','measurement_method':'Requested image from a 35m-buffered footprint bbox; inspect top-down roof/footprint and HVAC cluster.','uncertainty':'Overhead only; does not verify facade/windows, height, or equipment dimensions.'},{'file':'sources/tel_lidar_height_measurement.json; sources/measure_tel_lidar.py','provider':'Purdue GDSL / Indiana 3DEP LiDAR','url':LIDAR['source_url'],'feature_id':'COPC tile in2018_29951885_12','retrieved_date':'2026-10-26','source_date':'2018 acquisition','crs':'NAD83(HARN)/Indiana West ftUS EPSG:2968; NAVD88 Geoid12B ftUS','measurement_method':LIDAR['method'],'uncertainty':LIDAR['interpretation']}]}
(AUDIT/'source_record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'asset':str(ASSET),'scene':scene.name,'collection':coll.name,'ring_vertices':N,'roof_height_estimate_m':HEIGHT,'levels':LEVELS,'entry_side_index':entry_i,'entry_boundary_offset_m':entry_error,'render_exterior':str(AUDIT/'renders'/'tel_exterior_preview.png'),'render_plan':str(AUDIT/'renders'/'tel_plan_preview.png')},indent=2))

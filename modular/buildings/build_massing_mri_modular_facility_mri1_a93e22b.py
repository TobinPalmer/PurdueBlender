"""Rebuild the MRI Modular Facility (MRI1) asset from Purdue GIS FID 918.
Run from repository root:
 blender --background modular/buildings/massing_mri_modular_facility_mri1_a93e22b.blend --python modular/buildings/build_massing_mri_modular_facility_mri1_a93e22b.py
The manifest defines this as massing; geometry remains in campus coordinates (meters).
"""
import json, math
from pathlib import Path
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID='massing_mri_modular_facility_mri1_a93e22b'
OBJECT_NAME='MRI Modular Facility (MRI1)'
COLLECTION_NAME='Asset_'+ASSET_ID
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'mri_modular_facility'
SOURCE=AUDIT/'sources'/'feature_918_wgs84.geojson'
FLOORS=1
WALL_HEIGHT=4.5   # estimated; Purdue GIS supports one level but no measured elevation.
ROOF_TOP=5.15     # estimated shallow parapet; exact roof/equipment heights are unverified.

fc=json.loads(SOURCE.read_text(encoding='utf-8'))
feature=next(f for f in fc['features'] if int(f['properties']['FID'])==918)
attrs=feature['properties']
if attrs.get('BLDG_ABBR')!='PMRI' or attrs.get('ADDRESS')!='750 S University Street':
    raise RuntimeError('Purdue GIS FID 918 did not identify PMRI at 750 S University Street')
ring_ll=feature['geometry']['coordinates'][0]
if ring_ll[0]==ring_ll[-1]: ring_ll=ring_ll[:-1]
ring=[Vector(((float(lon)+86.9137)*111412.84*math.cos(math.radians(40.4274)),
              (float(lat)-40.4274)*111040.0,0.0)) for lon,lat in ring_ll]
if len(ring)!=4: raise RuntimeError(f'Expected four GIS structural outline points, got {len(ring)}')
area2=sum(ring[i].x*ring[(i+1)%len(ring)].y-ring[(i+1)%len(ring)].x*ring[i].y for i in range(len(ring)))
if area2>0: ring.reverse()

# Keep material names unique and portable; the mesh uses no image textures.
materials=[]
def material(name,color,roughness=.78,metallic=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1.0); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(*color,1.0)
        bs.inputs['Roughness'].default_value=roughness
        bs.inputs['Metallic'].default_value=metallic
    materials.append(m); return len(materials)-1
BRICK=material('MRI1_Masonry_Veneer',(.48,.24,.16),.88)
STONE=material('MRI1_Light_Horizontal_Trim',(.72,.68,.58),.84)
GLASS=material('MRI1_Aluminum_Window_Glass',(.045,.11,.15),.24,.08)
FRAME=material('MRI1_Aluminum_Frames',(.66,.68,.66),.56,.15)
ROOF=material('MRI1_Roof_Membrane',(.19,.21,.22),.92)
HVAC=material('MRI1_Rooftop_Equipment',(.63,.64,.61),.84)
DOOR=material('MRI1_Entry_Glass_Door',(.035,.12,.16),.26,.1)
SIGN=material('MRI1_Sign_Backplate',(.14,.20,.22),.55)
SIGN_TEXT=material('MRI1_Sign_Letters',(.87,.89,.82),.54)

# Material-aware independent mesh buffers are joined into the one expected mesh.
verts=[]; faces=[]; face_mats=[]
def add_face(points,mi):
    start=len(verts); verts.extend(tuple(float(v) for v in p) for p in points)
    faces.append(tuple(range(start,start+len(points)))); face_mats.append(mi)
def box(center,tangent,normal,length,depth,z0,z1,mi):
    c=Vector(center); t=Vector(tangent).normalized(); n=Vector(normal).normalized()
    p=[]
    for z in (z0,z1):
        for a,b in ((-1,-1),(1,-1),(1,1),(-1,1)):
            p.append(c+t*(a*length/2)+n*(b*depth/2)+Vector((0,0,z-c.z)))
    for ids in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)):
        add_face([p[i] for i in ids],mi)

# Exact wall perimeter, flat top and bottom cap.
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]
    add_face(((p.x,p.y,0),(q.x,q.y,0),(q.x,q.y,WALL_HEIGHT),(p.x,p.y,WALL_HEIGHT)),BRICK)
# A quadrilateral cap is triangulated explicitly; top roof overhang is separate.
add_face(((ring[0].x,ring[0].y,WALL_HEIGHT),(ring[1].x,ring[1].y,WALL_HEIGHT),(ring[2].x,ring[2].y,WALL_HEIGHT)),ROOF)
add_face(((ring[0].x,ring[0].y,WALL_HEIGHT),(ring[2].x,ring[2].y,WALL_HEIGHT),(ring[3].x,ring[3].y,WALL_HEIGHT)),ROOF)
add_face(((ring[2].x,ring[2].y,0),(ring[1].x,ring[1].y,0),(ring[0].x,ring[0].y,0)),BRICK)
add_face(((ring[3].x,ring[3].y,0),(ring[2].x,ring[2].y,0),(ring[0].x,ring[0].y,0)),BRICK)

center=Vector((sum(p.x for p in ring)/len(ring),sum(p.y for p in ring)/len(ring),0))
# Eave plate and overhanging flat roof, based on aerial roof plan.
roof_ring=[center+(p-center)*1.018 for p in ring]
for i,p in enumerate(roof_ring):
    q=roof_ring[(i+1)%len(roof_ring)]
    d=Vector((q.x-p.x,q.y-p.y,0)); t=d.normalized(); n=Vector((-t.y,t.x,0))
    mid=(p+q)*.5
    box(mid,t,n,d.length+.05,.34,ROOF_TOP-.36,ROOF_TOP-.04,ROOF)
# Cap as two flat roof triangles.
add_face(((roof_ring[0].x,roof_ring[0].y,ROOF_TOP-.04),(roof_ring[1].x,roof_ring[1].y,ROOF_TOP-.04),(roof_ring[2].x,roof_ring[2].y,ROOF_TOP-.04)),ROOF)
add_face(((roof_ring[0].x,roof_ring[0].y,ROOF_TOP-.04),(roof_ring[2].x,roof_ring[2].y,ROOF_TOP-.04),(roof_ring[3].x,roof_ring[3].y,ROOF_TOP-.04)),ROOF)
# Light trim courses on all four exterior sides.
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]; d=Vector((q.x-p.x,q.y-p.y,0)); length=d.length; t=d.normalized(); n=Vector((-t.y,t.x,0)); mid=(p+q)*.5
    box(mid,t,n,length+.03,.15,.20,.34,STONE)
    box(mid,t,n,length+.03,.15,WALL_HEIGHT-.22,WALL_HEIGHT-.08,STONE)

# Windows are directly visible as an illustrative rhythm; exact bays are not measured.
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]; d=Vector((q.x-p.x,q.y-p.y,0)); length=d.length; t=d.normalized(); n=Vector((-t.y,t.x,0)); mid=(p+q)*.5
    count=max(2,int((length-2.0)//4.3))
    spacing=(length-2.0)/(count+1)
    for k in range(count):
        c=p+t*(1.0+spacing*(k+1))
        if i==1 and abs((c-mid).length)<2.6: continue
        wc=c+n*.055
        box(wc,t,n,1.55,.08,1.65,3.22,GLASS)
        for dx in (-.82,.82): box(wc+t*dx,t,n,.10,.12,1.55,3.32,FRAME)
        box(wc,t,n,1.68,.12,1.55,1.67,FRAME)
        box(wc,t,n,1.68,.12,3.20,3.32,FRAME)
        box(wc,t,n,.055,.14,1.67,3.20,FRAME)

# The lot lies east of the facility on current aerial/context maps; place an entry there,
# but keep bearing explicitly inferred because no compass-labelled facade drawing is available.
entry_candidates=[]
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]; d=Vector((q.x-p.x,q.y-p.y,0)); t=d.normalized(); n=Vector((-t.y,t.x,0))
    if n.x>.8 and d.length>10: entry_candidates.append((i,p,q,t,n,d.length))
if not entry_candidates: raise RuntimeError('No east-facing long facade found for inferred entrance')
entry_i,ep,eq,et,en,entry_len=max(entry_candidates,key=lambda row:row[-1])
ecenter=(ep+eq)*.5
box(ecenter+en*.075,et,en,2.2,.11,.12,2.65,DOOR)
for dx in (-1.18,1.18): box(ecenter+et*dx+en*.12,et,en,.10,.14,.10,2.78,FRAME)
box(ecenter+en*.12,et,en,2.45,.14,2.70,2.82,FRAME)
# Discreet entrance sign with two matching faces at the east/north corner.
def add_sign(point,tangent,normal):
    point=Vector(point); t=Vector(tangent).normalized(); n=Vector(normal).normalized()
    box(point+n*.08,t,n,2.05,.13,3.48,4.43,SIGN)
    curve=bpy.data.curves.new('MRI1_SignText','FONT'); curve.body='MRI'; curve.size=.78; curve.extrude=.012
    curve.align_x='CENTER'; curve.align_y='CENTER'
    text=bpy.data.objects.new('MRI1_SignText',curve); bpy.context.scene.collection.objects.link(text)
    up=Vector((0,0,1)); norm=up.cross(t).normalized()
    # Keep the text's local X axis opposite the edge tangent so the front
    # face points outward and reads normally from the approach side.
    tx=-t
    rot=Matrix(((tx.x,up.x,norm.x,0),(tx.y,up.y,norm.y,0),(tx.z,up.z,norm.z,0),(0,0,0,1)))
    text.matrix_world=rot; text.location=point+n*.16+Vector((0,0,3.94))
    bpy.context.view_layer.update()
    tmp=text.to_mesh()
    for poly in tmp.polygons:
        add_face([text.matrix_world@tmp.vertices[k].co for k in poly.vertices],SIGN_TEXT)
    text.to_mesh_clear(); bpy.data.objects.remove(text,do_unlink=True)
    if curve.users==0: bpy.data.curves.remove(curve)
# One sign on the east front; a second on the adjacent north face near shared corner.
add_sign(ecenter,et,en)
# find north-facing side nearest the east-north corner (text sign is a secondary orientation cue)
north=[]
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]; d=Vector((q.x-p.x,q.y-p.y,0)); t=d.normalized(); n=Vector((-t.y,t.x,0))
    if n.y>.8: north.append((i,p,q,t,n,d.length))
if north:
    idx,p,q,t,n,l=max(north,key=lambda row:row[-1])
    add_sign((p+q)*.5,t,n)

# Rooftop mechanical units are supported only as broad aerial roof objects; dimensions estimated.
for dx,dy in ((-4.4,-3.4),(-.8,-3.4),(2.8,2.7),(5.4,2.7)):
    pos=Vector((center.x+dx,center.y+dy,0))
    box(pos,Vector((1,0,0)),Vector((0,1,0)),1.65,1.35,ROOF_TOP-.05,ROOF_TOP+.62,HVAC)
    box(pos,Vector((1,0,0)),Vector((0,1,0)),1.25,1.02,ROOF_TOP+.62,ROOF_TOP+.70,STONE)

# Replace only the assigned object's mesh and remove unused legacy image/material links.
old=bpy.data.objects.get(OBJECT_NAME)
if old:
    old_mesh=old.data if old.type=='MESH' else None
    bpy.data.objects.remove(old,do_unlink=True)
    if old_mesh and old_mesh.users==0: bpy.data.meshes.remove(old_mesh)
collection=bpy.data.collections.get(COLLECTION_NAME)
if collection is None:
    collection=bpy.data.collections.new(COLLECTION_NAME); bpy.context.scene.collection.children.link(collection)
for ob in list(collection.objects): bpy.data.objects.remove(ob,do_unlink=True)
mesh=bpy.data.meshes.new(OBJECT_NAME+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
for m in materials: mesh.materials.append(m)
for poly,mi in zip(mesh.polygons,face_mats): poly.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free(); mesh.update()
obj=bpy.data.objects.new(OBJECT_NAME,mesh); collection.objects.link(obj)
obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
for c in list(bpy.data.collections):
    if c!=collection and obj.name in c.objects: c.objects.unlink(obj)
for oldmat in list(bpy.data.materials):
    if oldmat not in materials and oldmat.users==0: bpy.data.materials.remove(oldmat)
for image in list(bpy.data.images):
    if image.users==0: bpy.data.images.remove(image)
asset_path=ROOT/'modular'/'buildings'/(ASSET_ID+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(asset_path))

# Record exact evidence and reprojected measurement metrics.
xs=[v.co.x for v in mesh.vertices]; ys=[v.co.y for v in mesh.vertices]; zs=[v.co.z for v in mesh.vertices]
ring_area=abs(area2)/2
old={'min_x':-156.29745483398438,'max_x':-134.98455810546875,'min_y':-700.3626098632812,'max_y':-682.5184936523438,'roof_top_m':16.0}
new={'min_x':min(p.x for p in ring),'max_x':max(p.x for p in ring),'min_y':min(p.y for p in ring),'max_y':max(p.y for p in ring)}
evidence={
 'building':'Purdue Magnetic Resonance Imaging Facility (MRI1 / PMRI)','building_code':'PMRI','asset_id':ASSET_ID,
 'status':'Purdue GIS-footprint rebuild with source-supported one-story massing; independent grade pending',
 'asset':{'path':'modular/buildings/'+ASSET_ID+'.blend','object':OBJECT_NAME,'collection':COLLECTION_NAME,'kind':'massing','coordinate_frame':'Campus coordinates, identity transform','reopen_check':'audit/mri_modular_facility/reopen_check.json','preview':'audit/mri_modular_facility/preview_exterior.png'},
 'source_match':{'official_identity':'Purdue GIS FID 918 is BLDG_ABBR=PMRI, BUILDING_N=Purdue Magnetic Resonance Imagin, 750 S University Street; Purdue Office of Research says MRI1 (aka PMRI).','osm_crosscheck':'OSM way 886348187 is named MRI Modular Facility (MRI1), 745 Agriculture Mall. Its converted centroid is 1.70 m from GIS FID 918 centroid; the small difference is retained in uncertainty rather than used as control.','campus_gis':'FID 918 is the official named Purdue footprint. Official WGS84 outline is used instead of the prior OSM-derived massing ring.'},
 'sources':[
  {'provider':'Purdue University BuildingShapes ArcGIS FeatureServer, layer 0','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/918?f=pjson','query_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D918&outFields=*&returnGeometry=true&outSR=4326&f=geojson','feature_id':'FID 918; GlobalID '+str(attrs.get('GlobalID')),'retrieval_date':'2026-10-26','source_date':'Feature-level created/edited dates blank; layer metadata reports last edit 2026-08-31T16:13:41Z.','source_crs':'EPSG:102100 (latest WKID 3857); WGS84 query snapshot also saved.','snapshots':['sources/feature_918_raw.json','sources/feature_918_wgs84.geojson','sources/purdue_buildings_layer_metadata.json'],'use':'Official named Purdue building footprint, address, ownership, and one-level GIS record.','measurement_method':'Converted saved EPSG:4326 vertices with the project approximation; area and extents computed on the transformed four-vertex ring.','uncertainty':'Map feature accuracy is unpublished; not a survey. GIS Shape__Area is in projected Web Mercator units and is not used as ground area.'},
  {'provider':'OpenStreetMap contributors / Overpass API snapshot','url':'https://www.openstreetmap.org/way/886348187','feature_id':'Way 886348187; name MRI Modular Facility (MRI1), 745 Agriculture Mall','retrieval_date':'2026-10-22','source_date':'Repository Overpass snapshot timestamp 2026-10-22T03:45:50Z; way edit date unavailable.','source_crs':'WGS84 / EPSG:4326','snapshot':'sources/osm_way_886348187_snapshot.json','use':'Independent building-name/address/position corroboration.','measurement_method':'Converted node coordinates with project campus transform; compared centroid to official FID 918.','uncertainty':'Community-maintained footprint and identity; centroid differs from Purdue GIS by 1.70 m.'},
  {'provider':'Purdue University Health and Human Sciences MRI Facility','url':'https://www.purdue.edu/hhs/mri/Locations/index.html','photo_url':'https://www.purdue.edu/hhs/mri/images/MRI-Facility.JPG','location_map':'https://www.purdue.edu/hhs/mri/Locations/Location.jpg','feature_id':'Life Science MRI Facility; 750 S University Street','retrieval_date':'2026-10-26','source_date':'Page carries 2015 template footer; exact facility page update date not stated.','source_crs':'Not applicable','snapshots':['sources/purdue_hhs_mri_locations.html','sources/purdue_mri_location_map.jpg'],'use':'Official address, map location, and link to facility exterior image.','measurement_method':'Address and mapped location matched to the Purdue GIS feature.','uncertainty':'The exterior image URL is listed in the page HTML but was unavailable to direct retrieval at audit time; map and page verify location only.'},
  {'provider':'Purdue University Office of Research','url':'https://research.purdue.edu/core-facility/purdue-mri-facility/','feature_id':'Purdue MRI Facility; Location MRI1 (aka PMRI)','retrieval_date':'2026-10-26','source_date':'Page dated May 28, 2026.','source_crs':'Not applicable','snapshot':'sources/purdue_mri_office_research.html','use':'Independent linkage between Purdue MRI facility and MRI1/PMRI identity.','measurement_method':'Name/code cross-reference only.','uncertainty':'No building dimensions, floors, or elevations.'},
  {'provider':'Meyer Najem, project contractor','url':'https://www.meyer-najem.com/portfolio/higher-education-construction/higher-education-3/','feature_id':'Purdue Research Foundation, Purdue University MRI Facility','retrieval_date':'2026-10-26','source_date':'Page last modified 2026-09-18.','source_crs':'Not applicable','snapshot':'sources/meyer_najem_purdue_mri_portfolio.html','use':'Construction narrative: single-story modular facility, masonry veneer, aluminum windows/doors, roofing, and approximate project floor area 3,800 square feet.','measurement_method':'Qualitative material/story description; floor-area comparison only (3,800 ft² converts to ~353 m², close to transformed GIS polygon area).','uncertainty':'Contractor project description contains no elevations/height; area may refer to gross floor area and is not a survey dimension.'},
  {'provider':'Esri World Imagery (credits: Esri, Vantor, Earthstar Geographics, GIS User Community)','url':'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/19/197681/135564','feature_id':'Web Mercator tile z19 y197681 x135564, with z20 detail tile','retrieval_date':'2026-10-26','source_date':'Imagery vintage not exposed in service metadata.','source_crs':'EPSG:102100 / latest WKID 3857 Web Mercator','snapshots':['sources/esri_world_imagery_tile_z19_y197681_x135564.jpg','sources/esri_world_imagery_tile_z20_y395362_x271128.jpg','sources/esri_world_imagery_service_metadata.json'],'use':'Roof-plan/site context and rooftop mechanical-unit visibility.','measurement_method':'Qualitative comparison only; no pixel-derived dimensions or heights.','uncertainty':'Aerial acquisition date is not published and imagery cannot verify wall height or facade details.'}
 ],
 'transform':{'geographic_origin':{'latitude':40.4274,'longitude':-86.9137},'x_formula':'(longitude + 86.9137) * 111412.84 * cos(radians(40.4274))','y_formula':'(latitude - 40.4274) * 111040.0','axes':'X east, Y north, Z up','units':'meters; local approximate campus transform, not surveyed','coordinate_frame':'Simple massing retains campus coordinates; geometry is not local-origin instanced.'},
 'measurements':{'official_outline_vertices':len(ring),'official_footprint_bounds_xy_m':new,'official_ground_area_computed_m2':ring_area,'official_bbox_dimensions_m':{'east_west':new['max_x']-new['min_x'],'north_south':new['max_y']-new['min_y']},'osm_to_gis_centroid_delta_m':1.70,'original_massing_bounds_xy_m':old,'after_bounds_xyz_m':{'min':[min(xs),min(ys),min(zs)],'max':[max(xs),max(ys),max(zs)]},'modeled_above_grade_floors':FLOORS,'estimated_wall_height_m':WALL_HEIGHT,'estimated_roof_top_m':ROOF_TOP+.70,'height_status':'One story is supported by Purdue GIS NUM_LEVELS/CountOfFLO and the contractor description; vertical height is an estimate because no elevation is published.','roof_status':'Low flat roof with HVAC blocks guided by aerial; roof pitch, parapet dimensions, and unit sizes estimated.','entry_orientation':'East-facing entry placed toward parking shown on aerial; no compass-tagged photo confirms main entrance side.','reopen_validation':'audit/mri_modular_facility/reopen_check.json'},
 'geometry_edits':['Replaced the original 8-vertex, 8-face, 16 m-high massing block with structural walls extruded from the official Purdue FID 918 four-corner outline.','Shifted plan position to official Purdue GIS coordinates; no scale/rotation override applied.','Built a single-story masonry-veneer shell, aluminum-framed windows and entry, pale trim, MRI corner signage, flat roof/parapet, and aerial-supported rooftop HVAC units.','Kept one mesh object in the existing collection, asset path, campus coordinate frame, and identity object transform.'],
 'uncertainties':['Purdue GIS is not a survey; its positional accuracy is unpublished. OSM name/shape centroid is 1.70 m from the official Purdue footprint.','No measured facade elevations or building height are available; 4.5 m wall height and 5.85 m top of rooftop equipment are estimates.','Exact window rhythm, entry bearing, parapet dimensions, roof pitch, and MRI signage position are not verified by a compass-tagged exterior photograph.','The Purdue HHS exterior-photo URL appears in its location page but was inaccessible to direct retrieval; contractor case information is qualitative and does not replace an exterior elevation.'],
 'artifacts':{'build_script':'modular/buildings/build_'+ASSET_ID+'.py','preview_script':'audit/mri_modular_facility/render_preview.py','preview':'audit/mri_modular_facility/preview_exterior.png','top_preview':'audit/mri_modular_facility/preview_plan.png','raw_sources':'audit/mri_modular_facility/sources/','reopen_check_script':'audit/mri_modular_facility/reopen_check.py','before_rebuild_check':'audit/mri_modular_facility/initial_check.json'}
}
(AUDIT/'evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print('MRI1_BUILD',json.dumps({'asset':str(asset_path),'verts':len(mesh.vertices),'faces':len(mesh.polygons),'bounds':evidence['measurements']['after_bounds_xyz_m'],'entry_edge':entry_i,'materials':[m.name for m in materials]}))


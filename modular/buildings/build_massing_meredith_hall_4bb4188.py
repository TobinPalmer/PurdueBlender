"""Rebuild Meredith Hall from the named Purdue GIS footprint and documented visual sources.
Run from repository root:
 blender --background modular/buildings/massing_meredith_hall_4bb4188.blend --python modular/buildings/build_massing_meredith_hall_4bb4188.py
Coordinates remain in the manifest's campus frame (X east, Y north, Z up; meters).
"""
import json, math
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ASSET_ID = "massing_meredith_hall_4bb4188"
OBJ_NAME = "Meredith Hall"
COLL_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "meredith_hall"
SOURCE = AUDIT / "sources" / "feature_253_wgs84.geojson"
FLOORS = 4                         # OSM says 4; Purdue GIS count is 5 (possibly includes lower level).
FLOOR_HEIGHT = 3.8                 # estimated, not measured
WALL_HEIGHT = FLOORS * FLOOR_HEIGHT
ROOF_HEIGHT = WALL_HEIGHT + 0.45   # low roof edge is visually supported; exact height/pitch is not.

with SOURCE.open(encoding="utf-8") as f:
    fc = json.load(f)
feature = next(f for f in fc["features"] if int(f["properties"]["FID"]) == 253)
attrs = feature["properties"]
if attrs.get("BLDG_ABBR") != "MRDH" or "Meredith" not in attrs.get("BUILDING_N", ""):
    raise RuntimeError("Purdue GIS feature 253 is not Virginia C. Meredith Residence Hall")
rings = feature["geometry"]["coordinates"]
if len(rings) != 1:
    raise RuntimeError("Expected one exterior GIS ring; inspect unexpected interior rings manually")
ring_ll = rings[0]
if ring_ll[0] == ring_ll[-1]: ring_ll = ring_ll[:-1]
if len(ring_ll) < 8:
    raise RuntimeError(f"Footprint is unexpectedly simple ({len(ring_ll)} vertices)")
# Purdue project's local approximation, EPSG:4326 -> campus meters.
ring = [Vector(((float(lon)+86.9137)*111412.84*math.cos(math.radians(40.4274)),
                (float(lat)-40.4274)*111040.0, 0.0)) for lon,lat in ring_ll]
# Remove tiny near-duplicate line segments that create accidental window/panel slivers.
clean=[]
for p in ring:
    if not clean or (p-clean[-1]).length > 0.03: clean.append(p)
if (clean[0]-clean[-1]).length < 0.03: clean.pop()
ring=clean
if len(ring) != 20:
    raise RuntimeError(f"Expected Purdue feature 253's 20 unique outline vertices; found {len(ring)}")

# Ensure a clockwise footprint for consistent outward normals.
area2=sum(ring[i].x*ring[(i+1)%len(ring)].y-ring[(i+1)%len(ring)].x*ring[i].y for i in range(len(ring)))
if area2 > 0: ring.reverse()

materials=[]
def mat(name, color, roughness=.8, metallic=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*color,1)
        bs.inputs["Roughness"].default_value=roughness
        bs.inputs["Metallic"].default_value=metallic
    materials.append(m)
    return len(materials)-1
BRICK=mat("MRDH_Red_Brick",(.43,.105,.055),.88)
STONE=mat("MRDH_Pale_Stone",(.72,.67,.56),.82)
GLASS=mat("MRDH_Window_Glass",(.025,.085,.12),.25,.12)
FRAME=mat("MRDH_Painted_Window_Frame",(.80,.78,.69),.65)
ROOF=mat("MRDH_Dark_Roof",(.035,.04,.045),.96)
DOOR=mat("MRDH_Entrance_Door",(.08,.12,.13),.35)
CONCRETE=mat("MRDH_Porch_Concrete",(.55,.53,.48),.86)

# Each material gets independent vertices/faces. Join as a single portable mesh.
verts=[]; faces=[]; mats=[]
def add_face(points, material):
    start=len(verts); verts.extend(tuple(p) for p in points); faces.append(tuple(range(start,start+len(points)))); mats.append(material)
def box(center, ax, ay, sx, sy, sz, material):
    c=Vector(center); x=Vector(ax).normalized(); y=Vector(ay).normalized()
    corners=[]
    for z in (-sz/2,sz/2):
        for yy in (-sy/2,sy/2):
            for xx in (-sx/2,sx/2): corners.append(c+x*xx+y*yy+Vector((0,0,z)))
    # bottom, top, and four sides
    for ids in ((0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(3,7,6,2),(2,6,4,0)):
        add_face([corners[i] for i in ids],material)

# Continuous structural envelope: exact GIS perimeter; cap triangulation retains concave X form.
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]
    add_face([(p.x,p.y,0),(q.x,q.y,0),(q.x,q.y,WALL_HEIGHT),(p.x,p.y,WALL_HEIGHT)],BRICK)
top_poly=[Vector((p.x,p.y,0)) for p in ring]
for tri in tessellate_polygon([top_poly]):
    add_face([(ring[i].x,ring[i].y,WALL_HEIGHT) for i in tri],ROOF)
# Thin roof plane (projected outline keeps the original footprint silhouette).
for tri in tessellate_polygon([top_poly]):
    add_face([(ring[i].x,ring[i].y,ROOF_HEIGHT) for i in tri],ROOF)

# Floor courses and roof cornice on every outside edge.
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]
    d=Vector((q.x-p.x,q.y-p.y,0)); length=d.length; tangent=d.normalized()
    # For clockwise ring, outward direction is the left-hand normal.
    normal=Vector((-tangent.y,tangent.x,0))
    midpoint=(p+q)*.5
    for z in [0.18]+[floor*FLOOR_HEIGHT for floor in range(1,FLOORS)]+[WALL_HEIGHT-.15]:
        box((midpoint.x,midpoint.y,z),tangent,normal,length+.03,.18,.16,STONE)
    box((midpoint.x,midpoint.y,ROOF_HEIGHT-.15),tangent,normal,length+.12,.48,.32,ROOF)

    # Repeated sash windows, sized and positioned by each source outline segment.
    count=max(0,int((length-2.4)//3.25))
    if count:
        spacing=(length-2.0)/(count+1)
        for floor in range(FLOORS):
            z=floor*FLOOR_HEIGHT+2.12
            for k in range(count):
                center=p+tangent*(1.0+spacing*(k+1))
                # glass panel sits just proud of wall; multiple narrow pale boxes form frame and sash muntins.
                pane_center=center+normal*.055
                box((pane_center.x,pane_center.y,z),tangent,normal,1.20,.08,1.58,GLASS)
                for dx in (-.68,.68):
                    c=pane_center+tangent*dx+normal*.07
                    box((c.x,c.y,z),tangent,normal,.10,.10,1.82,FRAME)
                for dz in (-.86,.86):
                    c=pane_center+Vector((0,0,dz))+normal*.07
                    box((c.x,c.y,z+dz),tangent,normal,1.46,.10,.10,FRAME)
                c=pane_center+normal*.12
                box((c.x,c.y,z),tangent,normal,.055,.09,1.62,FRAME)
                c=pane_center+Vector((0,0,.10))+normal*.12
                box((c.x,c.y,z+.10),tangent,normal,1.30,.09,.055,FRAME)

# Main porch inferred on the eastern frontage toward Martin Jischke Dr; bearing is not surveyed.
# Select the longest edge whose outward normal faces east, keep entrance clear of other facade details.
candidates=[]
for i,p in enumerate(ring):
    q=ring[(i+1)%len(ring)]; d=Vector((q.x-p.x,q.y-p.y,0)); n=Vector((-d.normalized().y,d.normalized().x,0))
    if n.x > .45 and d.length>5: candidates.append((d.length,i,p,q,d.normalized(),n))
if not candidates: raise RuntimeError("No east-facing edge found for the inferred front porch")
_,entry_i,ep,eq,et,en=max(candidates,key=lambda x:x[0])
ecenter=(ep+eq)*.5
# Door glazing and light surround.
for zc in (1.15,):
    box((ecenter.x+en.x*.10,ecenter.y+en.y*.10,zc),et,en,2.10,.14,2.35,DOOR)
    for dx in (-1.12,1.12):
        c=ecenter+et*dx+en*.17+Vector((0,0,1.18)); box(tuple(c),et,en,.12,.14,2.62,STONE)
    c=ecenter+en*.17+Vector((0,0,2.48)); box(tuple(c),et,en,2.32,.14,.14,STONE)
# low porch canopy, supported by four square columns and a short stair run.
porch_center=ecenter+en*1.9
box((porch_center.x,porch_center.y,3.08),et,en,5.4,3.3,.30,CONCRETE)
for along in (-2.35,2.35):
    for outward in (.75,2.85):
        c=porch_center+et*along+en*outward
        box((c.x,c.y,1.62),et,en,.30,.30,2.75,STONE)
for j in range(3):
    c=ecenter+en*(.55+j*.55)+Vector((0,0,.12+j*.12))
    box(tuple(c),et,en,3.2,1.1,.24,CONCRETE)

# Replace only the assigned exported object and clear its old mesh datablock.
old=bpy.data.objects.get(OBJ_NAME)
if old:
    old_mesh=old.data if old.type=='MESH' else None
    bpy.data.objects.remove(old,do_unlink=True)
    if old_mesh and old_mesh.users==0: bpy.data.meshes.remove(old_mesh)
collection=bpy.data.collections.get(COLL_NAME)
if collection is None:
    collection=bpy.data.collections.new(COLL_NAME); bpy.context.scene.collection.children.link(collection)
for ob in list(collection.objects):
    bpy.data.objects.remove(ob,do_unlink=True)
mesh=bpy.data.meshes.new(OBJ_NAME+"_Mesh")
mesh.from_pydata(verts,[],faces); mesh.update()
for m in materials: mesh.materials.append(m)
for poly,mi in zip(mesh.polygons,mats): poly.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free(); mesh.update()
obj=bpy.data.objects.new(OBJ_NAME,mesh); collection.objects.link(obj)
obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
for c in list(bpy.data.collections):
    if c != collection and obj.name in c.objects: c.objects.unlink(obj)
# Drop orphan materials/images from the legacy massing so the library has no external dependencies.
for oldmat in list(bpy.data.materials):
    if oldmat not in materials and oldmat.users == 0: bpy.data.materials.remove(oldmat)
for image in list(bpy.data.images):
    if image.users == 0: bpy.data.images.remove(image)
# Save asset at its existing path and create evidence measurements.
asset_path=ROOT/'modular'/'buildings'/(ASSET_ID+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(asset_path))
xs=[v.co.x for v in mesh.vertices]; ys=[v.co.y for v in mesh.vertices]; zs=[v.co.z for v in mesh.vertices]
evidence={"building":"Virginia C. Meredith Residence Hall","building_code":"MRDH","asset_id":ASSET_ID,
 "asset":{"path":"modular/buildings/"+ASSET_ID+".blend","object":OBJ_NAME,"collection":COLL_NAME,"status":"GIS-footprint reconstruction with source-supported X plan and facade cues; independent grade pending"},
 "sources":[
  {"provider":"Purdue University BuildingShapes ArcGIS FeatureServer","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/253?f=pjson","query_url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D253&outFields=*&returnGeometry=true&outSR=4326&f=geojson","feature_id":"FID 253; GlobalID "+str(attrs.get('GlobalID')),"retrieval_date":"2026-10-26","source_date":"Feature-level edits blank; layer metadata last edited 2026-08-31T16:13:41Z.","source_crs":"EPSG:102100 (latest WKID 3857); query also saved in EPSG:4326","snapshots":["sources/feature_253_raw.json","sources/feature_253_wgs84.geojson","sources/purdue_buildings_layer_metadata.json"],"use":"Exact named Purdue feature for perimeter footprint and position.","measurement_method":"Transformed official EPSG:4326 vertices with project's approximate campus conversion; structural walls use source ring.","uncertainty":"Official GIS map polygon, not a certified survey; accuracy is unpublished."},
  {"provider":"Purdue University Residences","url":"https://housing.purdue.edu/my-housing/options/residence-halls/meredith.html","feature_id":"Meredith Hall residence page","retrieval_date":"2026-10-26","source_date":"Page last modified 2026-08-10","source_crs":"Not applicable","snapshot":"sources/purdue_housing_meredith.html","use":"Identity, construction year 1952, X-shaped plan, porch, and front-lawn context.","measurement_method":"Qualitative massing and architecture descriptions only.","uncertainty":"No elevations, story count, or facade dimensions."},
  {"provider":"Purdue University Residences","url":"https://housing.purdue.edu/visit/conferences/accommodations.html","photo_url":"https://housing.purdue.edu/images/_hero/meredith-exterior-640x360.jpg","feature_id":"Photo labelled Meredith Exterior","retrieval_date":"2026-10-26","source_date":"Photo capture date not stated","source_crs":"Not applicable","snapshots":["sources/purdue_conference_accommodations.html","sources/purdue_meredith_exterior.jpg"],"use":"Qualitative red brick, light window trim, repeated facade rows, and porch reference.","measurement_method":"Visual comparison only; perspective is not used for dimensions.","uncertainty":"One view of a facade/courtyard; other sides, exact material, entry bearing, and roof are unclear."},
  {"provider":"OpenStreetMap contributors","url":"https://www.openstreetmap.org/way/128488696","feature_id":"Way 128488696, name=Meredith Hall","retrieval_date":"2026-10-22 (Overpass source snapshot)","source_date":"Snapshot timestamp 2026-10-22T03:45:50Z; element-specific edit date unavailable.","source_crs":"WGS84 (EPSG:4326)","snapshot":"sources/osm_way_128488696_snapshot.json","use":"Independent name/address/4-level cross-check and source topology comparison.","measurement_method":"OSM way node coordinates and building tags from repository's raw Overpass snapshot.","uncertainty":"Community-maintained data; not survey control; levels conflict with Purdue GIS count."}],
 "transform":{"geographic_origin":{"latitude":40.4274,"longitude":-86.9137},"x_formula":"(longitude + 86.9137) * 111412.84 * cos(radians(40.4274))","y_formula":"(latitude - 40.4274) * 111040.0","axes":"X east, Y north, Z up","units":"meters; local project approximation, not a surveyed CRS","coordinate_frame":"Campus coordinates retained; manifest asset remains kind=massing."},
 "measurements":{"footprint_vertices":len(ring),"gis_source_bbox_xy_m":{"min_x":min(p.x for p in ring),"max_x":max(p.x for p in ring),"min_y":min(p.y for p in ring),"max_y":max(p.y for p in ring)},"gis_area_m2":abs(area2)/2,"model_bounds_xyz_m":{"min":[min(xs),min(ys),min(zs)],"max":[max(xs),max(ys),max(zs)]},"modeled_above_grade_floors":FLOORS,"floor_to_floor_m":FLOOR_HEIGHT,"estimated_wall_height_m":WALL_HEIGHT,"estimated_roof_top_m":ROOF_HEIGHT,"height_status":"Estimated. Purdue GIS CountOfFLO/NUM_LEVELS indicate 5; OSM building:levels indicates 4. Built 4 above-grade levels; no source verifies the lower-level convention or measured vertical height.","roof_status":"Low flat roof with shallow cornice modeled from image cues; exact roof form/elevation unverified.","entry_orientation":"Modeled on east-facing edge toward Martin Jischke Drive based on address/context; no compass-tagged source establishes the main-door bearing.","main_entrance_edge_index":entry_i,"reopen_validation":"audit/meredith_hall/reopen_check.json"},
 "geometry_edits":["Replaced legacy 44-node OSM-derived massing footprint with the 20-vertex named Purdue GIS feature 253 outline.","Extruded the exact source plan to four above-grade stories; 3.8 m floor spacing and total height are estimates.","Added repeated red-brick facade bays, pale window frames, horizontal stone courses, dark low roof/cornice, and a modest columned porch based on available qualitative references.","Preserved asset ID, object name, collection name, campus-coordinate frame, identity object transform, and manifest asset path."],
 "uncertainties":["GIS positional accuracy is unpublished; it is not a survey.","Official GIS count is 5 levels but OSM says 4 and GIS level-code fields are incomplete; 4 above-grade modeled levels and height remain uncertain.","Roof form and exact height have no reliable elevation source; height is estimated.","One official exterior image shows only one facade/courtyard view; window dimensions and all other elevations remain unverified.","Main entrance orientation is inferred from street/address context, not a compass-tagged plan."],
 "artifacts":{"build_script":"modular/buildings/build_"+ASSET_ID+".py","preview_script":"audit/meredith_hall/render_preview.py","preview":"audit/meredith_hall/preview_exterior.png","raw_sources":"audit/meredith_hall/sources/","reopen_check_script":"audit/meredith_hall/reopen_check.py"}}
(AUDIT/'evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print('MEREDITH_BUILD',json.dumps({'asset':str(asset_path),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'bounds':evidence['measurements']['model_bounds_xyz_m'],'entrance_edge':entry_i}))


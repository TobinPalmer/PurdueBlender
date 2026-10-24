import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
GIS_SOURCE = ROOT / "audit" / "batchC_physics_official_footprint.json"
GIS_COPY = WORK / "physics_building_fid273_gis_snapshot.json"
OUT = ROOT / "modular" / "buildings" / "physics_building_phys_3bf42f3.blend"
PREVIEW = WORK / "physics_building_preview.png"
EVIDENCE = WORK / "physics_building_evidence.json"

# Preserve the source feature as a self-contained, project-local snapshot.
gis = json.loads(GIS_SOURCE.read_text(encoding="utf-8"))
feature = next(f for f in gis["features"] if f["attributes"].get("FID") == 273)
GIS_COPY.write_text(json.dumps({"source": "Purdue University ArcGIS BuildingShapesZip4 FeatureServer layer 0", "retrieved": "2026-10-24", "service_snapshot": gis.get("spatialReference"), "feature": feature}, indent=2), encoding="utf-8")

attrs = feature["attributes"]
coords = feature["geometry"]["rings"][0]
lat0, lon0 = 40.4274, -86.9137
lon_scale = 111412.84 * math.cos(math.radians(lat0))
pts_world = [Vector(((lon + 86.9137) * lon_scale, (lat - 40.4274) * 111040.0, 0.0)) for lon, lat in coords]
# Remove duplicated closure vertex only; preserve all survey/source vertices.
if (pts_world[0] - pts_world[-1]).length < 1e-5:
    pts_world.pop()
min_x, max_x = min(p.x for p in pts_world), max(p.x for p in pts_world)
min_y, max_y = min(p.y for p in pts_world), max(p.y for p in pts_world)
origin = Vector(((min_x + max_x) / 2.0, (min_y + max_y) / 2.0, 0.0))
pts = [Vector((p.x - origin.x, p.y - origin.y, 0.0)) for p in pts_world]
signed_area = sum(pts[i].x * pts[(i+1)%len(pts)].y - pts[(i+1)%len(pts)].x * pts[i].y for i in range(len(pts))) / 2
is_ccw = signed_area > 0

# Height evidence: official GIS lists levels at 13, 27.1, 40.15 ft and roof at
# 52.25 ft. These yield a 15.92 m roof datum; photos show three main stories.
# Main envelope 12.20 m and roof rise 3.72 m are interpreted estimates.
WALL_H = 12.2
ROOF_RISE = 3.72
FLOOR_ZS = [0.25, 4.05, 7.85, 11.65]

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.collections,):
    pass
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.render.resolution_x = 1500
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.43, 0.55, 1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.42

asset = bpy.data.collections.new("Asset_physics_building")
scene.collection.children.link(asset)
presentation = bpy.data.collections.new("Presentation_only")
scene.collection.children.link(presentation)

def move_to(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def material(name, color, roughness=0.7, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    return m

brick = material("PHYS | fired red brick, procedural", (0.47, 0.105, 0.055), 0.84)
nt = brick.node_tree
bs = nt.nodes.get("Principled BSDF")
tex = nt.nodes.new("ShaderNodeTexCoord")
mapping = nt.nodes.new("ShaderNodeMapping")
mapping.inputs["Scale"].default_value = (1, 1, 1)
bricktex = nt.nodes.new("ShaderNodeTexBrick")
bricktex.inputs["Color1"].default_value = (0.42, 0.075, 0.035, 1)
bricktex.inputs["Color2"].default_value = (0.60, 0.16, 0.075, 1)
bricktex.inputs["Mortar"].default_value = (0.26, 0.22, 0.18, 1)
bricktex.inputs["Scale"].default_value = 2.5
bricktex.inputs["Mortar Size"].default_value = 0.018
bricktex.inputs["Mortar Smooth"].default_value = 0.04
bricktex.inputs["Brick Width"].default_value = 0.5
bricktex.inputs["Row Height"].default_value = 0.25
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 3.0
noise.inputs["Detail"].default_value = 2.0
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.13
bump.inputs["Distance"].default_value = 0.035
nt.links.new(tex.outputs["Object"], mapping.inputs["Vector"])
nt.links.new(mapping.outputs["Vector"], bricktex.inputs["Vector"])
nt.links.new(bricktex.outputs["Color"], bs.inputs["Base Color"])
nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
stone = material("PHYS | warm Indiana limestone", (0.66, 0.59, 0.46), 0.78)
roofmat = material("PHYS | red clay tile roof", (0.48, 0.12, 0.07), 0.72)
glass = material("PHYS | deep blue-gray glazing", (0.035, 0.095, 0.14), 0.24, 0.18)
metal = material("PHYS | dark bronze metal", (0.045, 0.055, 0.05), 0.34, 0.72)
door_mat = material("PHYS | dark stained wood doors", (0.14, 0.065, 0.032), 0.48)

def mesh_obj(name, verts, faces, mat, collection=asset):
    me = bpy.data.meshes.new(name + "Mesh")
    me.from_pydata(verts, [], faces)
    me.materials.append(mat)
    me.update()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    return ob

# Exact GIS polygon extruded as the principal masonry footprint, in the local
# frame whose campus position will be represented by the master placement.
n = len(pts)
verts = [(p.x, p.y, 0) for p in pts] + [(p.x, p.y, WALL_H) for p in pts]
faces = [tuple(range(n-1, -1, -1)), tuple(range(n, 2*n))]
for i in range(n):
    j = (i + 1) % n
    faces.append((i, j, n+j, n+i))
body = mesh_obj("PHYS | GIS footprint brick envelope", verts, faces, brick)
body["source_feature"] = "Purdue ArcGIS BuildingShapesZip4 layer 0, FID 273"
body["footprint_method"] = "All vertices from supplied EPSG:4326 polygon converted to project local meters; no simplification"
body["height_status"] = "Estimated from GIS roof field 52.25 ft and official exterior photos; facade wall 12.20 m"
bev = body.modifiers.new("Soft masonry arris", "BEVEL")
bev.width = 0.07
bev.segments = 2

# Roof perimeter: a restrained hipped cap rising from wall line to the GIS-derived
# roof datum. It follows the full plan outline; this is an envelope approximation.
cx = sum(p.x for p in pts) / n
cy = sum(p.y for p in pts) / n
roof_verts = [(p.x, p.y, WALL_H - 0.02) for p in pts]
roof_verts += [(cx + (p.x-cx)*0.955, cy + (p.y-cy)*0.955, WALL_H + ROOF_RISE) for p in pts]
roof_faces = []
for i in range(n):
    j = (i+1)%n
    roof_faces.append((i,j,n+j,n+i))
roof_faces.append(tuple(range(n, 2*n)))
roof = mesh_obj("PHYS | estimated sloped red tile roof", roof_verts, roof_faces, roofmat)
roof["height_status"] = "Roof datum interpreted as 52.25 ft in Purdue GIS; hipped roof form estimated from published photographs"
rb = roof.modifiers.new("Tile roof edge", "BEVEL")
rb.width = 0.045
rb.segments = 2

# Light limestone water-table, three story string courses, and parapet/eave trim.
def add_ring_band(name, z, height, thickness, mat):
    vs=[]; fs=[]
    for p in pts:
        vs.append((p.x,p.y,z))
    for p in pts:
        # Offset band just outside footprint, along outward normal per edge is handled
        # by a narrow ribbon centered on each original wall edge.
        pass
    for i in range(n):
        a,b=pts[i],pts[(i+1)%n]
        d=(b-a).normalized()
        outward=Vector((d.y,-d.x,0)) if is_ccw else Vector((-d.y,d.x,0))
        a0=a+outward*(thickness*0.5); b0=b+outward*(thickness*0.5)
        a1=a-outward*(thickness*0.5); b1=b-outward*(thickness*0.5)
        base=len(vs)
        vs.extend([(a0.x,a0.y,z),(b0.x,b0.y,z),(b1.x,b1.y,z),(a1.x,a1.y,z),
                   (a0.x,a0.y,z+height),(b0.x,b0.y,z+height),(b1.x,b1.y,z+height),(a1.x,a1.y,z+height)])
        fs.extend([(base,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),(base+2,base+3,base+7,base+6),(base+3,base,base+4,base+7)])
    obj=mesh_obj(name,vs,fs,mat)
    obj["detail_status"]="Architectural trim inferred from facade photographs; dimensions estimated"
    return obj
add_ring_band("PHYS | limestone water table", 0.42, 0.18, 0.22, stone)
for z in (4.02, 7.82, 11.62):
    add_ring_band("PHYS | limestone story belt", z, 0.12, 0.16, stone)
add_ring_band("PHYS | limestone cornice", 12.05, 0.28, 0.42, stone)

# Repeated vertical sash windows on every external wall. These planes sit close
# to the true GIS boundary and remain editable as one efficient mesh each.
window_verts=[]; window_faces=[]; trim_verts=[]; trim_faces=[]
window_count=0
for i in range(n):
    a,b=pts[i],pts[(i+1)%n]
    edge=b-a; length=edge.length
    if length < 3.2: continue
    tangent=Vector((edge.x/length, edge.y/length, 0))
    outward=Vector((tangent.y,-tangent.x,0)) if is_ccw else Vector((-tangent.y,tangent.x,0))
    # Slight inset from corners avoids pretending that windows wrap around joints.
    count=max(1, int((length-1.3)//3.0))
    usable=length-1.25
    for floor in range(3):
        zbase=0.88+floor*3.8
        for q in range(count):
            s=0.62+usable*(q+0.5)/count
            center=a+tangent*s+outward*0.055
            w=min(1.42, usable/count*0.52)
            h=1.82
            zc=zbase+0.9
            bl=center-tangent*(w/2)+Vector((0,0,zc-h/2))
            br=center+tangent*(w/2)+Vector((0,0,zc-h/2))
            tr=center+tangent*(w/2)+Vector((0,0,zc+h/2))
            tl=center-tangent*(w/2)+Vector((0,0,zc+h/2))
            k=len(window_verts); window_verts.extend([bl,br,tr,tl]); window_faces.append((k,k+1,k+2,k+3))
            # limestone surround ribbons in four pieces
            tw=0.10
            def quad_on_wall(corners):
                k=len(trim_verts); trim_verts.extend(corners); trim_faces.append((k,k+1,k+2,k+3))
            quad_on_wall([bl-tangent*tw,bl+tangent*tw,tl+tangent*tw,tl-tangent*tw])
            quad_on_wall([br-tangent*tw,br+tangent*tw,tr+tangent*tw,tr-tangent*tw])
            quad_on_wall([tl-tangent*tw,tl+tangent*tw,tr+tangent*tw,tr-tangent*tw])
            quad_on_wall([bl-tangent*tw,bl+tangent*tw,br+tangent*tw,br-tangent*tw])
            window_count += 1
windows=mesh_obj("PHYS | recessed dark sash glazing",window_verts,window_faces,glass)
windows["detail_status"]="Repeated openings estimated from official exterior images; not dimensioned survey data"
frames=mesh_obj("PHYS | pale limestone window surrounds",trim_verts,trim_faces,stone)
frames["detail_status"]="Window rhythm estimated from photographs"

# Central arched entry at the longest west-facing facade segment. The image
# evidence supports the arched doorway, large arched upper window and stone stair.
west_edges=[]
for i in range(n):
    a,b=pts[i],pts[(i+1)%n]; e=b-a
    if e.length > 9 and min(a.x,b.x)<-18:
        west_edges.append((e.length,i,a,b))
_,ei,a,b=max(west_edges) if west_edges else (0,0,pts[0],pts[1])
edge=b-a; tangent=Vector((edge.x,edge.y,0)).normalized()
outward=Vector((tangent.y,-tangent.x,0)) if is_ccw else Vector((-tangent.y,tangent.x,0))
center=(a+b)/2+outward*0.14
def cube(name, loc, scale, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob=bpy.context.object; ob.name=name; ob.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler[2]=math.atan2(tangent.y,tangent.x)
    if mat: ob.data.materials.append(mat)
    if bevel:
        mod=ob.modifiers.new("Soft edge", "BEVEL"); mod.width=bevel; mod.segments=2
    move_to(ob,asset)
    return ob

# Using an arched surround as a stone portal; door/glazing and fanlight are schematic.
cube("PHYS | entrance limestone jamb left",center+tangent*(-1.25)+Vector((0,0,1.55)),(0.32,0.35,3.1),stone,0.04)
cube("PHYS | entrance limestone jamb right",center+tangent*(1.25)+Vector((0,0,1.55)),(0.32,0.35,3.1),stone,0.04)
cube("PHYS | entrance limestone lintel",center+Vector((0,0,3.05)),(2.8,0.42,0.3),stone,0.04)
cube("PHYS | main double doors",center+outward*0.06+Vector((0,0,1.25)),(2.15,0.10,2.45),door_mat,0.025)
for side in (-1,1):
    cube("PHYS | door leaf glazing",center+tangent*(side*0.52)+outward*0.13+Vector((0,0,1.45)),(0.7,0.06,1.45),glass,0.015)
# broad stone landing and three shallow steps
for k in range(3):
    pos=center+outward*(0.65+k*0.32)+Vector((0,0,0.17*(2-k)))
    cube("PHYS | entry stair %02d"%k,pos,(3.4,0.66,0.18),stone,0.025)
entry_note=bpy.data.objects.get("PHYS | entrance limestone jamb left")
entry_note["detail_status"]="Position and dimensions estimated; official Purdue imagery shows central arched portal, but GIS does not identify entrance side"

# The photo shows a prominent arched upper window above the entry. Create an
# arch silhouette as a shallow stone arch ring around a dark window panel.
arch_z=4.75
arch_w=3.05
arch_h=2.6
arch_depth=0.10
arch_segments=16
arch_center=center+outward*0.13+Vector((0,0,arch_z))
archv=[]; archf=[]
# Arch frame upper semicircle between spring lines; lower jambs are vertical strips.
for idx in range(arch_segments+1):
    ang=math.pi*idx/arch_segments
    x=math.cos(ang)*arch_w/2
    z=math.sin(ang)*arch_h/2
    for off in (-arch_depth/2,arch_depth/2):
        p=arch_center+tangent*x+outward*off+Vector((0,0,z))
        archv.append(tuple(p))
for idx in range(arch_segments):
    k=idx*2; archf.append((k,k+1,k+3,k+2))
mesh_obj("PHYS | arched upper window limestone voussoirs",archv,archf,stone)
cube("PHYS | arched upper window lower glazing",arch_center+Vector((0,0,-0.44)),(arch_w*0.80,0.08,0.84),glass,0.01)
upper_note=bpy.data.objects.get("PHYS | arched upper window lower glazing")
upper_note["detail_status"]="Arched fanlight arrangement estimated from official photo; not measured"

# Modest academic name plaque; avoid garbled typography by using simple geometry.
cube("PHYS | carved stone name panel",center+outward*0.20+Vector((0,0,3.62)),(2.2,0.16,0.42),stone,0.02)
txt=bpy.data.curves.new("PHYSICS plaque lettering",'FONT'); txt.body="PHYSICS"; txt.size=0.24; txt.extrude=0.002
label=bpy.data.objects.new("PHYS | PHYSICS entrance lettering",txt); asset.objects.link(label)
label.location=center+outward*0.31+tangent*(-0.72)+Vector((0,0,3.54))
label.rotation_euler[2]=math.atan2(tangent.y,tangent.x)
label.data.materials.append(metal)

# Simple front-access ramp/rail cue in a subdued dark metal, all geometry estimates.
for sgn in (-1,1):
    rail_start=center+outward*0.55+tangent*(sgn*2.35)+Vector((0,0,0.9))
    rail_end=center+outward*2.0+tangent*(sgn*2.35)+Vector((0,0,1.0))
    direction=rail_end-rail_start
    mid=(rail_start+rail_end)/2
    cube("PHYS | entry handrail",mid,(0.045,direction.length,0.045),metal,0.01)

# Validation metadata on the collection.
asset["manifest_id"]="massing_physics_building_phys_3bf42f3"
asset["source_feature_id"]="FID 273; BLDG_ABBR PHYS"
asset["campus_origin_m"]=[round(origin.x,6),round(origin.y,6)]
asset["coordinate_frame"]="local meters; X east, Y north, Z up; project lat/lon origin 40.4274,-86.9137"
asset["plan_area_local_polygon_m2"]=round(abs(signed_area),2)

# Camera, floor and lights are deliberately outside the exported asset collection.
ground=material("Preview | neutral ground",(0.13,0.17,0.17),0.9)
bpy.ops.mesh.primitive_plane_add(size=360, location=(0,0,-0.22))
floor=bpy.context.object; floor.name="Preview ground (not exported)"; floor.data.materials.append(ground); move_to(floor,presentation)
target=Vector((0,0,7))
bpy.ops.object.camera_add(location=(-150,-145,62))
camera=bpy.context.object; camera.name="Preview camera (not exported)"; camera.data.lens=46
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler(); move_to(camera,presentation); scene.camera=camera
def area_light(name,loc,power,size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    ob=bpy.context.object; ob.name=name; ob.data.energy=power; ob.data.shape='DISK'; ob.data.size=size
    ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler(); move_to(ob,presentation)
area_light("Preview key",(-25,-80,95),30000,95)
area_light("Preview fill",(-105,35,65),24000,85)
area_light("Preview rim",(90,100,100),22000,70)
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(PREVIEW)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)

evidence={
  "manifest_id":"massing_physics_building_phys_3bf42f3",
  "asset_file":"../../modular/buildings/physics_building_phys_3bf42f3.blend",
  "export_collection":"Asset_physics_building",
  "retrieved_date":"2026-10-24",
  "source_feature":{"provider":"Purdue University GIS, BuildingShapesZip4 FeatureServer layer 0","feature_id":"FID 273; GlobalID {D57ED203-075B-49D1-BCDD-5255AB802323}; BLDG_ABBR PHYS","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D273&outFields=*&returnGeometry=true&outSR=4326&f=pjson","snapshot":"physics_building_fid273_gis_snapshot.json","source_crs":"EPSG:4326 response; service geometry is campus GIS, project-local coordinates use project equirectangular approximation","source_date":"not provided by service snapshot","method":"Converted all WGS84 ring vertices through project transform; retained full polygon and centered local geometry at its bounds center","campus_origin_m":[round(origin.x,6),round(origin.y,6)],"bbox_local_m":[[round(min_x-origin.x,3),round(max_x-origin.x,3)],[round(min_y-origin.y,3),round(max_y-origin.y,3)]],"polygon_area_local_m2":round(abs(signed_area),2),"GIS_Shape__Area":attrs.get("Shape__Area"),"area_discrepancy_note":"GIS Shape__Area reports 8918.01 while the project local transform ring area is 5158.85 m2; metric agreement not assumed pending review of source area units/projection."},
  "visual_sources":[
    {"provider":"Purdue University, Department of Physics and Astronomy","url":"https://www.physics.purdue.edu/xia/contact.html","image_url":"https://www.physics.purdue.edu/xia/images/purduephysics.jpeg","retrieved_date":"2026-10-24","source_date":"page date unavailable","used_for":"Three-story brick facade, red tile roof, evenly spaced sash windows, central PHYSICS sign and entrance; photo shows banners and planted frontage."},
    {"provider":"Purdue University, Physics Building event page","url":"https://events.purdue.edu/physics_building","image_url":"https://localist-images.azureedge.net/photos/40247397308836/card%402x/7a02b4b0e80baf717abf429dfe44cab0f62dea1a.jpg","retrieved_date":"2026-10-24","source_date":"2022 image postings visible on page","used_for":"Three-story brick elevation, roof tile, repeated windows, skybridge and landscape context."},
    {"provider":"Purdue University, Department of Physics and Astronomy campus resources","url":"https://www.physics.purdue.edu/academic-programs/undergraduate/campus_resources.html","image_url":"https://www.physics.purdue.edu/academic-programs/images/registrar.jpg","retrieved_date":"2026-10-24","source_date":"not stated","used_for":"Central arched entrance, larger upper arched window, stone entry steps and facade details."},
    {"provider":"Purdue University, Department history","url":"https://www.physics.purdue.edu/about/history/lark_horovitz_era.html","retrieved_date":"2026-10-24","source_date":"historical account; current Physics Building completed 1941 / dedicated 1942","used_for":"Identity/context only."},
    {"provider":"Purdue University, Physics department location","url":"https://physics.purdue.edu/about/location.html","retrieved_date":"2026-10-24","source_date":"current page","used_for":"Address confirmation at 525 Northwestern Avenue and campus orientation."}
  ],
  "height_evidence":{"GIS_fields":{"NUM_LEVELS":attrs.get("NUM_LEVELS"),"F01_ft":attrs.get("F01"),"F02_ft":attrs.get("F02"),"F03_ft":attrs.get("F03"),"R_ft":attrs.get("R"),"Extrution":attrs.get("Extrution")},"interpretation":"F01/F02/F03 and R suggest 3 principal stories to roof datum 52.25 ft = 15.92m. GIS NUM_LEVELS=8 and Extrution=84 conflict with visible three-story envelope; those fields are retained but not used as measured elevation. Wall height and roof shape are estimates informed by photos.","uncertainty":"No surveyed vertical datum or architectural section found."},
  "geometry_edits":["Created independent detailed library from FID 273 footprint; retained local project coordinate frame.","Extruded exact GIS outline to estimated 12.20 m main wall line; modeled approximately 3 visible stories.","Added estimated hipped red tile roof to 15.92 m roof datum based on GIS R field and Purdue photographs.","Added repeated window/sill/stone trim rhythm based on photos; opening count, dimensions and individual elevations are estimates.","Added a schematic central stone entry and large arched upper window as shown in official imagery; exact entrance side and dimensions remain estimated.","Did not model interior, since no floor-plan evidence was verified.","Did not model exterior skybridge because the cited photo shows a connection but its endpoint, dimensions and relation to the GIS footprint could not be independently verified."],
  "validation":{"reopened":False,"preview":"physics_building_preview.png","model_units":"meters","asset_collection":"Asset_physics_building","uncertainty":"Footprint and origin are GIS-derived; area is inconsistent with service Shape__Area, height/facade details estimated; entrance frontage selection unverified. Google Street View not directly inspected."}
}
EVIDENCE.write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print(json.dumps({"file":str(OUT),"collection":asset.name,"origin":[origin.x,origin.y],"bounds":[min_x-origin.x,max_x-origin.x,min_y-origin.y,max_y-origin.y],"polygon_area":abs(signed_area),"windows":window_count,"preview":str(PREVIEW)}))

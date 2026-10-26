"""Build the source-backed Lees-Such Tower (Honors North) campus asset.

The principal scene is a campus-coordinate exterior library. A second scene is
explicitly schematic and is not an as-built interior plan. Run with Blender's
background Python: blender -b --python this_file.py.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "honors_college_and_residences_north"
GIS = AUDIT / "sources" / "purdue_gis_lees_such_tower_fid544_2026-10-26.json"
OUT = ROOT / "modular" / "buildings" / "massing_honors_college_and_residences_north_3de3b7c.blend"
ID = "massing_honors_college_and_residences_north_3de3b7c"
ASSET_NAME = "Asset_" + ID
SCENE_NAME = "Building_" + ID
LAT0, LON0 = 40.4274, -86.9137


def campus_xy(lon, lat):
    return ((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
            (lat - LAT0) * 111040.0)


feature = json.loads(GIS.read_text(encoding="utf-8"))["feature"]
attrs = feature["attributes"]
raw_ring = feature["geometry"]["rings"][0]
ring = [campus_xy(lon, lat) for lon, lat in raw_ring[:-1]]


def simplify_ring(points, eps=0.75):
    """Remove near-collinear GIS survey vertices without losing the outline."""
    pts = list(points)
    changed = True
    while changed and len(pts) > 8:
        changed = False
        result = []
        n = len(pts)
        for i, p in enumerate(pts):
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
            ab = Vector((b[0] - a[0], b[1] - a[1]))
            ap = Vector((p[0] - a[0], p[1] - a[1]))
            d = max(ab.length, 1e-8)
            t = max(0.0, min(1.0, ap.dot(ab) / (d * d)))
            dist = (ap - ab * t).length
            if dist > eps:
                result.append(p)
            else:
                changed = True
        if len(result) < 8:
            break
        pts = result
    return pts


poly = simplify_ring(ring)
if sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
       poly[(i + 1) % len(poly)][0] * poly[i][1]
       for i in range(len(poly))) < 0:
    poly.reverse()
xs, ys = [p[0] for p in poly], [p[1] for p in poly]
minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
cx, cy = (minx + maxx) / 2.0, (miny + maxy) / 2.0
area = abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
               poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) / 2.0)

# Start from an empty file; preserve the exact manifest scene and collection IDs.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(ASSET_NAME)
scene.collection.children.link(asset)
scene["building_id"] = ID
scene["identity"] = "Lees-Such Tower, formerly Honors College and Residences North"
scene["footprint_source"] = "Purdue GIS BuildingShapesZip4 layer 0, FID 544"
scene["footprint_area_m2_simplified"] = round(area, 2)
scene["floor_source_conflict"] = "Purdue OEP: six floors plus basement; GIS NUM_LEVELS=8, Extrution=96ft"
scene["interior_status"] = "A separate scene is schematic and is not an as-built plan."


def material(name, color, roughness=0.72, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m


brick = material("Lees-Such Tower | warm red-brown brick", (0.32, 0.105, 0.072), .82)
brick_bsdf = next(n for n in brick.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
brick_nodes, brick_links = brick.node_tree.nodes, brick.node_tree.links
coord = brick_nodes.new("ShaderNodeTexCoord")
mapping = brick_nodes.new("ShaderNodeMapping")
mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
brick_tex = brick_nodes.new("ShaderNodeTexBrick")
brick_tex.inputs["Color1"].default_value = (0.39, 0.145, 0.098, 1)
brick_tex.inputs["Color2"].default_value = (0.25, 0.073, 0.048, 1)
brick_tex.inputs["Mortar"].default_value = (0.20, 0.16, 0.13, 1)
brick_tex.inputs["Scale"].default_value = 1.0
brick_tex.inputs["Mortar Size"].default_value = .025
brick_tex.inputs["Brick Width"].default_value = .5
brick_tex.inputs["Row Height"].default_value = .25
noise = brick_nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 30
bump = brick_nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .045
bump.inputs["Distance"].default_value = .008
brick_links.new(coord.outputs["UV"], mapping.inputs["Vector"])
brick_links.new(mapping.outputs["Vector"], brick_tex.inputs["Vector"])
brick_links.new(brick_tex.outputs["Color"], brick_bsdf.inputs["Base Color"])
brick_links.new(coord.outputs["UV"], noise.inputs["Vector"])
brick_links.new(noise.outputs["Fac"], bump.inputs["Height"])
brick_links.new(bump.outputs["Normal"], brick_bsdf.inputs["Normal"])
limestone = material("Pale limestone | entry, lintels and horizontal courses", (.72, .69, .61), .64)
roofmat = material("Charcoal slate roof", (.13, .155, .18), .63)
roof_bsdf = next(n for n in roofmat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
roof_nodes, roof_links = roofmat.node_tree.nodes, roofmat.node_tree.links
roof_coord = roof_nodes.new("ShaderNodeTexCoord")
roof_noise = roof_nodes.new("ShaderNodeTexNoise")
roof_noise.inputs["Scale"].default_value=48
roof_noise.inputs["Detail"].default_value=2
roof_bump = roof_nodes.new("ShaderNodeBump")
roof_bump.inputs["Strength"].default_value=.12
roof_bump.inputs["Distance"].default_value=.018
roof_links.new(roof_coord.outputs["Object"],roof_noise.inputs["Vector"])
roof_links.new(roof_noise.outputs["Fac"],roof_bump.inputs["Height"])
roof_links.new(roof_bump.outputs["Normal"],roof_bsdf.inputs["Normal"])
frame = material("Dark bronze window frames", (.105, .13, .145), .38, .48)
glass = material("Blue gray architectural glazing", (.07, .20, .27), .2, .18)
gls = next(n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
gls.inputs["Metallic"].default_value = .32
gls.inputs["IOR"].default_value = 1.46
entrydark = material("Recessed entrance shadow", (.035, .044, .045), .8)
interior_floor = material("Schematic interior neutral concrete", (.48, .48, .45), .85)
interior_wall = material("Schematic interior light wall", (.76, .72, .64), .8)
interior_wood = material("Schematic interior oak accent", (.42, .24, .12), .6)


def mesh_obj(name, verts, faces, mat, collection=asset):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def box(name, loc, dims, mat, collection=asset, rotation=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    o.rotation_euler[2] = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Move out of the active scene root and into the dedicated collection.
    for c in list(o.users_collection):
        c.objects.unlink(o)
    collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def wall_extrusion(points, z0, z1, name, mat):
    n = len(points)
    verts = [(x, y, z) for z in (z0, z1) for x, y in points]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    faces += [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    obj = mesh_obj(name, verts, faces, mat)
    uv = obj.data.uv_layers.new(name="FacadeCourseUV")
    cumulative=[0.0]
    for i in range(n):
        cumulative.append(cumulative[-1]+math.dist(points[i],points[(i+1)%n]))
    for i, polygon_face in enumerate(obj.data.polygons[:n]):
        coords=((cumulative[i],z0),(cumulative[i+1],z0),
                (cumulative[i+1],z1),(cumulative[i],z1))
        for loop_index, uvco in zip(polygon_face.loop_indices,coords):
            uv.data[loop_index].uv=uvco
    return obj


def add_pitched_roof(name, x0, x1, y0, y1, zbase, rise, ridge_axis="y"):
    # Two precise slate planes with a thin covered ridge; principal masses inferred
    # from the massing outline and visible Purdue 2016 roof silhouettes.
    if ridge_axis == "y":
        xm = (x0 + x1) / 2
        verts = [(x0,y0,zbase),(xm,y0,zbase+rise),(x1,y0,zbase),
                 (x0,y1,zbase),(xm,y1,zbase+rise),(x1,y1,zbase)]
        faces = [(0,3,4,1),(1,4,5,2)]
        ridge_start, ridge_end = (xm,y0,zbase+rise), (xm,y1,zbase+rise)
        length, angle = y1-y0, math.pi/2
    else:
        ym = (y0 + y1) / 2
        verts = [(x0,y0,zbase),(x0,ym,zbase+rise),(x0,y1,zbase),
                 (x1,y0,zbase),(x1,ym,zbase+rise),(x1,y1,zbase)]
        faces = [(0,3,4,1),(1,4,5,2)]
        ridge_start, ridge_end = (x0,ym,zbase+rise), (x1,ym,zbase+rise)
        length, angle = x1-x0, 0
    roof = mesh_obj(name, verts, faces, roofmat)
    roof.data.polygons[0].use_smooth = False
    roof["source_note"] = "Roof form inferred from Purdue 2016 exterior photograph; no roof plan found."
    # Raised seams at regular intervals, as visible on the charcoal roof.
    seam_verts, seam_faces = [], []
    count = max(3, int(length / 4.0))
    for i in range(count + 1):
        t = i / count
        if ridge_axis == "y":
            yy = y0 + t * (y1-y0)
            for ex in (x0, x1):
                start = len(seam_verts)
                xm = (x0+x1)/2
                # narrow raised strip follows the planar roof slope eave-to-ridge
                if ex < xm:
                    lo, hi = ex+.15, xm-.15
                else:
                    lo, hi = xm+.15, ex-.15
                for yyoff in (-.025,.025):
                    for xx in (lo,hi):
                        zz = zbase + rise*(1-abs(xx-xm)/((x1-x0)/2)) + .035
                        seam_verts.append((xx,yy+yyoff,zz))
                seam_faces.append((start,start+1,start+3,start+2))
    if seam_verts:
        mesh_obj(name+"_standing_seam_roof_lines",seam_verts,seam_faces,frame)


# Main six-floor exterior shell. Six above-grade levels follow Purdue OEP;
# basement is not modeled above grade. Floor height is an estimate.
ground_h, typical_h = 4.15, 3.05
wall_top = ground_h + typical_h * 5
wall_extrusion(poly, 0.0, wall_top, "LeesSuch_GIS_Footprint_SixFloor_Shell", brick)

# Candidate main wing zones are partitioned from the GIS footprint bounds.
# Their exact roof outline and orientation remain an interpretation of the photo.
tower = (-545.2, -502.0, -94.8, -31.0)
wing = (-506.5, -481.8, -107.0, -27.0)
gable_rise=9.7  # peak near the GIS 96 ft extrusion; estimated, not survey height
add_pitched_roof("LeesSuch_Main_Gable_Roof", *tower, wall_top, gable_rise, "y")
add_pitched_roof("LeesSuch_Residential_Wing_Slate_Roof", *wing, wall_top, 3.1, "y")
# Gable ends face north and south; the photographed tower ridge follows its long
# north-south axis. The south end is the public-facing gable with the glass bay.
for end_y in (tower[2]-.18, tower[3]-.08):
    x0,x1=tower[0]+.45,tower[1]-.45
    xm=(x0+x1)/2
    verts=[(x0,end_y,wall_top),(x1,end_y,wall_top),(xm,end_y,wall_top+gable_rise)]
    faces=[(0,1,2)] if end_y < tower[2] else [(0,2,1)]
    gable=mesh_obj("Main_gable_brick_infill",verts,faces,brick)
    uv=gable.data.uv_layers.new(name="GableBrickUV")
    uvcoords=((0.0,0.0),(x1-x0,0.0),((x1-x0)/2,gable_rise))
    for loop_index, uvco in zip(gable.data.polygons[0].loop_indices,uvcoords):
        uv.data[loop_index].uv=uvco

# Stone water table and floor bands emphasize the masonry rhythm in the source.
band_verts, band_faces = [], []
for z, height in ((.65,.18),(ground_h-.16,.18),
                  (ground_h+typical_h*2-.09,.16),
                  (ground_h+typical_h*4-.09,.16),
                  (wall_top-.12,.20)):
    # Narrow extruded perimeter courses: repeat the outline as a solid horizontal ring.
    n = len(poly)
    base = len(band_verts)
    for zz in (z, z+height):
        band_verts.extend((x,y,zz) for x,y in poly)
    for i in range(n):
        j=(i+1)%n
        band_faces.append((base+i,base+j,base+n+j,base+n+i))
mesh_obj("Continuous_pale_stone_cornice_and_floor_bands", band_verts, band_faces, limestone)

# Facade windows: repeated framed glazing panels, aligned to each substantial GIS
# wall segment; ground level glazing is taller, upper windows are residential scale.
winverts, winfaces, winmat_ids = [], [], []
frameverts, framefaces = [], []


def append_box(verts, faces, center, dims, angle):
    x,y,z=center; w,d,h=dims
    c,s=math.cos(angle),math.sin(angle)
    start=len(verts)
    for zz in (-h/2,h/2):
        for yy in (-d/2,d/2):
            for xx in (-w/2,w/2):
                verts.append((x+c*xx-s*yy,y+s*xx+c*yy,z+zz))
    faces.extend([(start+0,start+1,start+3,start+2),(start+4,start+6,start+7,start+5),
                  (start+0,start+4,start+5,start+1),(start+2,start+3,start+7,start+6),
                  (start+0,start+2,start+6,start+4),(start+1,start+5,start+7,start+3)])


for edge_index, (a,b) in enumerate(zip(poly, poly[1:]+poly[:1])):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=math.hypot(dx,dy)
    if length < 5.0:
        continue
    tangent=Vector((dx/length,dy/length))
    # CCW ring means outward normal is right of tangent.
    normal=Vector((tangent.y,-tangent.x))
    angle=math.atan2(tangent.y,tangent.x)
    usable=length-2.0
    nwin=max(1,int(usable/4.7))
    spacing=usable/nwin
    mid=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2))
    for floor in range(6):
        zbase=0 if floor==0 else ground_h+(floor-1)*typical_h
        fheight=ground_h if floor==0 else typical_h
        wh=min(2.35, fheight*.66) if floor else 2.7
        ww=min(1.75, spacing*.48) if floor else min(2.0,spacing*.52)
        wz=zbase+fheight*.53
        for k in range(nwin):
            along=(k-(nwin-1)/2)*spacing
            center2=mid+tangent*along+normal*.11
            append_box(winverts,winfaces,(center2.x,center2.y,wz),(ww,.17,wh),angle)
            # dark bronze surround assembled as thin visible perimeter bars
            for xx in (-ww/2,ww/2):
                append_box(frameverts,framefaces,(center2.x,center2.y,wz+xx*0),(0.075,.24,wh+.14),angle)
            for zz in (-wh/2,wh/2):
                append_box(frameverts,framefaces,(center2.x,center2.y,wz+zz),(ww+.14,.24,.075),angle)
            append_box(frameverts,framefaces,(center2.x,center2.y,wz),(0.045,.25,wh),angle)
if winverts:
    obj=mesh_obj("Repeated_deep_set_residential_windows",winverts,winfaces,glass)
    obj["window_count"] = len(winverts)//8
if frameverts:
    mesh_obj("Dark_bronze_window_mullions_and_lintels",frameverts,framefaces,frame)

# Stone rake trim outlines the photographed south gable. The photo and GIS layout
# jointly support a south-end public facade; exact measured entrance coordinates
# were not published.
gable_y=tower[2]-.18
xmid=(tower[0]+tower[1])/2
for xa,za,xb,zb in ((tower[0]+.45,wall_top,xmid,wall_top+gable_rise),
                    (xmid,wall_top+gable_rise,tower[1]-.45,wall_top)):
    dx,dz=xb-xa,zb-za
    length=math.hypot(dx,dz)
    angle=math.atan2(-dz,dx) if dx>0 else math.atan2(-dz,dx)
    trim=box("Pale_stone_gable_rake_trim",((xa+xb)/2,gable_y,(za+zb)/2),(.42,length,.5),limestone)
    trim.rotation_euler[1]=angle
# Three-story projecting glazed bay at the gable front, matching Purdue's photo.
# Its face runs east-west; projection is south from the gable plane.
bay_x,bay_y,bay_w,bay_depth=xmid,-105.5,16.0,5.0
for level in range(3):
    z=4.25+level*3.15
    box("Projecting_glazed_entry_bay_spandrel",(bay_x,bay_y,z),(bay_w,bay_depth,.42),limestone)
    for col in range(7):
        xx=bay_x-bay_w/2+col*bay_w/6
        box("Entry_bay_vertical_mullion",(xx,bay_y,z+1.05),(.12,bay_depth+.12,2.25),frame)
    box("Entry_bay_glazing_panel",(bay_x,bay_y,z+1.00),(bay_w-.24,bay_depth-.12,2.12),glass)
box("Tall_stone_entry_portal",(bay_x,bay_y-2.7,2.05),(14.5,.72,4.1),limestone)
box("Deep_shadowed_main_entry",(bay_x,bay_y-3.12,1.7),(6.2,.18,3.15),entrydark)
box("Main_entry_glazing",(bay_x,bay_y-3.24,1.65),(5.7,.09,2.8),glass)

# Pale lintels/sills and brick pier cadence on the long residential wing.
for x in (-502.0,-496.0,-490.0,-484.0):
    box("Wing_masonry_pier",(x,-68.5,wall_top*.5),(.32,.26,wall_top-.35),brick)

# Dormers repeat down the long wing slope, as visible in Purdue's oblique photo.
# The roof has a north-south ridge; these small gables face outward from the east slope.
for i,y in enumerate((-91.0,-67.0,-43.0)):
    x=-483.5
    zbase=wall_top+.35
    box("Wing_dormer_cheek_north",(x,y+1.55,zbase+.48),(1.45,.2,.96),brick)
    box("Wing_dormer_cheek_south",(x,y-1.55,zbase+.48),(1.45,.2,.96),brick)
    box("Wing_dormer_glazing",(x+1.0,y,zbase+.58),(.12,2.6,.86),glass)
    verts=[(x+.05,y-1.7,zbase+.95),(x+1.4,y-1.7,zbase+.95),(x+.75,y-1.7,zbase+1.7),
           (x+.05,y+1.7,zbase+.95),(x+1.4,y+1.7,zbase+.95),(x+.75,y+1.7,zbase+1.7)]
    mesh_obj("Wing_dormer_pitched_slate",verts,[(0,1,4,3),(1,2,5,4)],roofmat)

# A second scene contains only a clearly labeled schematic of documented uses.
# It is not exported with the exterior asset collection and must not be read as a plan.
interior_scene=bpy.data.scenes.new(SCENE_NAME+"_SchematicInterior_NOT_AS_BUILT")
interior_scene["building_id"]=ID
interior_scene["status"]="Schematic illustration, not an as-built plan. Room positions and dimensions are invented."
interior_scene["program_sources"]="Purdue HCR/OEP and official Honors College guided tour"
interior_collection=bpy.data.collections.new("Schematic_Interior_NOT_AS_BUILT")
interior_scene.collection.children.link(interior_collection)
ix,iy=0.0,0.0
box("Diagram_floor_plate",(ix,iy,.0),(42,62,.5),interior_floor,interior_collection)
box("Diagram_outer_wall_north",(ix,31,2.3),(42,.35,4.6),interior_wall,interior_collection)
box("Diagram_outer_wall_south",(ix,-31,2.3),(42,.35,4.6),interior_wall,interior_collection)
box("Diagram_outer_wall_east",(21,iy,2.3),(.35,62,4.6),interior_wall,interior_collection)
box("Diagram_outer_wall_west",(-21,iy,2.3),(.35,62,4.6),interior_wall,interior_collection)
# Program zones in a simple conceptual ground-floor sequence.
box("Concept_Innovation_Forum",(-11,11,.65),(18,18,.35),interior_wood,interior_collection)
box("Concept_Forum_stage",(-11,18,1.2),(8,2,1.0),limestone,interior_collection)
box("Concept_Honors_Hall",(10,10,.65),(17,18,.35),interior_wood,interior_collection)
box("Concept_Dining",(10,-11,.65),(17,18,.35),interior_floor,interior_collection)
box("Concept_Advising_and_offices",(-11,-12,.65),(18,17,.35),interior_floor,interior_collection)
for x in (-18,-4,4,18):
    box("Concept_partition",(x,0,1.45),(.16,56,2.7),interior_wall,interior_collection)
for y in (-1,21):
    box("Concept_cross_partition",(0,y,1.45),(38,.16,2.7),interior_wall,interior_collection)
interior_scene.collection.children.unlink(interior_collection)
interior_scene.collection.children.link(interior_collection)

# Export-oriented viewport, selection, and file metadata.
for obj in asset.objects:
    obj.select_set(False)
bpy.context.view_layer.objects.active=None
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1200
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new("Lees-Such neutral preview world")
scene.world.use_nodes=True
background=next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND")
background.inputs["Color"].default_value=(.48,.56,.68,1)
background.inputs["Strength"].default_value=.40
scene.render.film_transparent=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=1.0
scene.render.image_settings.file_format="PNG"

# Build independent review camera and lights in a non-export stage collection.
stage=bpy.data.collections.new("Preview_Stage_NOT_EXPORTED")
scene.collection.children.link(stage)
def stage_object(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    stage.objects.link(obj)

bpy.ops.object.light_add(type="AREA", location=(cx-30,cy-90,72))
key=bpy.context.object; key.name="Preview_Key_Area"; key.data.energy=42000; key.data.shape="DISK"; key.data.size=58; stage_object(key)
bpy.ops.object.light_add(type="AREA", location=(cx+70,cy+15,48))
fill=bpy.context.object; fill.name="Preview_Fill_Area"; fill.data.energy=25000; fill.data.size=48; stage_object(fill)
bpy.ops.object.camera_add(location=(cx-55,cy-145,38))
cam=bpy.context.object; cam.name="Preview_ThreeQuarter_Camera"; cam.data.lens=50; stage_object(cam)
target=Vector((cx,cy,11)); cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
scene.camera=cam
scene.render.filepath=str(AUDIT/"preview_exterior.png")

# Save and render review view. The scene and asset collection names are stable.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)

record={
  "building_id":ID,
  "display_name":"Honors College and Residences North / Lees-Such Tower",
  "asset_path":"modular/buildings/massing_honors_college_and_residences_north_3de3b7c.blend",
  "scene":SCENE_NAME,
  "collection":ASSET_NAME,
  "source_evidence":[
    {"url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D544&outFields=*&returnGeometry=true&outSR=4326&f=pjson","provider":"Purdue GIS BuildingShapesZip4","feature":"FID 544; GlobalID {2A6774B1-C24B-4961-ACE0-DB3C256D90EF}; Lees-Such Tower","retrieved":"2026-10-26","source_crs":"WGS84 geographic coordinates (EPSG:4326)","method":"lon/lat transformed to project local campus frame using documented approximate conversion; collinear vertices simplified with 0.75m tolerance","uncertainty":"The GIS vertical attributes conflict with Purdue OEP's six-floor plus basement description. GIS plan geometry is the best available source for outline; not a survey control measurement."},
    {"url":"https://www.purdue.edu/operations/emergency-preparedness/hcr/","provider":"Purdue Operations and Emergency Preparedness","feature":"Honors College and Residences campus building overview","retrieved":"2026-10-26","source_crs":"not applicable","method":"Official text consulted for current complex identity and six floors plus basement","uncertainty":"No architectural plans or measured elevations provided on source page."},
    {"url":"https://www.purdue.edu/newsroom/archive/purduetoday/releases/2016/Q3/photo-gallery-honors-college-and-residences.html","provider":"Purdue Today","feature":"2016 exterior image, local snapshot sources/purdue_news_hcr_2016.jpg","retrieved":"2026-10-26","source_date":"2016","source_crs":"not applicable","method":"Visual comparison for brick palette, limestone trim, glazed projecting bay, dark roof, and dormers","uncertainty":"Single oblique photograph does not establish facade orientation or dimensions; those details are approximate."},
    {"url":"https://www.honors.purdue.edu/admissions/walking-tour.php","provider":"Purdue Honors College","feature":"Official campus tour and building/interior photographs","retrieved":"2026-10-26","source_crs":"not applicable","method":"Consulted for documented Innovation Forum and Honors Hall interior uses","uncertainty":"No public floor plan was located; secondary scene is only a schematic diagram."}
  ],
  "model_notes":{"footprint_simplified_vertices":len(poly),"footprint_area_simplified_m2":round(area,2),"outline_bounds_m":{"x":[minx,maxx],"y":[miny,maxy]},"above_grade_floors":6,"floor_heights_m":{"ground_estimate":ground_h,"typical_estimate":typical_h},"roof_peak_estimate_m":round(wall_top+gable_rise,2),"dimension_source_conflict":"The manifest's former massing bounds are close to the GIS polygon but shifted by 1-3m; this model follows the Purdue GIS polygon. Do not use the modeled wall/roof height as surveyed."},
  "interior":"Separate scene is expressly schematic / not as-built; it communicates official program spaces without claiming plan accuracy.",
  "validation":{"rebuild_script":"modular/buildings/build_massing_honors_college_and_residences_north_3de3b7c.py","fresh_open_validation":"pending"}
}
(AUDIT/"evidence_record.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
print("BUILT",OUT,"area",area,"verts",len(poly),"objects",len(asset.objects))

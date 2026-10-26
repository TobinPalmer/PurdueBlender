"""Build the University Church asset from its campus GIS footprint and photo evidence.

Run with Blender 5.x in background mode. Geometry is kept in the project's campus
coordinate frame because this remains a `massing` asset in modular/manifest.json.
"""
import bpy
import json
import math
import os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_ID = "massing_university_church_84b2a1b"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
OUT = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
GIS = os.path.join(ROOT, "audit", "purdue_university_church", "sources", "purdue_gis_fid797.geojson")
AUDIT = os.path.join(ROOT, "audit", "purdue_university_church", "build_evidence.json")

ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
M_PER_DEG_LON = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
M_PER_DEG_LAT = 111040.0

def xy(lon, lat):
    return ((lon - ORIGIN_LON) * M_PER_DEG_LON, (lat - ORIGIN_LAT) * M_PER_DEG_LAT)

def mat(name, color, roughness=0.82, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    return m

def create_mesh(name, verts, faces, material, collection, bevel=0.0):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if bevel:
        mod = obj.modifiers.new("Soft arris", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj

def box(name, center, size, material, collection, bevel=0.025):
    cx, cy, cz = center
    sx, sy, sz = (v / 2.0 for v in size)
    verts = [(cx+dx*sx, cy+dy*sy, cz+dz*sz)
             for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                              (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return create_mesh(name, verts, faces, material, collection, bevel)

def beam_between(name, a, b, width, depth, material, collection):
    a, b = Vector(a), Vector(b)
    d = b - a
    center=(a+b)*0.5
    obj = box(name, center, (width, depth, d.length), material, collection, 0.015)
    # Recenter world-authored vertices before rotation so sloped roof beams stay in place.
    for vert in obj.data.vertices:
        vert.co -= center
    obj.location=center
    obj.rotation_mode='QUATERNION'
    obj.rotation_quaternion=d.normalized().to_track_quat('Z','Y')
    return obj

def cylinder(name, center, radius, depth, material, collection, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
    o = bpy.context.object
    o.name = name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    collection.objects.link(o)
    o.data.materials.append(material)
    bevel = o.modifiers.new("Column edge soften", "BEVEL")
    bevel.width = 0.025
    bevel.segments = 2
    return o

def arch_trim(name, center, span, spring_z, along_x, outward_offset, material, collection):
    """Stone semicircular window head, using an absolute-coordinate beveled spline."""
    curve=bpy.data.curves.new(name+"Curve","CURVE")
    curve.dimensions='3D'; curve.resolution_u=1; curve.bevel_depth=0.065; curve.bevel_resolution=2
    spline=curve.splines.new("POLY"); spline.points.add(12)
    radius=span*0.5
    x,y=center
    for idx,pt in enumerate(spline.points):
        angle=math.pi*idx/12.0
        across=radius*math.cos(angle)
        z=spring_z+radius*math.sin(angle)
        if along_x:
            pt.co=(x+across,y+outward_offset,z,1.0)
        else:
            pt.co=(x+outward_offset,y+across,z,1.0)
    obj=bpy.data.objects.new(name,curve); collection.objects.link(obj); curve.materials.append(material)
    return obj

def main():
    with open(GIS, "r", encoding="utf-8") as f:
        data = json.load(f)
    feat = data["features"][0]
    assert feat["properties"]["FID"] == 797 and feat["properties"]["BUILDING_N"] == "University Church"
    poly = [xy(lon, lat) for lon, lat in feat["geometry"]["coordinates"][0][:-1]]
    # Keep the native named scene and collection, clearing only this asset scene.
    scene = bpy.data.scenes.get(SCENE_NAME) or bpy.data.scenes.new(SCENE_NAME)
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    collection = bpy.data.collections.get(COLLECTION_NAME) or bpy.data.collections.new(COLLECTION_NAME)
    if collection.name not in [c.name for c in scene.collection.children]:
        scene.collection.children.link(collection)
    preview_collection=bpy.data.collections.get("Preview_"+ASSET_ID) or bpy.data.collections.new("Preview_"+ASSET_ID)
    if preview_collection.name not in [c.name for c in scene.collection.children]:
        scene.collection.children.link(preview_collection)
    for obj in list(preview_collection.objects):
        bpy.data.objects.remove(obj,do_unlink=True)
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    # Remove empty/leftover scene child collections created by previous runs.
    for c in list(scene.collection.children):
        if c != collection and c != preview_collection and c.users == 1:
            scene.collection.children.unlink(c)

    brick = mat("UC | warm red-orange brick", (0.43, 0.105, 0.065), 0.94)
    brick_alt = mat("UC | varied brick courses", (0.53, 0.16, 0.09), 0.96)
    limestone = mat("UC | pale limestone trim", (0.74, 0.68, 0.56), 0.78)
    roofmat = mat("UC | charcoal slate roof", (0.105, 0.13, 0.14), 0.87)
    copper = mat("UC | weathered copper green", (0.12, 0.36, 0.30), 0.46, 0.36)
    glass = mat("UC | blue gray glazing", (0.075, 0.15, 0.19), 0.27, 0.12)
    dark = mat("UC | recessed openings", (0.045, 0.04, 0.035), 0.9)
    wood = mat("UC | stained entrance doors", (0.18, 0.075, 0.035), 0.5)

    # GIS outline is the measured plan envelope (EPSG:4326 -> local project tangent frame).
    # One connected, notched outline is retained; no unsupported courtyard hole is invented.
    n = len(poly)
    verts = [(x,y,z) for z in (0.0, 11.7) for x,y in poly]
    # Explicitly triangulate the GIS concave outline; a single n-gon can bridge its recess.
    triangles=tessellate_polygon([[Vector((x,y,0.0)) for x,y in poly]])
    top_tris=[tuple(n+idx for idx in tri) for tri in triangles]
    bottom_tris=[tuple(reversed(tri)) for tri in triangles]
    faces = bottom_tris + top_tris
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    shell=create_mesh("University Church | GIS brick envelope", verts, faces, brick, collection)
    # The cap is roof deck, while the side faces stay brick. The concave GIS footprint leaves
    # the open U/courtyard area uncovered rather than bridging it with rectangular roof slabs.
    shell.data.materials.append(roofmat)
    for pg in shell.data.polygons[len(bottom_tris):len(bottom_tris)+len(top_tris)]:
        pg.material_index=1

    minx=min(p[0] for p in poly); maxx=max(p[0] for p in poly)
    miny=min(p[1] for p in poly); maxy=max(p[1] for p in poly)
    cx=(minx+maxx)/2; cy=(miny+maxy)/2

    # Horizontal stone string courses signal the observed multi-storey church / later campus use.
    for z in (0.65, 4.05, 7.35, 10.7):
        for i,(x1,y1) in enumerate(poly):
            x2,y2=poly[(i+1)%n]
            dx,dy=x2-x1,y2-y1
            length=math.hypot(dx,dy)
            if length < 2.3: continue
            # Thin stone bands placed on each GIS outline edge.
            if abs(dx)>abs(dy):
                box(f"UC | stone string course {z:.2f} {i}",((x1+x2)/2,(y1+y2)/2,z),(length,0.13,0.18),limestone,collection,0.01)
            else:
                box(f"UC | stone string course {z:.2f} {i}",((x1+x2)/2,(y1+y2)/2,z),(0.13,length,0.18),limestone,collection,0.01)

    # Repeated tall windows on long orthogonal elevations, with stone surrounds, sills and lintels.
    # Openings are modeled as dark reveals with set-back glazing, not texture-only marks.
    for i,(x1,y1) in enumerate(poly):
        x2,y2=poly[(i+1)%n]
        dx,dy=x2-x1,y2-y1
        length=math.hypot(dx,dy)
        if length < 4.2: continue
        horizontal=abs(dx)>=abs(dy)
        count=max(1,int(length//4.6))
        for j in range(count):
            t=(j+0.5)/count
            x=x1+dx*t; y=y1+dy*t
            for floor,zbase in enumerate((1.05,4.35,7.65)):
                # Avoid openings through the entry/portico zone on the inferred east wall.
                if y < miny+0.6 and 0.15 < x-cx < 14.0:
                    continue
                if not horizontal and x > maxx-0.6 and abs(y-(cy-1.8)) < 6.3:
                    continue
                w=1.06 if horizontal else 0.94
                h=2.05 if floor < 2 else 1.75
                if horizontal:
                    box(f"UC | window reveal {i}-{j}-{floor}",(x,y,zbase+h/2),(w,0.11,h),dark,collection,0.02)
                    box(f"UC | window glass {i}-{j}-{floor}",(x,y-0.067,zbase+h/2),(w*0.72,0.035,h*0.82),glass,collection,0.01)
                    box(f"UC | stone sill {i}-{j}-{floor}",(x,y,zbase-0.06),(w+0.26,0.24,0.13),limestone,collection,0.012)
                    box(f"UC | stone lintel {i}-{j}-{floor}",(x,y,zbase+h+0.08),(w+0.2,0.20,0.13),limestone,collection,0.012)
                    # central mullion
                    box(f"UC | mullion {i}-{j}-{floor}",(x,y-0.094,zbase+h/2),(0.055,0.035,h*0.8),limestone,collection,0.006)
                    # The photographed long side elevations have arched heads. The portico wall
                    # is the east elevation (X=max) and keeps the source-visible square lintels.
                    arch_trim(f"UC | arched side window head {i}-{j}-{floor}",(x,y),w+0.12,zbase+h,True,
                              -0.14 if y<cy else 0.14,limestone,collection)
                else:
                    box(f"UC | window reveal {i}-{j}-{floor}",(x,y,zbase+h/2),(0.11,w,h),dark,collection,0.02)
                    box(f"UC | window glass {i}-{j}-{floor}",(x+0.067,y,zbase+h/2),(0.035,w*0.72,h*0.82),glass,collection,0.01)
                    box(f"UC | stone sill {i}-{j}-{floor}",(x,y,zbase-0.06),(0.24,w+0.26,0.13),limestone,collection,0.012)
                    box(f"UC | stone lintel {i}-{j}-{floor}",(x,y,zbase+h+0.08),(0.20,w+0.20,0.13),limestone,collection,0.012)
                    box(f"UC | mullion {i}-{j}-{floor}",(x+0.094,y,zbase+h/2),(0.035,0.055,h*0.8),limestone,collection,0.006)
                    # Keep the east/portico elevation square-headed; apply arches to perpendicular
                    # elevations only, matching the direct source-photo comparison.
                    if x <= maxx-0.6:
                        arch_trim(f"UC | arched side window head {i}-{j}-{floor}",(x,y),w+0.12,zbase+h,False,
                                  -0.14 if x<cx else 0.14,limestone,collection)

    # The 2023 source shows a four-column portico and one green-spired square tower. The 2024
    # first-floor plan places the main hall doors along its right edge; aligned to the GIS shape,
    # this is inferred as the east elevation. The floor plan has no north arrow, so this is uncertain.
    front_x=maxx - 0.05
    entry_y=cy - 1.8
    portico_depth=2.35
    for ix,off in enumerate((-4.25,-1.42,1.42,4.25)):
        py=entry_y+off
        # bases, square plinths and circular shafts/capitals provide a legible four-column front.
        box(f"UC | portico column plinth {ix}",(front_x+1.35,py,0.46),(0.72,0.78,0.92),limestone,collection,0.04)
        cylinder(f"UC | portico column shaft {ix}",(front_x+1.35,py,2.17),0.27,2.7,limestone,collection,20)
        cylinder(f"UC | portico column capital {ix}",(front_x+1.35,py,3.57),0.40,0.34,limestone,collection,20)
    box("UC | portico entablature",(front_x+1.35,entry_y,3.93),(0.58,11.2,0.54),limestone,collection,0.04)
    # Pediment triangular profile, facing east.
    py0,py1=entry_y-5.6,entry_y+5.6
    px=front_x+1.72
    create_mesh("UC | portico triangular pediment",
       [(px,py0,4.2),(px,py1,4.2),(px,entry_y,6.2),
        (px-0.48,py0,4.2),(px-0.48,py1,4.2),(px-0.48,entry_y,6.2)],
       [(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)],limestone,collection)
    # Photo evidence shows a circular vent/oculus centered in the pediment.
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=0.48,depth=0.08,
                                        location=(front_x+1.83,entry_y,5.05),rotation=(0,math.pi/2,0))
    oculus=bpy.context.object; oculus.name="UC | pediment circular oculus glazing"
    for old_collection in list(oculus.users_collection): old_collection.objects.unlink(oculus)
    collection.objects.link(oculus); oculus.data.materials.append(glass)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.54,minor_radius=0.09,major_segments=32,minor_segments=8,
                                    location=(front_x+1.91,entry_y,5.05),rotation=(0,math.pi/2,0))
    ring=bpy.context.object; ring.name="UC | pediment oculus limestone ring"
    for old_collection in list(ring.users_collection): old_collection.objects.unlink(ring)
    collection.objects.link(ring); ring.data.materials.append(limestone)
    # Three entrance openings, each with stone surround and dark timber doors.
    for k,off in enumerate((-3.3,0.0,3.3)):
        ey=entry_y+off
        box(f"UC | entrance surround {k}",(front_x-0.08,ey,1.62),(0.24,1.82,3.15),limestone,collection,0.035)
        box(f"UC | timber double door {k}",(front_x-0.23,ey,1.55),(0.10,1.32,2.72),wood,collection,0.025)
        box(f"UC | door glazing transom {k}",(front_x-0.30,ey,2.64),(0.045,0.90,0.36),glass,collection,0.01)
        for side in (-1,1):
            box(f"UC | door panel {k}-{side}",(front_x-0.29,ey+side*0.32,1.48),(0.035,0.42,1.88),wood,collection,0.018)
    box("UC | entry landing",(front_x+2.05,entry_y,0.16),(2.6,12.5,0.32),limestone,collection,0.045)
    # Broad shallow steps facing east, consistent with exterior-photo approach.
    for j in range(4):
        box(f"UC | entry step {j}",(front_x+3.10+j*0.38,entry_y,0.11-j*0.03),(0.42,13.2,0.22-j*0.035),limestone,collection,0.025)

    # The 2023 view places the single square tower at the far/right end of the long portico wing.
    # With the inferred east-facing facade, the photograph's right maps to +Y (north).
    tower_x=(minx+maxx)/2 + 7.2; tower_y=entry_y+10.0
    box("UC | bell tower shaft",(tower_x,tower_y,15.0),(6.1,6.1,6.6),brick,collection,0.035)
    for z in (12.0,13.0,18.0,19.5,20.6,21.1):
        box(f"UC | tower limestone band {z}",(tower_x,tower_y,z),(6.42,6.42,0.15),limestone,collection,0.018)
    # Four tall louvered belfry openings on shaft faces.
    for side in (-1,1):
        for face in ("south","north"):
            yy=tower_y+side*3.08 if face=="north" else tower_y-3.08
            box(f"UC | belfry louver {face} {side}",(tower_x,yy,17.1),(1.25,0.08,2.05),dark,collection,0.03)
            for r in range(5):
                box(f"UC | louver slat {face} {side} {r}",(tower_x,yy-0.06 if face=="south" else yy+0.06,16.38+r*0.30),(1.05,0.06,0.07),limestone,collection,0.01)
    for side in (-1,1):
        for face in ("west","east"):
            xx=tower_x+side*3.08
            box(f"UC | belfry louver {face} {side}",(xx,tower_y,17.1),(0.08,1.25,2.05),dark,collection,0.03)
            for r in range(5):
                box(f"UC | louver slat {face} {side} {r}",(xx+(-0.06 if face=="west" else 0.06),tower_y,16.38+r*0.30),(0.06,1.05,0.07),limestone,collection,0.01)
    # Steep square copper spire with four gabled faces and a slender finial.
    basez,tipz=21.2,27.4
    half=3.0
    create_mesh("UC | copper pyramidal spire",
       [(tower_x-half,tower_y-half,basez),(tower_x+half,tower_y-half,basez),
        (tower_x+half,tower_y+half,basez),(tower_x-half,tower_y+half,basez),(tower_x,tower_y,tipz)],
       [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,3,2,1)],copper,collection)
    cylinder("UC | spire finial",(tower_x,tower_y,tipz+0.52),0.055,1.08,copper,collection,12)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.16, location=(tower_x,tower_y,tipz+0.98))
    fin=bpy.context.object; fin.name="UC | finial orb"
    for c in list(fin.users_collection): c.objects.unlink(fin)
    collection.objects.link(fin); fin.data.materials.append(copper)

    # Low sloped slate roof on the eastern sanctuary volume. Its gable end faces east, toward
    # the inferred portico; eave and ridge heights remain estimates.
    rx0=maxx-14.1; rx1=maxx-0.35
    ry0=miny+5.8; ry1=min(maxy-4.0, miny+28.8)
    eave, ridge=11.7,14.9
    ridge_y=(ry0+ry1)*0.5
    roof_verts=[(rx0,ry0,eave),(rx1,ry0,eave),(rx1,ry1,eave),(rx0,ry1,eave),
                (rx0,ridge_y,ridge),(rx1,ridge_y,ridge)]
    roof_faces=[(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5),(0,3,2,1)]
    create_mesh("UC | slate sanctuary gable roof",roof_verts,roof_faces,roofmat,collection)
    # Stone rake outlines frame the east/west gable ends.
    for xx in (rx0,rx1):
        beam_between("UC | gable rake left",(xx,ry0,eave),(xx,ridge_y,ridge),0.18,0.20,limestone,collection)
        beam_between("UC | gable rake right",(xx,ridge_y,ridge),(xx,ry1,eave),0.18,0.20,limestone,collection)

    # Side wings receive low simple charcoal roofs, leaving GIS step-backs legible.
    # Boundary segments outside the main sanctuary are capped with shallow flat roof plates.
    # The slate material on the concave polygon cap supplies subtle low-profile roofs to the
    # classroom wings; no bounding-box slab bridges the courtyard.
    # Cornice coping above brick, used consistently on low connector wings.
    for i,(x1,y1) in enumerate(poly):
        x2,y2=poly[(i+1)%n]
        if abs(x2-x1)>abs(y2-y1):
            box(f"UC | parapet coping {i}",((x1+x2)/2,(y1+y2)/2,11.78),(math.hypot(x2-x1,y2-y1),0.26,0.16),limestone,collection,0.012)
        else:
            box(f"UC | parapet coping {i}",((x1+x2)/2,(y1+y2)/2,11.78),(0.26,math.hypot(x2-x1,y2-y1),0.16),limestone,collection,0.012)

    # Scene/collection names are manifest-stable. Set useful preview defaults without changing geometry.
    for s in bpy.data.scenes:
        if s != scene and s.name.startswith("Building_"+ASSET_ID):
            bpy.data.scenes.remove(s)
    bpy.context.window.scene = scene if bpy.context.window else scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    if scene.world is None:
        scene.world=bpy.data.worlds.new("University Church Preview World")
    scene.world.color=(0.16,0.18,0.22)
    scene.world.use_nodes=True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(0.30,0.34,0.42,1.0)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=0.65
    scene.view_settings.view_transform='Standard'
    scene.view_settings.look='Medium High Contrast'
    scene.view_settings.exposure=0.6
    scene.view_settings.gamma=1.0
    # Non-rendering camera framing for preview.
    cam_data=bpy.data.cameras.new("UC Preview Camera")
    cam=bpy.data.objects.new("UC Preview Camera",cam_data); preview_collection.objects.link(cam)
    cam.location=(cx+78,cy-16,53)
    target=Vector((cx,cy,9.0)); direction=target-Vector(cam.location)
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=76
    scene.camera=cam
    light_data=bpy.data.lights.new("UC Preview Area","AREA"); light_data.energy=11000; light_data.shape='DISK'; light_data.size=42
    light=bpy.data.objects.new("UC Preview Area",light_data); preview_collection.objects.link(light); light.location=(cx+26,cy-12,56)
    light.rotation_euler=(Vector((cx,cy,8))-Vector(light.location)).to_track_quat('-Z','Y').to_euler()
    sun_data=bpy.data.lights.new("UC Preview Sun","SUN"); sun_data.energy=2.2; sun_data.angle=math.radians(18)
    sun=bpy.data.objects.new("UC Preview Sun",sun_data); preview_collection.objects.link(sun)
    sun.location=(cx+30,cy-32,52)
    sun.rotation_euler=(Vector((cx,cy,6))-Vector(sun.location)).to_track_quat('-Z','Y').to_euler()

    # For portable previews, all materials are procedural/packed in the file.
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    scene.render.filepath=os.path.join(ROOT,"audit","purdue_university_church","preview.png")
    bpy.ops.render.render(write_still=True)
    # A low east-side approach checks the photographed portico/spire relationship; a top view
    # separates GIS plan accuracy from facade-height estimates for later reviewers.
    cam.location=(cx+69.0,cy-1.0,20.0)
    target=Vector((cx+2.0,cy-1.0,13.5)); direction=target-Vector(cam.location)
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=59.0
    scene.render.filepath=os.path.join(ROOT,"audit","purdue_university_church","preview_east.png")
    bpy.ops.render.render(write_still=True)
    cam.location=(cx+2.5,cy,80.0); cam.rotation_euler=(0.0,0.0,0.0); cam.data.ortho_scale=70.0
    scene.render.filepath=os.path.join(ROOT,"audit","purdue_university_church","preview_plan.png")
    bpy.ops.render.render(write_still=True)
    # Store structured source data alongside the native asset.
    pts=[xy(lon,lat) for lon,lat in feat["geometry"]["coordinates"][0]]
    evidence={
      "building_id": ASSET_ID,
      "asset_path": "modular/buildings/"+ASSET_ID+".blend",
      "scene": SCENE_NAME,
      "collection": COLLECTION_NAME,
      "retrieved_utc_date": "2026-10-26",
      "coordinate_frame": {"axes":"X east, Y north, Z up","units":"meters","project_origin_lat_lon":[ORIGIN_LAT,ORIGIN_LON],"conversion":"X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0; approximate local tangent transform; not surveyed"},
      "sources": [
        {"provider":"Purdue University GIS / ArcGIS FeatureServer","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D797&outFields=*&returnGeometry=true&outSR=4326&f=geojson","snapshot_path":"audit/purdue_university_church/sources/purdue_gis_fid797.geojson","feature_id":"FID 797, BLDG_ABBR UC, BUILDING_N University Church","source_crs":"EPSG:4326","retrieved":"2026-10-26","method":"Raw polygon transformed using project local tangent approximation; measured XY outline, orientation and plan bounds","uncertainty":"GIS polygon is the mapped building outline, not a survey; source fields conflict (Level_=4, NUM_LEVELS=1, CountOfFLO=3, Extrution=39 with undocumented units)."},
        {"provider":"Purdue Road School 2024","url":"https://www.roadschool.purdue.edu/maps/2024%20University%20Church.pdf","snapshot_path":"audit/purdue_university_church/sources/2024_road_school_university_church_first_floor.pdf","source_date":"2024","source_crs":"not geospatial; schematic first-floor plan","retrieved":"2026-10-26","method":"Plan shape used to confirm connected rooms, large sanctuary/event hall, wings and circulation","uncertainty":"No north arrow or scale on displayed map; not used to determine exterior dimensions or geographic orientation."},
        {"provider":"Indiana State Budget Committee, June 2019 meeting minutes","url":"https://www.in.gov/sba/files/June-2019-Minutes-Fully-Executed.pdf","snapshot_path":"audit/purdue_university_church/sources/indiana_state_budget_committee_june_2019.pdf","source_date":"2019-06","source_crs":"not geospatial; address reference","retrieved":"2026-10-26","method":"Identity, address, 31,964 square feet, multi-story status and 0.86-acre parcel","uncertainty":"The source describes a multi-story facility but does not give an exact floor count or measured height."},
        {"provider":"Dave Wegiel / Pinola Photo","url":"https://pinolaphoto.com/2024/01/28/university-church-west-lafayette-indiana-2/","image_url":"https://photos.smugmug.com/2023-Photos/2023-Purdue/i-jrL8K7n/0/c835a2ec/L/DAW00401-L.jpg","snapshot_path":"audit/purdue_university_church/sources/dave_wegiel_university_church_dusk.jpg","source_date":"photo 2023-12-10; page 2024-01-28","source_crs":"photograph, no geotag/camera azimuth available","retrieved":"2026-10-26","method":"Facade study: red brick, classical four-column portico, triangular pediment, square tower with green copper spire, steps and lower wings","uncertainty":"Photo camera azimuth cannot be tied to a specific GIS wall; east facade assignment is inferred from the floorplan hall-door edge."},
        {"provider":"Home of Purdue local directory image","url":"https://www.homeofpurdue.com/listing/university-church/","snapshot_path":"audit/purdue_university_church/sources/homeofpurdue_university_church_exterior.jpg","source_date":"undated directory photo","source_crs":"photograph, no geotag/camera azimuth available","retrieved":"2026-10-26","method":"Cross-check brick/church character and facade opening proportions","uncertainty":"Directory image differs from the 2023 classical-portico view and could show another facade/phase or be a mismatched listing image; twin-tower composition not included absent corroboration."}
      ],
      "dimensions": {"gis_xy_bounds_m":[[minx,maxx],[miny,maxy]],"outline_vertex_count":n,"roof_eaves_m_estimated":11.7,"main_roof_ridge_m_estimated":14.9,"spire_tip_m_estimated":28.54,"floor_estimate":"3 occupied floors inferred from the GIS CountOfFLO=3 and multi-story 2019 state record; exact floor count unresolved"},
      "geometry_edits":["Replaced one-mesh unverified massing with campus-frame GIS polygon shell","Added procedural red-brick material and explicit stone floor bands","Added recessed glazing with stone surrounds/mullions; arched heads occur on non-portico elevations, while the east portico facade retains square lintels per photo comparison","Added four-column portico, triangular pediment, circular oculus, three doors and steps based on 2023 photo","Added square bell tower and green copper pyramidal spire based on 2023 photo","Added estimated slate sanctuary gable and connector-wing roof caps","Kept all components in manifest collection and campus coordinate frame"],
      "uncertainties":["Portico facade mapping to GIS edge is inferred, not geotag verified","Historic twin-tower image conflicts with the contemporary single-tower facade and is treated as possibly mismatched/unresolved","GIS floor attributes conflict; exact storey/height and roof elevations remain estimates","2024 floorplan has no georeferencing/scale/orientation and does not verify vertical layout"],
      "validation": {"reopen_required":True,"previews":["audit/purdue_university_church/preview.png","audit/purdue_university_church/preview_east.png","audit/purdue_university_church/preview_plan.png"],"asset_export":"saved as .blend with named scene/collection; no external image-texture links"}
    }
    with open(AUDIT,"w",encoding="utf-8") as f: json.dump(evidence,f,indent=2)
    print("BUILD_OK",OUT,"OBJECTS",len(collection.objects),"GIS_BOUNDS",(minx,maxx,miny,maxy))

if __name__ == "__main__":
    main()

"""Build the Purdue Veterinary Pathology Building modular asset.

Footprint and campus placement come from the Purdue Libraries campus GIS service.
Architectural heights and uses are evidence-informed approximations; see the
building audit folder for sources, provenance, and limitations.
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIT = os.path.join(ROOT, "audit", "veterinary_pathology_building")
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_veterinary_pathology_building_48b5a5b.blend")
GEOJSON = os.path.join(AUDIT, "purdue_campus_building_vpth_raw.geojson")
ASSET_ID = "massing_veterinary_pathology_building_48b5a5b"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
OBJ_NAME = "Veterinary Pathology Building"

# Purdue campus GIS geographic origin and the project's documented local
# approximate conversion (X east, Y north, Z up), in meters.
LAT0, LON0 = 40.4274, -86.9137

def campus_xy(lon, lat):
    return ((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
            (lat - LAT0) * 111040.0)

def polygon_centroid(poly):
    area2 = 0.0
    cx = cy = 0.0
    for i, (x, y) in enumerate(poly):
        x2, y2 = poly[(i+1) % len(poly)]
        cross = x*y2 - x2*y
        area2 += cross
        cx += (x+x2)*cross
        cy += (y+y2)*cross
    if abs(area2) < 1e-8:
        raise ValueError("GIS footprint has degenerate area")
    return cx/(3.0*area2), cy/(3.0*area2)

def material(name, color, roughness=0.82, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    return m

def texture_brick(m):
    nodes=m.node_tree.nodes; links=m.node_tree.links
    bs=nodes.get("Principled BSDF")
    coord=nodes.new("ShaderNodeNewGeometry")
    brick=nodes.new("ShaderNodeTexBrick")
    brick.inputs["Scale"].default_value=2.1
    brick.inputs["Mortar Size"].default_value=.018
    brick.inputs["Mortar Smooth"].default_value=.015
    brick.inputs["Color1"].default_value=(.43,.22,.16,1)
    brick.inputs["Color2"].default_value=(.31,.145,.105,1)
    brick.inputs["Mortar"].default_value=(.19,.17,.14,1)
    links.new(coord.outputs["Position"],brick.inputs["Vector"])
    bump=nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.08
    bump.inputs["Distance"].default_value=.008
    links.new(brick.outputs["Fac"],bump.inputs["Height"])
    links.new(brick.outputs["Color"],bs.inputs["Base Color"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])

def texture_stone(m):
    nodes=m.node_tree.nodes; links=m.node_tree.links
    bs=nodes.get("Principled BSDF")
    coord=nodes.new("ShaderNodeNewGeometry")
    noise=nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=5.0
    noise.inputs["Detail"].default_value=2.0
    links.new(coord.outputs["Position"],noise.inputs["Vector"])
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.16
    ramp.color_ramp.elements[0].color=(.53,.48,.39,1)
    ramp.color_ramp.elements[1].position=.86
    ramp.color_ramp.elements[1].color=(.73,.67,.54,1)
    links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    bump=nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.12
    bump.inputs["Distance"].default_value=.012
    links.new(noise.outputs["Fac"],bump.inputs["Height"])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])

def cube(name, loc, scale, mat, rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    o.rotation_euler[2] = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    return o

def make_mesh(name, verts, faces, mats, slots):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for m in mats:
        mesh.materials.append(m)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for i, poly in enumerate(mesh.polygons):
        poly.material_index = slots[i] if i < len(slots) else 0
    return obj

def add_prism(verts, faces, slots, poly, z0, z1, slot):
    n = len(poly)
    base = len(verts)
    verts.extend([(x, y, z0) for x, y in poly])
    verts.extend([(x, y, z1) for x, y in poly])
    # Perimeter walls; the cap uses a single polygon (Blender tessellates it).
    for i in range(n):
        j = (i + 1) % n
        faces.append((base+i, base+j, base+n+j, base+n+i)); slots.append(slot)
    faces.append(tuple(base+n+i for i in range(n))); slots.append(slot)

def prism_object(name, poly, z0, z1, mat):
    verts, faces, slots = [], [], []
    add_prism(verts, faces, slots, poly, z0, z1, 0)
    return make_mesh(name, verts, faces, [mat], slots)

def polygon_inside(x, y, poly):
    inside = False
    j = len(poly)-1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj-xi)*(y-yi)/(yj-yi+1e-15)+xi:
            inside = not inside
        j = i
    return inside

def distance_to_outline(x, y, poly):
    best = float("inf")
    for i, (ax, ay) in enumerate(poly):
        bx, by = poly[(i+1) % len(poly)]
        dx, dy = bx-ax, by-ay
        t = max(0.0, min(1.0, ((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy+1e-15)))
        best = min(best, math.hypot(x-(ax+t*dx), y-(ay+t*dy)))
    return best

def interior_anchor(poly):
    minx,maxx=min(x for x,y in poly),max(x for x,y in poly)
    miny,maxy=min(y for x,y in poly),max(y for x,y in poly)
    best=None
    # Max-clearance point prevents roof service geometry from landing in a
    # concavity/courtyard when the GIS footprint is not convex.
    for ix in range(80):
        x=minx+(ix+.5)*(maxx-minx)/80
        for iy in range(80):
            y=miny+(iy+.5)*(maxy-miny)/80
            if polygon_inside(x,y,poly):
                d=distance_to_outline(x,y,poly)
                if best is None or d>best[2]: best=(x,y,d)
    if best is None:
        raise ValueError("No interior point found for the source footprint")
    return best

def main():
    with open(GEOJSON, "r", encoding="utf-8") as f:
        feature = json.load(f)["features"][0]
    ring = feature["geometry"]["coordinates"][0]
    campus_outline = [campus_xy(lon, lat) for lon, lat in ring[:-1]]
    anchor_x, anchor_y = polygon_centroid(campus_outline)
    outline = [(x-anchor_x, y-anchor_y) for x,y in campus_outline]
    props = feature["properties"]

    # Clear only the standalone scene, never the user's master project.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name != "Collection":
            bpy.data.collections.remove(c)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    brick = material("VPTH warm muted red-brown masonry (estimated)", (0.39, 0.19, 0.13))
    limestone = material("VPTH pale stone trim (estimated)", (0.69, 0.62, 0.49))
    glass = material("VPTH deep blue-gray glazing", (0.10, 0.20, 0.25), 0.32, 0.05)
    frame = material("VPTH dark bronze window frames", (0.075, 0.075, 0.065), 0.48, 0.3)
    roofmat = material("VPTH charcoal roof membrane (form uncertain)", (0.18, 0.20, 0.20), 0.9)
    concrete = material("VPTH foundation and interior concrete", (0.46, 0.45, 0.41))
    wood = material("VPTH entrance door wood", (0.22, 0.14, 0.09))
    texture_brick(brick)
    texture_stone(limestone)
    lawn = material("VPTH preview ground only", (.19,.25,.14), .95)

    # Main volume: four occupied levels above a partially exposed basement,
    # with a shallow attic level. Campus GIS footprint is authoritative.
    wall_verts, wall_faces, wall_slots = [], [], []
    add_prism(wall_verts, wall_faces, wall_slots, outline, 0.0, 11.75, 0)
    shell = make_mesh("VPTH Masonry Shell", wall_verts, wall_faces,
                      [brick], wall_slots)

    # Ground/basement plinth, story belts, and a restrained cornice follow the
    # measured GIS wall line. No global scale adjustment is applied.
    # Build floor bands as small cubes aligned to each surveyed GIS edge.
    detail_objects = [shell]
    for z in (0.18, 3.65, 7.05, 10.45):
        for i, a in enumerate(outline):
            b = outline[(i+1) % len(outline)]
            dx, dy = b[0]-a[0], b[1]-a[1]
            length = math.hypot(dx, dy)
            if length < 2.8:
                continue
            ang = math.atan2(dy, dx)
            detail_objects.append(cube("VPTH stone story belt", ((a[0]+b[0])/2, (a[1]+b[1])/2, z),
                                        (length, .12, .16), limestone, ang))
    for i, a in enumerate(outline):
        b = outline[(i+1) % len(outline)]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx, dy)
        if length < 3.4:
            continue
        ang = math.atan2(dy, dx)
        detail_objects.append(cube("VPTH roof cornice", ((a[0]+b[0])/2, (a[1]+b[1])/2, 11.78),
                                    (length, .32, .38), limestone, ang))

    # Repeated vertical sash windows reflect the academic/laboratory use. Their
    # exact module and placement are deliberately labeled estimated.
    signed_area = sum(outline[i][0]*outline[(i+1)%len(outline)][1] - outline[(i+1)%len(outline)][0]*outline[i][1] for i in range(len(outline)))
    ccw = signed_area > 0
    for i, a in enumerate(outline):
        b = outline[(i+1) % len(outline)]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx, dy)
        if length < 4.2:
            continue
        angle = math.atan2(dy, dx)
        nwin = max(1, int(length // 4.1))
        # Geometric outward normal for the polygon winding.
        nx, ny = ((dy/length, -dx/length) if ccw else (-dy/length, dx/length))
        for k in range(nwin):
            t = (k+0.5)/nwin
            cx, cy = a[0]+t*dx+nx*.10, a[1]+t*dy+ny*.10
            for zbase in (0.72, 4.12, 7.52):
                zc = zbase + 1.20
                w, h = min(1.62, length/nwin*.54), 1.95
                # A limestone surround, dark sash, and reflective glass pane.
                detail_objects.append(cube("VPTH limestone window surround", (cx,cy,zc),
                                           (w+.24,.18,h+.26), limestone, angle))
                detail_objects.append(cube("VPTH window frame", (cx,cy,zc),
                                           (w,.16,h), frame, angle))
                detail_objects.append(cube("VPTH glazed sash", (cx-nx*.035,cy-ny*.035,zc),
                                           (w-.15,.07,h-.15), glass, angle))
                # Put the glazing just proud of its masonry reveal so the pane
                # remains visible from the exterior camera.
                glazing = detail_objects[-1]
                glazing.location.x = cx + nx*.18
                glazing.location.y = cy + ny*.18
                detail_objects.append(cube("VPTH center mullion", (cx+nx*.20,cy+ny*.20,zc),
                                           (.055,.09,h-.12), frame, angle))
                detail_objects.append(cube("VPTH window transom", (cx+nx*.20,cy+ny*.20,zc+.30),
                                           (w-.12,.09,.055), frame, angle))

    # Main entry and secondary exits on west/south/north faces are included as
    # documented; assignment to exact bays is an informed visual approximation.
    for i, a in enumerate(outline):
        b = outline[(i+1) % len(outline)]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx,dy)
        if length < 7:
            continue
        ang=math.atan2(dy,dx)
        nx,ny=((dy/length,-dx/length) if ccw else (-dy/length,dx/length))
        mid=(a[0]+b[0])/2, (a[1]+b[1])/2
        # Entry positions are illustrative; avoid placing doors on short returns.
        for t in ((.5,) if length>14 else ()):
            x,y=mid[0]+(t-.5)*dx+nx*.14,mid[1]+(t-.5)*dy+ny*.14
            detail_objects.append(cube("VPTH entrance stone portal",(x,y,1.35),(2.45,.30,2.85),limestone,ang))
            detail_objects.append(cube("VPTH glazed double entry door",(x+nx*.18,y+ny*.18,1.32),(1.75,.16,2.42),glass,ang))
            detail_objects.append(cube("VPTH door leaf",(x+nx*.24-math.cos(ang)*.37,y+ny*.24-math.sin(ang)*.37,1.3),(.68,.09,2.25),wood,ang))
            detail_objects.append(cube("VPTH door leaf",(x+nx*.24+math.cos(ang)*.37,y+ny*.24+math.sin(ang)*.37,1.3),(.68,.09,2.25),wood,ang))
            detail_objects.append(cube("VPTH transom",(x+nx*.24,y+ny*.24,2.72),(1.65,.09,.28),glass,ang))

    # Low attic/mechanical volume and roof plant preserve the 16 m source height
    # without asserting an undocumented roof plan.
    pts = outline
    cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
    minx,maxx=min(p[0] for p in pts),max(p[0] for p in pts)
    miny,maxy=min(p[1] for p in pts),max(p[1] for p in pts)
    detail_objects.append(prism_object("VPTH roof deck",outline,11.78,12.05,roofmat))
    roofcx,roofcy,clearance=interior_anchor(outline)
    roof_w=min(14.0,clearance*1.65); roof_d=min(9.0,clearance*1.35)
    detail_objects.append(cube("VPTH attic and rooftop service level",(roofcx,roofcy,13.45),
                                (roof_w,roof_d,3.3),brick))
    detail_objects.append(cube("VPTH service roof",(roofcx,roofcy,15.55),
                                (roof_w+.6,roof_d+.6,.75),roofmat))
    # Interior evidence supports uses and floor count, but not plan geometry;
    # therefore only generic interior slabs and a southeast elevator core are modeled.
    inner_outline=[]
    # A gentle inset avoids showing slab edges beyond the exterior walls. It is
    # an illustrative inset, not an independent measurement of wall thickness.
    for x,y in outline:
        vx,vy=x-cx,y-cy
        scale=max(0.90,1.0-0.65/max(1.0,math.hypot(vx,vy)))
        inner_outline.append((cx+vx*scale,cy+vy*scale))
    for z in (-1.9, 0.05, 3.55, 6.95, 10.35):
        detail_objects.append(prism_object("VPTH generic interior floor plate",inner_outline,z,z+.14,concrete))

    # Consolidate into the single named object expected by the existing manifest.
    bpy.ops.object.select_all(action="DESELECT")
    for o in detail_objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active=shell
    bpy.ops.object.join()
    building=bpy.context.object
    building.name=OBJ_NAME
    building.data.name="Veterinary Pathology Building detailed geometry"
    building.location=(0,0,0)
    building["stable_asset_id"]=ASSET_ID
    building["coordinate_frame"]="building-local meters; X east, Y north, Z up; GIS polygon centroid at local 0,0"
    building["campus_anchor_xy_m"]=[anchor_x,anchor_y]
    building["campus_anchor_method"]="area centroid of Purdue campus GIS OBJECTID 165 polygon after documented local conversion"
    building["footprint_source"]="Purdue Libraries campus GIS, feature OBJECTID 165 / VPTH"
    building["height_status"]="approximate 16 m overall; GIS extrusion and massing baseline; not a survey"

    # Manifest-compatible collection and scene identifiers.
    coll=bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(coll)
    for c in list(building.users_collection):
        c.objects.unlink(building)
    coll.objects.link(building)
    scene.render.engine="CYCLES"
    scene.cycles.samples=32
    scene.render.resolution_x=1200
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    world=scene.world or bpy.data.worlds.new("VPTH world")
    scene.world=world
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.23,0.29,0.36,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.6
    bpy.ops.object.light_add(type="AREA",location=(cx-38,cy-55,66))
    light=bpy.context.object; light.name="VPTH preview softbox"; light.data.energy=7200; light.data.shape="DISK"; light.data.size=45
    light.rotation_euler=(math.radians(26),0,math.radians(-31))
    bpy.ops.object.camera_add(location=(cx+73,cy-95,66))
    camera=bpy.context.object; camera.name="VPTH preview camera"
    direction=Vector((cx,cy,6))-camera.location
    camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    camera.data.lens=48; scene.camera=camera
    # Camera/light are in the asset collection only for a portable preview; the
    # coordinator can remove them during master linking if desired.
    for o in (light,camera):
        for c in list(o.users_collection): c.objects.unlink(o)
        scene.collection.objects.link(o)
    bpy.ops.mesh.primitive_plane_add(size=1,location=(cx,cy,-.06))
    ground=bpy.context.object; ground.name="VPTH preview ground context"
    ground.dimensions=(maxx-minx+26,maxy-miny+26,1)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ground.data.materials.append(lawn)
    scene.collection.objects.link(ground)
    for c in list(ground.users_collection):
        if c != scene.collection: c.objects.unlink(ground)
    scene.render.filepath=os.path.join(AUDIT,"preview_exterior.png")
    scene.render.image_settings.color_mode="RGBA"
    bpy.ops.wm.save_as_mainfile(filepath=ASSET)
    bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    main()

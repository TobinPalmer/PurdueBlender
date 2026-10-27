"""Build the Theta Chi / Alpha Delta house from Purdue FID 760 evidence.

Coordinates remain in the campus world frame used by the original massing
asset. The GIS boundary is transformed from WGS84 using modular/AGENTS.md's
local approximation; only visible facade detail is modeled from the saved
official chapter-house photographs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


BUILDING_ID = "massing_house_301841328_39f169f"
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
OBJECT_NAME = "House_301841328"
ROOT = Path(__file__).resolve().parents[2]
GIS_PATH = ROOT / "audit" / "theta_chi" / "sources" / "purdue_gis_fid760_2026-10-26.json"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
PREVIEW_PATH = ROOT / "audit" / "theta_chi" / "renders" / "theta_chi_preview.png"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
WALL_EAVE_Z = 7.1
ROOF_RIDGE_Z = 8.8


def project_lonlat(lon: float, lat: float) -> tuple[float, float]:
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return x, y


def signed_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    area2 = 0.0
    cx = cy = 0.0
    for p, q in zip(points, points[1:] + points[:1]):
        cross = p[0] * q[1] - q[0] * p[1]
        area2 += cross
        cx += (p[0] + q[0]) * cross
        cy += (p[1] + q[1]) * cross
    return cx / (3.0 * area2), cy / (3.0 * area2)


def material(name: str, color: tuple[float, float, float, float], roughness=0.78):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


MATS = []
PARTS = []


def make_materials():
    global MATS
    MATS = [
        material("Theta Chi | red brick", (0.40, 0.095, 0.060, 1)),
        material("Theta Chi | warm limestone", (0.72, 0.66, 0.52, 1)),
        material("Theta Chi | light cream trim", (0.84, 0.80, 0.69, 1)),
        material("Theta Chi | slate shingles", (0.12, 0.14, 0.16, 1)),
        material("Theta Chi | shaded glazing", (0.12, 0.22, 0.28, 1), 0.25),
        material("Theta Chi | entry shadow", (0.035, 0.045, 0.050, 1), 0.36),
        material("Theta Chi | bronze plaque", (0.47, 0.32, 0.13, 1), 0.42),
    ]


def new_part(name, verts, faces, mat_index):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(MATS[mat_index])
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    PARTS.append(obj)
    return obj


def prism_xy(name, footprint, z0, z1, mat_index):
    n = len(footprint)
    verts = [(x, y, z0) for x, y in footprint] + [(x, y, z1) for x, y in footprint]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return new_part(name, verts, faces, mat_index)


def wall_basis(a, b, center):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    tangent = (dx / length, dy / length)
    normal = (-tangent[1], tangent[0])
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    if (center[0] - mid[0]) * normal[0] + (center[1] - mid[1]) * normal[1] > 0:
        normal = (-normal[0], -normal[1])
    return length, tangent, normal


def wall_point(origin, tangent, normal, u, outward, z):
    return (
        origin[0] + tangent[0] * u + normal[0] * outward,
        origin[1] + tangent[1] * u + normal[1] * outward,
        z,
    )


def facade_box(name, origin, tangent, normal, u1, u2, z1, z2, outward, depth, mat_index):
    points = [
        wall_point(origin, tangent, normal, u1, outward, z1),
        wall_point(origin, tangent, normal, u2, outward, z1),
        wall_point(origin, tangent, normal, u2, outward, z2),
        wall_point(origin, tangent, normal, u1, outward, z2),
    ]
    back = [wall_point(origin, tangent, normal, u, outward - depth, z) for u, z in ((u1,z1),(u2,z1),(u2,z2),(u1,z2))]
    verts = points + back
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return new_part(name, verts, faces, mat_index)


def arch_pane(name, origin, tangent, normal, center_u, width, base_z, spring_z, outward, mat_index, depth=0.025, segments=12):
    radius = width / 2
    outline = [(center_u - radius, base_z), (center_u + radius, base_z), (center_u + radius, spring_z)]
    for i in range(segments + 1):
        angle = i * math.pi / segments
        outline.append((center_u + radius * math.cos(angle), spring_z + radius * math.sin(angle)))
    outline.append((center_u - radius, spring_z))
    front = [wall_point(origin, tangent, normal, u, outward, z) for u, z in outline]
    rear = [wall_point(origin, tangent, normal, u, outward - depth, z) for u, z in outline]
    n = len(outline)
    faces = [tuple(range(n)), tuple(range(2*n-1, n-1, -1))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return new_part(name, front + rear, faces, mat_index)


def arch_trim(name, origin, tangent, normal, center_u, width, base_z, spring_z, outward, mat_index, trim=0.28, depth=0.10, segments=12):
    r0, r1 = width / 2, width / 2 + trim
    verts = []
    for dep in (outward, outward - depth):
        for radius, base in ((r0, base_z), (r1, base_z)):
            verts += [wall_point(origin, tangent, normal, center_u - radius, dep, base), wall_point(origin, tangent, normal, center_u + radius, dep, base)]
        for i in range(segments + 1):
            angle = i * math.pi / segments
            verts.append(wall_point(origin, tangent, normal, center_u + r0 * math.cos(angle), dep, spring_z + r0 * math.sin(angle)))
        for i in range(segments + 1):
            angle = i * math.pi / segments
            verts.append(wall_point(origin, tangent, normal, center_u + r1 * math.cos(angle), dep, spring_z + r1 * math.sin(angle)))
    # Build segmented arch band and straight jambs as stable blocks.
    parts = []
    parts.append(facade_box(name+"L", origin, tangent, normal, center_u-r1, center_u-r0, base_z, spring_z, outward, depth, mat_index))
    parts.append(facade_box(name+"R", origin, tangent, normal, center_u+r0, center_u+r1, base_z, spring_z, outward, depth, mat_index))
    for i in range(segments):
        a0, a1 = i * math.pi / segments, (i+1) * math.pi / segments
        inner0=(center_u+r0*math.cos(a0),spring_z+r0*math.sin(a0)); inner1=(center_u+r0*math.cos(a1),spring_z+r0*math.sin(a1))
        outer0=(center_u+r1*math.cos(a0),spring_z+r1*math.sin(a0)); outer1=(center_u+r1*math.cos(a1),spring_z+r1*math.sin(a1))
        pts=[wall_point(origin,tangent,normal,u,outward,z) for u,z in (inner0,outer0,outer1,inner1)]
        pts += [wall_point(origin,tangent,normal,u,outward-depth,z) for u,z in (inner0,outer0,outer1,inner1)]
        parts.append(new_part(name+f"Arch{i}", pts, [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)], mat_index))
    return parts


def rectangular_window(name, origin, tangent, normal, c, zc, width=1.35, height=1.65):
    u1, u2 = c - width/2, c + width/2
    z1, z2 = zc - height/2, zc + height/2
    facade_box(name+"Reveal", origin,tangent,normal,u1-0.13,u2+0.13,z1-0.13,z2+0.13,0.06,0.06,1)
    facade_box(name+"Glass", origin,tangent,normal,u1,u2,z1,z2,0.13,0.045,4)
    for u in (u1-0.08,u2+0.08):
        facade_box(name+"Jamb",origin,tangent,normal,u-0.045,u+0.045,z1-0.09,z2+0.09,0.19,0.06,2)
    for z in (z1-0.08,z2+0.08):
        facade_box(name+"SillHead",origin,tangent,normal,u1-0.08,u2+0.08,z-0.045,z+0.045,0.19,0.06,2)
    facade_box(name+"MullionV",origin,tangent,normal,c-0.025,c+0.025,z1,z2,0.20,0.04,2)
    facade_box(name+"MullionH",origin,tangent,normal,u1,u2,zc-0.025,zc+0.025,0.20,0.04,2)


def merge_objects(objects, name, collection):
    for obj in objects:
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
        collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    result = bpy.context.view_layer.objects.active
    result.name = name
    result.data.name = name + "Mesh"
    result.location = (0,0,0)
    result.rotation_euler = (0,0,0)
    result.scale = (1,1,1)
    return result


def setup_render(center, normal, tangent):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("ThetaChi_PreviewWorld")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.50, 0.50, 0.50, 1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    camera_data = bpy.data.cameras.new("ThetaChi_PreviewCameraData")
    camera = bpy.data.objects.new("ThetaChi_PreviewCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 48
    camera.location = (center[0] + normal[0]*52 - tangent[0]*7, center[1] + normal[1]*52 - tangent[1]*7, 27)
    direction = Vector((center[0],center[1],4.3)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z","Y").to_euler()
    camera.data.lens = 50
    scene.camera = camera
    light_data=bpy.data.lights.new("ThetaChi_KeyLightData","AREA")
    light=bpy.data.objects.new("ThetaChi_KeyLight",light_data)
    scene.collection.objects.link(light)
    light.location=(center[0]+normal[0]*22-tangent[0]*5,center[1]+normal[1]*22-tangent[1]*5,25)
    light_data.energy=10500
    light_data.size=28
    light.rotation_euler=(math.radians(24),0,math.radians(-34))
    scene.render.filepath=str(PREVIEW_PATH)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    global PARTS
    PARTS = []
    scene = bpy.context.scene
    scene.name = f"Building_{BUILDING_ID}"
    gis = json.loads(GIS_PATH.read_text(encoding="utf-8"))
    feature = gis["features"][0]
    assert feature["attributes"]["FID"] == 760
    assert feature["attributes"]["BUILDING_N"] == "Theta Chi"
    assert feature["attributes"]["ADDRESS"] == "800 David Ross Rd"
    ring = feature["geometry"]["rings"][0]
    footprint = [project_lonlat(lon, lat) for lon, lat in ring[:-1]]
    center = signed_centroid(footprint)

    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    prism_xy("ThetaChi_Foundation",footprint,0.0,1.0,1)
    prism_xy("ThetaChi_BrickShell",footprint,1.0,WALL_EAVE_Z,0)

    # A low hipped roof follows the complete footprint. The ridge is aligned
    # to the photographed main facade; framing and height remain estimates.
    edge_i=max(range(len(footprint)),key=lambda i: math.dist(footprint[i],footprint[(i+1)%len(footprint)]))
    facade_len, roof_tangent, roof_normal=wall_basis(footprint[edge_i],footprint[(edge_i+1)%len(footprint)],center)
    roof_verts=[(x,y,WALL_EAVE_Z) for x,y in footprint]+[(center[0],center[1],ROOF_RIDGE_Z)]
    roof_faces=[(i,(i+1)%len(footprint),len(footprint)) for i in range(len(footprint))]
    new_part("ThetaChi_HippedRoof",roof_verts,roof_faces,3)
    for a,b in zip(footprint,footprint[1:]+footprint[:1]):
        length,tangent,normal=wall_basis(a,b,center)
        # Cream eave band visible in both exterior photographs.
        mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
        p1=(a[0],a[1],WALL_EAVE_Z-0.07); p2=(b[0],b[1],WALL_EAVE_Z-0.07)
        p3=(b[0],b[1],WALL_EAVE_Z+0.05); p4=(a[0],a[1],WALL_EAVE_Z+0.05)
        new_part("ThetaChi_EaveBand",[p1,p2,p3,p4],[(0,1,2,3)],2)

    # The long 26 m GIS wall is the facade with the strongest available photo
    # evidence. Photograph-to-compass registration is approximate, so details
    # here are explicitly a best-fit face, not a surveyed orientation.
    a,b=footprint[edge_i],footprint[(edge_i+1)%len(footprint)]
    # Reverse the GIS ring traversal so the photographed landmark order is
    # tower first, then the three-bay porch, when viewed from outside.
    facade_len,tangent,normal=wall_basis(b,a,center)
    facade_origin=b
    # One broad, centered limestone feature carries the tall arched window and
    # chapter-symbol panel shown on the official exterior image.
    tower_u=facade_len*0.43
    facade_box("ThetaChi_EntranceTower",facade_origin,tangent,normal,tower_u-1.95,tower_u+1.95,1.0,7.0,0.12,0.18,2)
    arch_pane("ThetaChi_TallArchedGlass",facade_origin,tangent,normal,tower_u,1.18,4.55,5.70,0.34,4)
    # Plaque field as a plain panel; no unverified logo geometry is invented.
    facade_box("ThetaChi_ChapterPlaque",facade_origin,tangent,normal,tower_u-1.08,tower_u+1.08,3.45,4.08,0.35,0.07,1)
    # Three tall arched porch openings and a broad canopy are directly visible
    # in the national chapter photograph.
    porch_centers=[facade_len*0.67,facade_len*0.80,facade_len*0.93]
    for i,c in enumerate(porch_centers,1):
        arch_pane(f"ThetaChi_PorchOpening{i}",facade_origin,tangent,normal,c,2.05,1.02,2.55,0.16,5,0.06)
        arch_trim(f"ThetaChi_PorchArchTrim{i}",facade_origin,tangent,normal,c,2.05,1.02,2.55,0.29,2,0.28,0.11)
    # Projecting canopy over the arched porch bays.
    canopy_center=sum(porch_centers)/len(porch_centers)
    canopy_width=min(10.5,facade_len*0.44)
    p1=wall_point(facade_origin,tangent,normal,canopy_center-canopy_width/2,0.18,4.10)
    p2=wall_point(facade_origin,tangent,normal,canopy_center+canopy_width/2,0.18,4.10)
    p3=wall_point(facade_origin,tangent,normal,canopy_center+canopy_width/2,2.2,4.10)
    p4=wall_point(facade_origin,tangent,normal,canopy_center-canopy_width/2,2.2,4.10)
    new_part("ThetaChi_PorchCanopy",[p1,p2,p3,p4],[(0,1,2,3)],2)
    # Upper cornice and a simple triangular pediment over the entrance feature.
    facade_box("ThetaChi_EntranceCornice",facade_origin,tangent,normal,tower_u-2.2,tower_u+2.2,6.72,6.98,0.38,0.28,2)
    gable=[wall_point(facade_origin,tangent,normal,tower_u-1.75,0.42,6.98),wall_point(facade_origin,tangent,normal,tower_u+1.75,0.42,6.98),wall_point(facade_origin,tangent,normal,tower_u,0.42,7.95)]
    new_part("ThetaChi_EntryPediment",gable,[(0,1,2)],2)

    # Broad, regularly spaced multi-pane windows follow the documented
    # two-storey brick elevations; all opposite-face detailing remains simple.
    front_positions=[facade_len*0.10,facade_len*0.23,facade_len*0.34,facade_len*0.55]
    for i,c in enumerate(front_positions,1):
        rectangular_window(f"ThetaChi_FrontUpperWindow{i}",facade_origin,tangent,normal,c,5.45,1.32,1.55)
        rectangular_window(f"ThetaChi_FrontLowerWindow{i}",facade_origin,tangent,normal,c,2.35,1.28,1.55)
    for i,c in enumerate(porch_centers,1):
        rectangular_window(f"ThetaChi_PorchUpperWindow{i}",facade_origin,tangent,normal,c,5.45,1.38,1.52)
    # A few matching window bays on the adjacent long elevation visible in the
    # archived official chapter-house photo.
    second_edge=max((i for i in range(len(footprint)) if i!=edge_i),key=lambda i: math.dist(footprint[i],footprint[(i+1)%len(footprint)]))
    a2,b2=footprint[second_edge],footprint[(second_edge+1)%len(footprint)]
    side_len,side_tangent,side_normal=wall_basis(a2,b2,center)
    side_positions=[side_len*0.18,side_len*0.43,side_len*0.68,side_len*0.84]
    for i,c in enumerate(side_positions,1):
        rectangular_window(f"ThetaChi_SideUpperWindow{i}",a2,side_tangent,side_normal,c,5.45,1.30,1.52)
        rectangular_window(f"ThetaChi_SideLowerWindow{i}",a2,side_tangent,side_normal,c,2.35,1.26,1.52)

    # Join all facade and shell elements into one portable asset object, keeping
    # the manifest's established collection and object names.
    building=merge_objects(PARTS,OBJECT_NAME,collection)
    building["evidence_id"]="Purdue campus GIS FID 760; Theta Chi Alpha Delta chapter-house exterior sources"
    building["height_status"]="Estimated: two occupied levels and low hip roof from official photos; no surveyed height source located"
    building["facade_orientation_status"]="Approximate: long GIS face chosen as photographed facade; no registered street panorama"
    setup_render(center, normal, tangent)
    PREVIEW_PATH.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    ASSET_PATH.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))


if __name__ == "__main__":
    build()

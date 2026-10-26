"""Build the Rossen-assigned 2025 Pete Dye Clubhouse asset.

The footprint is the OSM way 1319175917 from the project's Overpass snapshot
(2026-10-22), which coincides with the existing FID 545 massing polygon to
under 0.0001 m. Exterior form is reconstructed from the CE Solutions portfolio
photographs. Overall two-story program is documented by Purdue Administrative
Operations; roof and facade dimensions are estimates because published plans
or elevations were not located.

Run from the repository root with Blender 4.5:
  blender -b modular/buildings/massing_the_pete_dye_clubhouse_a3a9641.blend \
    --python modular/buildings/build_massing_the_pete_dye_clubhouse_a3a9641.py
"""

import bpy
import math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_the_pete_dye_clubhouse_a3a9641.blend"
AUDIT = ROOT / "audit/massing_the_pete_dye_clubhouse_a3a9641"
PREVIEW = AUDIT / "preview"
ID = "massing_the_pete_dye_clubhouse_a3a9641"
COLLECTION_NAME = "Asset_" + ID
SCENE_NAME = "Building_" + ID


def material(name, color, roughness=0.65, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def mesh_obj(name, verts, faces, mat, collection, bevel=0.0):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if bevel:
        mod = obj.modifiers.new("Fine edge highlights", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def cube(name, center, dims, mat, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = CURRENT_YAW
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def setup():
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    # The original massing or this script's prior foundation stores the exact
    # georeferenced outline in its first four mesh vertices.
    source = bpy.data.objects.get("The Pete Dye Clubhouse")
    if source is None:
        source = bpy.data.objects.get("PDC structural foundation footprint")
    if source is None or source.type != "MESH" or len(source.data.vertices) < 4:
        raise RuntimeError("FID 545 source or saved foundation polygon was not found")
    world_poly = [Vector(v.co) + source.location for v in source.data.vertices[:4]]
    world_poly = [Vector((p.x, p.y, 0.0)) for p in world_poly]
    for c in list(source.users_collection):
        c.objects.unlink(source)
    bpy.data.objects.remove(source, do_unlink=True)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(collection)
    else:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.22, 0.25, 0.28, 1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.35
    return scene, collection, world_poly


def create_building(scene, collection, poly):
    # Perpendicular unit axes from the observed footprint. U is the long facade.
    a, b, c, d = poly
    center = sum(poly, Vector((0, 0, 0))) / 4.0
    uvec = ((c - b) + (d - a)) / 2.0
    vvec = ((b - a) + (c - d)) / 2.0
    udir, vdir = uvec.normalized(), vvec.normalized()
    uh = (uvec.length + ((c - b) + (d - a)).length / 2.0) / 4.0
    vh = (vvec.length + ((b - a) + (c - d)).length / 2.0) / 4.0
    global CURRENT_YAW
    CURRENT_YAW = math.atan2(udir.y, udir.x)

    def p(u, v, z):
        q = center + udir * u + vdir * v
        return (q.x, q.y, z)

    stone = material("PDC warm limestone and sandstone", (0.39, 0.285, 0.16), 0.86)
    pale_stone = material("PDC light stone trim", (0.53, 0.43, 0.29), 0.82)
    dark = material("PDC charcoal metal", (0.025, 0.032, 0.04), 0.48, 0.25)
    roofmat = material("PDC slate gray roof", (0.045, 0.055, 0.068), 0.62, 0.16)
    glass = material("PDC blue gray glazing", (0.025, 0.075, 0.105), 0.26, 0.25)
    door_mat = material("PDC dark bronze entrance", (0.09, 0.105, 0.105), 0.35, 0.35)
    concrete = material("PDC foundation concrete", (0.40, 0.41, 0.40), 0.82)

    # Retain the source polygon exactly; only roof eaves and terrace are allowed
    # to overhang, and those are architectural projections rather than footprint.
    mesh_obj("PDC structural foundation footprint", [tuple((q.x, q.y, 0.0)) for q in poly] +
             [tuple((q.x, q.y, 0.38)) for q in poly],
             [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2),
              (2, 6, 7, 3), (3, 7, 4, 0)], concrete, collection)

    # Story masses follow the full source wall perimeter. The lower floor is
    # stone; the upper floor alternates stone piers and dark window bays.
    for name, z0, z1, mat in (("PDC ground story stone shell", 0.38, 4.35, stone),
                              ("PDC upper story stone shell", 4.35, 8.55, pale_stone)):
        verts = [p(-uh, -vh, z0), p(uh, -vh, z0), p(uh, vh, z0), p(-uh, vh, z0),
                 p(-uh, -vh, z1), p(uh, -vh, z1), p(uh, vh, z1), p(-uh, vh, z1)]
        faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
                 (7, 6, 5, 4)]
        mesh_obj(name, verts, faces, mat, collection)

    # Ground and upper facade glazing on the course-facing broad side.
    front_v = -vh - 0.045
    back_v = vh + 0.045
    # Irregular storefront and dining bays inferred from the portfolio views.
    # The course elevation has broad paired openings, a narrow dark bay, and
    # varied upper windows; the parking elevation is quieter and more solid.
    facade_bays = {
        "course": [(-17.4, 2.5, 0.9, 3.8, 5.1, 7.6),
                   (-12.7, 3.8, 0.8, 3.9, 4.9, 7.9),
                   (-7.9, 2.4, 1.0, 3.8, 5.4, 7.8),
                   (7.6, 3.4, 0.85, 3.9, 4.8, 7.8),
                   (12.4, 2.5, 1.0, 3.85, 5.15, 7.8),
                   (17.2, 3.7, 0.9, 3.8, 4.9, 7.7)],
        "parking": [(-17.0, 2.8, 1.0, 3.7, 5.1, 7.4),
                    (-11.2, 3.1, 1.1, 3.7, 5.2, 7.5),
                    (-5.0, 2.2, 1.0, 3.7, 5.5, 7.4),
                    (6.2, 2.9, 0.95, 3.7, 5.0, 7.5),
                    (13.0, 3.4, 1.0, 3.7, 5.25, 7.6),
                    (18.0, 2.1, 1.0, 3.7, 5.1, 7.4)]}
    for side, vv in (("course", front_v), ("parking", back_v)):
        for i, (u, w, z0, z1, uz0, uz1) in enumerate(facade_bays[side]):
            u0, u1 = max(-uh + 1.1, u - w / 2), min(uh - 1.1, u + w / 2)
            mesh_obj(f"PDC {side} ground glazing {i+1}",
                     [p(u0, vv, z0), p(u1, vv, z0), p(u1, vv, z1), p(u0, vv, z1)],
                     [(0, 1, 2, 3)], glass, collection)
            for xf in (u0, (u0+u1)/2, u1):
                cube(f"PDC {side} ground mullion", p(xf, vv - 0.025, (z0+z1)/2),
                     (0.075, 0.08, z1-z0), dark, collection)
            if side == "course" and i in (1, 3, 5):
                mesh_obj(f"PDC {side} upper glazing {i+1}",
                         [p(u0, vv, uz0), p(u1, vv, uz0), p(u1, vv, uz1), p(u0, vv, uz1)],
                         [(0, 1, 2, 3)], glass, collection)
                for xf in (u0, (u0+u1)/2, u1):
                    cube(f"PDC {side} upper mullion", p(xf, vv - 0.03, (uz0+uz1)/2),
                         (0.07, 0.08, uz1-uz0), dark, collection)
            elif side == "parking" and i in (0, 2, 4):
                mesh_obj(f"PDC {side} upper glazing {i+1}",
                         [p(u0, vv, uz0), p(u1, vv, uz0), p(u1, vv, uz1), p(u0, vv, uz1)],
                         [(0, 1, 2, 3)], glass, collection)

    # Full-height charcoal fins mark the tall vertical window volumes evident
    # in the exterior photographs, breaking the otherwise warm stone facade.
    for u, width in ((-15.2, 0.8), (-9.9, 1.15), (8.9, 0.9), (15.5, 1.0)):
        cube("PDC dark vertical facade volume", p(u, front_v-0.045, 4.4),
             (width, 0.16, 7.7), dark, collection, 0.035)

    # Tall central course-facing glazed gable and the matching course entrance.
    mesh_obj("PDC two-story central gable glass", [p(-5.6, front_v-0.02, 4.4),
             p(5.6, front_v-0.02, 4.4), p(5.6, front_v-0.02, 10.35),
             p(0, front_v-0.02, 15.65), p(-5.6, front_v-0.02, 10.35)],
             [(0, 1, 2, 3, 4)], glass, collection)
    for uu in (-5.6, -3.75, -1.9, 0, 1.9, 3.75, 5.6):
        top = 15.65 - abs(uu) * (5.3/5.6)
        if top > 4.8:
            cube("PDC central gable vertical mullion", p(uu, front_v-0.055, (top+4.4)/2),
                 (0.095, 0.09, top-4.4), dark, collection)
    for z in (7.5, 10.25):
        mesh_obj("PDC central gable horizontal transom", [p(-5.55, front_v-0.06, z),
                 p(5.55, front_v-0.06, z), p(5.55, front_v-0.06, z+0.09),
                 p(-5.55, front_v-0.06, z+0.09)], [(0, 1, 2, 3)], dark, collection)

    # Main double-door entry and restrained stone surround.
    mesh_obj("PDC entrance double doors", [p(-1.45, front_v-0.08, 0.4),
             p(1.45, front_v-0.08, 0.4), p(1.45, front_v-0.08, 3.45),
             p(-1.45, front_v-0.08, 3.45)], [(0,1,2,3)], door_mat, collection)
    cube("PDC entry lintel", p(0, front_v-0.17, 3.56), (3.6, 0.32, 0.22), pale_stone, collection, 0.04)
    for u in (-1.63, 1.63):
        cube("PDC entrance stone pier", p(u, front_v-0.12, 2.15), (0.26, 0.28, 3.55), pale_stone, collection, 0.035)

    # A dominant long slate roof gives the low side wings a continuous shelter.
    # Its ridge is parallel to the long facade, unlike the earlier repeated
    # gable bands. Heights and pitch remain estimates from perspective photos.
    over = 0.5
    main_ridge_z, eave_z = 13.2, 8.55
    roof_u0, roof_u1 = -uh-over, uh+over
    mesh_obj("PDC main roof course slope",
             [p(roof_u0, -vh-over, eave_z), p(roof_u0, 0, main_ridge_z),
              p(roof_u1, 0, main_ridge_z), p(roof_u1, -vh-over, eave_z)],
             [(0,1,2,3)], roofmat, collection)
    mesh_obj("PDC main roof parking slope",
             [p(roof_u0, 0, main_ridge_z), p(roof_u0, vh+over, eave_z),
              p(roof_u1, vh+over, eave_z), p(roof_u1, 0, main_ridge_z)],
             [(0,1,2,3)], roofmat, collection)

    # The central course-facing gable is a taller, projecting cross-gable.
    # Its two roof planes intersect the lower main roof and frame the large
    # triangular glass wall visible in CE Solutions' course-side photographs.
    cg_u, cg_half, cg_peak, cg_eave = -0.4, 6.4, 15.65, 10.05
    cg_front, cg_back = -vh-0.65, -vh+8.6
    mesh_obj("PDC central cross gable left roof", [
             p(cg_u-cg_half, cg_front, cg_eave), p(cg_u, cg_front, cg_peak),
             p(cg_u, cg_back, cg_peak-0.35), p(cg_u-cg_half, cg_back, cg_eave)],
             [(0,1,2,3)], roofmat, collection)
    mesh_obj("PDC central cross gable right roof", [
             p(cg_u, cg_front, cg_peak), p(cg_u+cg_half, cg_front, cg_eave),
             p(cg_u+cg_half, cg_back, cg_eave), p(cg_u, cg_back, cg_peak-0.35)],
             [(0,1,2,3)], roofmat, collection)

    # A lower offset wing projects from the west course end. This short roof
    # intersects the main roof asymmetrically, matching the layered roofline
    # better than evenly spaced repeated longitudinal gables.
    wing_u0, wing_u1 = -uh-0.2, -7.0
    wing_umid = (wing_u0 + wing_u1) / 2
    wing_front, wing_back = -vh-0.9, 0.4
    wing_ridge_z, wing_eave_z = 11.45, 8.25
    mesh_obj("PDC west wing course roof slope", [
             p(wing_u0, wing_front, wing_eave_z), p(wing_umid, wing_front, wing_ridge_z),
             p(wing_umid, wing_back, wing_ridge_z), p(wing_u0, wing_back, wing_eave_z)],
             [(0,1,2,3)], roofmat, collection)
    mesh_obj("PDC west wing parking roof slope", [
             p(wing_umid, wing_front, wing_ridge_z), p(wing_u1, wing_front, wing_eave_z),
             p(wing_u1, wing_back, wing_eave_z), p(wing_umid, wing_back, wing_ridge_z)],
             [(0,1,2,3)], roofmat, collection)

    # Central terrace projecting to the course, based on visible balcony and
    # outdoor dining terrace in the portfolio photos.
    deck_v = -vh - 3.3
    deck_back_v = -vh + 0.15
    mesh_obj("PDC course terrace deck", [p(-8.7, deck_v, 4.25), p(8.7, deck_v, 4.25),
             p(8.7, deck_back_v, 4.25), p(-8.7, deck_back_v, 4.25)], [(0,1,2,3)], dark, collection)
    # dark metal terrace canopy/balustrade rail with 1 m high posts
    for u in [-8.5, -6.0, -3.5, -1.0, 1.5, 4.0, 6.5, 8.5]:
        cube("PDC terrace support or baluster", p(u, deck_v, 4.9), (0.11, 0.12, 1.3), dark, collection)
    cube("PDC terrace front rail", p(0, deck_v, 5.42), (17.2, 0.14, 0.13), dark, collection)
    for vv in (deck_v, deck_back_v):
        for u in (-7.7, 7.7):
            cube("PDC terrace pier", p(u, vv, 2.35), (0.42, 0.42, 4.1), stone, collection, 0.045)

    # Corner stone quoins and dark fascia under the roof eaves.
    for vv in (-vh-0.1, vh+0.1):
        for u in (-uh+0.25, uh-0.25):
            cube("PDC stone corner pier", p(u, vv, 4.35), (0.62, 0.5, 7.9), pale_stone, collection, 0.025)
    # Short dark slab edges articulate the terrace and one upper dining bay;
    # avoid a continuous belt that would flatten the photographed facade.
    cube("PDC terrace fascia", p(0, front_v-0.08, 4.3), (17.8, 0.28, 0.22), dark, collection, 0.025)
    cube("PDC upper bay lintel", p(-12.7, front_v-0.08, 7.95), (4.2, 0.22, 0.18), dark, collection, 0.02)

    # Four vertical end/side windows and downspout-like dark facade accents.
    for side_u in (-uh-0.04, uh+0.04):
        for vv in (-5.1, 0.0, 5.1):
            for z0,z1 in ((1.0,3.75),(5.0,7.85)):
                mesh_obj("PDC side elevation glazing", [p(side_u,vv-1.0,z0),p(side_u,vv+1.0,z0),
                         p(side_u,vv+1.0,z1),p(side_u,vv-1.0,z1)], [(0,1,2,3)], glass, collection)

    # Ensure all geometry is attached only to the assigned collection.
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith("PDC ") and collection not in obj.users_collection:
            for c in list(obj.users_collection):
                c.objects.unlink(obj)
            collection.objects.link(obj)
    return center, udir, vdir, uh, vh


def camera(scene, name, location, target, lens=50):
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    scene.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    scene.camera = cam
    return cam


def render_previews(scene, center, udir, vdir, uh, vh):
    PREVIEW.mkdir(parents=True, exist_ok=True)
    # Keep preview-only cameras and lights out of the saved asset.
    lights = []
    preview_collection = bpy.data.collections.new("PDC Preview Temporary Ground")
    scene.collection.children.link(preview_collection)
    grass = material("PDC preview ground only", (0.10, 0.17, 0.08), 0.94)
    mesh_obj("PDC Preview ground plane",
             [(center.x-150,center.y-150,-0.15),(center.x+150,center.y-150,-0.15),
              (center.x+150,center.y+150,-0.15),(center.x-150,center.y+150,-0.15)],
             [(0,1,2,3)],grass,preview_collection)
    ld = bpy.data.lights.new("PDC Preview softbox", "AREA")
    ld.energy = 18000
    ld.shape = "DISK"
    ld.size = 34
    lo = bpy.data.objects.new("PDC Preview softbox", ld)
    scene.collection.objects.link(lo)
    lo.location = center + Vector((90, -70, 85))
    lo.rotation_euler = (center - lo.location).to_track_quat("-Z", "Y").to_euler()
    lights.append(lo)
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = -0.25
    scene.view_settings.gamma = 1.0
    scene.render.resolution_x, scene.render.resolution_y = 1400, 1000
    # Course-facing three-quarter view.
    eye = center + udir * 49 - vdir * 52 + Vector((0,0,27))
    cam = camera(scene, "PDC Preview camera", eye, center + Vector((0,0,7.5)), 48)
    scene.render.filepath = str(PREVIEW / "course_facing_view.png")
    bpy.ops.render.render(write_still=True)
    # High oblique overview showing massing and intact source polygon.
    overview_target = center + Vector((0,0,7.5))
    cam.location = overview_target + udir*25 - vdir*38 + Vector((0,0,51))
    cam.rotation_euler = (overview_target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 37
    scene.render.filepath = str(PREVIEW / "roof_and_footprint_view.png")
    bpy.ops.render.render(write_still=True)
    # Opposite long elevation for the quieter parking-side massing read.
    side_target = center + Vector((0,0,7.3))
    cam.location = center - udir*43 + vdir*47 + Vector((0,0,24))
    cam.rotation_euler = (side_target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 48
    scene.render.filepath = str(PREVIEW / "parking_side_view.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = None
    camera_data = cam.data
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.collections.remove(preview_collection)
    for light in lights:
        bpy.data.objects.remove(light, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    bpy.data.lights.remove(ld)


def main():
    scene, collection, poly = setup()
    center, udir, vdir, uh, vh = create_building(scene, collection, poly)
    render_previews(scene, center, udir, vdir, uh, vh)
    # Remove unused source-library textures and preview-only materials so this
    # asset has no hidden dependency on another library's texture folder.
    for image in list(bpy.data.images):
        if image.users == 0 and image.name != "Render Result":
            bpy.data.images.remove(image)
    for mat in list(bpy.data.materials):
        if mat.users == 0:
            bpy.data.materials.remove(mat)
    # Restore a neutral preview resolution and save the library at its manifest path.
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print("PDC_BUILD_COMPLETE", str(ASSET), COLLECTION_NAME,
          "footprint_half_dims_m", round(uh,3), round(vh,3),
          "roof_peak_estimate_m", 15.65)


if __name__ == "__main__":
    main()

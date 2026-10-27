"""Build a source library for Purdue's Convergence Center.

Run with Blender 5.2 background Python from the project root.  The exported
asset collection is local to the approximate official footprint centroid; the
original campus-coordinate massing file is intentionally untouched.
"""
import bpy
import json
import math
import os
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEOJSON = os.path.join(os.path.dirname(__file__), "convergence_gis_feature_946.geojson")
OUT_BLEND = os.path.join(ROOT, "modular", "buildings", "convergence_center.blend")
OUT_PREVIEW = os.path.join(os.path.dirname(__file__), "convergence_center_preview.png")
OUT_EVIDENCE = os.path.join(os.path.dirname(__file__), "convergence_center_evidence.json")

# Project convention: local campus linear approximation, meters; X east, Y north.
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
SCALE_X = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
SCALE_Y = 111040.0
CENTROID_XY = (-1131.698568664057, -405.52500592356535)


def remove_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    root = bpy.context.scene.collection
    for child in list(root.children):
        if child.name == "Collection":
            root.children.unlink(child)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def make_material(name, color, roughness=0.55, metallic=0.0, noise_scale=24.0, bump_strength=0.08):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    tex = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 3.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.19
    ramp.color_ramp.elements[0].color = (*(c * 0.91 for c in color), 1.0)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (*(min(1, c * 1.04) for c in color), 1.0)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.025
    links.new(tex.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def move_to_collection(obj, collection):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def mesh_object(name, verts, faces, collection, material, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def prism(name, outline, z0, z1, collection, material):
    n = len(outline)
    verts = [(x, y, z0) for x, y in outline] + [(x, y, z1) for x, y in outline]
    # Official GIS ring is clockwise. Keep bottom normals down, top normals up,
    # and each extruded side normal outward.
    faces = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    faces.extend((i, i + n, (i + 1) % n + n, (i + 1) % n) for i in range(n))
    return mesh_object(name, verts, faces, collection, material)


def box(name, loc, dims, material, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = move_to_collection(bpy.context.object, collection)
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("small manufactured edge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def edge_basis(a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    tangent = (dx / length, dy / length)
    # GIS rings are clockwise in the projected local frame; right normal is outward.
    normal = (-tangent[1], tangent[0])
    return length, tangent, normal


def wall_strip(name, a, b, s0, s1, z0, z1, offset, collection, material):
    length, t, nrm = edge_basis(a, b)
    p0 = (a[0] + t[0] * s0 + nrm[0] * offset, a[1] + t[1] * s0 + nrm[1] * offset)
    p1 = (a[0] + t[0] * s1 + nrm[0] * offset, a[1] + t[1] * s1 + nrm[1] * offset)
    return mesh_object(name,
        [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)],
        [(0, 1, 2, 3)], collection, material)


def facade_skin_with_punched_windows(outline, floor_z, collection, material, fin_material):
    """Thin cladding skin with real openings matching individually glazed bays."""
    verts, faces, fin_verts, fin_faces = [], [], [], []

    def quad(target_verts, target_faces, a, b, s0, s1, z0, z1, offset):
        length, tangent, normal = edge_basis(a, b)
        p0=(a[0]+tangent[0]*s0+normal[0]*offset,a[1]+tangent[1]*s0+normal[1]*offset)
        p1=(a[0]+tangent[0]*s1+normal[0]*offset,a[1]+tangent[1]*s1+normal[1]*offset)
        i=len(target_verts)
        # Winding faces the outward normal, including edges with either tangent sign.
        target_verts.extend([(p0[0],p0[1],z0),(p0[0],p0[1],z1),(p1[0],p1[1],z1),(p1[0],p1[1],z0)])
        target_faces.append((i,i+1,i+2,i+3))

    for i,a in enumerate(outline):
        b=outline[(i+1)%len(outline)]
        length,t,nrm=edge_basis(a,b)
        if length < 1.25: continue
        for story in range(1,5):
            zlow=4.15 if story==1 else floor_z[story]
            zhigh=floor_z[story+1]
            win_low=floor_z[story]+1.02
            win_high=zhigh-.56
            bay_size=4.8
            bay_count=max(1,int((length-.8)/bay_size))
            usable=length-.8
            module=usable/bay_count
            window_width=min(2.55,module*.62)
            intervals=[]
            for j in range(bay_count):
                center=.4+(j+.5)*module
                intervals.append((center-window_width/2,center+window_width/2))
            # The façade panels rise below/above each window and between the bays.
            quad(verts,faces,a,b,0,length,zlow,win_low,.025)
            quad(verts,faces,a,b,0,length,win_high,zhigh,.025)
            cursor=0.0
            for s0,s1 in intervals:
                if s0>cursor+.04:
                    quad(verts,faces,a,b,cursor,s0,win_low,win_high,.025)
                    # Fine vertical reveals/fins on the opaque panel piers only.
                    n_fins=max(0,int((s0-cursor)/.42))
                    for k in range(1,n_fins+1):
                        s=cursor+(s0-cursor)*k/(n_fins+1)
                        quad(fin_verts,fin_faces,a,b,s-.018,s+.018,zlow+.12,zhigh-.12,.12)
                cursor=max(cursor,s1)
            if cursor<length-.04:
                quad(verts,faces,a,b,cursor,length,win_low,win_high,.025)
                n_fins=max(0,int((length-cursor)/.42))
                for k in range(1,n_fins+1):
                    s=cursor+(length-cursor)*k/(n_fins+1)
                    quad(fin_verts,fin_faces,a,b,s-.018,s+.018,zlow+.12,zhigh-.12,.12)
    skin=mesh_object("CONV_GIS_five_story_cladding_volume",verts,faces,collection,material)
    fins=mesh_object("CONV_vertical_metal_panel_fins",fin_verts,fin_faces,collection,fin_material)
    return skin,fins


def text_on_plane(name, body, size, loc, tangent, normal, material, collection, vertical=False):
    curve=bpy.data.curves.new(name+" font", "FONT")
    curve.body=body; curve.size=size; curve.extrude=.006
    curve.align_x="CENTER"; curve.align_y="CENTER"
    text=bpy.data.objects.new(name,curve); collection.objects.link(text)
    if vertical:
        baseline=Vector((0,0,1)); face_normal=Vector((normal[0],normal[1],0)).normalized()
        up=face_normal.cross(baseline).normalized()
        matrix=Matrix((baseline,up,face_normal)).transposed()
    else:
        up=Vector((0,0,1))
        face_normal=Vector((normal[0],normal[1],0)).normalized()
        baseline=up.cross(face_normal).normalized()
        matrix=Matrix((baseline,up,face_normal)).transposed()
    text.rotation_euler=matrix.to_euler(); text.location=loc; curve.materials.append(material)
    return text


def main():
    remove_scene()
    scene = bpy.context.scene
    asset = bpy.data.collections.new("Asset_convergence_center")
    preview = bpy.data.collections.new("Preview_Only")
    scene.collection.children.link(asset)
    scene.collection.children.link(preview)

    with open(GEOJSON, "r", encoding="utf-8-sig") as f:
        feature = json.load(f)["features"][0]
    assert feature["properties"]["FID"] == 946
    assert feature["properties"]["BLDG_ABBR"] == "CONV"
    ring_ll = feature["geometry"]["coordinates"][0]
    outline = []
    for lon, lat in ring_ll[:-1]:
        x = (lon - ORIGIN_LON) * SCALE_X - CENTROID_XY[0]
        y = (lat - ORIGIN_LAT) * SCALE_Y - CENTROID_XY[1]
        outline.append((x, y))
    # Independently recompute the linear-ring centroid from the downloaded GIS
    # feature and verify that it matches the declared local placement origin.
    projected_abs = [((lon - ORIGIN_LON) * SCALE_X, (lat - ORIGIN_LAT) * SCALE_Y) for lon, lat in ring_ll]
    twice_area = centroid_x_num = centroid_y_num = 0.0
    for (x0, y0), (x1, y1) in zip(projected_abs, projected_abs[1:]):
        cross = x0 * y1 - x1 * y0
        twice_area += cross
        centroid_x_num += (x0 + x1) * cross
        centroid_y_num += (y0 + y1) * cross
    gis_area_m2 = abs(twice_area / 2.0)
    gis_centroid = (centroid_x_num / (3.0 * twice_area), centroid_y_num / (3.0 * twice_area))
    centroid_delta = (gis_centroid[0] - CENTROID_XY[0], gis_centroid[1] - CENTROID_XY[1])
    assert math.hypot(*centroid_delta) < 0.02, f"GIS ring centroid differs from manifest origin: {centroid_delta}"

    # Architectural readings: GIS footprint is authoritative for plan shape;
    # floor heights and curtain-wall module are estimates from five-story imagery.
    mat_shell = make_material("Convergence | pale vertical ribbed metal cladding", (0.55, 0.58, 0.59), 0.62, 0.30, 48, 0.08)
    mat_light = make_material("Convergence | satin aluminum trim and fins", (0.78, 0.80, 0.78), 0.38, 0.42, 60, 0.045)
    mat_spandrel = make_material("Convergence | charcoal horizontal spandrel", (0.14, 0.17, 0.18), 0.38, 0.24, 26, 0.05)
    mat_brick = make_material("Convergence | dark red ground-floor brick piers", (0.29, 0.105, 0.065), 0.82, 0.0, 52, 0.14)
    mat_wood = make_material("Convergence | warm oak lobby furniture", (0.34, 0.18, 0.075), 0.42, 0.02, 25, 0.045)
    mat_fabric = make_material("Convergence | muted blue-gray lobby upholstery", (0.18, 0.26, 0.29), 0.86, 0.0, 32, 0.04)
    mat_green = make_material("Convergence | lobby planting foliage", (0.09, 0.22, 0.12), 0.9, 0.0, 11, 0.06)
    mat_glass = bpy.data.materials.new("Convergence | blue-gray low-e glazing")
    mat_glass.diffuse_color = (0.075, 0.16, 0.20, 1.0)
    mat_glass.use_nodes = True
    glass_bsdf = next(n for n in mat_glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    glass_bsdf.inputs["Base Color"].default_value = (0.075, 0.16, 0.20, 1)
    glass_bsdf.inputs["Roughness"].default_value = 0.2
    glass_bsdf.inputs["Metallic"].default_value = 0.28
    glass_bsdf.inputs["Alpha"].default_value = 0.58
    if hasattr(mat_glass, "surface_render_method"):
        mat_glass.surface_render_method = "DITHERED"
    if "Transmission Weight" in glass_bsdf.inputs:
        glass_bsdf.inputs["Transmission Weight"].default_value = 0.18
    if "IOR" in glass_bsdf.inputs:
        glass_bsdf.inputs["IOR"].default_value = 1.46
    glass_nodes, glass_links = mat_glass.node_tree.nodes, mat_glass.node_tree.links
    glass_coord = glass_nodes.new("ShaderNodeTexCoord")
    glass_noise = glass_nodes.new("ShaderNodeTexNoise")
    glass_noise.inputs["Scale"].default_value = 95.0
    glass_noise.inputs["Detail"].default_value = 2.0
    glass_ramp = glass_nodes.new("ShaderNodeMapRange")
    glass_ramp.inputs["From Min"].default_value = 0.0
    glass_ramp.inputs["From Max"].default_value = 1.0
    glass_ramp.inputs["To Min"].default_value = 0.17
    glass_ramp.inputs["To Max"].default_value = 0.25
    glass_bump = glass_nodes.new("ShaderNodeBump")
    glass_bump.inputs["Strength"].default_value = 0.012
    glass_bump.inputs["Distance"].default_value = 0.006
    glass_links.new(glass_coord.outputs["Generated"], glass_noise.inputs["Vector"])
    glass_links.new(glass_noise.outputs["Fac"], glass_ramp.inputs["Value"])
    glass_links.new(glass_ramp.outputs["Result"], glass_bsdf.inputs["Roughness"])
    glass_links.new(glass_noise.outputs["Fac"], glass_bump.inputs["Height"])
    glass_links.new(glass_bump.outputs["Normal"], glass_bsdf.inputs["Normal"])
    mat_roof = make_material("Convergence | dark membrane roof", (0.105, 0.125, 0.14), 0.83, 0.06, 32, 0.12)
    mat_concrete = make_material("Convergence | architectural concrete", (0.48, 0.49, 0.46), 0.88, 0.0, 18, 0.16)
    mat_interior = make_material("Convergence | warm lobby interior", (0.64, 0.46, 0.25), 0.4, 0.0, 10, 0.04)
    mat_sign = make_material("Convergence | identity sign charcoal", (0.055, 0.066, 0.071), 0.45, 0.12, 28, 0.03)

    # GIS polygon produces the main wall envelope at 35 x 84 m with the verified
    # stepped southern shoulders. Five floors are source-backed; vertical dimensions
    # remain estimates. The facade skin is split around window bays so the glazing
    # is not buried against a solid massing prism.
    floor_z = [0.0, 4.25, 8.3, 12.35, 16.4, 20.45]
    roof_z = 20.45
    # Ground-level slab and a five-storey articulated exterior skin.
    prism("CONV_GIS_ground_plate", outline, -0.25, 0.20, asset, mat_concrete)
    facade_skin_with_punched_windows(outline, floor_z, asset, mat_shell, mat_light)
    prism("CONV_flat_roof", outline, roof_z, roof_z + 0.32, asset, mat_roof)

    # A recessed shadow line and floor bands clearly articulate five levels.
    for level, z in enumerate(floor_z[1:5], 1):
        prism(f"CONV_floor_{level}_continuous_spandrel_band", outline, z - 0.13, z + 0.16, asset, mat_spandrel)
        prism(f"CONV_floor_{level}_aluminum_slab_edge", outline, z + 0.16, z + 0.25, asset, mat_light)

    # Continuous ground-floor curtain wall around the exact GIS perimeter.
    for i, a in enumerate(outline):
        b = outline[(i + 1) % len(outline)]
        length, t, nrm = edge_basis(a, b)
        wall_strip(f"CONV_lobby_glass_{i:02d}", a, b, 0.30, length - 0.30, 0.48, 4.05, 0.10, asset, mat_glass)
        # Fine dark mullions, approximately 1.55 m on center.
        count = max(1, int(length / 1.55))
        for j in range(1, count):
            s = length * j / count
            cx = a[0] + t[0] * s + nrm[0] * 0.13
            cy = a[1] + t[1] * s + nrm[1] * 0.13
            box(f"CONV_lobby_mullion_{i:02d}_{j:02d}", (cx, cy, 2.24), (0.065, 0.065, 3.48), mat_spandrel, asset)
        # The built photos show intermittent red-brown masonry piers at grade,
        # separating storefront glazing from the white lobby portal.
        if length > 6.0:
            pier_count=max(1,int(length/5.8))
            for j in range(1,pier_count):
                s=length*j/pier_count
                px=a[0]+t[0]*s+nrm[0]*.22
                py=a[1]+t[1]*s+nrm[1]*.22
                dims=(.52,.55,3.35) if abs(t[1])>abs(t[0]) else (.55,.52,3.35)
                box(f"CONV_ground_floor_brick_pier_{i:02d}_{j:02d}",(px,py,2.18),dims,mat_brick,asset,.025)

        # Upper storeys: punched, tall window bays separated by metal-panel piers.
        for story in range(1, 5):
            z0 = floor_z[story] + 1.02
            z1 = floor_z[story + 1] - 0.56
            if z1 <= z0:
                continue
            # Discrete window openings match the architect's built exterior photo.
            bay = 4.8
            n_bays = max(1, int((length - 0.8) / bay))
            usable = length - 0.8
            actual_bay = usable / n_bays
            window_width = min(2.55, actual_bay * .62)
            for j in range(n_bays):
                center_s = .4 + (j + .5) * actual_bay
                s0 = center_s - window_width / 2
                s1 = center_s + window_width / 2
                if s1 > s0:
                    wall_strip(f"CONV_upper_glazing_F{story}_{i:02d}_{j:02d}", a, b, s0, s1, z0, z1, 0.075, asset, mat_glass)
                    # Light metal panel piers separate the windows from neighbors.
                    if j > 0:
                        sm = (s0 + s1) / 2
                        p0 = (a[0] + t[0] * sm + nrm[0] * 0.135,
                              a[1] + t[1] * sm + nrm[1] * 0.135)
                        p1 = (p0[0] + t[0] * 0.07, p0[1] + t[1] * 0.07)
                        mesh_object(f"CONV_mullion_F{story}_{i:02d}_{j:02d}",
                            [(p0[0],p0[1],z0),(p1[0],p1[1],z0),(p1[0],p1[1],z1),(p0[0],p0[1],z1)],
                            [(0,1,2,3)], asset, mat_light)

        # Thin charcoal coping follows the flat roof, without inventing a penthouse.
        wall_strip(f"CONV_roof_edge_{i:02d}", a, b, 0.0, length, 20.72, 20.98, 0.14, asset, mat_spandrel)

    # The west frontage faces Foundry Drive. Purdue's 2020 photo shows a large
    # white portal around the glazed lobby and a separate plaza monument sign.
    # The exact bay and sign offset are inferred, not dimensioned.
    west_edge = max(range(len(outline)), key=lambda i: edge_basis(outline[i], outline[(i + 1) % len(outline)])[0]
                    if abs((outline[i][0] + outline[(i + 1) % len(outline)][0]) * 0.5 - min(x for x, _ in outline)) < 0.7 else 0)
    a, b = outline[west_edge], outline[(west_edge + 1) % len(outline)]
    length, t, nrm = edge_basis(a, b)
    center_s = length * 0.50
    cx = a[0] + t[0] * center_s
    cy = a[1] + t[1] * center_s
    longitudinal = abs(t[1]) > abs(t[0])
    portal_width=min(23.0,length*.48)
    portal_depth=3.4
    portal_face=(cx+nrm[0]*.70,cy+nrm[1]*.70)
    if longitudinal:
        beam_dims=(.72,portal_width,.85); column_dims=(.72,.78,4.55)
        canopy_dims=(portal_depth,portal_width+1.2,.42); vestibule_dims=(1.15,9.5,3.65)
    else:
        beam_dims=(portal_width,.72,.85); column_dims=(.78,.72,4.55)
        canopy_dims=(portal_width+1.2,portal_depth,.42); vestibule_dims=(9.5,1.15,3.65)
    beam_center=(portal_face[0]+nrm[0]*.12,portal_face[1]+nrm[1]*.12,4.40)
    box("CONV_west_entry_canopy",(cx+nrm[0]*2.35,cy+nrm[1]*2.35,4.46),canopy_dims,mat_light,asset,.07)
    box("CONV_white_portal_head",beam_center,beam_dims,mat_light,asset,.035)
    for side,sign in (("A",-1.0),("B",1.0)):
        jamb_center=(portal_face[0]+t[0]*sign*(portal_width/2),portal_face[1]+t[1]*sign*(portal_width/2),2.25)
        box(f"CONV_white_portal_jamb_{side}",jamb_center,column_dims,mat_light,asset,.035)
    vestibule_center=(cx+nrm[0]*.72,cy+nrm[1]*.72,2.05)
    box("CONV_glazed_entry_vestibule", vestibule_center, vestibule_dims, mat_glass, asset, 0.02)
    # Main double doors, side-lights, and an over-door Convergence identity.
    door_center=(cx+nrm[0]*1.38,cy+nrm[1]*1.38,1.82)
    door_dims=(.10,3.15,2.85) if longitudinal else (3.15,.10,2.85)
    box("CONV_glazed_pair_of_entry_doors",door_center,door_dims,mat_glass,asset,.015)
    for side,sign in (("A",-1.0),("B",1.0)):
        post=(cx+t[0]*sign*portal_width*.34+nrm[0]*2.4,cy+t[1]*sign*portal_width*.34+nrm[1]*2.4,2.12)
        support_dims=(.24,.24,4.2)
        box(f"CONV_canopy_support_column_{side}",post,support_dims,mat_light,asset,.025)

    sign_loc=(cx+nrm[0]*.42,cy+nrm[1]*.42,4.02)
    sign_dims=(.24,8.0,.72) if longitudinal else (8.0,.24,.72)
    box("CONV_convergence_identity_sign_backing",sign_loc,sign_dims,mat_sign,asset,.035)
    text_on_plane("CONV_identity_sign_text","CONVERGENCE",.70,
        (cx+nrm[0]*.56,cy+nrm[1]*.56,4.02),t,nrm,mat_light,asset)

    # Source-supported freestanding entry monument in the public plaza. Its
    # exact position relative to the entrance is approximate from the photos.
    sign_s=length*.34
    sign_xy=(a[0]+t[0]*sign_s+nrm[0]*5.7,a[1]+t[1]*sign_s+nrm[1]*5.7)
    sign_body_dims=(.92,3.25,4.25) if longitudinal else (3.25,.92,4.25)
    monument_center=(sign_xy[0],sign_xy[1],2.22)
    box("CONV_freestanding_monument_sign_body",monument_center,sign_body_dims,mat_light,asset,.035)
    front_dims=(.06,2.72,3.25) if longitudinal else (2.72,.06,3.25)
    front_center=(sign_xy[0]+nrm[0]*.50,sign_xy[1]+nrm[1]*.50,2.35)
    box("CONV_monument_sign_address_face",front_center,front_dims,mat_sign,asset,.025)
    text_on_plane("CONV_monument_address_text","101 Foundry Drive",.34,
        (front_center[0]+nrm[0]*.045,front_center[1]+nrm[1]*.045,3.45),t,nrm,mat_light,asset)
    side_n=(-nrm[1],nrm[0])
    side_dims=(.92,.06,3.25) if longitudinal else (.06,.92,3.25)
    side_offset=1.625 if longitudinal else .46
    side_center=(sign_xy[0]+side_n[0]*side_offset,sign_xy[1]+side_n[1]*side_offset,2.35)
    box("CONV_monument_sign_identity_face",side_center,side_dims,mat_sign,asset,.025)
    text_on_plane("CONV_monument_vertical_convergence_text","CONVERGENCE",.27,
        (side_center[0]+side_n[0]*.045,side_center[1]+side_n[1]*.045,2.28),t,side_n,mat_light,asset,vertical=True)

    # Interior visible through the glass is a source-guided but schematic lobby:
    # architect photos show a reception desk, large social area, mezzanine edge,
    # black display wall, wood/metal tables, lounge chairs, and plantings.
    lobby_cx = cx - nrm[0] * 5.0
    lobby_cy = cy - nrm[1] * 5.0
    prism("CONV_visible_lobby_floor", [
        (lobby_cx - 11.0, lobby_cy - 11.0), (lobby_cx + 11.0, lobby_cy - 11.0),
        (lobby_cx + 11.0, lobby_cy + 11.0), (lobby_cx - 11.0, lobby_cy + 11.0)],
        0.42, 0.52, asset, mat_interior)
    # Desk and its oak transaction counter face the public entry.
    desk_center=(cx-nrm[0]*4.1,cy-nrm[1]*4.1,1.10)
    desk_dims=(1.05,5.8,1.05) if longitudinal else (5.8,1.05,1.05)
    box("CONV_lobby_reception_desk_visible_cue",desk_center,desk_dims,mat_concrete,asset,.10)
    counter_center=(desk_center[0],desk_center[1],1.66)
    counter_dims=(1.18,6.1,.16) if longitudinal else (6.1,1.18,.16)
    box("CONV_lobby_oak_reception_counter",counter_center,counter_dims,mat_wood,asset,.035)
    # Dark screen wall with a restrained lobby wordmark; its exact bay is schematic.
    wall_center=(cx-nrm[0]*16.0,cy-nrm[1]*16.0,4.2)
    wall_dims=(.38,16.0,7.2) if longitudinal else (16.0,.38,7.2)
    box("CONV_schematic_double_height_lobby_feature_wall",wall_center,wall_dims,mat_sign,asset,.02)
    text_on_plane("CONV_lobby_feature_wall_wordmark","CONVERGENCE",1.05,
        (wall_center[0]+nrm[0]*.22,wall_center[1]+nrm[1]*.22,4.5),t,nrm,mat_light,asset)
    # Partial mezzanine/bridge at the rear of the public atrium leaves the entry
    # volume open, matching the architect's double-height lobby image.
    mx=cx-nrm[0]*12.0; my=cy-nrm[1]*12.0
    mezz_poly=[(mx-5.0,my-10.0),(mx+5.0,my-10.0),(mx+5.0,my+10.0),(mx-5.0,my+10.0)]
    prism("CONV_schematic_lobby_mezzanine",mezz_poly,4.28,4.52,asset,mat_concrete)
    rail_z=5.65
    rail_a=(mx-5.0,my-10.0); rail_b=(mx-5.0,my+10.0)
    wall_strip("CONV_schematic_mezzanine_guardrail",rail_a,rail_b,0,20,rail_z-.045,rail_z+.045,0,asset,mat_spandrel)
    for j in range(1,13):
        ry=my-10.0+j*(20.0/13.0)
        box(f"CONV_schematic_mezzanine_baluster_{j:02d}",(mx-5.0,ry,5.1),(.08,.08,.9),mat_spandrel,asset)
    # Small lounge group: source supports loose seating and low tables, not an exact plan.
    for i,(dx,dy) in enumerate([(5.7,-4.4),(10.5,-4.1),(7.8,4.6)]):
        sx=cx-nrm[0]*dx+t[0]*dy; sy=cy-nrm[1]*dx+t[1]*dy
        sofa_dims=(2.7,1.15,.72) if longitudinal else (1.15,2.7,.72)
        box(f"CONV_schematic_lobby_lounge_seat_{i+1}",(sx,sy,.88),sofa_dims,mat_fabric,asset,.12)
        table_dims=(1.25,.85,.14) if longitudinal else (.85,1.25,.14)
        box(f"CONV_schematic_lobby_coffee_table_{i+1}",(sx-nrm[0]*1.0,sy-nrm[1]*1.0,.66),table_dims,mat_wood,asset,.025)
    for i,dy in enumerate((-8.0,8.0)):
        px=cx-nrm[0]*7.2+t[0]*dy; py=cy-nrm[1]*7.2+t[1]*dy
        box(f"CONV_schematic_lobby_planter_{i+1}",(px,py,.75),(.9,.9,.55),mat_concrete,asset,.04)
        for leaf in range(7):
            ang=leaf*math.tau/7
            lx=px+.38*math.cos(ang); ly=py+.38*math.sin(ang)
            box(f"CONV_schematic_lobby_plant_leaf_{i+1}_{leaf}",(lx,ly,1.48),(.10,.10,1.2),mat_green,asset,.045)

    # Roof screen and rooftop mechanical units are intentionally restrained and
    # not treated as verified equipment locations.
    # An open mechanical screen follows the roof perimeter; keep the center roof
    # open so the rooftop plant remains visually legible.
    for i, a in enumerate(outline):
        b = outline[(i + 1) % len(outline)]
        length, t, nrm = edge_basis(a, b)
        wall_strip(f"CONV_roof_screen_panel_{i:02d}", a, b, 0.0, length, 21.02, 21.62, -1.0, asset, mat_shell)
        nslats = max(2, int(length / 1.5))
        for j in range(1, nslats):
            s = length * j / nslats
            px = a[0] + t[0] * s + nrm[0] * -0.86
            py = a[1] + t[1] * s + nrm[1] * -0.86
            box(f"CONV_roof_screen_louver_{i:02d}_{j:02d}", (px, py, 21.32), (0.075, 0.075, 0.56), mat_spandrel, asset)
    for idx, (x, y, sx, sy) in enumerate([(-8, 15, 5, 3.2), (0, 15, 5, 3.2), (8, 15, 5, 3.2), (-5, 6, 3.8, 2.8), (4, 6, 3.8, 2.8)]):
        box(f"CONV_roof_HVAC_estimated_{idx+1}", (x, y, 21.45), (sx, sy, 0.85), mat_spandrel, asset, 0.08)

    # Stable source identity and placement metadata for the modular integrator.
    asset["source_feature_id"] = 946
    asset["building_id"] = "convergence_center"
    asset["placement_origin_xy_m"] = list(CENTROID_XY)
    asset["local_coordinates"] = True
    asset["stories_verified"] = 5
    asset["main_roof_height_estimate_m"] = roof_z
    asset["GIS_footprint_area_estimate_m2"] = gis_area_m2
    asset["GIS_footprint_vertices"] = len(outline)
    asset["footprint_local_bounds_m"] = [[min(x for x,_ in outline),max(x for x,_ in outline)],
                                           [min(y for _,y in outline),max(y for _,y in outline)]]
    asset["monument_sign_position_status"] = "photo-supported design; precise plaza offset estimated"
    asset["interior_layout_status"] = "schematic; no georegistered full-building floor plan used"

    # Preview-only ground, naturalistic daylight and two views; not part of asset.
    ground_mat = make_material("Preview | neutral pavement", (0.23, 0.26, 0.27), 0.88, 0, 9, 0.12)
    box("Preview_ground", (0, 0, -0.66), (145, 150, 0.32), ground_mat, preview)
    world = bpy.data.worlds.new("Convergence preview | clear sky") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.34, 0.50, 0.68, 1)
    bg.inputs["Strength"].default_value = 0.48
    light_data = bpy.data.lights.new("Preview_sun", "SUN")
    light_obj = bpy.data.objects.new("Preview_sun", light_data)
    preview.objects.link(light_obj)
    light_obj.rotation_euler = (math.radians(28), math.radians(-24), math.radians(-28))
    light_data.energy = 3.0
    area = bpy.data.lights.new("Preview_softbox", "AREA")
    area.energy = 4200
    area.shape = "DISK"
    area.size = 34
    area_obj = bpy.data.objects.new("Preview_softbox", area)
    preview.objects.link(area_obj)
    area_obj.location = (55, -68, 62)
    area_obj.rotation_euler = (Vector((0, 0, 9)) - area_obj.location).to_track_quat("-Z", "Y").to_euler()

    cam_data = bpy.data.cameras.new("Preview_camera")
    cam = bpy.data.objects.new("Preview_camera", cam_data)
    preview.objects.link(cam)
    cam.location = (-112, -126, 77)
    target = Vector((0, 0, 8.8))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 54
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = 80
    scene.render.filepath = OUT_PREVIEW
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.camera.data.dof.use_dof = False
    # Hide preview-only objects when the collection is linked into the master.
    preview.hide_render = True
    # render with preview visibility enabled temporarily
    preview.hide_render = False
    original_camera=(cam.location.copy(),cam.rotation_euler.copy(),cam_data.lens,cam_data.type,cam_data.ortho_scale)
    bpy.ops.render.render(write_still=True)
    # Long west elevation, entrance/monument close view, lobby interior cue, and roof plan.
    cam_data.type='PERSP'; cam_data.lens=35
    cam.location=Vector((cx+nrm[0]*80,cy+nrm[1]*80,15.0))
    cam.rotation_euler=(Vector((cx,cy,10.0))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=os.path.join(os.path.dirname(__file__),'convergence_center_west_elevation.png')
    bpy.ops.render.render(write_still=True)
    cam_data.lens=35
    cam.location=Vector((cx+nrm[0]*55,cy+nrm[1]*55,5.2))
    entry_target=Vector((cx+nrm[0]*1.5,cy+nrm[1]*1.5,3.6))
    cam.rotation_euler=(entry_target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=os.path.join(os.path.dirname(__file__),'convergence_center_entry_detail.png')
    bpy.ops.render.render(write_still=True)
    cam_data.lens=38
    lobby_target=Vector((cx-nrm[0]*14+t[0]*1,cy-nrm[1]*14+t[1]*1,4.1))
    cam.location=Vector((cx-nrm[0]*4+t[0]*-8,cy-nrm[1]*4+t[1]*-8,3.1))
    cam.rotation_euler=(lobby_target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=os.path.join(os.path.dirname(__file__),'convergence_center_lobby_detail.png')
    bpy.ops.render.render(write_still=True)
    cam_data.type='ORTHO'; cam_data.ortho_scale=125
    cam.location=Vector((0,0,145)); cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=os.path.join(os.path.dirname(__file__),'convergence_center_roof_plan.png')
    bpy.ops.render.render(write_still=True)
    cam.location=original_camera[0]; cam.rotation_euler=original_camera[1]
    cam_data.lens=original_camera[2]; cam_data.type=original_camera[3]; cam_data.ortho_scale=original_camera[4]
    preview.hide_render = True

    # Save a clean asset file; collection is the only content to be linked by the master.
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

    # Evidence carries original native GIS snapshot and transformed footprint metrics.
    bounds = {
        "x_min": min(x for x, _ in outline), "x_max": max(x for x, _ in outline),
        "y_min": min(y for _, y in outline), "y_max": max(y for _, y in outline),
        "width_m": max(x for x, _ in outline) - min(x for x, _ in outline),
        "depth_m": max(y for _, y in outline) - min(y for _, y in outline),
    }
    evidence = {
        "building_id": "convergence_center",
        "asset_file": "modular/buildings/convergence_center.blend",
        "exported_collection": "Asset_convergence_center",
        "original_massing_asset_preserved": "modular/buildings/massing_convergence_center_for_innovation_and_collaboration_conv_ce5226e.blend",
        "retrieved_utc_date": "2026-10-27",
        "sources": [
            {"provider": "Purdue University News", "url": "https://www.purdue.edu/newsroom/archive/releases/2018/Q4/discovery-park-district-lays-welcome-mat-with-construction-of-145,000-square-foot,-five-story-building.html", "use": "official name, five-story count, 145,000-sq-ft area, large lobby/plaza, first-floor retail; 2018 construction announcement includes design rendering"},
            {"provider": "Purdue University News / Purdue Research Foundation", "url": "https://www.purdue.edu/uns/images/2018/convergence-rendering.jpg", "use": "official 2018 design rendering: glazed ground-floor portal, light vertical metal cladding, five-floor window rhythm and original branding; design intent, not an as-built survey"},
            {"provider": "Purdue University News / Purdue Research Foundation", "url": "https://www.purdue.edu/uns/images/2020/convergence-traskLO.jpg", "use": "official 2020 as-built daylight exterior: punched window bays, pale vertically ribbed metal panels, large white entrance frame, glass lobby and freestanding monument sign labeled 101 Foundry Drive / Convergence"},
            {"provider": "Purdue University News / Purdue Research Foundation", "url": "https://www.purdue.edu/uns/images/2021/convergence-buildingLO.jpg", "use": "official exterior/sign close view: freestanding entry monument profile and legible Convergence identity"},
            {"provider": "Purdue University News / Purdue Research Foundation", "url": "https://www.purdue.edu/newsroom/archive/releases/2021/Q3/purdue,-purdue-research-foundation-launch-lab-to-life-6g-digital-innovation-at-discovery-park-district.html", "use": "official building photo caption and operational identity"},
            {"provider": "Purdue University News / Purdue Research Foundation", "url": "https://www.purdue.edu/newsroom/archive/releases/2021/Q1/wabash-national-set-to-open-collaboration-space-in-purdues-discovery-park-district.html", "use": "official exterior photo associated with occupied Convergence Center"},
            {"provider": "CSO Architects (project architect)", "url": "https://www.csoinc.net/projects/convergence-center/", "use": "architect's built exterior and interior photos; confirms five stories, 157,172-sq-ft project data, large atrium, class-A office/retail, coworking and meeting/event program"},
            {"provider": "CSO Architects image gallery", "url": "https://www.csoinc.net/wp-content/uploads/2026/02/03_Convergence.jpg", "use": "architect exterior night view for flat roof, dark cladding, window grid and plaza context"},
            {"provider": "CSO Architects image gallery", "url": "https://www.csoinc.net/wp-content/uploads/2026/02/02_Convergence.jpg", "use": "architect interior photo for double-height lobby, reception desk, mezzanine guardrail, lounge seating and feature wall; room placement is not georegistered"},
            {"provider": "Purdue Innovates", "url": "https://purdueinnovates.org/venue/the-convergence-center-for-innovation-and-collaboration/", "use": "current venue identity and exact address 101 Foundry Drive"},
            {"provider": "Google Maps", "url": "https://www.google.com/maps/place/The+Convergence+Center+for+Innovation+and+Collaboration/@40.4237313,-86.929787,17z/data=!3m1!4b1!4m6!3m5!1s0x8812e38bd7e04541:0xc20b61b4bddde859!8m2!3d40.4237313!4d-86.9272121!16s%2Fg%2F11j7kpptjx", "use": "verified exact place listing/address and site map context; map places the west frontage on Foundry Drive with State Street north of the site and District Boulevard south; frontage inference only, not dimensional evidence"},
            {"provider": "Google Maps Street View", "url": "https://www.google.com/maps/@40.4235695,-86.9268681,3a,75y/data=!3m7!1e1!3m5!1s0x0:0x0!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D90%26panoid%3D0x0%253A0x0%26yaw%3D0!7i8192!8i4096", "use": "street-view coverage attempted on 2026-10-23; Google reports no street-level imagery at selected point and serves a Carr Workplaces interior panorama instead. Exterior facade therefore comes from official Purdue images, not Street View."},
            {"provider": "Purdue official CampusMap ArcGIS FeatureServer", "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0", "feature_query": "query?where=FID%3D946&outFields=*&returnGeometry=true", "feature_id": 946, "code": "CONV", "source_crs": "EPSG:3857 (WKID 102100, latest WKID 3857); captured feature transformed to EPSG:4326 for GeoJSON and reprojected with project approximation for model", "use": "authoritative official-campus footprint/source-feature identity"},
        ],
        "gis_snapshot": {"native": "audit/convergence_gis_feature_946_native.json", "wgs84": "audit/convergence_gis_feature_946.geojson", "layer_metadata": "audit/convergence_gis_layer_metadata.json", "retrieval_date": "2026-10-23", "native_crs": "EPSG:3857", "output_crs": "EPSG:4326", "feature_id": 946, "name": "Convergence", "BLDG_ABBR": "CONV", "address": "101 Foundry Drive, West Lafayette, IN"},
        "coordinate_frame": {"units": "meters", "axes": "X east, Y north, Z up", "project_origin_latitude": ORIGIN_LAT, "project_origin_longitude": ORIGIN_LON, "local_origin_xy_m": list(CENTROID_XY), "origin_definition": "official GIS polygon largest-ring centroid from existing Purdue official footprint reference; use master placement marker at this XY", "transform": "X=(longitude + 86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude - 40.4274)*111040; local XY subtract centroid"},
        "footprint_local_bounds_m": bounds,
        "footprint_validation": {"GIS_polygon_area_m2_projected": gis_area_m2, "centroid_xy_m_projected": list(gis_centroid), "local_origin_centroid_delta_m": list(centroid_delta), "transform_method": "ArcGIS EPSG:3857 source was requested as EPSG:4326 GeoJSON; vertices were transformed to the project's local approximate east/north metric frame, then the ring centroid was recalculated by shoelace formula. The independently calculated centroid matches the saved campus reference center exactly."},
        "geometry_edits": ["preserved the official FID 946 stepped footprint and local centroid", "replaced the solid upper mass prism with an outward cladding skin split around discrete glazing openings", "changed continuous ribbons to source-matched punched windows with broad pale vertical panel piers and fine vertical metal fins", "added a tall white portal frame and broad canopy around the Foundry-side glazed lobby", "added the source-supported freestanding 101 Foundry Drive / Convergence plaza monument rather than attaching the sign to the roof or facade", "added first-floor brick piers, dark horizontal floor spandrels, flat dark roof coping and restrained estimated roof equipment", "expanded the visible lobby into a photo-guided schematic with reception, screen wall, partial mezzanine, seating, tables and planters", "used connected procedural materials only; no source photos are embedded as textures"],
        "source_snapshots": [
            {"path": "audit/convergence_center/official_purdue_2018_rendering.jpg", "source_url": "https://www.purdue.edu/uns/images/2018/convergence-rendering.jpg", "retrieved_date": "2026-10-27", "use": "design intent comparison"},
            {"path": "audit/convergence_center/official_purdue_2020_photo.jpg", "source_url": "https://www.purdue.edu/uns/images/2020/convergence-traskLO.jpg", "retrieved_date": "2026-10-27", "use": "as-built daylight facade, portal and monument sign comparison"},
            {"path": "audit/convergence_center/official_purdue_2021_exterior.jpg", "source_url": "https://www.purdue.edu/uns/images/2021/convergence-buildingLO.jpg", "retrieved_date": "2026-10-27", "use": "as-built monument sign close comparison"},
            {"path": "audit/convergence_center/official_cso_convergence_03.jpg", "source_url": "https://www.csoinc.net/wp-content/uploads/2026/02/03_Convergence.jpg", "retrieved_date": "2026-10-27", "use": "project architect's built exterior view"},
            {"path": "audit/convergence_center/official_cso_convergence_02.jpg", "source_url": "https://www.csoinc.net/wp-content/uploads/2026/02/02_Convergence.jpg", "retrieved_date": "2026-10-27", "use": "project architect's double-height lobby/interior finishes and furniture"}
        ],
        "vertical_evidence": {"story_count": {"value": 5, "status": "verified from Purdue construction release and CSO architect project page"}, "main_roof_height_m": {"value_estimate": 20.45, "status": "estimated, not measured; derived from five-story count and approximate floor-to-floor heights"}, "freestanding_monument_height_m": {"value_estimate": 4.25, "status": "photo-scaled estimate; not surveyed"}, "floor_heights": "estimated: ground floor 4.25 m, four upper stories approximately 4.05 m each"},
        "interior_interpretation": "Schematic only. The architect photo supports a double-height public lobby, reception counter, dark display wall, partial mezzanine/guardrail, lounge seating, low tables and planting. No complete, georegistered building plan was found; furniture, atrium extent, orientation, partition locations and individual room layouts are not surveyed.",
        "uncertainty": ["The official GIS FID 946 confirms the building identity and plan polygon but is not a certified survey; its 12-point ring cannot verify the wall line, openings, dimensions or entrance offset.", "The five-story count is verified; individual floor-to-floor heights, roof elevation and monument height remain photo-scaled estimates.", "The West/Foundry frontage and portal direction are inferred from official address, source photos and Google Maps context; the precise door bay and freestanding sign offset are estimated.", "The flat roof and parapet are photo-supported, while exact roof equipment type and locations remain illustrative.", "The interior is a source-guided lobby vignette; it is not a reconstructed floor plan because no full plan could be registered to the GIS shell."],
        "preview": "audit/convergence_center_preview.png",
        "additional_previews": ["audit/convergence_center_west_elevation.png", "audit/convergence_center_entry_detail.png", "audit/convergence_center_lobby_detail.png", "audit/convergence_center_roof_plan.png"],
        "source_urls_and_retrieval_date": "URLs, providers and source snapshots recorded above; sources consulted 2026-10-27",
    }
    with open(OUT_EVIDENCE, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
        f.write("\n")
    print(json.dumps({"saved": OUT_BLEND, "preview": OUT_PREVIEW, "evidence": OUT_EVIDENCE, "outline_vertices": len(outline), "bounds": bounds, "asset_object_count": len(asset.objects)}))


if __name__ == "__main__":
    main()

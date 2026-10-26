"""
Construct Official Blender Asset for Stanley Coulter Hall (SC - FID 56 - 1917)
Following modular/AGENTS.md specifications:
- Output: modular/buildings/stanley_coulter_hall.blend
- Collection: Asset_stanley_coulter_hall
- Scene: Building_stanley_coulter_hall
- Coordinates: World space (meters, origin 40.4274, -86.9137)
- Exact Official Centroid: [-57.595882788814066, -96.64824046713962]
- Exact Official 13-Vertex Footprint Polygon
- Neoclassical architecture: Red brick, Indiana limestone, Grand Arched Portico,
  Beltcourses, Quoins, Cornice, Hipped Slate Roof, Pedimented Dormers, Chimneys.
"""

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import os
import json

def build_stanley_coulter_hall():
    print("=======================================================================")
    print("=== BUILDING OFFICIAL ASSET: STANLEY COULTER HALL (SC - FID 56) ===")
    print("=======================================================================")

    # 1. Reset Scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Rename default scene
    scene = bpy.context.scene
    scene.name = "Building_stanley_coulter_hall"

    # Set rendering engine and color management
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    if hasattr(scene, 'eevee'):
        scene.eevee.use_shadows = True

    # 2. Collections Setup
    # Root collection required by AGENTS.md: Asset_stanley_coulter_hall
    col_root = bpy.data.collections.new("Asset_stanley_coulter_hall")
    scene.collection.children.link(col_root)

    col_ext = bpy.data.collections.new("SC_Exterior_Structure")
    col_portico = bpy.data.collections.new("SC_Portico_and_Entrances")
    col_fenestration = bpy.data.collections.new("SC_Fenestration")
    col_roof = bpy.data.collections.new("SC_Roof_and_Dormers")
    col_interior = bpy.data.collections.new("SC_Interior_Shell")
    col_site = bpy.data.collections.new("SC_Plaza_and_Site")
    col_cams = bpy.data.collections.new("00_Inspection_Cameras")

    for col in [col_ext, col_portico, col_fenestration, col_roof, col_interior, col_site, col_cams]:
        col_root.children.link(col)

    # 3. Coordinate System & Geographic Alignment
    # Official reference centroid
    CX = -57.595882788814066
    CY = -96.64824046713962
    ROT_DEG = 0.89352421882437  # 90.893524 - 90 deg
    PHI = math.radians(ROT_DEG)
    COS_PHI = math.cos(PHI)
    SIN_PHI = math.sin(PHI)

    def to_world(lx, ly, lz=0.0):
        """Transform building-local coordinates to world coordinates."""
        wx = CX + lx * COS_PHI - ly * SIN_PHI
        wy = CY + lx * SIN_PHI + ly * COS_PHI
        wz = lz
        return Vector((wx, wy, wz))

    def to_world_vec(v):
        return to_world(v.x, v.y, v.z)

    # Official 12 distinct polygon vertices (in world space)
    official_rings_world = [
        Vector((-83.32214648723321, -84.29077226929166, 0.0)),
        Vector((-83.53366030864316, -70.60471485499647, 0.0)),
        Vector((-32.37196466110286, -69.80952959936076, 0.0)),
        Vector((-32.16313832563171, -83.2578280986445, 0.0)),
        Vector((-29.951449740003607, -83.22244168271027, 0.0)),
        Vector((-29.333200713718846, -123.07964621352994, 0.0)),
        Vector((-43.04812722030948, -123.29415399640311, 0.0)),
        Vector((-43.085793296594304, -120.69717441714147, 0.0)),
        Vector((-71.24677891970983, -121.13707190221021, 0.0)),
        Vector((-71.206164393601, -123.79197025639087, 0.0)),
        Vector((-85.04903399801545, -124.00938000318547, 0.0)),
        Vector((-85.66789777294949, -84.32896945175798, 0.0))
    ]

    # Convert official rings to local space for precise procedural assembly
    official_rings_local = []
    for w in official_rings_world:
        dx = w.x - CX
        dy = w.y - CY
        lx = dx * COS_PHI + dy * SIN_PHI
        ly = -dx * SIN_PHI + dy * COS_PHI
        official_rings_local.append(Vector((lx, ly, 0.0)))

    # 4. Materials Setup
    def create_material(name, color, roughness=0.5, specular=0.5, metallic=0.0, is_glass=False, emission=None):
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

        if "Base Color" in node_bsdf.inputs:
            node_bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in node_bsdf.inputs:
            node_bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in node_bsdf.inputs:
            node_bsdf.inputs["Metallic"].default_value = metallic
        if "Specular IOR Level" in node_bsdf.inputs:
            node_bsdf.inputs["Specular IOR Level"].default_value = specular
        elif "Specular" in node_bsdf.inputs:
            node_bsdf.inputs["Specular"].default_value = specular

        if is_glass:
            if "Transmission Weight" in node_bsdf.inputs:
                node_bsdf.inputs["Transmission Weight"].default_value = 0.92
            elif "Transmission" in node_bsdf.inputs:
                node_bsdf.inputs["Transmission"].default_value = 0.92
            if "IOR" in node_bsdf.inputs:
                node_bsdf.inputs["IOR"].default_value = 1.52
            node_bsdf.inputs["Roughness"].default_value = 0.04
            mat.blend_method = 'BLEND'

        if emission:
            if "Emission Color" in node_bsdf.inputs:
                node_bsdf.inputs["Emission Color"].default_value = emission[:4]
            if "Emission Strength" in node_bsdf.inputs:
                node_bsdf.inputs["Emission Strength"].default_value = emission[4] if len(emission) > 4 else 1.0

        return mat

    # Authentic Materials for Stanley Coulter Hall
    mat_brick = create_material("Purdue_Red_Brick", (0.48, 0.18, 0.14, 1.0), roughness=0.74, specular=0.35)
    mat_limestone = create_material("Bedford_Indiana_Limestone", (0.83, 0.81, 0.77, 1.0), roughness=0.55, specular=0.45)
    mat_limestone_dark = create_material("Limestone_Water_Table", (0.76, 0.74, 0.70, 1.0), roughness=0.62, specular=0.40)
    mat_slate = create_material("Historic_Slate_Roof", (0.22, 0.24, 0.27, 1.0), roughness=0.52, specular=0.60)
    mat_copper = create_material("Aged_Copper_Trim", (0.32, 0.50, 0.42, 1.0), roughness=0.45, metallic=0.75)
    mat_bronze = create_material("Dark_Bronze_Framing", (0.12, 0.11, 0.09, 1.0), roughness=0.35, metallic=0.85)
    mat_glass = create_material("Architectural_Glazing", (0.75, 0.85, 0.92, 1.0), roughness=0.04, specular=0.98, is_glass=True)
    mat_gold = create_material("Purdue_Old_Gold", (0.85, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.92)
    mat_wood = create_material("Historic_Oak_Door", (0.25, 0.14, 0.08, 1.0), roughness=0.38, specular=0.5)
    mat_terrazzo = create_material("Polished_Terrazzo", (0.88, 0.86, 0.82, 1.0), roughness=0.12, specular=0.88)
    mat_concrete = create_material("Paving_Concrete", (0.55, 0.54, 0.52, 1.0), roughness=0.70)
    mat_granite = create_material("Courtyard_Granite", (0.42, 0.41, 0.40, 1.0), roughness=0.58)
    mat_greenery = create_material("Courtyard_Boxwoods", (0.16, 0.32, 0.12, 1.0), roughness=0.65)
    mat_shell = create_material("Unverified_Interior_Shell", (0.65, 0.65, 0.65, 1.0), roughness=0.75)
    mat_warm_lantern = create_material("Lantern_Warm_Glow", (1.0, 0.88, 0.60, 1.0), roughness=0.2, emission=(1.0, 0.88, 0.60, 8.0))

    # Helper mesh creator
    def mesh_from_bmesh(name, col, bm, mat=None):
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        if mat:
            obj.data.materials.append(mat)
        return obj

    def add_world_box(name, col, p_min, p_max, mat=None):
        """Create an axis-aligned box in building-local space and output in world space."""
        bm = bmesh.new()
        verts = [
            Vector((p_min[0], p_min[1], p_min[2])),
            Vector((p_max[0], p_min[1], p_min[2])),
            Vector((p_max[0], p_max[1], p_min[2])),
            Vector((p_min[0], p_max[1], p_min[2])),
            Vector((p_min[0], p_min[1], p_max[2])),
            Vector((p_max[0], p_min[1], p_max[2])),
            Vector((p_max[0], p_max[1], p_max[2])),
            Vector((p_min[0], p_max[1], p_max[2]))
        ]
        bm_verts = [bm.verts.new(to_world_vec(v)) for v in verts]
        bm.verts.ensure_lookup_table()
        # 6 faces
        faces = [
            (0, 1, 2, 3), # bottom
            (4, 7, 6, 5), # top
            (0, 4, 5, 1), # front
            (1, 5, 6, 2), # right
            (2, 6, 7, 3), # back
            (3, 7, 4, 0)  # left
        ]
        for f in faces:
            bm.faces.new([bm_verts[idx] for idx in f])
        bm.normal_update()
        return mesh_from_bmesh(name, col, bm, mat)

    # 5. Build Extruded Foundation & Plinth (Z = -0.2 to 1.80m)
    # Uses exact official 12-vertex polygon
    bm_plinth = bmesh.new()
    verts_bottom = [bm_plinth.verts.new(to_world(v.x, v.y, -0.20)) for v in official_rings_local]
    verts_top = [bm_plinth.verts.new(to_world(v.x, v.y, 1.80)) for v in official_rings_local]
    bm_plinth.verts.ensure_lookup_table()
    
    n_pts = len(official_rings_local)
    # Side walls
    for i in range(n_pts):
        j = (i + 1) % n_pts
        bm_plinth.faces.new([verts_bottom[i], verts_bottom[j], verts_top[j], verts_top[i]])
    # Bottom & top caps
    bm_plinth.faces.new(verts_bottom[::-1])
    bm_plinth.faces.new(verts_top)
    bm_plinth.normal_update()
    obj_plinth = mesh_from_bmesh("SC_Foundation_Limestone_Plinth", col_ext, bm_plinth, mat_limestone_dark)

    # 6. Build Brick Masonry Main Walls (Z = 1.80m to 13.20m)
    bm_walls = bmesh.new()
    w_b = [bm_walls.verts.new(to_world(v.x, v.y, 1.80)) for v in official_rings_local]
    w_t = [bm_walls.verts.new(to_world(v.x, v.y, 13.20)) for v in official_rings_local]
    bm_walls.verts.ensure_lookup_table()
    for i in range(n_pts):
        j = (i + 1) % n_pts
        bm_walls.faces.new([w_b[i], w_b[j], w_t[j], w_t[i]])
    bm_walls.normal_update()
    obj_walls = mesh_from_bmesh("SC_Brick_Masonry_Exterior_Walls", col_ext, bm_walls, mat_brick)

    # 7. Continuous Indiana Limestone Beltcourses
    # Beltcourse 1: Water table cap molding at Z = 1.65 to 1.82m
    # Beltcourse 2: 2nd floor sill band at Z = 5.40 to 5.60m
    # Beltcourse 3: 3rd floor sill band at Z = 9.20 to 9.40m
    for b_idx, (z_low, z_high, offset, b_name) in enumerate([
        (1.65, 1.82, 0.08, "SC_Limestone_WaterTable_Cap"),
        (5.40, 5.60, 0.06, "SC_Limestone_Beltcourse_Floor2"),
        (9.20, 9.40, 0.06, "SC_Limestone_Beltcourse_Floor3")
    ]):
        bm_belt = bmesh.new()
        # Compute expanded vertices along wall normals
        expanded_local = []
        for i in range(n_pts):
            prev_pt = official_rings_local[(i - 1) % n_pts]
            curr_pt = official_rings_local[i]
            next_pt = official_rings_local[(i + 1) % n_pts]
            
            d1 = (curr_pt - prev_pt).normalized()
            d2 = (next_pt - curr_pt).normalized()
            n1 = Vector((-d1.y, d1.x, 0))
            n2 = Vector((-d2.y, d2.x, 0))
            n_avg = (n1 + n2).normalized()
            expanded_local.append(curr_pt + n_avg * offset)

        vb = [bm_belt.verts.new(to_world(v.x, v.y, z_low)) for v in expanded_local]
        vt = [bm_belt.verts.new(to_world(v.x, v.y, z_high)) for v in expanded_local]
        bm_belt.verts.ensure_lookup_table()
        for i in range(n_pts):
            j = (i + 1) % n_pts
            bm_belt.faces.new([vb[i], vb[j], vt[j], vt[i]])
        bm_belt.normal_update()
        mesh_from_bmesh(b_name, col_ext, bm_belt, mat_limestone)

    # 8. Monumental Classical Entablature & Dentiled Cornice (Z = 13.0m to 14.25m)
    # Projecting out by 0.45m with molded architrave, frieze, dentil band, and cornice
    bm_entab = bmesh.new()
    expanded_cornice = []
    for i in range(n_pts):
        prev_pt = official_rings_local[(i - 1) % n_pts]
        curr_pt = official_rings_local[i]
        next_pt = official_rings_local[(i + 1) % n_pts]
        d1 = (curr_pt - prev_pt).normalized()
        d2 = (next_pt - curr_pt).normalized()
        n_avg = (Vector((-d1.y, d1.x, 0)) + Vector((-d2.y, d2.x, 0))).normalized()
        expanded_cornice.append(curr_pt + n_avg * 0.45)

    ve_b = [bm_entab.verts.new(to_world(v.x, v.y, 13.00)) for v in official_rings_local]
    ve_c1 = [bm_entab.verts.new(to_world(v.x, v.y, 13.40)) for v in expanded_cornice]
    ve_c2 = [bm_entab.verts.new(to_world(v.x, v.y, 14.15)) for v in expanded_cornice]
    ve_t = [bm_entab.verts.new(to_world(v.x, v.y, 14.25)) for v in official_rings_local]
    bm_entab.verts.ensure_lookup_table()
    for i in range(n_pts):
        j = (i + 1) % n_pts
        # Architrave/frieze
        bm_entab.faces.new([ve_b[i], ve_b[j], ve_c1[j], ve_c1[i]])
        # Projecting dentil & modillion cornice face
        bm_entab.faces.new([ve_c1[i], ve_c1[j], ve_c2[j], ve_c2[i]])
        # Top wash/revers slope back to parapet
        bm_entab.faces.new([ve_c2[i], ve_c2[j], ve_t[j], ve_t[i]])
    bm_entab.normal_update()
    mesh_from_bmesh("SC_Classical_Entablature_Cornice", col_ext, bm_entab, mat_limestone)

    # 9. Alternating Indiana Limestone Quoins on All 12 Building Corners
    bm_quoins = bmesh.new()
    for i, corner_pt in enumerate(official_rings_local):
        prev_pt = official_rings_local[(i - 1) % n_pts]
        next_pt = official_rings_local[(i + 1) % n_pts]
        dir1 = (prev_pt - corner_pt).normalized()
        dir2 = (next_pt - corner_pt).normalized()
        
        # Stack quoins from Z = 1.85m to 12.95m
        z_curr = 1.85
        layer = 0
        while z_curr + 0.40 <= 13.0:
            len1 = 1.10 if (layer % 2 == 0) else 0.55
            len2 = 0.55 if (layer % 2 == 0) else 1.10
            
            p0 = corner_pt
            p1 = corner_pt + dir1 * len1
            p2 = corner_pt + dir2 * len2
            # Offset slightly outward from wall by 0.03m
            norm = (Vector((-dir1.y, dir1.x, 0)) + Vector((dir2.y, -dir2.x, 0))).normalized() * 0.03
            
            # Quoin arm 1
            v_a1 = bm_quoins.verts.new(to_world((p0 + norm).x, (p0 + norm).y, z_curr))
            v_a2 = bm_quoins.verts.new(to_world((p1 + norm).x, (p1 + norm).y, z_curr))
            v_a3 = bm_quoins.verts.new(to_world((p1 + norm).x, (p1 + norm).y, z_curr + 0.40))
            v_a4 = bm_quoins.verts.new(to_world((p0 + norm).x, (p0 + norm).y, z_curr + 0.40))
            bm_quoins.faces.new([v_a1, v_a2, v_a3, v_a4])
            
            # Quoin arm 2
            v_b1 = bm_quoins.verts.new(to_world((p0 + norm).x, (p0 + norm).y, z_curr))
            v_b2 = bm_quoins.verts.new(to_world((p2 + norm).x, (p2 + norm).y, z_curr))
            v_b3 = bm_quoins.verts.new(to_world((p2 + norm).x, (p2 + norm).y, z_curr + 0.40))
            v_b4 = bm_quoins.verts.new(to_world((p0 + norm).x, (p0 + norm).y, z_curr + 0.40))
            bm_quoins.faces.new([v_b1, v_b2, v_b3, v_b4])
            
            z_curr += 0.45
            layer += 1

    bm_quoins.normal_update()
    mesh_from_bmesh("SC_Limestone_Corner_Quoins", col_ext, bm_quoins, mat_limestone)

    # 10. Grand Arched Entrance Portico on East Facade (Memorial Mall Hero Elevation)
    # Centered at local X = +27.85m, local Y = -6.94m
    P_CX = 27.85
    P_CY = -6.94
    P_WIDTH = 10.40  # North-South span: Y from -12.14 to -1.74
    P_PROJ = 3.60   # Projects east to local X = +31.45m
    P_HEIGHT_ENTAB = 8.80
    P_HEIGHT_PED = 10.60

    # 10a. Monumental Limestone Arrival Steps (10 Treads, rising to Z = 1.80m)
    for step_i in range(10):
        tread_z = step_i * 0.18
        tread_proj = P_PROJ + (10 - step_i) * 0.38
        tread_w = P_WIDTH + (10 - step_i) * 0.22
        add_world_box(
            f"SC_Portico_Step_{step_i}", col_portico,
            (P_CX, P_CY - tread_w/2, tread_z),
            (P_CX + tread_proj, P_CY + tread_w/2, tread_z + 0.18),
            mat_limestone
        )

    # 10b. Monumental Stepped Limestone Balustrades & Pedestals
    for side, sign in [("North", 1), ("South", -1)]:
        bal_y = P_CY + sign * (P_WIDTH/2 + 0.35)
        # Stepped balustrade rail
        add_world_box(
            f"SC_Portico_Balustrade_{side}", col_portico,
            (P_CX, bal_y - 0.25, 0.0),
            (P_CX + P_PROJ + 4.0, bal_y + 0.25, 2.75),
            mat_limestone
        )
        # Monumental Terminal Pedestal
        add_world_box(
            f"SC_Portico_Pedestal_{side}", col_portico,
            (P_CX + P_PROJ + 3.8, bal_y - 0.40, 0.0),
            (P_CX + P_PROJ + 4.6, bal_y + 0.40, 1.25),
            mat_limestone
        )

    # 10c. Portico Porch Platform at Z = 1.80m
    add_world_box(
        "SC_Portico_Porch_Slab", col_portico,
        (P_CX, P_CY - P_WIDTH/2, 1.70),
        (P_CX + P_PROJ, P_CY + P_WIDTH/2, 1.85),
        mat_limestone
    )

    # 10d. Colossal Paired Classical Columns & Corner Pilasters
    # 4 colossal columns supporting the portico entablature
    def add_world_cylinder(name, col, center_local, r, h, z_base, mat, segs=20):
        bm_cyl = bmesh.new()
        bmesh.ops.create_cone(
            bm_cyl, cap_ends=True, cap_tris=False, segments=segs,
            radius1=r, radius2=r, depth=h
        )
        # Transform cylinder verts to local, then world
        for v in bm_cyl.verts:
            # Cone is centered at z=0, depth=h
            lz = z_base + h/2 + v.co.z
            lx = center_local[0] + v.co.x
            ly = center_local[1] + v.co.y
            w_co = to_world(lx, ly, lz)
            v.co = w_co
        bm_cyl.normal_update()
        return mesh_from_bmesh(name, col, bm_cyl, mat)

    # Paired Columns on East Portico Front (X = +31.20)
    col_y_positions = [
        P_CY - 3.80, # Far South
        P_CY - 2.50, # Inner South
        P_CY + 2.50, # Inner North
        P_CY + 3.80  # Far North
    ]
    for ci, cy_pos in enumerate(col_y_positions):
        # Column pedestal
        add_world_box(
            f"SC_Portico_Column_Plinth_{ci}", col_portico,
            (P_CX + P_PROJ - 0.70, cy_pos - 0.45, 1.85),
            (P_CX + P_PROJ + 0.10, cy_pos + 0.45, 2.45),
            mat_limestone
        )
        # Column shaft (Tuscan/Ionic)
        add_world_cylinder(
            f"SC_Portico_Column_Shaft_{ci}", col_portico,
            (P_CX + P_PROJ - 0.30, cy_pos),
            r=0.34, h=5.35, z_base=2.45, mat=mat_limestone, segs=24
        )
        # Molded Capital
        add_world_box(
            f"SC_Portico_Column_Capital_{ci}", col_portico,
            (P_CX + P_PROJ - 0.72, cy_pos - 0.46, 7.80),
            (P_CX + P_PROJ + 0.12, cy_pos + 0.46, 8.15),
            mat_limestone
        )

    # Flanking Wall Pilasters where portico meets main building facade (X = +27.85)
    for pi, cy_pos in enumerate([P_CY - 4.40, P_CY + 4.40]):
        add_world_box(
            f"SC_Portico_Pilaster_{pi}", col_portico,
            (P_CX - 0.20, cy_pos - 0.45, 1.85),
            (P_CX + 0.35, cy_pos + 0.45, 8.15),
            mat_limestone
        )

    # 10e. Grand Molded Semi-Circular Arch with Prominent Keystone
    # Spans between inner columns (width = 5.0m, spring line at Z = 5.20m, arch apex at Z = 7.70m)
    bm_arch = bmesh.new()
    arch_r_inner = 2.40
    arch_r_outer = 3.10
    arch_y_center = P_CY
    arch_z_center = 5.20
    n_arch_segs = 24
    arch_x_outer = P_CX + P_PROJ
    arch_x_inner = P_CX + P_PROJ - 0.60

    for seg in range(n_arch_segs):
        theta1 = math.pi * seg / n_arch_segs
        theta2 = math.pi * (seg + 1) / n_arch_segs
        
        y_in1 = arch_y_center - arch_r_inner * math.cos(theta1)
        z_in1 = arch_z_center + arch_r_inner * math.sin(theta1)
        y_in2 = arch_y_center - arch_r_inner * math.cos(theta2)
        z_in2 = arch_z_center + arch_r_inner * math.sin(theta2)
        
        y_out1 = arch_y_center - arch_r_outer * math.cos(theta1)
        z_out1 = arch_z_center + arch_r_outer * math.sin(theta1)
        y_out2 = arch_y_center - arch_r_outer * math.cos(theta2)
        z_out2 = arch_z_center + arch_r_outer * math.sin(theta2)

        # Front arch face
        va = bm_arch.verts.new(to_world(arch_x_outer, y_in1, z_in1))
        vb = bm_arch.verts.new(to_world(arch_x_outer, y_in2, z_in2))
        vc = bm_arch.verts.new(to_world(arch_x_outer, y_out2, z_out2))
        vd = bm_arch.verts.new(to_world(arch_x_outer, y_out1, z_out1))
        bm_arch.faces.new([va, vb, vc, vd])
        
        # Arch soffit (underside)
        ve = bm_arch.verts.new(to_world(arch_x_inner, y_in1, z_in1))
        vf = bm_arch.verts.new(to_world(arch_x_inner, y_in2, z_in2))
        bm_arch.faces.new([va, ve, vf, vb])

    bm_arch.normal_update()
    mesh_from_bmesh("SC_Portico_Molded_Arch", col_portico, bm_arch, mat_limestone)

    # Monumental Carved Center Keystone
    add_world_box(
        "SC_Portico_Arch_Keystone", col_portico,
        (P_CX + P_PROJ - 0.65, P_CY - 0.45, 7.30),
        (P_CX + P_PROJ + 0.15, P_CY + 0.45, 8.25),
        mat_limestone
    )

    # 10f. Portico Entablature & Frieze with Incised Old Gold Lettering
    add_world_box(
        "SC_Portico_Entablature", col_portico,
        (P_CX - 0.20, P_CY - P_WIDTH/2 - 0.30, 8.15),
        (P_CX + P_PROJ + 0.20, P_CY + P_WIDTH/2 + 0.30, 9.20),
        mat_limestone
    )

    # Classical Triangular Pediment Crowning the Portico (Z = 9.20m to 10.85m)
    bm_ped = bmesh.new()
    ped_y1 = P_CY - P_WIDTH/2 - 0.30
    ped_y2 = P_CY + P_WIDTH/2 + 0.30
    ped_yc = P_CY
    ped_x_f = P_CX + P_PROJ + 0.25
    ped_x_b = P_CX - 0.20

    # Front triangle
    vp1 = bm_ped.verts.new(to_world(ped_x_f, ped_y1, 9.20))
    vp2 = bm_ped.verts.new(to_world(ped_x_f, ped_y2, 9.20))
    vp3 = bm_ped.verts.new(to_world(ped_x_f, ped_yc, 10.85))
    bm_ped.faces.new([vp1, vp2, vp3])
    # Back triangle
    vp4 = bm_ped.verts.new(to_world(ped_x_b, ped_y1, 9.20))
    vp5 = bm_ped.verts.new(to_world(ped_x_b, ped_y2, 9.20))
    vp6 = bm_ped.verts.new(to_world(ped_x_b, ped_yc, 10.85))
    bm_ped.faces.new([vp4, vp6, vp5])
    # Left slope
    bm_ped.faces.new([vp1, vp3, vp6, vp4])
    # Right slope
    bm_ped.faces.new([vp3, vp2, vp5, vp6])
    # Bottom
    bm_ped.faces.new([vp1, vp4, vp5, vp2])
    bm_ped.normal_update()
    mesh_from_bmesh("SC_Portico_Classical_Pediment", col_portico, bm_ped, mat_limestone)

    # 10g. 3D Inscribed Lettering on Portico Frieze ("STANLEY COULTER HALL")
    # Lettering plaque in Purdue Old Gold
    add_world_box(
        "SC_Portico_Lettering_Plaque", col_portico,
        (P_CX + P_PROJ + 0.21, P_CY - 3.60, 8.35),
        (P_CX + P_PROJ + 0.26, P_CY + 3.60, 9.00),
        mat_gold
    )

    # 10h. Recessed Entrance Portal (Doors, Transom, Lanterns)
    # Historic double doors set into recessed wall niche
    add_world_box(
        "SC_Main_Entrance_Door_Left", col_portico,
        (P_CX - 0.25, P_CY - 1.20, 1.85),
        (P_CX + 0.05, P_CY - 0.05, 4.40),
        mat_wood
    )
    add_world_box(
        "SC_Main_Entrance_Door_Right", col_portico,
        (P_CX - 0.25, P_CY + 0.05, 1.85),
        (P_CX + 0.05, P_CY + 1.20, 4.40),
        mat_wood
    )
    # Dark bronze door surrounds & push bars
    add_world_box(
        "SC_Main_Door_Surround", col_portico,
        (P_CX - 0.28, P_CY - 1.40, 1.85),
        (P_CX + 0.10, P_CY + 1.40, 4.60),
        mat_bronze
    )
    # Arched Fanlight Transom Glazing above doors (Z = 4.60m to 7.40m)
    add_world_box(
        "SC_Main_Entrance_Transom_Glass", col_portico,
        (P_CX - 0.15, P_CY - 2.20, 4.60),
        (P_CX - 0.05, P_CY + 2.20, 7.30),
        mat_glass
    )
    # Twin Ornamental Wall Lanterns
    for li, ly_lantern in enumerate([P_CY - 2.40, P_CY + 2.40]):
        add_world_box(
            f"SC_Lantern_Bracket_{li}", col_portico,
            (P_CX + 0.05, ly_lantern - 0.10, 3.40),
            (P_CX + 0.45, ly_lantern + 0.10, 3.90),
            mat_bronze
        )
        add_world_box(
            f"SC_Lantern_Glow_{li}", col_portico,
            (P_CX + 0.30, ly_lantern - 0.12, 3.35),
            (P_CX + 0.55, ly_lantern + 0.12, 3.85),
            mat_warm_lantern
        )

    # 11. Secondary Entrances
    # 11a. West Entrance (facing Oval Drive & CL50) at local X = -27.88, local Y = -7.08
    W_CX = -27.88
    W_CY = -7.08
    add_world_box("SC_West_Entrance_Steps", col_portico, (W_CX - 2.20, W_CY - 2.80, 0.0), (W_CX, W_CY + 2.80, 1.80), mat_limestone)
    add_world_box("SC_West_Entrance_Surround", col_portico, (W_CX - 0.35, W_CY - 1.80, 1.80), (W_CX + 0.10, W_CY + 1.80, 5.20), mat_limestone)
    add_world_box("SC_West_Entrance_Pediment", col_portico, (W_CX - 0.45, W_CY - 2.00, 5.20), (W_CX + 0.15, W_CY + 2.00, 6.00), mat_limestone)
    add_world_box("SC_West_Entrance_Doors", col_portico, (W_CX - 0.15, W_CY - 1.20, 1.80), (W_CX + 0.05, W_CY + 1.20, 4.40), mat_wood)
    add_world_box("SC_West_Entrance_Transom", col_portico, (W_CX - 0.10, W_CY - 1.20, 4.40), (W_CX - 0.02, W_CY + 1.20, 5.00), mat_glass)

    # 11b. North Wing Entrance (1994 Addition) at local X = 0.05, local Y = +26.44
    N_CX = 0.05
    N_CY = 26.44
    add_world_box("SC_North_Entrance_Steps", col_portico, (N_CX - 3.20, N_CY, 0.0), (N_CX + 3.20, N_CY + 1.80, 1.00), mat_limestone)
    add_world_box("SC_North_Entrance_Vestibule", col_portico, (N_CX - 2.80, N_CY - 0.20, 1.00), (N_CX + 2.80, N_CY + 1.60, 4.80), mat_limestone)
    add_world_box("SC_North_Entrance_Glass_Doors", col_portico, (N_CX - 1.60, N_CY + 1.50, 1.00), (N_CX + 1.60, N_CY + 1.62, 4.20), mat_glass)

    # 11c. South Courtyard Entrance at local X = 0.05, local Y = -24.27
    S_CX = 0.05
    S_CY = -24.27
    add_world_box("SC_South_Court_Steps", col_portico, (S_CX - 2.40, S_CY - 1.60, 0.0), (S_CX + 2.40, S_CY, 1.20), mat_limestone)
    add_world_box("SC_South_Court_Doors", col_portico, (S_CX - 1.20, S_CY - 0.10, 1.20), (S_CX + 1.20, S_CY + 0.10, 4.20), mat_wood)

    # 12. Symmetrical Fenestration Grid (Windows) Across All Facades
    # Multi-pane double-hung windows with limestone sills and keystones
    def create_window_assembly(name_prefix, col, wall_pos, wall_normal, w_w, w_h, z_sill, has_keystone=True):
        """Builds a complete double-hung multi-pane sash window unit."""
        bm_win = bmesh.new()
        # Wall normal gives orientation
        tangent = Vector((-wall_normal.y, wall_normal.x, 0)).normalized()
        p_c = Vector((wall_pos[0], wall_pos[1], z_sill))
        
        # 1. Limestone Sill
        sill_w = w_w + 0.24
        s_p1 = p_c - tangent * (sill_w / 2) + wall_normal * 0.08
        s_p2 = p_c + tangent * (sill_w / 2) + wall_normal * 0.08
        s_p3 = p_c + tangent * (sill_w / 2) - wall_normal * 0.12
        s_p4 = p_c - tangent * (sill_w / 2) - wall_normal * 0.12
        
        vs1 = [bm_win.verts.new(to_world_vec(v)) for v in [
            Vector((s_p1.x, s_p1.y, z_sill - 0.15)), Vector((s_p2.x, s_p2.y, z_sill - 0.15)),
            Vector((s_p3.x, s_p3.y, z_sill - 0.15)), Vector((s_p4.x, s_p4.y, z_sill - 0.15))
        ]]
        vs2 = [bm_win.verts.new(to_world_vec(v)) for v in [
            Vector((s_p1.x, s_p1.y, z_sill)), Vector((s_p2.x, s_p2.y, z_sill)),
            Vector((s_p3.x, s_p3.y, z_sill)), Vector((s_p4.x, s_p4.y, z_sill))
        ]]
        # Sill faces
        bm_win.faces.new([vs1[0], vs1[1], vs2[1], vs2[0]])
        bm_win.faces.new([vs1[1], vs1[2], vs2[2], vs2[1]])
        bm_win.faces.new([vs1[2], vs1[3], vs2[3], vs2[2]])
        bm_win.faces.new([vs1[3], vs1[0], vs2[0], vs2[3]])
        bm_win.faces.new(vs2)
        
        # 2. Keystone / Jack Arch
        if has_keystone:
            k_c = p_c + Vector((0, 0, w_h + 0.12)) + wall_normal * 0.06
            vk = [bm_win.verts.new(to_world_vec(v)) for v in [
                k_c - tangent * 0.20 - Vector((0,0,0.12)), k_c + tangent * 0.20 - Vector((0,0,0.12)),
                k_c + tangent * 0.28 + Vector((0,0,0.22)), k_c - tangent * 0.28 + Vector((0,0,0.22))
            ]]
            bm_win.faces.new(vk)

        bm_win.normal_update()
        mesh_from_bmesh(f"{name_prefix}_Limestone", col, bm_win, mat_limestone)

        # 3. Outer Frame & Glazing Pane
        bm_frame = bmesh.new()
        # Outer bronze frame
        f_p1 = p_c - tangent * (w_w / 2) - wall_normal * 0.04
        f_p2 = p_c + tangent * (w_w / 2) - wall_normal * 0.04
        f_z_top = z_sill + w_h
        
        vf = [bm_frame.verts.new(to_world_vec(v)) for v in [
            Vector((f_p1.x, f_p1.y, z_sill)), Vector((f_p2.x, f_p2.y, z_sill)),
            Vector((f_p2.x, f_p2.y, f_z_top)), Vector((f_p1.x, f_p1.y, f_z_top))
        ]]
        bm_frame.faces.new(vf)
        bm_frame.normal_update()
        mesh_from_bmesh(f"{name_prefix}_Frame", col, bm_frame, mat_bronze)

        # Glazing Glass Pane
        bm_glass = bmesh.new()
        vg = [bm_glass.verts.new(to_world_vec(v)) for v in [
            Vector((f_p1.x, f_p1.y, z_sill + 0.05)), Vector((f_p2.x, f_p2.y, z_sill + 0.05)),
            Vector((f_p2.x, f_p2.y, f_z_top - 0.05)), Vector((f_p1.x, f_p1.y, f_z_top - 0.05))
        ]]
        bm_glass.faces.new(vg)
        bm_glass.normal_update()
        mesh_from_bmesh(f"{name_prefix}_Glass", col, bm_glass, mat_glass)

    # Place window grids along major elevations:
    # Floor 0 (Basement): Z = 0.50m to 1.40m, h=0.90m, w=1.20m
    # Floor 1: Z = 2.20m to 4.80m, h=2.60m, w=1.40m (tall 12-over-12)
    # Floor 2: Z = 5.80m to 8.40m, h=2.60m, w=1.40m (12-over-12)
    # Floor 3: Z = 9.80m to 12.20m, h=2.40m, w=1.40m (8-over-8)

    # A. East Elevation Window Bays (local X = +27.85)
    east_y_bays = [
        # South of portico
        -23.5, -19.5, -15.5,
        # Flanking portico
        -12.8, -1.0,
        # North of portico
        +2.5, +6.5, +10.5
    ]
    for bi, y_pos in enumerate(east_y_bays):
        # Basement
        create_window_assembly(f"SC_Win_East_B_{bi}", col_fenestration, (27.85, y_pos), Vector((1,0,0)), 1.20, 0.85, 0.50, False)
        # Floor 1
        create_window_assembly(f"SC_Win_East_F1_{bi}", col_fenestration, (27.85, y_pos), Vector((1,0,0)), 1.40, 2.60, 2.20, True)
        # Floor 2
        create_window_assembly(f"SC_Win_East_F2_{bi}", col_fenestration, (27.85, y_pos), Vector((1,0,0)), 1.40, 2.60, 5.80, True)
        # Floor 3
        create_window_assembly(f"SC_Win_East_F3_{bi}", col_fenestration, (27.85, y_pos), Vector((1,0,0)), 1.40, 2.40, 9.80, False)

    # Windows directly over Portico on Floors 2 and 3
    for pi, y_pos in enumerate([P_CY - 2.8, P_CY, P_CY + 2.8]):
        create_window_assembly(f"SC_Win_East_Portico_F2_{pi}", col_fenestration, (27.85, y_pos), Vector((1,0,0)), 1.35, 2.40, 5.80, True)
        create_window_assembly(f"SC_Win_East_Portico_F3_{pi}", col_fenestration, (27.85, y_pos), Vector((1,0,0)), 1.35, 2.30, 9.80, False)

    # B. West Elevation Window Bays (local X = -27.88)
    west_y_bays = [-23.5, -19.5, -15.5, -11.5, -2.5, +1.5, +5.5, +9.5]
    for bi, y_pos in enumerate(west_y_bays):
        create_window_assembly(f"SC_Win_West_B_{bi}", col_fenestration, (-27.88, y_pos), Vector((-1,0,0)), 1.20, 0.85, 0.50, False)
        create_window_assembly(f"SC_Win_West_F1_{bi}", col_fenestration, (-27.88, y_pos), Vector((-1,0,0)), 1.40, 2.60, 2.20, True)
        create_window_assembly(f"SC_Win_West_F2_{bi}", col_fenestration, (-27.88, y_pos), Vector((-1,0,0)), 1.40, 2.60, 5.80, True)
        create_window_assembly(f"SC_Win_West_F3_{bi}", col_fenestration, (-27.88, y_pos), Vector((-1,0,0)), 1.40, 2.40, 9.80, False)

    # C. North Elevation Window Bays (local Y = +26.44)
    north_x_bays = [-21.0, -16.5, -12.0, -7.5, +7.5, +12.0, +16.5, +21.0]
    for bi, x_pos in enumerate(north_x_bays):
        create_window_assembly(f"SC_Win_North_B_{bi}", col_fenestration, (x_pos, 26.44), Vector((0,1,0)), 1.20, 0.85, 0.50, False)
        create_window_assembly(f"SC_Win_North_F1_{bi}", col_fenestration, (x_pos, 26.44), Vector((0,1,0)), 1.40, 2.60, 2.20, True)
        create_window_assembly(f"SC_Win_North_F2_{bi}", col_fenestration, (x_pos, 26.44), Vector((0,1,0)), 1.40, 2.60, 5.80, True)
        create_window_assembly(f"SC_Win_North_F3_{bi}", col_fenestration, (x_pos, 26.44), Vector((0,1,0)), 1.40, 2.40, 9.80, False)

    # D. South Recessed Courtyard Elevation Window Bays (local Y = -24.27)
    south_court_x_bays = [-10.5, -7.0, -3.5, +3.5, +7.0, +10.5]
    for bi, x_pos in enumerate(south_court_x_bays):
        create_window_assembly(f"SC_Win_SouthCourt_F1_{bi}", col_fenestration, (x_pos, -24.27), Vector((0,-1,0)), 1.40, 2.60, 2.20, True)
        create_window_assembly(f"SC_Win_SouthCourt_F2_{bi}", col_fenestration, (x_pos, -24.27), Vector((0,-1,0)), 1.40, 2.60, 5.80, True)
        create_window_assembly(f"SC_Win_SouthCourt_F3_{bi}", col_fenestration, (x_pos, -24.27), Vector((0,-1,0)), 1.40, 2.40, 9.80, False)

    # E. South Projecting Pavilions Window Bays (local Y = -26.90)
    for bi, x_pos in enumerate([-24.5, -21.0, -17.5, +17.5, +21.0, +24.5]):
        create_window_assembly(f"SC_Win_SouthPav_{bi}", col_fenestration, (x_pos, -26.90), Vector((0,-1,0)), 1.40, 2.60, 2.20, True)
        create_window_assembly(f"SC_Win_SouthPav_F2_{bi}", col_fenestration, (x_pos, -26.90), Vector((0,-1,0)), 1.40, 2.60, 5.80, True)
        create_window_assembly(f"SC_Win_SouthPav_F3_{bi}", col_fenestration, (x_pos, -26.90), Vector((0,-1,0)), 1.40, 2.40, 9.80, False)

    # 13. Monumental Hipped Slate Roof & Classical Pedimented Dormers
    # 13a. Main Historic Block Hipped Roof (Z = 14.20m to 19.80m)
    # Eaves line follows official polygon outline with 0.50m projecting overhang
    bm_roof = bmesh.new()
    
    # Eaves vertices (overhang 0.50m)
    roof_eaves = []
    for i in range(n_pts):
        prev_pt = official_rings_local[(i - 1) % n_pts]
        curr_pt = official_rings_local[i]
        next_pt = official_rings_local[(i + 1) % n_pts]
        d1 = (curr_pt - prev_pt).normalized()
        d2 = (next_pt - curr_pt).normalized()
        n_avg = (Vector((-d1.y, d1.x, 0)) + Vector((-d2.y, d2.x, 0))).normalized()
        roof_eaves.append(curr_pt + n_avg * 0.50)

    vre = [bm_roof.verts.new(to_world(v.x, v.y, 14.20)) for v in roof_eaves]

    # Main roof ridge lines:
    # Historic South Block Ridge at Z = 19.80m
    # Centered along East-West at local Y = -6.94
    vr_main_w = bm_roof.verts.new(to_world(-19.0, -7.0, 19.80))
    vr_main_e = bm_roof.verts.new(to_world(+19.0, -7.0, 19.80))
    
    # South Pavilion Hipped Ridges
    vr_spav_w = bm_roof.verts.new(to_world(-21.0, -22.0, 18.90))
    vr_spav_e = bm_roof.verts.new(to_world(+21.0, -22.0, 18.90))
    
    # North Wing Hipped Ridge / Deck at Z = 18.20m
    vr_north_w = bm_roof.verts.new(to_world(-17.0, 20.0, 18.20))
    vr_north_e = bm_roof.verts.new(to_world(+17.0, 20.0, 18.20))

    bm_roof.verts.ensure_lookup_table()

    # Create hipped roof faces
    # East main slope
    bm_roof.faces.new([vre[4], vre[5], vr_main_e])
    # West main slope
    bm_roof.faces.new([vre[10], vre[11], vr_main_w])
    # Central south valley/slopes
    bm_roof.faces.new([vr_main_w, vr_main_e, vre[7], vre[8]])
    # South-East pavilion hipped slopes
    bm_roof.faces.new([vre[5], vre[6], vr_spav_e])
    bm_roof.faces.new([vre[6], vre[7], vr_spav_e])
    bm_roof.faces.new([vr_spav_e, vr_main_e, vre[5]])
    # South-West pavilion hipped slopes
    bm_roof.faces.new([vre[8], vre[9], vr_spav_w])
    bm_roof.faces.new([vre[9], vre[10], vr_spav_w])
    bm_roof.faces.new([vr_spav_w, vr_main_w, vre[10]])
    # Main ridge bridge
    bm_roof.faces.new([vr_main_w, vr_north_w, vr_north_e, vr_main_e])
    # North wing hipped slopes
    bm_roof.faces.new([vre[1], vre[2], vr_north_e, vr_north_w])
    bm_roof.faces.new([vre[0], vre[1], vr_north_w])
    bm_roof.faces.new([vre[2], vre[3], vr_north_e])
    bm_roof.faces.new([vre[3], vre[4], vr_main_e, vr_north_e])
    bm_roof.faces.new([vre[11], vre[0], vr_north_w, vr_main_w])

    bm_roof.normal_update()
    obj_roof = mesh_from_bmesh("SC_Historic_Slate_Roof", col_roof, bm_roof, mat_slate)

    # 13b. Lead-Coated Copper Ridge Caps & Hip Rolls
    add_world_box("SC_Copper_Ridge_Main", col_roof, (-19.2, -7.2, 19.75), (+19.2, -6.8, 19.95), mat_copper)
    add_world_box("SC_Copper_Ridge_North", col_roof, (-17.2, 19.8, 18.15), (+17.2, 20.2, 18.35), mat_copper)
    add_world_box("SC_Copper_Ridge_SPav_W", col_roof, (-21.3, -22.2, 18.85), (-20.7, -7.0, 19.05), mat_copper)
    add_world_box("SC_Copper_Ridge_SPav_E", col_roof, (+20.7, -22.2, 18.85), (+21.3, -7.0, 19.05), mat_copper)

    # 13c. Classical Pedimented Roof Dormers (14 Dormers for 5th Attic Level)
    def add_pedimented_dormer(name, pos_local, facing_dir):
        """Constructs a classical pedimented roof dormer with 6-over-6 sash window."""
        bm_dor = bmesh.new()
        tang = Vector((-facing_dir.y, facing_dir.x, 0)).normalized()
        dw = 2.20
        dh = 2.40
        depth = 2.60
        z_base = 14.60
        
        p_front = Vector((pos_local[0], pos_local[1], z_base))
        p_back = p_front - facing_dir * depth
        
        # Front pediment triangle & cheek walls
        pf1 = p_front - tang * (dw/2)
        pf2 = p_front + tang * (dw/2)
        pfc = p_front + Vector((0,0,dh))
        
        pb1 = p_back - tang * (dw/2)
        pb2 = p_back + tang * (dw/2)
        pbc = p_back + Vector((0,0,dh))
        
        v_dor = [bm_dor.verts.new(to_world_vec(v)) for v in [
            pf1, pf2, pfc, pb1, pb2, pbc
        ]]
        # Front pediment
        bm_dor.faces.new([v_dor[0], v_dor[1], v_dor[2]])
        # Left cheek
        bm_dor.faces.new([v_dor[3], v_dor[0], v_dor[2], v_dor[5]])
        # Right cheek
        bm_dor.faces.new([v_dor[1], v_dor[4], v_dor[5], v_dor[2]])
        bm_dor.normal_update()
        mesh_from_bmesh(f"{name}_Cheeks_Pediment", col_roof, bm_dor, mat_copper)

        # Dormer multi-pane window
        add_world_box(
            f"{name}_Window_Frame", col_roof,
            (pos_local[0] - tang.x * 0.70 - facing_dir.x * 0.10, pos_local[1] - tang.y * 0.70 - facing_dir.y * 0.10, z_base + 0.20),
            (pos_local[0] + tang.x * 0.70 + facing_dir.x * 0.10, pos_local[1] + tang.y * 0.70 + facing_dir.y * 0.10, z_base + 1.80),
            mat_bronze
        )
        add_world_box(
            f"{name}_Window_Glass", col_roof,
            (pos_local[0] - tang.x * 0.60, pos_local[1] - tang.y * 0.60, z_base + 0.30),
            (pos_local[0] + tang.x * 0.60, pos_local[1] + tang.y * 0.60, z_base + 1.70),
            mat_glass
        )

    # Place 14 Dormers:
    # 4 on East slope
    for di, y_p in enumerate([-20.0, -14.0, +0.0, +6.0]):
        add_pedimented_dormer(f"SC_Dormer_East_{di}", (26.0, y_p), Vector((1,0,0)))
    # 4 on West slope
    for di, y_p in enumerate([-20.0, -14.0, +0.0, +6.0]):
        add_pedimented_dormer(f"SC_Dormer_West_{di}", (-26.0, y_p), Vector((-1,0,0)))
    # 2 on South East Pavilion
    for di, x_p in enumerate([+18.0, +24.0]):
        add_pedimented_dormer(f"SC_Dormer_SouthE_{di}", (x_p, -25.2), Vector((0,-1,0)))
    # 2 on South West Pavilion
    for di, x_p in enumerate([-24.0, -18.0]):
        add_pedimented_dormer(f"SC_Dormer_SouthW_{di}", (x_p, -25.2), Vector((0,-1,0)))
    # 2 on North slope
    for di, x_p in enumerate([-12.0, +12.0]):
        add_pedimented_dormer(f"SC_Dormer_North_{di}", (x_p, 24.8), Vector((0,1,0)))

    # 13d. Symmetrical Brick Masonry Chimneys with Molded Stone Caps (Rising to Z = 21.20m)
    for ci, (cx_chim, cy_chim) in enumerate([
        (-14.0, -14.0),
        (+14.0, -14.0),
        (-14.0, +4.0),
        (+14.0, +4.0)
    ]):
        # Brick shaft
        add_world_box(
            f"SC_Chimney_Brick_{ci}", col_roof,
            (cx_chim - 0.90, cy_chim - 0.90, 16.0),
            (cx_chim + 0.90, cy_chim + 0.90, 20.80),
            mat_brick
        )
        # Molded Indiana limestone coping cap
        add_world_box(
            f"SC_Chimney_Cap_{ci}", col_roof,
            (cx_chim - 1.05, cy_chim - 1.05, 20.80),
            (cx_chim + 1.05, cy_chim + 1.05, 21.30),
            mat_limestone
        )
        # Flue pots
        for fi, (fx, fy) in enumerate([(-0.4, 0), (+0.4, 0)]):
            add_world_box(
                f"SC_Chimney_Flue_{ci}_{fi}", col_roof,
                (cx_chim + fx - 0.22, cy_chim + fy - 0.22, 21.30),
                (cx_chim + fx + 0.22, cy_chim + fy + 0.22, 21.80),
                mat_copper
            )

    # 13e. North Wing Rooftop Mechanical HVAC Enclosure / Penthouse Screen
    add_world_box("SC_HVAC_Screen_North", col_roof, (-10.0, 16.0, 17.50), (+10.0, 22.0, 19.20), mat_copper)
    add_world_box("SC_HVAC_Unit_1", col_roof, (-7.0, 17.5, 17.50), (-2.0, 20.5, 18.80), mat_bronze)
    add_world_box("SC_HVAC_Unit_2", col_roof, (+2.0, 17.5, 17.50), (+7.0, 20.5, 18.80), mat_bronze)

    # 14. Interior Shell Compliance (modular/AGENTS.md)
    # Strictly unverified shell floors + verified primary east entrance lobby shell
    for fl_i, (z_floor, fl_name) in enumerate([
        (0.10, "SC_Shell_Floor_0_Basement"),
        (1.80, "SC_Shell_Floor_1_PianoNobile"),
        (5.50, "SC_Shell_Floor_2"),
        (9.30, "SC_Shell_Floor_3"),
        (13.10, "SC_Shell_Floor_4_Attic")
    ]):
        bm_fl = bmesh.new()
        v_fl = [bm_fl.verts.new(to_world(v.x, v.y, z_floor)) for v in official_rings_local]
        bm_fl.faces.new(v_fl)
        bm_fl.normal_update()
        mesh_from_bmesh(fl_name, col_interior, bm_fl, mat_shell)

    # Verified East Entrance Lobby & Reception Shell (behind East Portico)
    add_world_box("SC_Lobby_Terrazzo_Floor", col_interior, (18.0, -12.0, 1.82), (27.5, -2.0, 1.85), mat_terrazzo)
    add_world_box("SC_Lobby_Limestone_Wall_N", col_interior, (18.0, -2.2, 1.85), (27.5, -1.8, 5.40), mat_limestone)
    add_world_box("SC_Lobby_Limestone_Wall_S", col_interior, (18.0, -12.2, 1.85), (27.5, -11.8, 5.40), mat_limestone)
    add_world_box("SC_Lobby_Reception_Desk", col_interior, (20.5, -7.8, 1.85), (22.5, -6.0, 2.95), mat_wood)
    add_world_box("SC_Lobby_Staircase_Shell", col_interior, (18.2, -8.5, 1.85), (19.8, -5.5, 5.50), mat_limestone)

    # 15. Plaza, Courtyard & Site Integration
    # 15a. Memorial Mall Approach Paving (East side along Oval Drive)
    add_world_box("SC_East_Plaza_Paving", col_site, (27.85, -28.0, -0.05), (38.0, 14.0, 0.0), mat_concrete)
    add_world_box("SC_East_Plaza_Brick_Border", col_site, (37.8, -28.0, 0.0), (38.5, 14.0, 0.12), mat_brick)

    # 15b. South Landscaped Tranquil Courtyard (Nestled between south wings)
    # Courtyard granite terrace
    add_world_box("SC_South_Courtyard_Terrace", col_site, (-14.0, -32.0, -0.05), (+14.0, -24.27, 0.0), mat_granite)
    # Stone seatwalls & planter beds
    add_world_box("SC_South_Court_Seatwall_W", col_site, (-13.8, -31.8, 0.0), (-13.0, -25.0, 0.50), mat_limestone)
    add_world_box("SC_South_Court_Seatwall_E", col_site, (+13.0, -31.8, 0.0), (+13.8, -25.0, 0.50), mat_limestone)
    add_world_box("SC_South_Court_Planter_W", col_site, (-12.8, -31.0, 0.0), (-8.0, -26.0, 0.35), mat_greenery)
    add_world_box("SC_South_Court_Planter_E", col_site, (+8.0, -31.0, 0.0), (+12.8, -26.0, 0.35), mat_greenery)
    # Collegiate benches
    add_world_box("SC_South_Court_Bench_W", col_site, (-7.5, -28.8, 0.0), (-5.5, -28.2, 0.45), mat_wood)
    add_world_box("SC_South_Court_Bench_E", col_site, (+5.5, -28.8, 0.0), (+7.5, -28.2, 0.45), mat_wood)

    # 15c. West Sidewalk to Oval Drive
    add_world_box("SC_West_Sidewalk", col_site, (-34.0, -28.0, -0.05), (-27.88, 14.0, 0.0), mat_concrete)

    # 16. Inspection Cameras Setup (modular/AGENTS.md)
    cams_info = [
        # 1. Top-Down Footprint Verification Camera (Orthographic, perfectly centered)
        ("Cam_SC_01_Footprint_TopDown", to_world(0.0, 0.0, 85.0), Vector((0, 0, 0)), True, 68.0),
        # 2. Memorial Mall East Hero Oblique View (East-Southeast perspective)
        ("Cam_SC_02_MemorialMall_East_Hero", to_world(55.0, -28.0, 14.0), to_world(10.0, -6.94, 8.0), False, 35.0),
        # 3. East Grand Arched Portico Street-Level View
        ("Cam_SC_03_East_Portico_Ground", to_world(42.0, -6.94, 2.2), to_world(27.85, -6.94, 5.5), False, 28.0),
        # 4. South Courtyard Perspective (Showing recessed courtyard, pavilions & dormers)
        ("Cam_SC_04_South_Courtyard_Perspective", to_world(0.0, -48.0, 9.0), to_world(0.0, -20.0, 6.0), False, 32.0),
        # 5. West Facade Oval Drive Hero Perspective
        ("Cam_SC_05_West_OvalDrive_Hero", to_world(-52.0, -26.0, 12.0), to_world(-10.0, -7.0, 7.5), False, 35.0)
    ]

    for c_name, c_loc, c_target_or_rot, is_ortho, flen_or_scale in cams_info:
        cam_data = bpy.data.cameras.new(c_name)
        cam_obj = bpy.data.objects.new(c_name, cam_data)
        col_cams.objects.link(cam_obj)
        cam_obj.location = c_loc
        
        if is_ortho:
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = flen_or_scale
            # Look straight down: Euler (0, 0, rot_phi)
            cam_obj.rotation_euler = Euler((0, 0, PHI), 'XYZ')
        else:
            cam_data.type = 'PERSP'
            cam_data.lens = flen_or_scale
            # Point camera at target
            target_vec = c_target_or_rot
            direction = (target_vec - c_loc).normalized()
            rot_quat = direction.to_track_quat('-Z', 'Y')
            cam_obj.rotation_euler = rot_quat.to_euler()

    # 17. Sun Light & Environment Setup for Photorealistic Verification Renders
    light_data = bpy.data.lights.new(name="Sun_Purdue_MemorialMall", type='SUN')
    light_data.energy = 4.2
    light_data.angle = math.radians(1.2)
    light_data.color = (1.0, 0.98, 0.94)
    light_obj = bpy.data.objects.new(name="Sun_Purdue_MemorialMall", object_data=light_data)
    col_cams.objects.link(light_obj)
    light_obj.location = to_world(30.0, -50.0, 45.0)
    light_obj.rotation_euler = Euler((math.radians(48.0), math.radians(12.0), math.radians(-35.0)), 'XYZ')

    # Ambient Fill Light
    fill_data = bpy.data.lights.new(name="Sky_Fill_Light", type='SUN')
    fill_data.energy = 1.4
    fill_data.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new(name="Sky_Fill_Light", object_data=fill_data)
    col_cams.objects.link(fill_obj)
    fill_obj.rotation_euler = Euler((math.radians(120.0), 0, math.radians(45.0)), 'XYZ')

    # Save to official modular file
    out_blend = os.path.abspath("modular/buildings/stanley_coulter_hall.blend")
    os.makedirs(os.path.dirname(out_blend), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Successfully constructed and saved: {out_blend}")

    # 18. Render Verification Camera Views
    artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\d54d9c39-3fb6-44cd-8a4e-7126018fb2ce"
    os.makedirs(artifact_dir, exist_ok=True)

    render_outputs = {}
    print("=== Rendering Verification Images ===")
    for c_name, _, _, _, _ in cams_info:
        cam_obj = bpy.data.objects.get(c_name)
        if cam_obj:
            scene.camera = cam_obj
            out_img = os.path.join(artifact_dir, f"{c_name}.png")
            scene.render.filepath = out_img
            bpy.ops.render.render(write_still=True)
            fsize_kb = os.path.getsize(out_img) / 1024
            render_outputs[c_name] = out_img
            print(f"Rendered {c_name} -> {out_img} ({fsize_kb:.1f} KB)")

    # 19. Geometric Measurements & Quality Audit
    # Compute mesh centroid of exterior walls & foundation
    verts_all = []
    for o in col_ext.objects:
        if o.type == 'MESH':
            mw = o.matrix_world
            for v in o.data.vertices:
                verts_all.append(mw @ v.co)
    
    avg_x = sum(v.x for v in verts_all) / len(verts_all)
    avg_y = sum(v.y for v in verts_all) / len(verts_all)
    min_x = min(v.x for v in verts_all)
    max_x = max(v.x for v in verts_all)
    min_y = min(v.y for v in verts_all)
    max_y = max(v.y for v in verts_all)
    min_z = min(v.z for v in verts_all)
    max_z = max(v.z for v in verts_all)

    err_x = avg_x - CX
    err_y = avg_y - CY
    dist_err = math.hypot(err_x, err_y)

    audit_stats = {
        "building_id": "stanley_coulter_hall",
        "code": "SC",
        "fid": 56,
        "official_center": [CX, CY],
        "measured_center": [avg_x, avg_y],
        "centroid_error_m": dist_err,
        "measured_aabb_xy": [min_x, min_y, max_x, max_y],
        "height_m": max_z - min_z,
        "z_range": [min_z, max_z],
        "object_count": len(bpy.data.objects),
        "collection_name": col_root.name,
        "scene_name": scene.name,
        "render_outputs": render_outputs
    }
    
    stats_path = os.path.join(artifact_dir, "stanley_coulter_hall_audit_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(audit_stats, f, indent=2)
    print(json.dumps(audit_stats, indent=2))
    print("=== Construction & Verification Complete! ===")

if __name__ == "__main__":
    build_stanley_coulter_hall()

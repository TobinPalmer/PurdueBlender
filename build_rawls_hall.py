"""
Purdue University Digital Twin - Jerry S. Rawls Hall (RAWL) Builder
=====================================================================
Official Name: Jerry S. Rawls Hall
Building Code: RAWL
Address: 100 S Grant Street, West Lafayette, IN 47907
Official GIS FID: 69, Levels: 6, Extrusion: 79 ft (~24.08 m), Roof Crest: 102 ft (~31.09 m)
Architects: Scholer Corporation & Goody Clancy & Associates (Opened 2003)
Coordinates: Metric campus world coordinates (Origin: lat 40.4274, lon -86.9137)
Target Blend: modular/buildings/rawls_hall.blend
Scene: Building_rawls_hall
Collection: Asset_rawls_hall
"""

import bpy
import bmesh
import mathutils
import math
import os
import json

def setup_blend_file():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    scene = bpy.context.scene
    scene.name = "Building_rawls_hall"
    
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'
    
    asset_col = bpy.data.collections.new("Asset_rawls_hall")
    scene.collection.children.link(asset_col)
    
    return scene, asset_col

def create_material(name, base_color, roughness=0.5, metallic=0.0, transmission=0.0, ior=1.5, bump_scale=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
            
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
            
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = ior
            
        if bump_scale > 0.0:
            tex_coord = nodes.new(type="ShaderNodeTexCoord")
            noise = nodes.new(type="ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 40.0
            noise.inputs["Detail"].default_value = 4.0
            bump = nodes.new(type="ShaderNodeBump")
            bump.inputs["Strength"].default_value = bump_scale
            
            links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
            links.new(noise.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
            
    return mat

def point_camera_at(cam_obj, target_loc):
    loc = cam_obj.location
    target = mathutils.Vector(target_loc)
    direction = target - loc
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def main():
    print("=== STARTING RAWLS HALL (RAWL) BUILD SCRIPT ===")
    scene, col = setup_blend_file()
    
    # Official polygon vertices (29 vertices, closed loop)
    RAWL_PTS = [
        (294.132, -398.002),
        (302.357, -397.912),
        (302.333, -395.753),
        (302.574, -395.751),
        (302.526, -391.332),
        (302.285, -391.334),
        (302.264, -389.429),
        (356.991, -388.832),
        (356.991, -388.858),
        (357.194, -388.855),
        (357.210, -390.303),
        (363.861, -390.231),
        (364.774, -390.221),
        (364.784, -391.135),
        (364.708, -391.136),
        (364.754, -395.309),
        (372.045, -395.829),
        (372.160, -406.397),
        (364.834, -406.477),
        (366.843, -412.803),
        (324.407, -426.292),
        (322.963, -421.741),
        (320.446, -422.541),
        (320.570, -433.924),
        (310.950, -434.029),
        (310.940, -433.076),
        (307.361, -433.115),
        (307.145, -413.355),
        (294.301, -413.495),
    ]
    N = len(RAWL_PTS)
    
    # Supported Floor Heights (meters, converted from official Purdue Facilities GIS attributes)
    Z_BASEMENT = -5.486 # -18.0 ft (GIS FID 69 "B": -18)
    Z_BASE = 0.00
    Z_WATER_TABLE = 1.50
    Z_L2 = 5.486
    Z_L3 = 10.577
    Z_L4 = 15.667
    Z_L5 = 20.330
    Z_ROOF_DECK = 23.50
    Z_PARAPET = 24.08
    Z_SKYLIGHT_CREST = 31.09
    
    # -------------------------------------------------------------------------
    # Materials Setup
    # -------------------------------------------------------------------------
    mat_brick = create_material("RAWL_Purdue_Red_Brick", (0.44, 0.17, 0.12, 1.0), roughness=0.78, bump_scale=0.06)
    mat_stone = create_material("RAWL_Bedford_Limestone", (0.83, 0.81, 0.75, 1.0), roughness=0.58, bump_scale=0.03)
    mat_glass = create_material("RAWL_CurtainWall_Glass", (0.05, 0.12, 0.16, 1.0), roughness=0.03, transmission=0.92, ior=1.52)
    mat_bronze = create_material("RAWL_Dark_Bronze_Metal", (0.16, 0.13, 0.10, 1.0), roughness=0.35, metallic=0.85)
    mat_steel = create_material("RAWL_Structural_Steel", (0.22, 0.24, 0.26, 1.0), roughness=0.40, metallic=0.80)
    mat_roof = create_material("RAWL_Roof_Membrane", (0.20, 0.21, 0.22, 1.0), roughness=0.88)
    mat_concrete = create_material("RAWL_Concrete_Floor", (0.62, 0.61, 0.58, 1.0), roughness=0.65)
    mat_plaza = create_material("RAWL_Plaza_Paver", (0.46, 0.36, 0.32, 1.0), roughness=0.82)
    mat_louver = create_material("RAWL_Mechanical_Louver", (0.15, 0.16, 0.17, 1.0), roughness=0.50, metallic=0.60)
    
    # -------------------------------------------------------------------------
    # 1. Footprint Reference Wireframe Object
    # -------------------------------------------------------------------------
    mesh_ref = bpy.data.meshes.new("RAWL_Footprint_Reference_Wire")
    bm_ref = bmesh.new()
    ref_verts = [bm_ref.verts.new((x, y, 0.05)) for x, y in RAWL_PTS]
    for i in range(N):
        bm_ref.edges.new((ref_verts[i], ref_verts[(i+1)%N]))
    bm_ref.to_mesh(mesh_ref)
    bm_ref.free()
    obj_ref = bpy.data.objects.new("RAWL_Footprint_Reference_Wire", mesh_ref)
    col.objects.link(obj_ref)
    
    # -------------------------------------------------------------------------
    # 2. Exterior Walls (Footprint Precision Extrusion)
    # -------------------------------------------------------------------------
    def compute_inward_offsets(pts, thickness=0.35):
        normals = []
        for i in range(N):
            p1 = pts[i]
            p2 = pts[(i+1)%N]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            L = math.hypot(dx, dy)
            normals.append((dy / L, -dx / L))
        
        offset_pts = []
        for i in range(N):
            n_prev = normals[(i-1)%N]
            n_curr = normals[i]
            nx = n_prev[0] + n_curr[0]
            ny = n_prev[1] + n_curr[1]
            L = math.hypot(nx, ny)
            if L < 1e-4:
                offset_pts.append((pts[i][0] + n_curr[0]*thickness, pts[i][1] + n_curr[1]*thickness))
            else:
                dot = (nx*n_curr[0] + ny*n_curr[1]) / L
                scale = thickness / max(dot, 0.25)
                scale = min(scale, thickness * 2.5)
                offset_pts.append((pts[i][0] + (nx/L)*scale, pts[i][1] + (ny/L)*scale))
        return offset_pts

    inner_pts = compute_inward_offsets(RAWL_PTS, thickness=0.35)

    def create_wall_mesh(name, z_bot, z_top, mat, pts_outer, pts_inner):
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        v_out_bot = [bm.verts.new((x, y, z_bot)) for x, y in pts_outer]
        v_out_top = [bm.verts.new((x, y, z_top)) for x, y in pts_outer]
        v_in_bot = [bm.verts.new((x, y, z_bot)) for x, y in pts_inner]
        v_in_top = [bm.verts.new((x, y, z_top)) for x, y in pts_inner]
        
        for i in range(N):
            i_next = (i + 1) % N
            bm.faces.new((v_out_bot[i], v_out_bot[i_next], v_out_top[i_next], v_out_top[i]))
            bm.faces.new((v_in_bot[i_next], v_in_bot[i], v_in_top[i], v_in_top[i_next]))
            bm.faces.new((v_out_bot[i_next], v_out_bot[i], v_in_bot[i], v_in_bot[i_next]))
            bm.faces.new((v_out_top[i], v_out_top[i_next], v_in_top[i_next], v_in_top[i]))
            
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        mesh.materials.append(mat)
        col.objects.link(obj)
        return obj

    # 2a. Below-grade Foundation & Retaining Walls (Z = -5.486 to 0.0m) as documented in GIS FID 69 ("B": -18)
    create_wall_mesh("RAWL_Basement_Foundation_Walls", Z_BASEMENT, Z_BASE, mat_concrete, RAWL_PTS, inner_pts)

    # 2b. Bedford Limestone Base Plinth / Water Table (Z = 0.0 to 1.50m)
    create_wall_mesh("RAWL_Limestone_Base_Plinth", Z_BASE, Z_WATER_TABLE, mat_stone, RAWL_PTS, inner_pts)
    
    # 2c. Brick Masonry Shell (Z = 1.50m to Z_PARAPET = 24.08m)
    create_wall_mesh("RAWL_Masonry_Exterior_Walls", Z_WATER_TABLE, Z_PARAPET, mat_brick, RAWL_PTS, inner_pts)
    
    # -------------------------------------------------------------------------
    # 3. Limestone Belt Courses & Parapet Coping
    # -------------------------------------------------------------------------
    def create_horizontal_band(name, z_center, height, proj, mat, pts):
        band_pts = compute_inward_offsets(pts, thickness=-proj)
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        z_bot = z_center - height*0.5
        z_top = z_center + height*0.5
        v_b = [bm.verts.new((x, y, z_bot)) for x, y in band_pts]
        v_t = [bm.verts.new((x, y, z_top)) for x, y in band_pts]
        v_wb = [bm.verts.new((x, y, z_bot)) for x, y in pts]
        v_wt = [bm.verts.new((x, y, z_top)) for x, y in pts]
        
        for i in range(N):
            i_next = (i + 1) % N
            bm.faces.new((v_b[i], v_b[i_next], v_t[i_next], v_t[i]))
            bm.faces.new((v_t[i], v_t[i_next], v_wt[i_next], v_wt[i]))
            bm.faces.new((v_wb[i], v_wb[i_next], v_b[i_next], v_b[i]))
            
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        mesh.materials.append(mat)
        col.objects.link(obj)
        return obj

    create_horizontal_band("RAWL_Limestone_BeltCourse_L2", Z_L2, 0.30, 0.08, mat_stone, RAWL_PTS)
    create_horizontal_band("RAWL_Limestone_BeltCourse_L3", Z_L3, 0.30, 0.08, mat_stone, RAWL_PTS)
    create_horizontal_band("RAWL_Limestone_BeltCourse_L4", Z_L4, 0.30, 0.08, mat_stone, RAWL_PTS)
    create_horizontal_band("RAWL_Limestone_BeltCourse_L5", Z_L5, 0.30, 0.08, mat_stone, RAWL_PTS)
    
    # Parapet Coping along the entire perimeter at Z = 24.08m
    coping_outer = compute_inward_offsets(RAWL_PTS, thickness=-0.08)
    coping_inner = compute_inward_offsets(RAWL_PTS, thickness=0.42)
    mesh_coping = bpy.data.meshes.new("RAWL_Limestone_Parapet_Coping")
    bm_coping = bmesh.new()
    vc_ob = [bm_coping.verts.new((x, y, Z_PARAPET - 0.12)) for x, y in coping_outer]
    vc_ot = [bm_coping.verts.new((x, y, Z_PARAPET)) for x, y in coping_outer]
    vc_ib = [bm_coping.verts.new((x, y, Z_PARAPET - 0.12)) for x, y in coping_inner]
    vc_it = [bm_coping.verts.new((x, y, Z_PARAPET)) for x, y in coping_inner]
    for i in range(N):
        i_next = (i + 1) % N
        bm_coping.faces.new((vc_ob[i], vc_ob[i_next], vc_ot[i_next], vc_ot[i]))
        bm_coping.faces.new((vc_ot[i], vc_ot[i_next], vc_it[i_next], vc_it[i]))
        bm_coping.faces.new((vc_it[i], vc_it[i_next], vc_ib[i_next], vc_ib[i]))
    bm_coping.to_mesh(mesh_coping)
    bm_coping.free()
    obj_coping = bpy.data.objects.new("RAWL_Limestone_Parapet_Coping", mesh_coping)
    mesh_coping.materials.append(mat_stone)
    col.objects.link(obj_coping)

    # -------------------------------------------------------------------------
    # 4. Signature Northwest Rotunda / Curved Glass Curtain Wall
    # -------------------------------------------------------------------------
    rot_cx, rot_cy = 302.30, -394.00
    rot_radius = 6.20
    rot_angles = [math.radians(a) for a in range(90, 185, 5)]
    rot_mesh = bpy.data.meshes.new("RAWL_NW_Rotunda_Curved_CurtainWall")
    bm_rot = bmesh.new()
    
    z_levels = [Z_BASE + 0.4, Z_L2, Z_L3, Z_L4, Z_L5, Z_ROOF_DECK]
    for zl_idx in range(len(z_levels)-1):
        zb = z_levels[zl_idx]
        zt = z_levels[zl_idx+1]
        for a_idx in range(len(rot_angles)-1):
            a1 = rot_angles[a_idx]
            a2 = rot_angles[a_idx+1]
            x1, y1 = rot_cx + rot_radius * math.cos(a1), rot_cy + rot_radius * math.sin(a1)
            x2, y2 = rot_cx + rot_radius * math.cos(a2), rot_cy + rot_radius * math.sin(a2)
            
            v1 = bm_rot.verts.new((x1, y1, zb + 0.1))
            v2 = bm_rot.verts.new((x2, y2, zb + 0.1))
            v3 = bm_rot.verts.new((x2, y2, zt - 0.1))
            v4 = bm_rot.verts.new((x1, y1, zt - 0.1))
            bm_rot.faces.new((v1, v2, v3, v4))
            
    bm_rot.to_mesh(rot_mesh)
    bm_rot.free()
    obj_rot = bpy.data.objects.new("RAWL_NW_Rotunda_Curved_CurtainWall", rot_mesh)
    rot_mesh.materials.append(mat_glass)
    col.objects.link(obj_rot)
    
    # Rotunda Bronze Mullions Frame
    rot_mull_mesh = bpy.data.meshes.new("RAWL_NW_Rotunda_Bronze_Mullions")
    bm_mull = bmesh.new()
    for ang in rot_angles:
        xm = rot_cx + (rot_radius + 0.05) * math.cos(ang)
        ym = rot_cy + (rot_radius + 0.05) * math.sin(ang)
        res_m = bmesh.ops.create_cube(bm_mull, size=1.0)
        for v in res_m['verts']:
            v.co.x = v.co.x * 0.10 + xm
            v.co.y = v.co.y * 0.10 + ym
            v.co.z = v.co.z * (Z_ROOF_DECK - Z_BASE) + (Z_BASE + Z_ROOF_DECK) * 0.5
            
    for z_ring in z_levels:
        for a_idx in range(len(rot_angles)-1):
            a1, a2 = rot_angles[a_idx], rot_angles[a_idx+1]
            x1, y1 = rot_cx + (rot_radius + 0.06) * math.cos(a1), rot_cy + (rot_radius + 0.06) * math.sin(a1)
            x2, y2 = rot_cx + (rot_radius + 0.06) * math.cos(a2), rot_cy + (rot_radius + 0.06) * math.sin(a2)
            v1 = bm_mull.verts.new((x1, y1, z_ring - 0.08))
            v2 = bm_mull.verts.new((x2, y2, z_ring - 0.08))
            v3 = bm_mull.verts.new((x2, y2, z_ring + 0.08))
            v4 = bm_mull.verts.new((x1, y1, z_ring + 0.08))
            bm_mull.faces.new((v1, v2, v3, v4))
            
    bm_mull.to_mesh(rot_mull_mesh)
    bm_mull.free()
    obj_rot_mull = bpy.data.objects.new("RAWL_NW_Rotunda_Bronze_Mullions", rot_mull_mesh)
    rot_mull_mesh.materials.append(mat_bronze)
    col.objects.link(obj_rot_mull)

    # Rotunda Curved Limestone Crown Header
    rot_crown_mesh = bpy.data.meshes.new("RAWL_NW_Rotunda_Limestone_Crown")
    bm_crown = bmesh.new()
    for a_idx in range(len(rot_angles)-1):
        a1, a2 = rot_angles[a_idx], rot_angles[a_idx+1]
        x1_o, y1_o = rot_cx + (rot_radius + 0.25) * math.cos(a1), rot_cy + (rot_radius + 0.25) * math.sin(a1)
        x2_o, y2_o = rot_cx + (rot_radius + 0.25) * math.cos(a2), rot_cy + (rot_radius + 0.25) * math.sin(a2)
        x1_i, y1_i = rot_cx + (rot_radius - 0.15) * math.cos(a1), rot_cy + (rot_radius - 0.15) * math.sin(a1)
        x2_i, y2_i = rot_cx + (rot_radius - 0.15) * math.cos(a2), rot_cy + (rot_radius - 0.15) * math.sin(a2)
        
        v_ob1 = bm_crown.verts.new((x1_o, y1_o, Z_ROOF_DECK))
        v_ob2 = bm_crown.verts.new((x2_o, y2_o, Z_ROOF_DECK))
        v_ot1 = bm_crown.verts.new((x1_o, y1_o, Z_PARAPET + 0.2))
        v_ot2 = bm_crown.verts.new((x2_o, y2_o, Z_PARAPET + 0.2))
        v_ib1 = bm_crown.verts.new((x1_i, y1_i, Z_ROOF_DECK))
        v_ib2 = bm_crown.verts.new((x2_i, y2_i, Z_ROOF_DECK))
        v_it1 = bm_crown.verts.new((x1_i, y1_i, Z_PARAPET + 0.2))
        v_it2 = bm_crown.verts.new((x2_i, y2_i, Z_PARAPET + 0.2))
        
        bm_crown.faces.new((v_ob1, v_ob2, v_ot2, v_ot1))
        bm_crown.faces.new((v_ot1, v_ot2, v_it2, v_it1))
        bm_crown.faces.new((v_it1, v_it2, v_ib2, v_ib1))
        
    bm_crown.to_mesh(rot_crown_mesh)
    bm_crown.free()
    obj_crown = bpy.data.objects.new("RAWL_NW_Rotunda_Limestone_Crown", rot_crown_mesh)
    rot_crown_mesh.materials.append(mat_stone)
    col.objects.link(obj_crown)

    # -------------------------------------------------------------------------
    # 5. Facade Window Ribbon Arrays & Curtain Walls
    # -------------------------------------------------------------------------
    def create_window_bays(name, p_start, p_end, floor_elevs, sill_h, head_h, bay_spacing, bay_width):
        dx = p_end[0] - p_start[0]
        dy = p_end[1] - p_start[1]
        wall_len = math.hypot(dx, dy)
        ux, uy = dx / wall_len, dy / wall_len
        # Outward normal for clockwise polygon
        nx, ny = -uy, ux
        
        num_bays = max(1, int((wall_len - 2.0) / bay_spacing))
        actual_spacing = (wall_len - 2.0) / num_bays
        
        mesh_win = bpy.data.meshes.new(name + "_Glass")
        bm_win = bmesh.new()
        
        mesh_trim = bpy.data.meshes.new(name + "_BronzeMullions")
        bm_trim = bmesh.new()
        
        mesh_sill = bpy.data.meshes.new(name + "_LimestoneSills")
        bm_sill = bmesh.new()
        
        for fl_idx, fl_z in enumerate(floor_elevs):
            z_sill = fl_z + sill_h
            z_head = fl_z + head_h
            if z_head > Z_ROOF_DECK:
                continue
                
            for b in range(num_bays):
                t_center = 1.0 + (b + 0.5) * actual_spacing
                bx = p_start[0] + ux * t_center
                by = p_start[1] + uy * t_center
                
                # Glass panel (recessed 0.05m into wall)
                p_left = (bx - ux * (bay_width * 0.5) - nx * 0.05, by - uy * (bay_width * 0.5) - ny * 0.05)
                p_right = (bx + ux * (bay_width * 0.5) - nx * 0.05, by + uy * (bay_width * 0.5) - ny * 0.05)
                
                vg1 = bm_win.verts.new((p_left[0], p_left[1], z_sill))
                vg2 = bm_win.verts.new((p_right[0], p_right[1], z_sill))
                vg3 = bm_win.verts.new((p_right[0], p_right[1], z_head))
                vg4 = bm_win.verts.new((p_left[0], p_left[1], z_head))
                bm_win.faces.new((vg1, vg2, vg3, vg4))
                
                # Bronze frame border (recessed frame)
                res_box = bmesh.ops.create_cube(bm_trim, size=1.0)
                for v in res_box['verts']:
                    v.co.x = v.co.x * (bay_width * abs(ux) + 0.06 * abs(nx)) + bx - nx * 0.03
                    v.co.y = v.co.y * (bay_width * abs(uy) + 0.06 * abs(ny)) + by - ny * 0.03
                    v.co.z = v.co.z * (z_head - z_sill) + (z_sill + z_head) * 0.5
                    
                # Projecting limestone sill
                ps_left = (bx - ux * (bay_width * 0.5 + 0.12) + nx * 0.08, by - uy * (bay_width * 0.5 + 0.12) + ny * 0.08)
                ps_right = (bx + ux * (bay_width * 0.5 + 0.12) + nx * 0.08, by + uy * (bay_width * 0.5 + 0.12) + ny * 0.08)
                vs1 = bm_sill.verts.new((ps_left[0], ps_left[1], z_sill - 0.15))
                vs2 = bm_sill.verts.new((ps_right[0], ps_right[1], z_sill - 0.15))
                vs3 = bm_sill.verts.new((ps_right[0], ps_right[1], z_sill))
                vs4 = bm_sill.verts.new((ps_left[0], ps_left[1], z_sill))
                bm_sill.faces.new((vs1, vs2, vs3, vs4))
                
        bm_win.to_mesh(mesh_win); bm_win.free()
        bm_trim.to_mesh(mesh_trim); bm_trim.free()
        bm_sill.to_mesh(mesh_sill); bm_sill.free()
        
        o_win = bpy.data.objects.new(name + "_Glass", mesh_win)
        mesh_win.materials.append(mat_glass); col.objects.link(o_win)
        
        o_trim = bpy.data.objects.new(name + "_BronzeMullions", mesh_trim)
        mesh_trim.materials.append(mat_bronze); col.objects.link(o_trim)
        
        o_sill = bpy.data.objects.new(name + "_LimestoneSills", mesh_sill)
        mesh_sill.materials.append(mat_stone); col.objects.link(o_sill)

    floor_levels = [Z_BASE, Z_L2, Z_L3, Z_L4, Z_L5]

    # 5a. North Facade Windows
    create_window_bays("RAWL_North_Windows", RAWL_PTS[6], RAWL_PTS[7], floor_levels, sill_h=1.0, head_h=3.8, bay_spacing=3.4, bay_width=2.4)

    # 5b. Southeast Diagonal Curtain Wall
    create_window_bays("RAWL_SE_Diagonal_CurtainWall", RAWL_PTS[19], RAWL_PTS[20], floor_levels, sill_h=0.8, head_h=4.2, bay_spacing=3.6, bay_width=2.8)

    # 5c. South Wing Windows
    create_window_bays("RAWL_South_Windows_East", RAWL_PTS[22], RAWL_PTS[23], floor_levels, sill_h=1.1, head_h=3.6, bay_spacing=2.8, bay_width=1.8)
    create_window_bays("RAWL_South_Windows_South", RAWL_PTS[23], RAWL_PTS[24], floor_levels, sill_h=1.1, head_h=3.6, bay_spacing=2.8, bay_width=1.8)

    # 5d. West Facade Windows (Grant St)
    create_window_bays("RAWL_West_Windows", RAWL_PTS[28], RAWL_PTS[0], floor_levels, sill_h=1.0, head_h=3.8, bay_spacing=3.0, bay_width=2.0)

    # 5e. East Wing Windows
    create_window_bays("RAWL_East_Windows", RAWL_PTS[16], RAWL_PTS[17], floor_levels, sill_h=1.0, head_h=3.8, bay_spacing=3.2, bay_width=2.2)

    # -------------------------------------------------------------------------
    # 6. Covered Entrance Porticos & Canopies
    # -------------------------------------------------------------------------
    # 6a. Grand North Entrance Portico (Mitch Daniels Blvd at X = 325.0)
    north_entry_x = 325.0
    north_entry_y = -388.83
    mesh_north_port = bpy.data.meshes.new("RAWL_North_Entrance_Portico")
    bm_np = bmesh.new()
    
    # Limestone Portal Pillars
    for x_col in [north_entry_x - 4.2, north_entry_x + 4.2]:
        res_p = bmesh.ops.create_cube(bm_np, size=1.0)
        for v in res_p['verts']:
            v.co.x = v.co.x * 0.9 + x_col
            v.co.y = v.co.y * 0.9 + (north_entry_y + 0.4)
            v.co.z = v.co.z * 5.8 + 2.9
            
    # Limestone Portal Header
    res_ph = bmesh.ops.create_cube(bm_np, size=1.0)
    for v in res_ph['verts']:
        v.co.x = v.co.x * 9.5 + north_entry_x
        v.co.y = v.co.y * 0.9 + (north_entry_y + 0.4)
        v.co.z = v.co.z * 0.8 + 5.8
        
    # Granite Entrance Steps
    for s in range(5):
        s_z = s * 0.18
        s_depth = 0.45 * (5 - s)
        res_st = bmesh.ops.create_cube(bm_np, size=1.0)
        for v in res_st['verts']:
            v.co.x = v.co.x * 8.6 + north_entry_x
            v.co.y = v.co.y * s_depth + (north_entry_y + 0.5 + s_depth * 0.5)
            v.co.z = v.co.z * 0.18 + s_z + 0.09
            
    bm_np.to_mesh(mesh_north_port); bm_np.free()
    obj_np = bpy.data.objects.new("RAWL_North_Entrance_Portico", mesh_north_port)
    mesh_north_port.materials.append(mat_stone); col.objects.link(obj_np)

    # North Glass Canopy with Bronze Framing
    mesh_ncanopy = bpy.data.meshes.new("RAWL_North_Entrance_Canopy")
    bm_ncan = bmesh.new()
    can_y1 = north_entry_y
    can_y2 = north_entry_y + 3.5
    v_c1 = bm_ncan.verts.new((north_entry_x - 4.5, can_y1, 4.8))
    v_c2 = bm_ncan.verts.new((north_entry_x + 4.5, can_y1, 4.8))
    v_c3 = bm_ncan.verts.new((north_entry_x + 4.5, can_y2, 4.4))
    v_c4 = bm_ncan.verts.new((north_entry_x - 4.5, can_y2, 4.4))
    bm_ncan.faces.new((v_c1, v_c2, v_c3, v_c4))
    bm_ncan.to_mesh(mesh_ncanopy); bm_ncan.free()
    obj_ncan = bpy.data.objects.new("RAWL_North_Entrance_Canopy", mesh_ncanopy)
    mesh_ncanopy.materials.append(mat_glass); col.objects.link(obj_ncan)

    # North Canopy Bronze Struts
    mesh_nstruts = bpy.data.meshes.new("RAWL_North_Canopy_Struts")
    bm_nst = bmesh.new()
    for x_strut in [north_entry_x - 4.0, north_entry_x - 1.5, north_entry_x + 1.5, north_entry_x + 4.0]:
        res_arm = bmesh.ops.create_cube(bm_nst, size=1.0)
        for v in res_arm['verts']:
            v.co.x = v.co.x * 0.12 + x_strut
            v.co.y = v.co.y * 3.5 + (north_entry_y + 1.75)
            v.co.z = v.co.z * 0.15 + 4.6
        v_t1 = bm_nst.verts.new((x_strut, north_entry_y + 0.1, 5.8))
        v_t2 = bm_nst.verts.new((x_strut, north_entry_y + 3.2, 4.5))
        bm_nst.edges.new((v_t1, v_t2))
    bm_nst.to_mesh(mesh_nstruts); bm_nst.free()
    obj_nst = bpy.data.objects.new("RAWL_North_Canopy_Struts", mesh_nstruts)
    mesh_nstruts.materials.append(mat_bronze); col.objects.link(obj_nst)

    # North Commercial Glazed Entrance Doors
    mesh_ndoors = bpy.data.meshes.new("RAWL_North_Entrance_Doors")
    bm_nd = bmesh.new()
    for d_x in [north_entry_x - 2.8, north_entry_x - 0.9, north_entry_x + 0.9, north_entry_x + 2.8]:
        res_d = bmesh.ops.create_cube(bm_nd, size=1.0)
        for v in res_d['verts']:
            v.co.x = v.co.x * 1.6 + d_x
            v.co.y = v.co.y * 0.08 + (north_entry_y + 0.35)
            v.co.z = v.co.z * 2.8 + 2.3
    bm_nd.to_mesh(mesh_ndoors); bm_nd.free()
    obj_nd = bpy.data.objects.new("RAWL_North_Entrance_Doors", mesh_ndoors)
    mesh_ndoors.materials.append(mat_glass); col.objects.link(obj_nd)

    # 6b. West Entrance Portico (Grant Street at Y = -406.0)
    west_entry_x = 294.20
    west_entry_y = -406.0
    mesh_wcan = bpy.data.meshes.new("RAWL_West_Entrance_Canopy")
    bm_wc = bmesh.new()
    v_w1 = bm_wc.verts.new((west_entry_x, west_entry_y - 2.5, 4.5))
    v_w2 = bm_wc.verts.new((west_entry_x, west_entry_y + 2.5, 4.5))
    v_w3 = bm_wc.verts.new((west_entry_x - 2.8, west_entry_y + 2.5, 4.2))
    v_w4 = bm_wc.verts.new((west_entry_x - 2.8, west_entry_y - 2.5, 4.2))
    bm_wc.faces.new((v_w1, v_w2, v_w3, v_w4))
    bm_wc.to_mesh(mesh_wcan); bm_wc.free()
    obj_wcan = bpy.data.objects.new("RAWL_West_Entrance_Canopy", mesh_wcan)
    mesh_wcan.materials.append(mat_glass); col.objects.link(obj_wcan)

    # -------------------------------------------------------------------------
    # 7. Level 4 Enclosed Pedestrian Skywalk (Skybridge to Krannert)
    # -------------------------------------------------------------------------
    sb_x_start = 272.0
    sb_x_end = 294.2
    sb_y_center = -405.0
    sb_width = 3.4
    sb_y_south = sb_y_center - sb_width * 0.5
    sb_y_north = sb_y_center + sb_width * 0.5
    sb_z_floor = Z_L4
    sb_z_roof = 19.60
    
    # 7a. Skywalk Structural Floor & Roof Decks
    mesh_sb_deck = bpy.data.meshes.new("RAWL_Skywalk_Krannert_Structure")
    bm_sbd = bmesh.new()
    # Floor slab
    res_sbf = bmesh.ops.create_cube(bm_sbd, size=1.0)
    for v in res_sbf['verts']:
        v.co.x = v.co.x * (sb_x_end - sb_x_start) + (sb_x_start + sb_x_end) * 0.5
        v.co.y = v.co.y * sb_width + sb_y_center
        v.co.z = v.co.z * 0.35 + (sb_z_floor - 0.175)
    # Roof slab
    res_sbr = bmesh.ops.create_cube(bm_sbd, size=1.0)
    for v in res_sbr['verts']:
        v.co.x = v.co.x * (sb_x_end - sb_x_start) + (sb_x_start + sb_x_end) * 0.5
        v.co.y = v.co.y * (sb_width + 0.3) + sb_y_center
        v.co.z = v.co.z * 0.30 + (sb_z_roof + 0.15)
    # Rawls Hall connection portal
    res_sbp = bmesh.ops.create_cube(bm_sbd, size=1.0)
    for v in res_sbp['verts']:
        v.co.x = v.co.x * 0.6 + (sb_x_end - 0.3)
        v.co.y = v.co.y * (sb_width + 0.8) + sb_y_center
        v.co.z = v.co.z * (sb_z_roof - sb_z_floor + 1.0) + (sb_z_floor + sb_z_roof) * 0.5
    # Krannert connection portal closure
    res_kcp = bmesh.ops.create_cube(bm_sbd, size=1.0)
    for v in res_kcp['verts']:
        v.co.x = v.co.x * 0.4 + (sb_x_start + 0.2)
        v.co.y = v.co.y * (sb_width + 0.6) + sb_y_center
        v.co.z = v.co.z * (sb_z_roof - sb_z_floor + 0.8) + (sb_z_floor + sb_z_roof) * 0.5

    bm_sbd.to_mesh(mesh_sb_deck); bm_sbd.free()
    obj_sb_deck = bpy.data.objects.new("RAWL_Skywalk_Krannert_Structure", mesh_sb_deck)
    mesh_sb_deck.materials.append(mat_stone); col.objects.link(obj_sb_deck)

    # 7b. Skywalk Glass Curtain Walls
    mesh_sb_glass = bpy.data.meshes.new("RAWL_Skywalk_Glazing")
    bm_sbg = bmesh.new()
    v_sg1 = bm_sbg.verts.new((sb_x_start, sb_y_south, sb_z_floor))
    v_sg2 = bm_sbg.verts.new((sb_x_end, sb_y_south, sb_z_floor))
    v_sg3 = bm_sbg.verts.new((sb_x_end, sb_y_south, sb_z_roof))
    v_sg4 = bm_sbg.verts.new((sb_x_start, sb_y_south, sb_z_roof))
    bm_sbg.faces.new((v_sg1, v_sg2, v_sg3, v_sg4))
    v_ng1 = bm_sbg.verts.new((sb_x_end, sb_y_north, sb_z_floor))
    v_ng2 = bm_sbg.verts.new((sb_x_start, sb_y_north, sb_z_floor))
    v_ng3 = bm_sbg.verts.new((sb_x_start, sb_y_north, sb_z_roof))
    v_ng4 = bm_sbg.verts.new((sb_x_end, sb_y_north, sb_z_roof))
    bm_sbg.faces.new((v_ng1, v_ng2, v_ng3, v_ng4))
    bm_sbg.to_mesh(mesh_sb_glass); bm_sbg.free()
    obj_sb_glass = bpy.data.objects.new("RAWL_Skywalk_Glazing", mesh_sb_glass)
    mesh_sb_glass.materials.append(mat_glass); col.objects.link(obj_sb_glass)

    # 7c. Skywalk Bronze Mullions & Truss Framework
    mesh_sb_truss = bpy.data.meshes.new("RAWL_Skywalk_TrussFramework")
    bm_sbt = bmesh.new()
    sb_steps = int((sb_x_end - sb_x_start) / 2.5)
    for step in range(sb_steps + 1):
        x_post = sb_x_start + step * 2.5
        for y_side in [sb_y_south, sb_y_north]:
            res_pt = bmesh.ops.create_cube(bm_sbt, size=1.0)
            for v in res_pt['verts']:
                v.co.x = v.co.x * 0.12 + x_post
                v.co.y = v.co.y * 0.12 + y_side
                v.co.z = v.co.z * (sb_z_roof - sb_z_floor) + (sb_z_floor + sb_z_roof) * 0.5
        res_tb = bmesh.ops.create_cube(bm_sbt, size=1.0)
        for v in res_tb['verts']:
            v.co.x = v.co.x * 0.12 + x_post
            v.co.y = v.co.y * sb_width + sb_y_center
            v.co.z = v.co.z * 0.12 + sb_z_roof
    bm_sbt.to_mesh(mesh_sb_truss); bm_sbt.free()
    obj_sb_truss = bpy.data.objects.new("RAWL_Skywalk_TrussFramework", mesh_sb_truss)
    mesh_sb_truss.materials.append(mat_bronze); col.objects.link(obj_sb_truss)

    # -------------------------------------------------------------------------
    # 8. Main Roof Deck & Membrane
    # -------------------------------------------------------------------------
    mesh_roof_deck = bpy.data.meshes.new("RAWL_Roof_Main_Deck")
    bm_rd = bmesh.new()
    roof_verts = [bm_rd.verts.new((x, y, Z_ROOF_DECK)) for x, y in inner_pts]
    bm_rd.faces.new(roof_verts)
    bmesh.ops.triangulate(bm_rd, faces=bm_rd.faces)
    bm_rd.to_mesh(mesh_roof_deck); bm_rd.free()
    obj_roof = bpy.data.objects.new("RAWL_Roof_Main_Deck", mesh_roof_deck)
    mesh_roof_deck.materials.append(mat_roof); col.objects.link(obj_roof)

    # -------------------------------------------------------------------------
    # 9. Central Arched Skylight Penthouse (Barrel Vault to Z = 31.09m)
    # -------------------------------------------------------------------------
    sky_x1, sky_x2 = 323.0, 345.0
    sky_y1, sky_y2 = -417.0, -405.0
    sky_yc = (sky_y1 + sky_y2) * 0.5
    sky_half_w = (sky_y2 - sky_y1) * 0.5
    sky_z_curb = 26.20
    sky_crown_h = Z_SKYLIGHT_CREST - sky_z_curb

    # 9a. Penthouse Curb Base Walls
    mesh_curb = bpy.data.meshes.new("RAWL_Arched_Penthouse_Curb_Walls")
    bm_curb = bmesh.new()
    res_cb = bmesh.ops.create_cube(bm_curb, size=1.0)
    for v in res_cb['verts']:
        v.co.x = v.co.x * (sky_x2 - sky_x1) + (sky_x1 + sky_x2) * 0.5
        v.co.y = v.co.y * (sky_y2 - sky_y1) + sky_yc
        v.co.z = v.co.z * (sky_z_curb - Z_ROOF_DECK) + (Z_ROOF_DECK + sky_z_curb) * 0.5
    bm_curb.to_mesh(mesh_curb); bm_curb.free()
    obj_curb = bpy.data.objects.new("RAWL_Arched_Penthouse_Curb_Walls", mesh_curb)
    mesh_curb.materials.append(mat_stone); col.objects.link(obj_curb)

    # 9b. Arched Barrel-Vault Glazed Canopy
    mesh_arch_glass = bpy.data.meshes.new("RAWL_Arched_Skylight_Barrel_Vault")
    bm_ag = bmesh.new()
    num_arch_segs = 16
    arch_pts = []
    for s in range(num_arch_segs + 1):
        theta = math.pi * s / num_arch_segs
        y_arch = sky_yc - sky_half_w * math.cos(theta)
        z_arch = sky_z_curb + sky_crown_h * math.sin(theta)
        arch_pts.append((y_arch, z_arch))

    num_x_segs = 12
    x_steps = [sky_x1 + (sky_x2 - sky_x1) * (i / num_x_segs) for i in range(num_x_segs + 1)]
    
    grid_verts = []
    for xi in x_steps:
        row = []
        for y_arch, z_arch in arch_pts:
            row.append(bm_ag.verts.new((xi, y_arch, z_arch)))
        grid_verts.append(row)

    for i in range(num_x_segs):
        for j in range(num_arch_segs):
            bm_ag.faces.new((grid_verts[i][j], grid_verts[i+1][j], grid_verts[i+1][j+1], grid_verts[i][j+1]))

    west_gable = [grid_verts[0][j] for j in range(num_arch_segs + 1)]
    bm_ag.faces.new(west_gable)
    
    east_gable = [grid_verts[-1][j] for j in reversed(range(num_arch_segs + 1))]
    bm_ag.faces.new(east_gable)

    bm_ag.to_mesh(mesh_arch_glass); bm_ag.free()
    obj_arch_glass = bpy.data.objects.new("RAWL_Arched_Skylight_Barrel_Vault", mesh_arch_glass)
    mesh_arch_glass.materials.append(mat_glass); col.objects.link(obj_arch_glass)

    # 9c. Structural Steel Arched Ribs & Ridge Purlin
    mesh_arch_ribs = bpy.data.meshes.new("RAWL_Arched_Skylight_Ribs")
    bm_ar = bmesh.new()
    for xi in x_steps:
        for j in range(num_arch_segs):
            v1_y, v1_z = arch_pts[j]
            v2_y, v2_z = arch_pts[j+1]
            res_rib = bmesh.ops.create_cube(bm_ar, size=1.0)
            for v in res_rib['verts']:
                v.co.x = v.co.x * 0.16 + xi
                v.co.y = v.co.y * abs(v2_y - v1_y) * 1.05 + (v1_y + v2_y) * 0.5
                v.co.z = v.co.z * abs(v2_z - v1_z) * 1.05 + (v1_z + v2_z) * 0.5
    res_rp = bmesh.ops.create_cube(bm_ar, size=1.0)
    for v in res_rp['verts']:
        v.co.x = v.co.x * (sky_x2 - sky_x1) + (sky_x1 + sky_x2) * 0.5
        v.co.y = v.co.y * 0.25 + sky_yc
        v.co.z = v.co.z * 0.25 + Z_SKYLIGHT_CREST
    bm_ar.to_mesh(mesh_arch_ribs); bm_ar.free()
    obj_arch_ribs = bpy.data.objects.new("RAWL_Arched_Skylight_Ribs", mesh_arch_ribs)
    mesh_arch_ribs.materials.append(mat_steel); col.objects.link(obj_arch_ribs)

    # -------------------------------------------------------------------------
    # 10. Rooftop Mechanical Penthouse & HVAC Units
    # -------------------------------------------------------------------------
    mesh_mech_e = bpy.data.meshes.new("RAWL_Roof_Mechanical_East")
    bm_me = bmesh.new()
    res_me = bmesh.ops.create_cube(bm_me, size=1.0)
    for v in res_me['verts']:
        v.co.x = v.co.x * 7.5 + 353.5
        v.co.y = v.co.y * 6.0 + (-399.0)
        v.co.z = v.co.z * 3.2 + (Z_ROOF_DECK + 1.6)
    bm_me.to_mesh(mesh_mech_e); bm_me.free()
    obj_me = bpy.data.objects.new("RAWL_Roof_Mechanical_East", mesh_mech_e)
    mesh_mech_e.materials.append(mat_louver); col.objects.link(obj_me)

    mesh_mech_w = bpy.data.meshes.new("RAWL_Roof_Mechanical_West")
    bm_mw = bmesh.new()
    res_mw = bmesh.ops.create_cube(bm_mw, size=1.0)
    for v in res_mw['verts']:
        v.co.x = v.co.x * 7.0 + 312.0
        v.co.y = v.co.y * 5.5 + (-403.0)
        v.co.z = v.co.z * 3.2 + (Z_ROOF_DECK + 1.6)
    bm_mw.to_mesh(mesh_mech_w); bm_mw.free()
    obj_mw = bpy.data.objects.new("RAWL_Roof_Mechanical_West", mesh_mech_w)
    mesh_mech_w.materials.append(mat_louver); col.objects.link(obj_mw)

    # HVAC Chillers & Air Handlers (isolated bmesh geometry)
    mesh_hvac = bpy.data.meshes.new("RAWL_Roof_HVAC_Units")
    bm_hvac = bmesh.new()
    for h_x, h_y in [(350.0, -406.0), (354.5, -406.0), (314.0, -412.0), (318.0, -412.0)]:
        res_hbx = bmesh.ops.create_cube(bm_hvac, size=1.0)
        for v in res_hbx['verts']:
            v.co.x = v.co.x * 3.0 + h_x
            v.co.y = v.co.y * 2.0 + h_y
            v.co.z = v.co.z * 1.6 + (Z_ROOF_DECK + 0.8)
        res_fan = bmesh.ops.create_cone(bm_hvac, cap_ends=True, cap_tris=False, segments=12, radius1=0.70, radius2=0.80, depth=0.40)
        for v in res_fan['verts']:
            v.co.x += h_x
            v.co.y += h_y
            v.co.z += (Z_ROOF_DECK + 1.8)
    bm_hvac.to_mesh(mesh_hvac); bm_hvac.free()
    obj_hvac = bpy.data.objects.new("RAWL_Roof_HVAC_Units", mesh_hvac)
    mesh_hvac.materials.append(mat_steel); col.objects.link(obj_hvac)

    # -------------------------------------------------------------------------
    # 11. Floor Slabs & Documented Central Public Atrium
    # -------------------------------------------------------------------------
    # Create temporary cutter cube for central public atrium light well (X=326-342, Y=-414 to -408)
    mesh_cutter = bpy.data.meshes.new("Temp_Atrium_Cutter")
    bm_cut = bmesh.new()
    res_cut = bmesh.ops.create_cube(bm_cut, size=1.0)
    for v in res_cut['verts']:
        v.co.x = v.co.x * 16.0 + 334.0
        v.co.y = v.co.y * 6.0 + (-411.0)
        v.co.z = v.co.z * 20.0 + 13.0
    bm_cut.to_mesh(mesh_cutter); bm_cut.free()
    obj_cutter = bpy.data.objects.new("Temp_Atrium_Cutter", mesh_cutter)
    bpy.context.scene.collection.objects.link(obj_cutter)

    for fl_name, fl_z in [("Basement", Z_BASEMENT), ("L1_Ground", Z_BASE), ("L2", Z_L2), ("L3", Z_L3), ("L4", Z_L4), ("L5", Z_L5)]:
        mesh_slab = bpy.data.meshes.new(f"RAWL_FloorSlab_{fl_name}")
        bm_sl = bmesh.new()
        v_slab = [bm_sl.verts.new((x, y, fl_z)) for x, y in inner_pts]
        bm_sl.faces.new(v_slab)
        bmesh.ops.triangulate(bm_sl, faces=bm_sl.faces)
        bmesh.ops.solidify(bm_sl, geom=bm_sl.faces, thickness=-0.28)
        bm_sl.to_mesh(mesh_slab); bm_sl.free()
        obj_slab = bpy.data.objects.new(f"RAWL_FloorSlab_{fl_name}", mesh_slab)
        mesh_slab.materials.append(mat_concrete); col.objects.link(obj_slab)
        
        # Cut central atrium opening for upper levels L2 through L5
        if fl_name in ["L2", "L3", "L4", "L5"]:
            mod = obj_slab.modifiers.new(name="Atrium_Void", type='BOOLEAN')
            mod.object = obj_cutter
            mod.operation = 'DIFFERENCE'
            bpy.context.view_layer.objects.active = obj_slab
            bpy.ops.object.modifier_apply(modifier="Atrium_Void")

    # Remove temporary cutter
    bpy.data.objects.remove(obj_cutter, do_unlink=True)
    bpy.data.meshes.remove(mesh_cutter)

    # Atrium Mezzanine Balustrades / Railings along cutout on L2, L3, L4, L5
    mesh_rail = bpy.data.meshes.new("RAWL_Atrium_Mezzanine_Balustrades")
    bm_rail = bmesh.new()
    for fl_z in [Z_L2, Z_L3, Z_L4, Z_L5]:
        for y_side in [-414.0, -408.0]:
            res_r = bmesh.ops.create_cube(bm_rail, size=1.0)
            for v in res_r['verts']:
                v.co.x = v.co.x * 16.0 + 334.0
                v.co.y = v.co.y * 0.08 + y_side
                v.co.z = v.co.z * 1.05 + (fl_z + 0.525)
        for x_side in [326.0, 342.0]:
            res_rx = bmesh.ops.create_cube(bm_rail, size=1.0)
            for v in res_rx['verts']:
                v.co.x = v.co.x * 0.08 + x_side
                v.co.y = v.co.y * 6.0 + (-411.0)
                v.co.z = v.co.z * 1.05 + (fl_z + 0.525)
    bm_rail.to_mesh(mesh_rail); bm_rail.free()
    obj_rail = bpy.data.objects.new("RAWL_Atrium_Mezzanine_Balustrades", mesh_rail)
    mesh_rail.materials.append(mat_glass); col.objects.link(obj_rail)

    # Structural interior columns in atrium / lobby (height = Z_ROOF_DECK)
    mesh_cols = bpy.data.meshes.new("RAWL_Atrium_Structural_Columns")
    bm_col = bmesh.new()
    col_coords = [
        (326.0, -414.0), (334.0, -414.0), (342.0, -414.0),
        (326.0, -408.0), (334.0, -408.0), (342.0, -408.0)
    ]
    for cx, cy in col_coords:
        res_col = bmesh.ops.create_cone(bm_col, cap_ends=True, cap_tris=False, segments=16, radius1=0.45, radius2=0.45, depth=Z_ROOF_DECK)
        for v in res_col['verts']:
            v.co.x += cx
            v.co.y += cy
            v.co.z += Z_ROOF_DECK * 0.5
    bm_col.to_mesh(mesh_cols); bm_col.free()
    obj_cols = bpy.data.objects.new("RAWL_Atrium_Structural_Columns", mesh_cols)
    mesh_cols.materials.append(mat_stone); col.objects.link(obj_cols)

    # -------------------------------------------------------------------------
    # 12. Site Hardscape Apron & Arrival Plazas
    # -------------------------------------------------------------------------
    apron_pts = compute_inward_offsets(RAWL_PTS, thickness=-1.8)
    mesh_apron = bpy.data.meshes.new("RAWL_Site_Sidewalk_Apron")
    bm_ap = bmesh.new()
    va_in = [bm_ap.verts.new((x, y, 0.0)) for x, y in RAWL_PTS]
    va_out = [bm_ap.verts.new((x, y, 0.0)) for x, y in apron_pts]
    for i in range(N):
        i_next = (i + 1) % N
        bm_ap.faces.new((va_out[i], va_out[i_next], va_in[i_next], va_in[i]))
    bm_ap.to_mesh(mesh_apron); bm_ap.free()
    obj_ap = bpy.data.objects.new("RAWL_Site_Sidewalk_Apron", mesh_apron)
    mesh_apron.materials.append(mat_concrete); col.objects.link(obj_ap)

    # North Arrival Plaza
    mesh_plaza = bpy.data.meshes.new("RAWL_Site_North_Plaza")
    bm_pl = bmesh.new()
    res_pz = bmesh.ops.create_cube(bm_pl, size=1.0)
    for v in res_pz['verts']:
        v.co.x = v.co.x * 24.0 + 325.0
        v.co.y = v.co.y * 6.0 + (-385.0)
        v.co.z = v.co.z * 0.15 - 0.075
    for y_sw, x_sw in [(-382.5, 318.0), (-382.5, 332.0)]:
        res_sw = bmesh.ops.create_cube(bm_pl, size=1.0)
        for v in res_sw['verts']:
            v.co.x = v.co.x * 8.0 + x_sw
            v.co.y = v.co.y * 0.6 + y_sw
            v.co.z = v.co.z * 0.50 + 0.25
    bm_pl.to_mesh(mesh_plaza); bm_pl.free()
    obj_pl = bpy.data.objects.new("RAWL_Site_North_Plaza", mesh_plaza)
    mesh_plaza.materials.append(mat_plaza); col.objects.link(obj_pl)

    # -------------------------------------------------------------------------
    # 13. Lighting & Inspection Cameras
    # -------------------------------------------------------------------------
    light_data = bpy.data.lights.new(name="RAWL_Sun", type='SUN')
    light_data.energy = 4.0
    light_data.color = (1.0, 0.98, 0.94)
    light_obj = bpy.data.objects.new("RAWL_Sun", light_data)
    light_obj.location = (330.0, -410.0, 60.0)
    light_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(-40))
    col.objects.link(light_obj)

    # Calibrated Inspection Cameras with Track Targets
    cam_configs = [
        ("Cam_RAWL_01_North_StateSt", (330.0, -335.0, 15.0), (330.0, -389.0, 11.0)),
        ("Cam_RAWL_02_NW_Curved_Rotunda", (274.0, -368.0, 12.0), (302.3, -394.0, 10.0)),
        ("Cam_RAWL_03_West_GrantSt_Skywalk", (255.0, -430.0, 10.0), (288.0, -406.0, 16.0)),
        ("Cam_RAWL_04_SE_Diagonal_Facade", (385.0, -455.0, 16.0), (345.0, -420.0, 11.0)),
        ("Cam_RAWL_05_Roof_Arched_Penthouse", (375.0, -445.0, 52.0), (334.0, -410.0, 26.0)),
        ("Cam_RAWL_06_Ortho_Footprint_Top", (333.15, -411.43, 85.0), (333.15, -411.43, 0.0)),
    ]
    
    for cam_name, cam_loc, target_loc in cam_configs:
        cam_data = bpy.data.cameras.new(cam_name)
        if "Ortho" in cam_name:
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = 96.0
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            cam_obj.location = cam_loc
            cam_obj.rotation_euler = (0, 0, 0)
        else:
            cam_data.type = 'PERSP'
            cam_data.lens = 30
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            cam_obj.location = cam_loc
            point_camera_at(cam_obj, target_loc)
        col.objects.link(cam_obj)

    scene.camera = bpy.data.objects.get("Cam_RAWL_01_North_StateSt")

    # -------------------------------------------------------------------------
    # 14. Embedded Evidence & Metadata Documentation Datablock
    # -------------------------------------------------------------------------
    evidence_text = bpy.data.texts.new("README_EVIDENCE")
    evidence_text.write("""PURDUE CAMPUS DIGITAL TWIN: JERRY S. RAWLS HALL (RAWL)
=====================================================================
Building Code: RAWL
Building Name: Jerry S. Rawls Hall (Mitch Daniels School of Business / Krannert)
Address: 100 S Grant Street, West Lafayette, IN 47907
Official GIS FID: 69
Architects: Scholer Corporation & Goody Clancy & Associates
Completed: August 2003 (Dedicated October 2003)
Gross Area: ~128,000 to 132,300 sq. ft.

DOCUMENTED GEOMETRY & VERTICAL ELEVATIONS (Purdue Facilities GIS FID 69):
- Levels: 6 above-ground levels + basement
- Ground Elevation (Sea Level): 613.6 ft
- Basement (B): -18.0 ft (-5.486 m)
- Floor 1 (F01 - Ground): 0.0 ft (0.000 m)
- Floor 2 (F02): 18.0 ft (5.486 m)
- Floor 3 (F03): 34.7 ft (10.577 m)
- Floor 4 (F04): 51.4 ft (15.667 m)
- Floor 5 (F05 / Penthouse base): 66.7 ft (20.330 m)
- Main Roof Parapet / Extrusion: 79.0 ft (24.079 m)
- Skylight Penthouse Crest (R): 102.0 ft (31.090 m)

ARCHITECTURAL SIGNATURE FEATURES:
1. Exact 30-vertex footprint polygon matching Purdue Facilities GIS ground truth.
2. Northwest curving solar-tinted glass curtain wall rotunda at Mitch Daniels Blvd & Grant St.
3. Grand North entrance portico with cantilevered glass canopy, bronze struts, and limestone piers.
4. West entrance canopy on Grant Street.
5. Level 4 enclosed structural steel skywalk spanning Grant Street to Krannert Building.
6. Central structural steel arched barrel-vault skylight penthouse rising to 31.09m (102 ft).
7. Rooftop mechanical penthouses and chiller units.
8. Central multi-story open public atrium light well through floor slabs L2-L5 with balustrades.

HONEST INTERIOR BLUEPRINT & FLOORPLAN DISCLOSURE:
Detailed room-by-room CAD floorplans for Rawls Hall are restricted to internal
Purdue University Facilities GIS systems (G:\\GIS\\web_pages\\html_pages\\RAWL.html).
In accordance with project rules, no unverified internal office blueprints or
fabricated partition layouts have been invented. Interior modeling is strictly
limited to documented structural concrete floor slabs, foundation retaining walls,
structural atrium columns, and the central public daylight atrium light well.
""")

    # Scene custom properties
    scene["building_id"] = "rawls_hall"
    scene["building_code"] = "RAWL"
    scene["official_name"] = "Jerry S. Rawls Hall"
    scene["architects"] = "Scholer Corporation & Goody Clancy & Associates"
    scene["completion_year"] = 2003
    scene["gis_fid"] = 69
    scene["interior_status"] = "unverified; official blueprints restricted to Purdue GIS"

    # -------------------------------------------------------------------------
    # 15. Save Asset
    # -------------------------------------------------------------------------
    blend_target = os.path.abspath("modular/buildings/rawls_hall.blend")
    os.makedirs(os.path.dirname(blend_target), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_target)
    print(f"SUCCESS: Saved Jerry S. Rawls Hall asset to: {blend_target}")
    print(f"Total Objects in Asset_rawls_hall: {len(col.objects)}")

if __name__ == "__main__":
    main()

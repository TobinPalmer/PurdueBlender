import bpy
import bmesh
import mathutils
import math

def apply_pass4_fountain_polish():
    print("=== APPLYING PASS 4 POLISH TO ENGINEERING & LOEB FOUNTAINS ===")
    
    mat_water = bpy.data.materials.get("Wabash_River_Water")
    mat_black_granite = bpy.data.materials.get("Purdue_Polished_Black_Granite")
    mat_gray_granite = bpy.data.materials.get("Purdue_Barre_Granite")
    
    # -------------------------------------------------------------
    # 1. POLISH LOEB FOUNTAIN LAMINAR WATER ARCS (PARABOLIC BEZIER SPLINES)
    # -------------------------------------------------------------
    col_loeb = bpy.data.collections.get("16_Loeb_Fountain_and_Founders_Park")
    if col_loeb:
        lf_cx, lf_cy = -50.0, -255.0
        
        # Remove old straight cone laminar streams
        for i in range(16):
            old_name = f"LoebFountain_Inward_Laminar_Stream_{i}"
            if old_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[old_name], do_unlink=True)
                
        # Create true parabolic curved tube meshes for all 16 jets
        for b_idx in range(16):
            ang = math.radians(b_idx * 22.5)
            # Bollard nozzle start
            sx = lf_cx + 8.2 * math.cos(ang)
            sy = lf_cy + 8.2 * math.sin(ang)
            sz = 0.88
            
            # Central platform impact target
            ex = lf_cx + 3.1 * math.cos(ang)
            ey = lf_cy + 3.1 * math.sin(ang)
            ez = 0.28
            
            # Generate points along parabola: z(t) = (1-t)*sz + t*ez + 4.0 * t * (1-t)
            curve_pts = []
            num_steps = 14
            for s in range(num_steps + 1):
                t = s / num_steps
                px = (1.0 - t) * sx + t * ex
                py = (1.0 - t) * sy + t * ey
                pz = (1.0 - t) * sz + t * ez + 4.2 * t * (1.0 - t)
                curve_pts.append(mathutils.Vector((px, py, pz)))
                
            # Build tube along points using bmesh
            mesh = bpy.data.meshes.new(f"LoebFountain_Parabolic_Laminar_Arc_{b_idx}")
            bm = bmesh.new()
            
            ring_verts = []
            tube_segments = 8
            for idx, pt in enumerate(curve_pts):
                t = idx / num_steps
                radius = 0.038 * (1.0 - 0.3 * t) # tapers smoothly from 3.8cm to 2.6cm
                
                # Tangent vector
                if idx < len(curve_pts) - 1:
                    tangent = (curve_pts[idx + 1] - pt).normalized()
                else:
                    tangent = (pt - curve_pts[idx - 1]).normalized()
                    
                # Up vector / normal
                up = mathutils.Vector((0, 0, 1))
                norm = tangent.cross(up)
                if norm.length < 1e-4:
                    norm = mathutils.Vector((1, 0, 0))
                else:
                    norm.normalize()
                binorm = tangent.cross(norm).normalized()
                
                ring = []
                for a_i in range(tube_segments):
                    theta = 2.0 * math.pi * a_i / tube_segments
                    offset = (norm * math.cos(theta) + binorm * math.sin(theta)) * radius
                    v = bm.verts.new(pt + offset)
                    ring.append(v)
                ring_verts.append(ring)
                
            # Create faces between rings
            for r_i in range(len(ring_verts) - 1):
                r1 = ring_verts[r_i]
                r2 = ring_verts[r_i + 1]
                for seg_i in range(tube_segments):
                    next_seg = (seg_i + 1) % tube_segments
                    bm.faces.new([r1[seg_i], r1[next_seg], r2[next_seg], r2[seg_i]])
                    
            bm.to_mesh(mesh)
            bm.free()
            
            arc_obj = bpy.data.objects.new(f"LoebFountain_Parabolic_Laminar_Arc_{b_idx}", mesh)
            if mat_water:
                mesh.materials.append(mat_water)
            col_loeb.objects.link(arc_obj)
            
        print("Loeb Fountain 16 parabolic laminar arcs generated successfully.")
        
        # Add 8 Geyser Peak Spray Crowns (falling mushroom droplets)
        for s_idx in range(8):
            spray_name = f"LoebFountain_Peak_Spray_Droplet_{s_idx}"
            if spray_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[spray_name], do_unlink=True)
            sp_ang = math.radians(s_idx * 45.0)
            sp_x = lf_cx + 1.2 * math.cos(sp_ang)
            sp_y = lf_cy + 1.2 * math.sin(sp_ang)
            
            sp_mesh = bpy.data.meshes.new(spray_name)
            sp_bm = bmesh.new()
            bmesh.ops.create_icosphere(sp_bm, subdivisions=1, radius=0.28)
            sp_bm.to_mesh(sp_mesh)
            sp_bm.free()
            
            sp_obj = bpy.data.objects.new(spray_name, sp_mesh)
            sp_obj.location = (sp_x, sp_y, 8.4)
            if mat_water:
                sp_mesh.materials.append(mat_water)
            col_loeb.objects.link(sp_obj)

    # -------------------------------------------------------------
    # 2. POLISH ENGINEERING FOUNTAIN WATERFALL SHEETS
    # -------------------------------------------------------------
    col_eng = bpy.data.collections.get("08_Engineering_Fountain_and_Mall")
    if col_eng:
        ef_cx, ef_cy = 0.0, 195.0
        
        # Add 4 sculpted parabolic cascading waterfall curtains hugging inner pylon face
        for p_idx, p_ang_deg in enumerate([45, 135, 225, 315]):
            curtain_name = f"EngFountain_Sculpted_Waterfall_Curtain_{p_ang_deg}"
            if curtain_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[curtain_name], do_unlink=True)
                
            p_ang = math.radians(p_ang_deg)
            # Create a 10-tier curved curtain sheet falling from z=11.2m to z=0.15m
            c_mesh = bpy.data.meshes.new(curtain_name)
            c_bm = bmesh.new()
            
            tiers = 12
            strip_width = 1.15
            side_vec = mathutils.Vector((-math.sin(p_ang), math.cos(p_ang), 0.0)) * (strip_width * 0.5)
            
            strip_rows = []
            for t_i in range(tiers + 1):
                fraction = t_i / tiers
                z = 11.2 * (1.0 - fraction) + 0.15 * fraction
                # Radius curves from 1.5m at top to 3.2m at bottom
                curv_r = 1.45 + 1.75 * (fraction ** 1.6)
                center_pt = mathutils.Vector((
                    ef_cx + curv_r * math.cos(p_ang),
                    ef_cy + curv_r * math.sin(p_ang),
                    z
                ))
                v_left = c_bm.verts.new(center_pt - side_vec * (1.0 + 0.4 * fraction))
                v_right = c_bm.verts.new(center_pt + side_vec * (1.0 + 0.4 * fraction))
                strip_rows.append((v_left, v_right))
                
            for t_i in range(tiers):
                v_l1, v_r1 = strip_rows[t_i]
                v_l2, v_r2 = strip_rows[t_i + 1]
                c_bm.faces.new([v_l1, v_r1, v_r2, v_l2])
                
            c_bm.to_mesh(c_mesh)
            c_bm.free()
            
            curtain_obj = bpy.data.objects.new(curtain_name, c_mesh)
            if mat_water:
                c_mesh.materials.append(mat_water)
            col_eng.objects.link(curtain_obj)
            
        print("Engineering Fountain 4 parabolic waterfall curtains sculpted and linked.")
        
    # Save master blend file
    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Master scene successfully saved with Pass 4 fountain polish: {save_path}")

if __name__ == "__main__":
    apply_pass4_fountain_polish()

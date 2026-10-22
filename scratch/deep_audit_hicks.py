import bpy
import bmesh
import json
import math
from mathutils import Vector

def run_deep_audit():
    print("=" * 80)
    print("INDEPENDENT ARCHITECTURAL QA AUDIT: HICKS UNDERGRADUATE LIBRARY (HIKS)")
    print("=" * 80)
    
    scene = bpy.context.scene
    print(f"Active Scene: '{scene.name}'")
    
    # 1. UNIT SETTINGS
    print("\n[SECTION 1: UNITS & MASTER COMPATIBILITY]")
    units = scene.unit_settings
    print(f"  Unit System: {units.system} (Expected: METRIC)")
    print(f"  Unit Scale: {units.scale_length} (Expected: 1.0)")
    print(f"  Length Unit: {units.length_unit} (Expected: METERS)")
    
    # Custom properties
    print("  Scene Custom Properties:")
    for k, v in sorted(scene.items()):
        if not k.startswith("_"):
            print(f"    {k}: {repr(v)}")
            
    # 2. COLLECTIONS & HIERARCHY
    print("\n[SECTION 2: COLLECTION STRUCTURE]")
    master_col = bpy.data.collections.get("Asset_hicks_library")
    print(f"  Master Collection 'Asset_hicks_library': {'EXISTS' if master_col else 'MISSING'}")
    if master_col:
        print(f"  Child collections ({len(master_col.children)}):")
        for c in master_col.children:
            print(f"    - {c.name} ({len(c.objects)} objects)")
            for obj in c.objects:
                print(f"        * {obj.name} (type={obj.type})")
        print(f"  Total unique objects in hierarchy: {len(master_col.all_objects)}")
        
    # Check if scene collection has loose objects outside master collection
    loose_objs = [o.name for o in scene.collection.objects if master_col and o.name not in master_col.all_objects]
    print(f"  Loose objects in Scene Collection outside master: {loose_objs if loose_objs else 'None (Clean)'}")

    # 3. GEOMETRY & TRANSFORMS AUDIT
    print("\n[SECTION 3: TRANSFORMS, TOPOLOGY & MESH AUDIT]")
    mesh_objects = [o for o in master_col.all_objects if o.type == 'MESH']
    print(f"  Total Mesh Objects: {len(mesh_objects)}")
    
    non_identity_transforms = []
    unapplied_modifiers = []
    non_manifold_report = []
    
    total_verts = 0
    total_faces = 0
    
    for obj in mesh_objects:
        # Check transforms
        loc = obj.location
        rot = obj.rotation_euler
        sca = obj.scale
        if (loc.x != 0 or loc.y != 0 or loc.z != 0 or 
            rot.x != 0 or rot.y != 0 or rot.z != 0 or 
            sca.x != 1 or sca.y != 1 or sca.z != 1):
            non_identity_transforms.append((obj.name, tuple(round(x, 4) for x in loc), tuple(round(x, 4) for x in rot), tuple(round(x, 4) for x in sca)))
            
        # Modifiers
        if obj.modifiers:
            unapplied_modifiers.append((obj.name, [m.type for m in obj.modifiers]))
            
        mesh = obj.data
        total_verts += len(mesh.vertices)
        total_faces += len(mesh.polygons)
        
        # BMesh inspection for topology
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        
        non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
        non_manifold_verts = [v for v in bm.verts if not v.is_manifold]
        boundary_edges = [e for e in bm.edges if e.is_boundary]
        wire_edges = [e for e in bm.edges if e.is_wire]
        
        if non_manifold_edges or non_manifold_verts or wire_edges:
            non_manifold_report.append({
                "name": obj.name,
                "nm_edges": len(non_manifold_edges),
                "nm_verts": len(non_manifold_verts),
                "boundary_edges": len(boundary_edges),
                "wire_edges": len(wire_edges),
                "verts": len(bm.verts),
                "faces": len(bm.faces)
            })
        bm.free()
        
    print(f"  Total Vertices across all meshes: {total_verts}")
    print(f"  Total Faces across all meshes: {total_faces}")
    print(f"  Objects with non-identity local transforms: {len(non_identity_transforms)}")
    if non_identity_transforms:
        for name, loc, rot, sca in non_identity_transforms[:5]:
            print(f"    {name}: loc={loc}, rot={rot}, sca={sca}")
    print(f"  Objects with unapplied modifiers: {len(unapplied_modifiers)}")
    if unapplied_modifiers:
        for name, mods in unapplied_modifiers:
            print(f"    {name}: {mods}")
    print(f"  Mesh topology inspection (open surfaces / boundaries): {len(non_manifold_report)} objects with boundary or non-manifold elements")
    for r in non_manifold_report:
        print(f"    {r['name']}: verts={r['verts']}, faces={r['faces']}, nm_edges={r['nm_edges']} (boundary={r['boundary_edges']}), wire={r['wire_edges']}")

    # 4. FOOTPRINT & GIS ACCURACY AUDIT
    print("\n[SECTION 4: FOOTPRINT & GIS PLACEMENT AUDIT]")
    with open("modular/buildings/target_buildings_gis.json", "r") as f:
        target_gis = json.load(f)["HIKS"]
    gis_poly = target_gis["world_polygon"]
    
    wall = bpy.data.objects.get("HIKS_Exterior_Masonry_Walls")
    if wall:
        wall_verts = [wall.matrix_world @ v.co for v in wall.data.vertices]
        xs = [v.x for v in wall_verts]
        ys = [v.y for v in wall_verts]
        zs = [v.z for v in wall_verts]
        
        gis_xs = [p[0] for p in gis_poly]
        gis_ys = [p[1] for p in gis_poly]
        
        print(f"  Target GIS Vertices Count: {len(gis_poly)} (Closed polygon with {len(gis_poly)-1} unique corners)")
        print(f"  GIS Bounding Box: X=[{min(gis_xs):.4f}, {max(gis_xs):.4f}], Y=[{min(gis_ys):.4f}, {max(gis_ys):.4f}]")
        print(f"  Wall Bounding Box: X=[{min(xs):.4f}, {max(xs):.4f}], Y=[{min(ys):.4f}, {max(ys):.4f}], Z=[{min(zs):.4f}, {max(zs):.4f}]")
        
        print("\n  Per-Vertex Distance Analysis from GIS polygon corners:")
        vertex_errors = []
        for i, gp in enumerate(gis_poly[:-1]):
            # Find closest vertex in wall mesh in XY plane
            dists = [math.hypot(v.x - gp[0], v.y - gp[1]) for v in wall_verts]
            min_d = min(dists)
            closest_idx = dists.index(min_d)
            closest_v = wall_verts[closest_idx]
            vertex_errors.append((i, gp, min_d, closest_v))
            print(f"    GIS Corner {i:02d} ({gp[0]:.3f}, {gp[1]:.3f}) -> Closest Wall Vtx ({closest_v.x:.3f}, {closest_v.y:.3f}, z={closest_v.z:.3f}) | Error: {min_d*1000:.3f} mm")
            
        max_err = max(e[2] for e in vertex_errors)
        mean_err = sum(e[2] for e in vertex_errors) / len(vertex_errors)
        print(f"\n  Summary of Footprint Deviations:")
        print(f"    Max Vertex Error:  {max_err*1000:.4f} mm ({max_err:.6f} m)")
        print(f"    Mean Vertex Error: {mean_err*1000:.4f} mm ({mean_err:.6f} m)")
        print(f"    Strict 0.0m GIS Alignment (tolerance < 1.0mm): {'PASSED' if max_err < 0.001 else 'EXCEEDED'}")

    # 5. VERTICAL ELEVATION AUDIT
    print("\n[SECTION 5: VERTICAL ELEVATIONS AUDIT]")
    # Official reference heights:
    # Grade: 0.0m
    # Extrusion (parapet base / roof deck level): 8 ft = 2.4384 m
    # Roof apex (Skylight R): 24 ft = 7.3152 m
    # Ground floor slab G: -17.4 ft = -5.30352 m
    # Basement floor slab B: -31.0 ft = -9.4488 m
    
    elevation_checks = [
        ("Roof Peak (R=24ft)", "HIKS_Pyramidal_Skylights_Bronze_Framing", 'max_z', 7.3152, 24.0),
        ("Pyramidal Glazing Peak", "HIKS_Pyramidal_Skylights_Solar_Glazing", 'max_z', 7.3152, 24.0),
        ("Parapet Coping Peak", "HIKS_Limestone_Parapet_Coping_and_Base", 'max_z', 3.048, 10.0),
        ("Exterior Wall Top", "HIKS_Exterior_Masonry_Walls", 'max_z', 2.898, 9.5),
        ("Roof Gravel Ballast Deck", "HIKS_Roof_Gravel_Ballast_Deck", 'min_z', 2.4384, 8.0),
        ("Ground Level Grade (F01)", "HIKS_Plaza_Pavement_North", 'max_z', 0.0, 0.0),
        ("Ground Floor Slab Top (G=-17.4ft)", "HIKS_FloorSlab_Ground_Subterranean", 'max_z', -5.30352, -17.4),
        ("Basement Floor Slab Top (B=-31ft)", "HIKS_FloorSlab_Basement_Foundation", 'max_z', -9.4488, -31.0),
        ("Foundation Footing Base", "HIKS_Subterranean_Foundation_Walls", 'min_z', -9.95, -32.64)
    ]
    
    for label, obj_name, mode, target_m, target_ft in elevation_checks:
        obj = bpy.data.objects.get(obj_name)
        if obj and obj.type == 'MESH':
            world_zs = [(obj.matrix_world @ v.co).z for v in obj.data.vertices]
            val = max(world_zs) if mode == 'max_z' else min(world_zs)
            diff_m = val - target_m
            diff_mm = diff_m * 1000
            print(f"  {label:<35}: Measured={val:8.4f} m | Target={target_m:8.4f} m ({target_ft:5.1f} ft) | Diff={diff_mm:+7.2f} mm")
        else:
            print(f"  {label:<35}: Object '{obj_name}' NOT FOUND")

    # 6. ARCHITECTURAL ARTICULATION & DETAILS AUDIT
    print("\n[SECTION 6: ARCHITECTURAL ARTICULATION & ELEMENTS]")
    all_objs_by_name = {o.name: o for o in master_col.all_objects}
    key_features = [
        "HIKS_Exterior_Masonry_Walls",
        "HIKS_Limestone_Parapet_Coping_and_Base",
        "HIKS_Limestone_Accent_Bands",
        "HIKS_North_Entrance_Vestibule_Glazing",
        "HIKS_North_Entrance_Bronze_Mullions",
        "HIKS_North_Entrance_Double_Doors",
        "HIKS_North_Entrance_Canopy",
        "HIKS_Roof_Gravel_Ballast_Deck",
        "HIKS_Pyramidal_Skylights_Bronze_Framing",
        "HIKS_Pyramidal_Skylights_Solar_Glazing",
        "HIKS_Subterranean_Foundation_Walls",
        "HIKS_FloorSlab_Ground_Subterranean",
        "HIKS_FloorSlab_Basement_Foundation",
        "HIKS_Subterranean_Structural_Columns",
        "HIKS_Central_Spiral_Staircase",
        "HIKS_Atrium_Bronze_Guardrails",
        "HIKS_Stewart_Center_Tunnel_Connector",
        "HIKS_Plaza_Pavement_North",
        "HIKS_Plaza_Lightwells_Retaining_Walls",
        "HIKS_Site_Grading_and_Lawn"
    ]
    for feat in key_features:
        if feat in all_objs_by_name:
            obj = all_objs_by_name[feat]
            vcount = len(obj.data.vertices) if obj.type == 'MESH' else 0
            fcount = len(obj.data.polygons) if obj.type == 'MESH' else 0
            mats = [m.name for m in obj.data.materials if m] if obj.type == 'MESH' else []
            print(f"  [OK] {feat:<42}: Verts={vcount:5d}, Faces={fcount:5d}, Mats={mats}")
        else:
            print(f"  [MISSING] {feat}")

    # 7. MATERIALS & PBR SHADERS AUDIT
    print("\n[SECTION 7: MATERIALS & PBR SHADERS]")
    for mat in sorted(bpy.data.materials, key=lambda m: m.name):
        print(f"\n  Material: '{mat.name}' (use_nodes={mat.use_nodes})")
        if mat.use_nodes and mat.node_tree:
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                base_color = bsdf.inputs["Base Color"].default_value[:]
                roughness = bsdf.inputs["Roughness"].default_value
                metallic = bsdf.inputs["Metallic"].default_value
                ior = bsdf.inputs["IOR"].default_value
                transmission = bsdf.inputs["Transmission Weight"].default_value if "Transmission Weight" in bsdf.inputs else bsdf.inputs.get("Transmission", None)
                alpha = bsdf.inputs["Alpha"].default_value
                
                # Check normal input connection
                normal_input = bsdf.inputs["Normal"]
                has_normal = normal_input.is_linked
                normal_source = normal_input.links[0].from_node.type if has_normal else "None"
                
                print(f"    Principled BSDF Settings:")
                print(f"      Base Color: ({base_color[0]:.3f}, {base_color[1]:.3f}, {base_color[2]:.3f}, {base_color[3]:.3f})")
                print(f"      Roughness:  {roughness:.3f}")
                print(f"      Metallic:   {metallic:.3f}")
                print(f"      IOR:        {ior:.3f}")
                print(f"      Alpha:      {alpha:.3f}")
                if transmission is not None:
                    trans_val = transmission.default_value if hasattr(transmission, 'default_value') else transmission
                    print(f"      Transmission: {trans_val}")
                print(f"      Normal Node: {normal_source}")
                
                # List node types
                node_types = [n.type for n in nodes]
                print(f"      Node Types: {node_types}")
            else:
                print("    NO Principled BSDF node found!")
        else:
            print("    Does not use nodes!")

    # 8. FLOORPLAN & EVIDENCE AUDIT
    print("\n[SECTION 8: FLOORPLAN FIDELITY & EMBEDDED DOCUMENTATION]")
    text_block = bpy.data.texts.get("EVIDENCE_AND_INTERIOR_NOTES.txt")
    if text_block:
        print(f"  Embedded Text Block: 'EVIDENCE_AND_INTERIOR_NOTES.txt' ({len(text_block.lines)} lines)")
        print("-" * 60)
        for line in text_block.lines:
            print(f"  | {line.body}")
        print("-" * 60)
    else:
        print("  WARNING: 'EVIDENCE_AND_INTERIOR_NOTES.txt' NOT FOUND in bpy.data.texts")

    # 9. CAMERAS AUDIT
    print("\n[SECTION 9: INSPECTION CAMERAS AUDIT]")
    cams = [o for o in bpy.data.objects if o.type == 'CAMERA']
    print(f"  Total Cameras: {len(cams)}")
    for cam in cams:
        loc = cam.location
        rot = cam.rotation_euler
        lens = cam.data.lens
        clip_end = cam.data.clip_end
        print(f"    {cam.name:<35}: Loc=({loc.x:7.2f}, {loc.y:7.2f}, {loc.z:7.2f}), Rot=({math.degrees(rot.x):6.1f}, {math.degrees(rot.y):6.1f}, {math.degrees(rot.z):6.1f}) deg, Lens={lens:.1f}mm, ClipEnd={clip_end:.1f}m")

    print("\n" + "=" * 80)
    print("DEEP AUDIT FINISHED")
    print("=" * 80)

if __name__ == "__main__":
    run_deep_audit()

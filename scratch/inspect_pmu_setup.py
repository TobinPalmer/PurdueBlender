import bpy

# Check PMU camera
cam_pmu = bpy.data.objects.get('Cam_67_PMU_StateStreet_South_Hero')
if cam_pmu:
    print(f"PMU Camera found: {cam_pmu.name}, loc: {cam_pmu.location}, rot: {cam_pmu.rotation_euler}")
    print(f"Lens: {cam_pmu.data.lens}mm, clip: {cam_pmu.data.clip_start}-{cam_pmu.data.clip_end}")
else:
    print("Cam_67_PMU_StateStreet_South_Hero not found! Searching PMU cameras:")
    for o in bpy.data.objects:
        if 'pmu' in o.name.lower() or 'union' in o.name.lower():
            if o.type == 'CAMERA':
                print(f"  Camera: {o.name}")

# Check World nodes
w = bpy.context.scene.world
if w and w.node_tree:
    print(f"\nWorld '{w.name}' nodes:")
    for n in w.node_tree.nodes:
        print(f"  Node: {n.name} ({n.type})")
        if n.type == 'TEX_SKY':
            print(f"    sky_type: {getattr(n, 'sky_type', 'N/A')}")
            print(f"    sun_direction: {getattr(n, 'sun_direction', 'N/A')}")
            print(f"    sun_elevation: {getattr(n, 'sun_elevation', 'N/A')}")
            print(f"    sun_rotation: {getattr(n, 'sun_rotation', 'N/A')}")
            print(f"    altitude: {getattr(n, 'altitude', 'N/A')}")
            print(f"    air: {getattr(n, 'air_density', 'N/A')}")
            print(f"    dust: {getattr(n, 'dust_density', 'N/A')}")
            print(f"    ozone: {getattr(n, 'ozone_density', 'N/A')}")

# Check all Sun lights
print("\nAll Sun lights in master scene:")
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN':
        print(f"  Sun: {o.name}, energy: {o.data.energy}, color: {list(o.data.color)}, hidden: {o.hide_render}")

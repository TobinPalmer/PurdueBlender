import bpy

# Check available compute devices in Blender
prefs = bpy.context.preferences
cprefs = prefs.addons.get('cycles')
if cprefs:
    cprefs = cprefs.preferences
    print("Cycles compute device types:", [i.identifier for i in cprefs.bl_rna.properties['compute_device_type'].enum_items])
    for dt in ['OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL']:
        try:
            cprefs.compute_device_type = dt
            cprefs.get_devices()
            devices = cprefs.devices
            print(f"Device type {dt}: {[d.name for d in devices if d.use]}")
            break
        except Exception as e:
            pass

# Check scene lights
print("\n--- Current Lights in master scene ---")
for o in bpy.data.objects:
    if o.type == 'LIGHT':
        print(f"Light: {o.name}, type: {o.data.type}, energy: {o.data.energy}, color: {list(o.data.color)}")

# Check world
w = bpy.context.scene.world
print("\n--- Current World ---")
if w:
    print(f"World: {w.name}")
    if w.node_tree:
        for n in w.node_tree.nodes:
            print(f"  Node: {n.name} ({n.type})")
            if n.type == 'BACKGROUND':
                print(f"    Strength: {n.inputs['Strength'].default_value}, Color: {list(n.inputs['Color'].default_value)}")

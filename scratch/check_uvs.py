import bpy

print("--- UV MAP AUDIT ---")
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        uv_layers = obj.data.uv_layers
        has_uv = len(uv_layers) > 0
        mat_names = [m.name for m in obj.data.materials if m]
        needs_uv = any("Brick" in m or "Limestone" in m for m in mat_names)
        print(f"  {obj.name:<42}: UV layers={len(uv_layers)} ({[l.name for l in uv_layers]}), mats={mat_names}")

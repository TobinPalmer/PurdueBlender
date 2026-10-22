import bpy

print(f"{'Object Name':<42} | {'Min Z':<8} | {'Max Z':<8} | {'Height':<8}")
print("-" * 72)
for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if obj.type == 'MESH':
        zs = [(obj.matrix_world @ v.co).z for v in obj.data.vertices]
        min_z, max_z = min(zs), max(zs)
        h = max_z - min_z
        print(f"{obj.name:<42} | {min_z:8.4f} | {max_z:8.4f} | {h:8.4f}")

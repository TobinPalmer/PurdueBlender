import bpy

print("Scene:", bpy.context.scene.name)
print("Collections:", [c.name for c in bpy.data.collections])
for obj in bpy.data.objects:
    print(f"Object: {obj.name}, type: {obj.type}, loc: {obj.location}, dims: {obj.dimensions}")
    for mat_slot in obj.material_slots:
        if mat_slot.material:
            print(f"  Material: {mat_slot.material.name}")

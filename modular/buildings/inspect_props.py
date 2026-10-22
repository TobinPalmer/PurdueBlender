import bpy

print("=== SCENE PROPS ===")
for k, v in bpy.context.scene.items():
    print(f"  {k}: {v}")

print("\n=== COLLECTION PROPS ===")
for c in bpy.data.collections:
    print(f"Collection {c.name}:")
    for k, v in c.items():
        print(f"  {k}: {v}")

print("\n=== OBJECT PROPS ===")
for o in bpy.data.objects:
    if len(o.keys()) > 0:
        props = {k: o[k] for k in o.keys() if not k.startswith("_")}
        if props:
            print(f"Object {o.name}: {props}")

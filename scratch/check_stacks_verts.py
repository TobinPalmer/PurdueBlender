import bpy

stacks = bpy.data.objects.get("HIKS_Subterranean_Book_Stacks_Massing")
if stacks:
    for i, v in enumerate(stacks.data.vertices[:16]):
        print(f"v{i}: {v.co}")

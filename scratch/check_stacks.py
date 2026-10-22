import bpy

stacks = bpy.data.objects.get("HIKS_Subterranean_Book_Stacks_Massing")
if stacks:
    zs = [(stacks.matrix_world @ v.co).z for v in stacks.data.vertices]
    print(f"Book stacks Z bounds: [{min(zs):.3f}, {max(zs):.3f}]")
    print(f"Book stacks dimensions: {stacks.dimensions}")
    print(f"Book stacks location: {stacks.location}")

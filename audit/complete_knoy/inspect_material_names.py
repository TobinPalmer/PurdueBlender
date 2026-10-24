import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/knoy_hall.blend')
print(json.dumps([m.name for m in bpy.data.materials],indent=2))

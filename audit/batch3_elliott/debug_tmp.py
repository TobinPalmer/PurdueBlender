import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']
print(len(w.data.vertices));print([(round(v.co.x,2),round(v.co.y,2),round(v.co.z,2)) for v in w.data.vertices[:10]]);print(min(v.co.x for v in w.data.vertices[:188]),max(v.co.x for v in w.data.vertices[:188]),min(v.co.y for v in w.data.vertices[:188]),max(v.co.y for v in w.data.vertices[:188]))

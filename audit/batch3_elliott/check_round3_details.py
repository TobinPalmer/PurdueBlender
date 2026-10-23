import bpy
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend';bpy.ops.wm.open_mainfile(filepath=p)
for n in ['ELLT_Estimated_Stage_Fly_Tower','ELLT_Estimated_Raised_Clay_Tile_Courses','ELLT_Access_North_Estimated_Level_Interior_Route','ELLT_Access_South_Estimated_Level_Interior_Route']:
 o=bpy.data.objects.get(n);print(n,tuple(round(x,2) for x in o.dimensions),dict(o.items()))

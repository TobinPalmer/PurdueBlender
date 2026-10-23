import bpy,json
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_elliott_hall_of_music']
print(json.dumps({'opened':bpy.data.filepath,'mesh_count':sum(o.type=='MESH' for o in c.objects),'temporary_hovde_objects':[o.name for o in bpy.data.objects if o.name.startswith('TEMP_R7_')],'round7_objects':sum(o.name.startswith('ELLT_R7_') for o in c.objects)}))

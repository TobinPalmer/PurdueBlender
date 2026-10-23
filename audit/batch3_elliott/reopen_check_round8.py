import bpy,json
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=p);c=bpy.data.collections['Asset_elliott_hall_of_music']
print(json.dumps({'opened':bpy.data.filepath,'mesh_count':sum(o.type=='MESH' for o in c.objects),'round8_objects':sum(o.name.startswith('ELLT_R8_') for o in c.objects),'old_connector_objects':[o.name for o in c.objects if o.name.startswith('ELLT_R5_Hovde_Link_') or o.name.startswith('ELLT_R4_Hovde_Walkway_')],'temporary_render_objects':[o.name for o in bpy.data.objects if o.name.startswith('TEMP_R8_')]}))

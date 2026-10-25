import bpy,os,json
from mathutils import Vector
asset=bpy.data.collections.get('Asset_lawson_hall');root=bpy.data.objects.get('AssetRoot_lawson_hall')
assert asset and root and bpy.data.filepath
objs=[o for o in asset.all_objects if o]; meshes=[o for o in objs if o.type=='MESH']
results={'file':bpy.data.filepath,'reopened_saved_source':os.path.normcase(os.path.abspath(bpy.path.abspath(bpy.data.filepath)))==os.path.normcase(os.path.abspath(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend')),'object_count':len(objs),'mesh_count':len(meshes),'root_transform':[list(r) for r in root.matrix_world],'old_entry_objects':[o.name for o in objs if o.name=='LWSN_R3_Curved_Limestone_Main_Entry_Canopy' or o.name.startswith('LWSN_R3_Entry_') or o.name=='LWSN_R3_Entrance_Sign_Text'],'r7_objects':[o.name for o in objs if o.name.startswith('LWSN_R7_')],'wall_dims':list(bpy.data.objects['LWSN_1130_Harris_Video_Wall'].dimensions)}
print(json.dumps(results,indent=2))

import bpy
for n in ['DUHME_EAST_F3_Room_Partition_2_-1','DUHME_EAST_F2_Room_Partition_2_-1','DUHME_EAST_F1_Room_Partition_2_-1','DUHME_EAST_F3_Room_Partition_3_-1']:
 o=bpy.data.objects[n];print(n,'loc',tuple(round(v,2) for v in o.location),'dims',tuple(round(v,2) for v in o.dimensions),'mat',[m.name for m in o.data.materials])
 print('corners',[(round((o.matrix_world@__import__('mathutils').Vector(v)).x,2),round((o.matrix_world@__import__('mathutils').Vector(v)).y,2),round((o.matrix_world@__import__('mathutils').Vector(v)).z,2)) for v in o.bound_box[:4]])

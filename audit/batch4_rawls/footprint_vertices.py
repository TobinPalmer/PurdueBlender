import bpy
for n in ['RAWL_Footprint_Reference_Wire','RAWL_FloorSlab_L1_Ground']:
 o=bpy.data.objects[n];print(n);print('verts',[(round(v.co.x,2),round(v.co.y,2),round(v.co.z,2)) for v in o.data.vertices[:60]])

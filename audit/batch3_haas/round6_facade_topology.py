import bpy
for name in ['HAAS_Photo_Entrance_Limestone_Facade','HAAS_Brick_Wall_East']:
 o=bpy.data.objects[name];print(name,'type',o.type,'v',len(o.data.vertices),'p',len(o.data.polygons),'mats',[(i,m.name) for i,m in enumerate(o.data.materials)]); print('poly mats', {i:sum(1 for p in o.data.polygons if p.material_index==i) for i in range(len(o.data.materials))})

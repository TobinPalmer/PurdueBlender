import bpy, math, json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for name in ['SC_Foundation_Limestone_Plinth','SC_Brick_Masonry_Exterior_Walls','SC_Official_GIS_Footprint_Overlay_Ribbon']:
 o=bpy.data.objects.get(name);print(name,o.type,len(o.data.vertices) if o.type=='MESH' else len(o.data.splines),o.data.polygons.__len__() if o.type=='MESH' else '-')
 print('parent',o.parent.name if o.parent else None,'coll',[(c.name) for c in o.users_collection])

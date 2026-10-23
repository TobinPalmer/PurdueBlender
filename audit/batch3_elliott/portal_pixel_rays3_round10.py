import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');s=bpy.context.scene;campos=Vector((58,21,11));target=Vector((44.1,9.2,5.8));q=(target-campos).to_track_quat('-Z','Y');right=q@Vector((1,0,0));up=q@Vector((0,1,0));direction=q@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get()
for px,py in [(780,610),(790,600),(920,580),(940,590),(850,610),(905,610),(930,560)]:
 x=(px/1600-.5)*17.5;y=(.5-py/1050)*(17.5*1050/1600);origin=campos+right*x+up*y;ok,h,no,f,ob,ma=s.ray_cast(dg,origin,direction);print((px,py),tuple(round(v,2) for v in h),ob.name if ob else None)
for name in ['ELLT_R6_Continuous_Limestone_Belt_Courses_Estimated','ELLT_R6_Continuous_Limestone_Belt_Courses_Estimated.001']:
 o=bpy.data.objects[name];print(name,'poly',len(o.data.polygons),'data',o.data.name,'users',o.data.users,'mod',len(o.modifiers))

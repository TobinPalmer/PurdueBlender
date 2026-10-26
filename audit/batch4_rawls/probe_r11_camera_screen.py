import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']; p=g.data.polygons[4]; c=sum((g.matrix_world@g.data.vertices[i].co for i in p.vertices),Vector())/4; n=(g.matrix_world.to_3x3()@p.normal).normalized(); ss=[bpy.data.objects[x].matrix_world.translation for x in ['RAWL_1086_R10_Schematic_Projection_Surface_01','RAWL_1086_R10_Schematic_Projection_Surface_02']]; t=sum(ss,Vector())/2+Vector((0,0,.2)); vd=(t-c).normalized(); loc=c-vd*5.2; d=bpy.data.cameras.new('diagcam'); o=bpy.data.objects.new('diagcam',d); sc.collection.objects.link(o); o.location=loc; o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler(); d.lens=42; sc.camera=o; bpy.context.view_layer.update(); sc.render.resolution_x=1080; sc.render.resolution_y=810
print('camera',tuple(loc),'target',tuple(t),'normaldot',vd.dot(n))
for name in ['RAWL_1086_R10_Schematic_Projection_Surface_01','RAWL_1086_R10_Schematic_Projection_Surface_02']:
 q=bpy.data.objects[name]; co=q.matrix_world.translation; ndc=world_to_camera_view(sc,o,co); print(name,'center',tuple(round(v,3) for v in ndc),'mat',q.data.materials[0].name if q.data.materials else None)
mat=bpy.data.materials['RAWL_Interior_WarmWhite']; bs=next(x for x in mat.node_tree.nodes if x.type=='BSDF_PRINCIPLED'); print('white',bs.inputs['Base Color'].default_value[:],bs.inputs['Emission Color'].default_value[:],bs.inputs['Emission Strength'].default_value)


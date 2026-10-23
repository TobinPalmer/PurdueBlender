import bpy, json
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_brown_laboratory_of_chemistry_brwn_aed3885.blend'
bpy.ops.wm.open_mainfile(filepath=p); o=bpy.context.scene.objects[0]
print('verts',len(o.data.vertices),'faces',len(o.data.polygons))
print('footprint verts:')
for v in o.data.vertices:
 if abs(v.co.z)<1e-4: print(tuple(round(float(a),3) for a in (o.matrix_world@v.co)))

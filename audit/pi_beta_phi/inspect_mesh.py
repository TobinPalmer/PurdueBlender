import bpy, json
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301838781_891384f.blend'
bpy.ops.wm.open_mainfile(filepath=p); o=bpy.data.objects['House_301838781']
d={'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'faces':[list(poly.vertices) for poly in o.data.polygons]}
open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\pi_beta_phi\original_mesh.json','w').write(json.dumps(d,indent=2))

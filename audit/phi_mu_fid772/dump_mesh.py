import bpy, json, math
p=r'modular/buildings/massing_house_301836574_fff1661.blend'; bpy.ops.wm.open_mainfile(filepath=p); o=bpy.data.objects['House_301836574']; me=o.data
verts=[list(v.co) for v in me.vertices]
faces=[{'v':list(poly.vertices),'mat':poly.material_index} for poly in me.polygons]
open(r'audit/phi_mu_fid772/base_mesh.json','w').write(json.dumps({'verts':verts,'faces':faces},indent=2))

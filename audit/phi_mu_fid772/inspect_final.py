import bpy,json,collections
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_house_301836574_fff1661.blend')
o=bpy.data.objects['House_301836574']; d={}
for m in o.data.materials:
 if m:
  p=m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
  d[m.name]={"diffuse":list(m.diffuse_color),"bsdf":list(p.inputs['Base Color'].default_value) if p else None}
c=collections.Counter((o.data.materials[p.material_index].name if p.material_index < len(o.data.materials) and o.data.materials[p.material_index] else 'NONE') for p in o.data.polygons)
open(r'audit/phi_mu_fid772/final_material_inspection.json','w').write(json.dumps({'materials':d,'faces_by_material':c,'materials_count':len(o.data.materials),'faces':len(o.data.polygons),'verts':len(o.data.vertices)},indent=2))

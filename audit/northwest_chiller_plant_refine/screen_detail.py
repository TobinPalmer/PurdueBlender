import bpy, os, json, hashlib
from mathutils import Vector
p=os.path.abspath('modular/buildings/northwest_chiller_plant.blend')
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_northwest_chiller_plant']
def mat(name,color,metallic=.4,rough=.52):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough; return m
def box(name,loc,dim,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for cc in list(o.users_collection): cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.clear();o.data.materials.append(ma);return o
screen=mat('NWCP_refine_screen_charcoal',(.22,.25,.25),.46,.58)
slat=mat('NWCP_refine_screen_fin_metal',(.30,.34,.34),.64,.42)
obj=bpy.data.objects['NWCP_roof_equipment_screen'];obj.data.materials.clear();obj.data.materials.append(screen)
pts=[obj.matrix_world@Vector(v) for v in obj.bound_box];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
# narrow standing screen fins articulate its visible long face without changing screen envelope
added=[]
for i in range(23):
 x=lo[0]+.35+(hi[0]-lo[0]-.7)*(i/22)
 added.append(box(f'NWCP_refine_screen_vertical_fin_{i+1}',(x,lo[1]-.035, (lo[2]+hi[2])*.5),(.035,.055,hi[2]-lo[2]-.20),slat).name)
# save and capture checks
bpy.ops.wm.save_as_mainfile(filepath=p)
print('added_screen_fins',len(added),'collection_objects',len(c.all_objects),'shell_bounds',lo,hi)

import bpy,json,bmesh
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];m=bpy.data.materials['POTR_Current_Roof_Membrane_Estimate'];m.diffuse_color=(.12,.14,.15,1);bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.12,.14,.15,1);bs.inputs['Roughness'].default_value=.9
# make sure roof slab and T-shaped plate both use the same restrained matte membrane estimate
for name in ['POTR_Official_864_Roof','POTR_Historic2016_Room401_Penthouse_Roof']:
 o=c.objects[name]
 if m.name not in [x.name for x in o.data.materials if x]:o.data.materials.append(m)
 o['material_status']='Estimated dark gray low-sheen roof membrane; not measured or confirmed by current close imagery.'
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];print('reopened',len(c.all_objects),list(c.objects['AssetRoot_potter_engineering'].location))

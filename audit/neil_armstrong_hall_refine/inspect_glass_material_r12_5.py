import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
for name in ['ARMS_Clear_Safety_Glass','ARMS_Solar_Curtain_Glass','ARMS_R6_Reflective_Blue_Glass']:
 m=bpy.data.materials.get(name); b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m else None
 print(json.dumps({'name':name,'exists':bool(m),'surface_render_method':getattr(m,'surface_render_method',None) if m else None,'blend_method':getattr(m,'blend_method',None) if m else None,'base':list(b.inputs['Base Color'].default_value) if b else None,'alpha':float(b.inputs['Alpha'].default_value) if b else None,'transmission':float(b.inputs['Transmission Weight'].default_value) if b and 'Transmission Weight' in b.inputs else None,'rough':float(b.inputs['Roughness'].default_value) if b else None,'metal':float(b.inputs['Metallic'].default_value) if b else None},indent=2))

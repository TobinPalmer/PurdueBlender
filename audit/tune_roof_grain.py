import bpy, os
bid=os.path.splitext(os.path.basename(bpy.data.filepath))[0]
matname={'hicks_library':'Mat_HIKS_Roof_Gravel_Ballast','lawson_hall':'LWSN_Roof_Gravel','krannert_building':'KRAN_Roof_Membrane'}[bid]
mat=bpy.data.materials[matname];nt=mat.node_tree
gr=next(n for n in nt.nodes if n.label=='Roof Grain Color Variation')
gr.inputs['Scale'].default_value=2.8;gr.inputs['Detail'].default_value=1.0
ramp=next(n for n in nt.nodes if n.label=='Restrained tonal variation')
ramp.color_ramp.elements[0].position=.40;ramp.color_ramp.elements[1].position=.60
print('FINAL ROOF GRAIN',bid,'scale',gr.inputs['Scale'].default_value,'ramp',[(e.position,tuple(round(c,4) for c in e.color[:3])) for e in ramp.color_ramp.elements])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

import bpy,os
for key,matname,scale,low,high,bumpdist in [
 ('mccutcheon_hall','Roof_Membrane',1.6,.94,1.06,.0005),
 ('niswonger_aviation_tech','NISW_Roof_Membrane',1.6,.94,1.06,.0005)]:
 path=os.path.abspath('modular/buildings/'+key+'.blend'); bpy.ops.wm.open_mainfile(filepath=path); bpy.context.preferences.filepaths.save_version=0
 m=bpy.data.materials[matname]; nodes=m.node_tree.nodes
 noise=next(n for n in nodes if n.type=='TEX_NOISE' and n.get('texture_final_two'))
 remap=next(n for n in nodes if n.type=='MAP_RANGE' and n.label=='Low contrast color range')
 bump=next((n for n in nodes if n.type=='BUMP' and n.get('texture_final_two')),None)
 noise.inputs['Scale'].default_value=scale; remap.inputs['To Min'].default_value=low; remap.inputs['To Max'].default_value=high
 if bump: bump.inputs['Distance'].default_value=bumpdist
 m['texture_finish_final_two']=f'roof: object-space {scale:.1f}/m low-contrast mineral/aggregate variation ±6%, hue preserving; micro relief {bumpdist*1000:.2f} mm.'
 bpy.ops.wm.save_as_mainfile(filepath=path); print('UPDATED',key,matname,'noise',scale,'color range',low,high,'bump',bumpdist)

import bpy
for m in bpy.data.materials:
 nt=m.node_tree
 if not nt: continue
 noises=[n for n in nt.nodes if n.type=='TEX_NOISE']
 bumps=[n for n in nt.nodes if n.type=='BUMP']
 if not noises and not bumps: continue
 p=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
 color=p.inputs['Base Color'].default_value[:3] if p and not p.inputs['Base Color'].is_linked else 'linked'
 print('MAT',m.name,'color',color,'rough',p.inputs['Roughness'].default_value if p else '-', 'noises',[(n.inputs['Scale'].default_value,n.inputs['Detail'].default_value, [(l.from_node.type,l.from_socket.name,l.to_socket.name) for l in nt.links if l.to_node==n]) for n in noises], 'bumps',[(b.inputs['Strength'].default_value,b.inputs['Distance'].default_value) for b in bumps])

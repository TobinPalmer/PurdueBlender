import bpy, os, sys
file=bpy.data.filepath
changed=[]
for mat in bpy.data.materials:
    nt=mat.node_tree
    if not nt: continue
    # Keep each material's existing colors and texture graph, but make procedural scales stable in world-sized object coordinates.
    for link in list(nt.links):
        if link.from_node.type=='TEX_COORD' and link.from_socket.name=='Generated' and link.to_socket.name=='Vector':
            nt.links.new(link.from_node.outputs['Object'], link.to_socket)
    is_ground=any(k in mat.name.lower() for k in ('lawn','paver','paving','plaza','gravel','roof','terrazzo','concrete','slab'))
    is_masonry=any(k in mat.name.lower() for k in ('brick','limestone','granite','bedford'))
    for noise in (n for n in nt.nodes if n.type=='TEX_NOISE'):
        # Noise driving surface relief should read as fine grain, not visible speckling.
        if any(l.to_node.type=='BUMP' and l.to_socket.name=='Height' for l in nt.links if l.from_node==noise):
            old=noise.inputs['Scale'].default_value
            noise.inputs['Scale'].default_value=min(max(old,5.0),24.0)
            noise.inputs['Detail'].default_value=min(noise.inputs['Detail'].default_value,2.0)
            if old != noise.inputs['Scale'].default_value: changed.append((mat.name,'noise',old,noise.inputs['Scale'].default_value))
    for bump in (n for n in nt.nodes if n.type=='BUMP'):
        height_link=next((l for l in nt.links if l.to_node==bump and l.to_socket.name=='Height'),None)
        if not height_link: continue
        old_s=bump.inputs['Strength'].default_value; old_d=bump.inputs['Distance'].default_value
        max_d=.002 if is_masonry else (.003 if is_ground else .0015)
        bump.inputs['Distance'].default_value=min(old_d,max_d)
        bump.inputs['Strength'].default_value=min(old_s,.12 if is_masonry else .10)
        if old_s!=bump.inputs['Strength'].default_value or old_d!=bump.inputs['Distance'].default_value:
            changed.append((mat.name,'bump',old_s,old_d,bump.inputs['Strength'].default_value,bump.inputs['Distance'].default_value))
print('UPDATED MATERIAL SETTINGS',changed)
bpy.ops.wm.save_as_mainfile(filepath=file)

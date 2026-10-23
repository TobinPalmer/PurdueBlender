import bpy
m=bpy.data.materials['HAAS_R6_Red_Brick_Inlay']
for n in m.node_tree.nodes:
 print('\n',n.name,n.type)
 if n.type=='TEX_BRICK':
  for k in ['Color1','Color2','Mortar','Scale','Mortar Size','Mortar Smooth','Brick Width','Row Height']:
   if k in n.inputs:
    v=n.inputs[k].default_value
    try:v=list(v)
    except:pass
    print(k,v)
 if n.type=='BUMP':print('strength',n.inputs['Strength'].default_value,'distance',n.inputs['Distance'].default_value)
 if n.type=='TEX_NOISE':
  for k in ['Scale','Detail','Roughness']:print(k,n.inputs[k].default_value)

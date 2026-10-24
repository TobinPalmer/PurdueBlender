import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\engineering_foliage_library.blend'
with bpy.data.libraries.load(p,link=False) as (src,dst): dst.collections=['PH_Tree_Small_02_LOD2','PH_Fir_Sapling_A_LOD2','PH_Fir_Sapling_B_LOD2','PH_Fir_Sapling_C_LOD2']; dst.materials=['grass_ground','asphalt_01']
for c in dst.collections:
 print('ASSET',c.name,[(o.name,len(o.data.polygons),len(o.data.vertices)) for o in c.all_objects if o.type=='MESH'])
for m in dst.materials:
 print('MATERIAL',m.name)
 for n in m.node_tree.nodes:
  if n.type in ('TEX_COORD','MAPPING','TEX_IMAGE','NORMAL_MAP','BSDF_PRINCIPLED','BUMP'):
   print(' NODE',n.name,n.type,n.inputs.get('Vector').default_value[:] if n.type=='TEX_IMAGE' and n.inputs.get('Vector') else '')
   if n.type=='TEX_IMAGE' and n.image: print(' IMAGE',n.image.name,list(n.image.size),n.image.packed_file is not None)
 for l in m.node_tree.links:
  if l.to_node.type in ('TEX_IMAGE','BSDF_PRINCIPLED','NORMAL_MAP','BUMP'): print(' LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

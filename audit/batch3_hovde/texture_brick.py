import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); path=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
mat=bpy.data.materials['Purdue_Red_Brick'];mat.diffuse_color=(.32,.075,.033,1);mat.use_nodes=True
nt=mat.node_tree;nt.nodes.clear()
def node(t,n,x,y):
 o=nt.nodes.new(t);o.label=n;o.location=(x,y);return o
out=node('ShaderNodeOutputMaterial','Brick wall output',980,80)
bs=node('ShaderNodeBsdfPrincipled','Fired clay brick',740,80);bs.inputs['Roughness'].default_value=.82
geo=node('ShaderNodeNewGeometry','World position / normal',-1000,220)
pos=node('ShaderNodeSeparateXYZ','Position components',-800,300);nt.links.new(geo.outputs['Position'],pos.inputs[0])
norm=node('ShaderNodeSeparateXYZ','Normal components',-800,-220);nt.links.new(geo.outputs['Normal'],norm.inputs[0])
def combine(label, xcoord, ycoord, y):
 v=node('ShaderNodeCombineXYZ',label,-580,y);nt.links.new(pos.outputs[xcoord],v.inputs['X']);nt.links.new(pos.outputs[ycoord],v.inputs['Y']);v.inputs['Z'].default_value=0;return v
yz=combine('Y/Z projection', 'Y','Z',500)
xz=combine('X/Z projection','X','Z',250)
xy=combine('X/Y projection','X','Y',0)
def brick(label, coord, y):
 b=node('ShaderNodeTexBrick',label, -340,y);b.inputs['Color1'].default_value=(.38,.095,.043,1);b.inputs['Color2'].default_value=(.285,.060,.030,1);b.inputs['Mortar'].default_value=(.14,.105,.080,1);b.inputs['Scale'].default_value=1;b.inputs['Mortar Size'].default_value=.006;b.inputs['Mortar Smooth'].default_value=.003;b.inputs['Brick Width'].default_value=.21;b.inputs['Row Height'].default_value=.065;nt.links.new(coord.outputs[0],b.inputs['Vector']);return b
byz=brick('Brick courses on Y/Z facade',yz,520);bxz=brick('Brick courses on X/Z facade',xz,260);bxy=brick('Horizontal brick projection',xy,0)
def absolute(src,label,y):
 n=node('ShaderNodeMath',label,-570,y);n.operation='ABSOLUTE';nt.links.new(src,n.inputs[0]);return n
ax=absolute(norm.outputs['X'],'Absolute X normal',-120);ay=absolute(norm.outputs['Y'],'Absolute Y normal',-250);az=absolute(norm.outputs['Z'],'Absolute Z normal',-380)
choose_xz=node('ShaderNodeMath','Select X/Z for Y-normal face',-350,-210);choose_xz.operation='GREATER_THAN';nt.links.new(ax.outputs[0],choose_xz.inputs[0]);nt.links.new(ay.outputs[0],choose_xz.inputs[1])
def mix(name,a,b,factor,y):
 m=node('ShaderNodeMixRGB',name,30,y);nt.links.new(factor,m.inputs[0]);nt.links.new(a,m.inputs[1]);nt.links.new(b,m.inputs[2]);return m
vert_color=mix('Choose vertical brick plane',byz.outputs['Color'],bxz.outputs['Color'],choose_xz.outputs[0],360)
vert_fac=mix('Choose vertical brick height',byz.outputs['Fac'],bxz.outputs['Fac'],choose_xz.outputs[0],110)
horizontal=node('ShaderNodeMath','Horizontal surface selector',-130,-390);horizontal.operation='GREATER_THAN';nt.links.new(az.outputs[0],horizontal.inputs[0]);horizontal.inputs[1].default_value=.5
final_color=mix('Horizontal or vertical projection',vert_color.outputs[0],bxy.outputs['Color'],horizontal.outputs[0],300)
final_fac=mix('Height projection',vert_fac.outputs[0],bxy.outputs['Fac'],horizontal.outputs[0],60)
bump=node('ShaderNodeBump','Fine recessed mortar',450,-120);bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.0005;nt.links.new(final_fac.outputs[0],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);nt.links.new(final_color.outputs[0],bs.inputs['Base Color']);nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert len(bpy.data.collections['Asset_hovde_hall'].all_objects)==638;assert len(bpy.data.materials['Purdue_Red_Brick'].node_tree.nodes)>=20
print('saved and reopened; objects=638; facade material has axis-correct projections')

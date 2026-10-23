import bpy,math,json
from mathutils import Vector
C=bpy.data.collections['Asset_lawson_hall']
def mat(n,c):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);return m
wall=mat('LWSN_Interior_Painted_Plaster',(.79,.77,.69));wood=mat('LWSN_Interior_Maple',(.43,.24,.1));metal=mat('LWSN_Furniture_Dark_Metal',(.055,.06,.065));fabric=mat('LWSN_Seating_Upholstery',(.19,.25,.27))
def cube(n,p,s,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.append(m);o['evidence']='Purdue lawson_1.PDF traced first floor; heights/furniture dimensions estimated';return o
def xy(x,y):return (-15.55+(x-327)*.0944,42.27-(y-88)*.0944)
def seg(a,b,n='Partition',z=1.8,h=2.8):
 x,y=xy(*a);xx,yy=xy(*b);o=cube('LWSN_Plan_'+n,((x+xx)/2,(y+yy)/2,z),(math.hypot(xx-x,yy-y),.14,h),wall);o.rotation_euler.z=math.atan2(yy-y,xx-x)
# Trace official plan wall centerlines, preserving door breaks.
segments=[((374,90),(374,125)),((374,140),(374,318)),((374,333),(374,366)),((327,123),(363,123)),((327,157),(363,157)),((327,189),(363,189)),((327,222),(363,222)),((327,255),(363,255)),((327,289),(363,289)),((327,322),(363,322)),((327,366),(363,366)),((392,90),(392,124)),((428,90),(428,124)),((461,90),(461,124)),((494,90),(494,134)),((392,137),(494,137)),((435,158),(492,158)),((435,158),(435,247)),((435,247),(492,247)),((492,158),(492,247)),((514,174),(514,270)),((514,174),(549,174)),((514,205),(549,205)),((514,237),(549,237)),((514,270),(559,270)),((559,174),(559,270)),((578,176),(578,357)),((578,194),(613,194)),((578,226),(613,226)),((578,258),(613,258)),((578,290),(613,290)),((578,322),(613,322)),((478,327),(478,357)),((478,357),(625,357)),((433,327),(433,436)),((391,371),(391,436)),((478,379),(478,515)),((478,531),(625,531)),((327,531),(356,531)),((327,564),(356,564)),((327,605),(363,605)),((327,637),(363,637)),((327,670),(363,670)),((327,703),(363,703)),((374,584),(374,736)),((390,584),(390,736)),((390,584),(434,584)),((390,621),(434,621)),((390,661),(434,661)),((390,701),(434,701)),((434,584),(434,736)),((327,883),(392,883)),((408,883),(467,883)),((408,883),(408,983)),((550,737),(615,737)),((550,737),(550,810)),((550,810),(615,810)),((550,836),(615,836)),((572,836),(572,872))]
for a,b in segments:seg(a,b)
# tiered seminar classroom 1142 according to plan
for row in range(7):
 py=391+row*17;x,y=xy(550,py)
 cube('LWSN_1142_Tier', (x,y,.47+row*.105),(12.6,1.6,.12+row*.21),wall)
 for col in range(9):
  x,y=xy(496+col*13,py);zz=.65+row*.21
  cube('LWSN_1142_Seat',(x,y,zz+.45),(.45,.46,.12),fabric);cube('LWSN_1142_Back',(x,y+.22,zz+.75),(.45,.09,.52),fabric)
# offices documented around north perimeter, furniture arrangements illustrative
for py in [106,140,172,205,238,272,305,340]:
 x,y=xy(346,py);cube('LWSN_Office_Desk',(x,y,1.13),(1.55,.75,.07),wood);cube('LWSN_Office_Chair',(x+.7,y, .88),(.45,.45,.1),fabric)
# Commons 1130 video wall source official room description
x,y=xy(609,618);cube('LWSN_1130_Harris_Video_Wall',(x,y,2.0),(.12,5.5,2.4),metal)
for px,py in [(552,565),(568,610),(572,664),(523,693)]:
 x,y=xy(px,py);cube('LWSN_Commons_Table',(x,y,1.14),(1.5,.85,.08),wood)
 for side in [-1,1]:cube('LWSN_Commons_Chair',(x,y+side*.7,.87),(.45,.45,.12),fabric)
# brick texture: Object coordinates in meters; project horizontal facade using dominant normal
m=bpy.data.materials.get('LWSN_Purdue_Red_Brick');m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexBrick');tex.inputs['Color1'].default_value=(.32,.09,.045,1);tex.inputs['Color2'].default_value=(.19,.045,.025,1);tex.inputs['Mortar'].default_value=(.38,.34,.27,1);tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=.203;tex.inputs['Row Height'].default_value=.067;tex.inputs['Mortar Size'].default_value=.008
geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);comb=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(sep.outputs['X'],comb.inputs['X']);nt.links.new(sep.outputs['Z'],comb.inputs['Y']);nt.links.new(comb.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],p.inputs['Base Color']);b=nt.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.003;nt.links.new(tex.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

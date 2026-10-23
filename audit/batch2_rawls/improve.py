import bpy,math,json,os
from mathutils import Vector
OUT=os.path.dirname(__file__); col=bpy.data.collections['Asset_rawls_hall']; origin=(323.6582336425781,-409.62242126464844)
def mat(n,c,r=.6):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=r;return m
plaster=mat('RAWL_Interior_WarmWhite',(.72,.70,.62));wood=mat('RAWL_Interior_Wood',(.27,.105,.035));ochre=mat('RAWL_Interior_Ochre',(.63,.30,.045));carpet=mat('RAWL_Interior_CharcoalCarpet',(.055,.075,.09));metal=bpy.data.materials['RAWL_Dark_Bronze_Metal']
def box(n,p,d,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name='RAWL_2026_'+n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(m);o['evidence']='2024 Roadschool first-floor plan; approximate similarity registration';return o
def xy(p):return (399.0-.12*p[1]-origin[0],-384.0-.12*p[0]-origin[1])
def segment(n,a,b,z=1.8,h=3.6,m=plaster):
 a=xy(a);b=xy(b);o=box(n,((a[0]+b[0])/2,(a[1]+b[1])/2,z),(math.dist(a,b),.16,h),m);o.rotation_euler.z=math.atan2(b[1]-a[1],b[0]-a[0]);return o
def line(n,pts):
 for i,(a,b) in enumerate(zip(pts,pts[1:])):segment(n+str(i),a,b)
# Published classroom boundaries. Door gaps left where plan shows swings.
line('1086',[(127,318),(120,295),(245,256),(301,437),(176,475),(131,333)])
line('1071',[(77,536),(88,457),(142,457),(169,545),(83,551)])
line('1062',[(184,500),(197,544),(216,605)])
# Trace the curved classroom boundaries with cubic Bezier samples from the map.
def curve(n,p):
 pts=[]
 for i in range(25):
  t=i/24;pts.append(tuple((1-t)**3*p[0][j]+3*(1-t)**2*t*p[1][j]+3*(1-t)*t*t*p[2][j]+t**3*p[3][j] for j in range(2)))
 line(n,pts)
curve('1062_Curve',[(216,605),(287,589),(320,538),(306,462)])
curve('1057_Curve',[(68,551),(67,620),(122,663),(200,660)])
line('1057',[(68,551),(169,545),(191,607)])
line('1057_DoorGap',[(196,625),(200,660),(201,746)])
line('1011',[(112,870),(112,800),(233,800),(233,756)])
line('Core',[(240,732),(385,732),(385,655),(305,655),(305,732)])
line('Core2',[(347,655),(347,732)])
line('1098',[(121,215),(121,246),(190,246),(190,215)])
# Framed wood door leaves at documented classroom entry locations; retain passage gaps.
for n,a,b in [('1086',(127,318),(131,333)),('1062',(176,475),(184,500)),('1057',(191,607),(196,625))]:
 segment('Door_'+n,a,b,1.08,2.16,wood)
# Photo-supported palette and finishes. Furnishing placements below are illustrative, not surveyed.
for m in [wood,ochre,plaster,carpet]:
 nt=m.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=35;tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Object'],n.inputs['Vector']);b=nt.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.0015;b.inputs['Strength'].default_value=.15;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],nt.nodes['Principled BSDF'].inputs['Normal'])
# Real-world brick scale in meters; normalized object transforms baked to preserve scale.
brick=bpy.data.materials['RAWL_Purdue_Red_Brick'];nt=brick.node_tree;bs=nt.nodes['Principled BSDF'];tc=nt.nodes.new('ShaderNodeTexCoord');tex=nt.nodes.new('ShaderNodeTexBrick');tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=.215;tex.inputs['Row Height'].default_value=.075;tex.inputs['Mortar Size'].default_value=.006;tex.inputs['Color1'].default_value=(.31,.085,.04,1);tex.inputs['Color2'].default_value=(.46,.16,.075,1);tex.inputs['Mortar'].default_value=(.39,.36,.31,1)
# Separate projections for facade orientations; use geometry normals to blend vertical brick planes.
sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tc.outputs['Object'],sep.inputs[0]);comb=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(sep.outputs['X'],comb.inputs['X']);nt.links.new(sep.outputs['Z'],comb.inputs['Y']);nt.links.new(comb.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);b=nt.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.004;b.inputs['Strength'].default_value=.28;nt.links.new(tex.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
for m in bpy.data.materials:
 if m.use_nodes:
  bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:m.diffuse_color=bs.inputs['Base Color'].default_value
# Classroom 1086 desks and chairs follow room orientation, quantities illustrative.
for row in range(6):
 for seat in range(7):
  p=xy((156+seat*12+row*3,310+row*23-seat*3.7));o=box('1086_Desk',(*p,.75),(1.22,.55,.055),wood);o['evidence']='Illustrative furniture, not exact 2024 seating inventory';box('1086_Chair',(p[0]-.6,p[1],.45),(.43,.43,.07),carpet)
text=bpy.data.texts.new('RAWL_2026_EVIDENCE');text.write('First-floor partitions traced from https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf (2024). Approximate plan registration X=399-.12*pixelY Y=-384-.12*pixelX then local origin subtraction. Plan rendered 486x972. Registration uncertainty 1-2m; wall heights/door construction estimated. Interior finish palette observed in Purdue Libraries photo PPBUC03065 dated 2003-07-25 https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/3050/ . Upper-floor interiors unresolved; furniture illustrative. Google Maps could not be accessed; not verified. Original GIS floor heights not certified measured.')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('RAWLS_SAVED',len(col.all_objects))

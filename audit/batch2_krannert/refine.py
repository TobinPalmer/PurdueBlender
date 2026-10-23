import bpy,os,math,json
from mathutils import Vector,Matrix
C=bpy.data.collections['Asset_krannert_building']
# orient chairs around their seat using creation-order groups
obs=[o for o in bpy.data.objects if o.name.startswith('KRAN_New_Seat')]
for seat in obs:
 x,y,z=seat.location;worldy=y-412.71900939941406
 if abs(worldy-(-413.22))<.02:
  # corresponding six objects by mesh creation index; names suffix agree for seat/back, legs index differs
  suffix=seat.name.removeprefix('KRAN_New_Seat');back=bpy.data.objects.get('KRAN_New_Back'+suffix)
  if back:back.location.y=y-.23
 if abs(worldy+419.6)<.02:
  # stools need continuous longer legs to floor3.9, not a floating standard chair
  for o in C.objects:
   if o.name.startswith('KRAN_New_ChairLeg') and abs(o.location.x-x)<.3 and abs(o.location.y-y)<.3:
    o.location.z-=.15;o.dimensions.z+=.3
# physically directional oak grain
m=bpy.data.materials['KRAN_Photo_Oak'];nodes=m.node_tree.nodes;links=m.node_tree.links;q=next(n for n in nodes if n.type=='TEX_NOISE');tex=next(n for n in nodes if n.type=='TEX_COORD');v=nodes.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(.7,15,15);links.new(tex.outputs['Object'],v.inputs[0]);links.new(v.outputs[0],q.inputs['Vector']);r=nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.24,.1,.025,1);r.color_ramp.elements[1].color=(.52,.3,.1,1);links.new(q.outputs['Fac'],r.inputs[0]);links.new(r.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
# preserve source wall normals but expose validation status
bpy.context.scene['batch2_review_status']='partial completion; honest independent5.4/10 prior latest fixes; room XY inferred; remaining interior unverified'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

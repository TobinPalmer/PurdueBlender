import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');c=bpy.data.collections['Asset_class_of_1950'];w=bpy.data.objects['CL50_Corrected_GIS_Wall_Envelope'];print('MATS',[(m.name if m else None) for m in w.data.materials]);m=w.data.materials[0]
for o in c.all_objects:
 if o and 'RoundBrickColumn' in o.name:o.data.materials.clear();o.data.materials.append(m)
# continuous circulation floor within official perimeter
r=next(x for x in json.loads((P/'audit/official_building_references.json').read_text())['buildings'] if x['code']=='CL50')['rings_xy_m'][0];ring=[(x+107.69000244140625,y+116.9949951171875,.4) for x,y in r[:-1]];me=bpy.data.meshes.new('CL50_Continuous_Ground');me.from_pydata(ring,[],[tuple(range(len(ring)))]);me.update();o=bpy.data.objects.new('CL50_New_Continuous_Circulation_Floor',me);c.objects.link(o);me.materials.append(bpy.data.materials['CL50_Pale_Terrazzo'])
# wood grain variation via elongated procedural coordinates
ma=bpy.data.materials['CL50_Photographic_Brown_Wood'];t=ma.node_tree;tex=t.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;mapping=t.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(.4,30,8);co=t.nodes.new('ShaderNodeTexCoord');ramp=t.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.06,.022,.009,1);ramp.color_ramp.elements[1].color=(.3,.14,.04,1);t.links.new(co.outputs['Object'],mapping.inputs[0]);t.links.new(mapping.outputs[0],tex.inputs['Vector']);t.links.new(tex.outputs['Fac'],ramp.inputs[0]);t.links.new(ramp.outputs['Color'],t.nodes.get('Principled BSDF').inputs['Base Color'])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

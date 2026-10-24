import bpy, json, os
from mathutils import Vector
path=os.path.normcase(os.path.abspath(bpy.data.filepath))
expected=os.path.normcase(os.path.abspath('modular/buildings/mccutcheon_hall.blend'))
if path != expected: raise RuntimeError(f'Unexpected file {path}')
asset=bpy.data.collections.get('Asset_mccutcheon_hall')
assert asset and bpy.data.objects.get('MCUT_Official_Footprint_Overlay')

def make_surface(name, dark, light, scale, bump_distance):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color=(*dark,1.0)
    mat.use_nodes=True
    nt=mat.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); out.location=(620,20)
    bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); bs.location=(360,20)
    bs.inputs['Roughness'].default_value=0.92
    tex=nt.nodes.new('ShaderNodeTexCoord'); tex.location=(-800,80)
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.location=(-580,80)
    noise.inputs['Scale'].default_value=scale
    noise.inputs['Detail'].default_value=2.0
    noise.inputs['Roughness'].default_value=0.68
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.location=(-300,120)
    ramp.color_ramp.elements[0].position=0.22; ramp.color_ramp.elements[0].color=(*dark,1.0)
    ramp.color_ramp.elements[1].position=0.78; ramp.color_ramp.elements[1].color=(*light,1.0)
    bump=nt.nodes.new('ShaderNodeBump'); bump.location=(100,-160)
    bump.inputs['Strength'].default_value=0.1
    bump.inputs['Distance'].default_value=bump_distance
    nt.links.new(tex.outputs['Generated'],noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return mat

lawn=make_surface('MCUT_Grass_Lawn_Qualitative',(0.025,0.075,0.018),(0.07,0.16,0.035),52.0,0.012)
asphalt=make_surface('MCUT_Asphalt_Drive_Qualitative',(0.045,0.05,0.055),(0.09,0.095,0.10),68.0,0.004)
assignments={'Site_Lawn_Base':lawn,'Site_McCutcheon_Drive':asphalt,'Site_MacArthur_Drive':asphalt}
for name,mat in assignments.items():
    obj=bpy.data.objects.get(name)
    if obj is None or obj.type!='MESH': raise RuntimeError(f'Missing expected site mesh {name}')
    if len(obj.data.materials): obj.data.materials[0]=mat
    else: obj.data.materials.append(mat)
    obj['surface_material_status']='Qualitative procedural surface; material category is supported by site context, exact color/aggregate is not measured.'
# Diagnostic overlay remains viewport-visible, render-hidden.
overlay=bpy.data.objects['MCUT_Official_Footprint_Overlay']
overlay.hide_render=True; overlay.hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=expected)
print('MCUT_R2_APPLIED='+json.dumps({'assignments':{k:v.name for k,v in assignments.items()},'overlay_render_hidden':overlay.hide_render,'collection_objects':len(asset.all_objects)}))

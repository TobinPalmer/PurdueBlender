import bpy,json
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_rawls\rawls_hall_r10_candidate.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
mat=bpy.data.materials['RAWL_CurtainWall_Glass']
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value=(0.48,0.59,0.62,1)
bsdf.inputs['Roughness'].default_value=0.18
bsdf.inputs['Transmission Weight'].default_value=0.28
bsdf.inputs['Coat Weight'].default_value=0.02
bsdf.inputs['Specular IOR Level'].default_value=0.28
mat.diffuse_color=(0.48,0.59,0.62,0.48)
mat['r10_note']='Moderately bright, lower-reflection glazing tuning prompted by the R9 through-glass review; this is a visual material estimate, not a measured facade specification.'
bpy.ops.wm.save_as_mainfile(filepath=str(p))
print(json.dumps({'material':mat.name,'base_color':[0.48,0.59,0.62,1],'roughness':0.18,'transmission':0.28,'coat':0.02,'specular':0.28}))

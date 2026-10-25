"""R3 roof finish/edge pass, guided by ArcGIS overhead imagery.
No footprint or roof elevations are moved; inferred plate extents remain approximate.
"""
import bpy, math, shutil
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET_PATH=ROOT/'modular/buildings/niswonger_aviation_tech.blend'
OUT=ROOT/'audit/niswonger_aviation_tech_refine'
asset=bpy.data.collections['Asset_niswonger_aviation_tech']; assert asset
names=['NISW_R2_Roof_Brick_Wing','NISW_R2_Roof_Classroom_Wing']
roofs=[bpy.data.objects[n] for n in names]
# Unique, subdued roof finish so refinement does not alter the inherited Hangar 1 or connector material.
matname='NISW_R3_Roof_Membrane_Weathered_Graphite'
mat=bpy.data.materials.get(matname) or bpy.data.materials.new(matname)
mat.diffuse_color=(.17,.185,.20,1);mat.use_nodes=True
nt=mat.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); out.location=(650,0)
bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.location=(400,0)
bs.inputs['Base Color'].default_value=(.16,.18,.20,1)
bs.inputs['Metallic'].default_value=.16
bs.inputs['Roughness'].default_value=.64
noise=nt.nodes.new('ShaderNodeTexNoise');noise.location=(-600,-80);noise.inputs['Scale'].default_value=38;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65
coord=nt.nodes.new('ShaderNodeTexCoord');coord.location=(-820,-80)
nt.links.new(coord.outputs['Generated'],noise.inputs['Vector'])
bump=nt.nodes.new('ShaderNodeBump');bump.location=(150,-120);bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.012
nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
# Keep Generated coordinates anchored per roof plate; a fine, low-amplitude roughness breakup prevents the broad planes reading as white plastic.
rough=nt.nodes.new('ShaderNodeMapRange');rough.location=(120,100);rough.inputs['From Min'].default_value=.0;rough.inputs['From Max'].default_value=1.;rough.inputs['To Min'].default_value=.58;rough.inputs['To Max'].default_value=.72
nt.links.new(noise.outputs['Fac'],rough.inputs['Value']);nt.links.new(rough.outputs['Result'],bs.inputs['Roughness'])
mat['source_basis']='Qualitative gray roof tone and visible broad roof zones from Esri World Imagery aerial tiles in audit/niswonger_aviation_tech_refine/arcgis_world_imagery/; no measured finish or material identification claimed.'
mat['finish_basis']='Subtle fine surface response only; no external textures.'
for ob in roofs:
    ob.data.materials.clear(); ob.data.materials.append(mat)
    ob['roof_extent_status']='Approximate closure retained from prior round, based on modeled wall tops; checked qualitatively against overhead imagery, not surveyed.'
    ob['roof_surface_status']='Neutral dark-gray membrane-like finish; photographic material identification unavailable.'
# Clean/rebuild prior R3 details on reruns.
for ob in list(asset.objects):
    if ob.name.startswith('NISW_R3_Roof_') and ob.name not in names:
        bpy.data.objects.remove(ob,do_unlink=True)
# Roof edge metal: a low, narrow edge cap echoes the crisp, dark borders visible in the overhead imagery.
trim=bpy.data.materials.get('NISW_R3_Roof_Edge_Metal') or bpy.data.materials.new('NISW_R3_Roof_Edge_Metal')
trim.diffuse_color=(.23,.26,.28,1);trim.use_nodes=True
pbs=trim.node_tree.nodes.get('Principled BSDF');pbs.inputs['Base Color'].default_value=(.21,.24,.26,1);pbs.inputs['Metallic'].default_value=.34;pbs.inputs['Roughness'].default_value=.44
trim['basis']='Low-profile edge metal is an illustrative roof-boundary treatment guided by overhead roof outlines; exact section/detail is unverified.'
# Low 12-cm wide, 3.5-cm high strips, following the existing plate edges; these are caps, not parapet-height walls.
def bar(name,loc,dim):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    # keep just the newly created object in the export collection
    for c in list(ob.users_collection):c.objects.unlink(ob)
    asset.objects.link(ob);ob.data.materials.append(trim)
    bevel=ob.modifiers.new('Edge cap soft arris','BEVEL');bevel.width=.012;bevel.segments=2
    norm=ob.modifiers.new('Edge cap normals','WEIGHTED_NORMAL');norm.keep_sharp=True
    return ob
# Low profile details placed at shell/transition boundaries. The connector-facing edges use the existing fascia as the visible transition.
# Brick wing caps: outer west and north boundary, plus raised-step east edge.
bar('NISW_R3_Roof_Edge_Brick_West',(-39.40,24.75,4.745),(.12,35.20,.045))
bar('NISW_R3_Roof_Edge_Brick_North',(-35.65,42.30,4.745),(7.50,.12,.045))
bar('NISW_R3_Roof_Edge_Brick_South',(-35.65,7.20,4.745),(7.50,.12,.045))
# Main classroom roof perimeter: parapet cap line on north, west and south, and a short metal transition at the glazed connector.
bar('NISW_R3_Roof_Edge_Classroom_North',(-13.43,43.90,7.865),(36.50,.12,.045))
bar('NISW_R3_Roof_Edge_Classroom_West',(-31.65,25.55,7.865),(.12,36.80,.045))
bar('NISW_R3_Roof_Edge_Classroom_South',(-13.43,7.20,7.865),(36.50,.12,.045))
# Light, closely spaced lap / panel joints, interpreted from repeated linear breaks in the overhead roof surface.
# Shallow raised bars (12 mm) and restrained contrast avoid implying a specific roof manufacturer or exact seam pitch.
seammat=bpy.data.materials.get('NISW_R3_Roof_Lap_Seam') or bpy.data.materials.new('NISW_R3_Roof_Lap_Seam')
seammat.diffuse_color=(.125,.14,.155,1);seammat.use_nodes=True
sb=seammat.node_tree.nodes.get('Principled BSDF');sb.inputs['Base Color'].default_value=(.12,.135,.15,1);sb.inputs['Metallic'].default_value=.12;sb.inputs['Roughness'].default_value=.68
seammat['basis']='Qualitative linear roof breaks visible in Esri World Imagery; seam spacing in model is illustrative, not a surveyed measurement.'
for i,x in enumerate([-29.0,-23.0,-17.0,-11.0,-5.0,1.0]):
    bar(f'NISW_R3_Roof_Lap_Classroom_{i:02d}',(x,25.55,7.855),(.018,36.20,.012)).data.materials.clear();bpy.data.objects[f'NISW_R3_Roof_Lap_Classroom_{i:02d}'].data.materials.append(seammat)
bar('NISW_R3_Roof_Lap_Brick_00',(-35.70,24.75,4.735),(.018,34.80,.012)).data.materials.clear();bpy.data.objects['NISW_R3_Roof_Lap_Brick_00'].data.materials.append(seammat)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
print('Saved R3 membrane finish and low-profile roof edge/joint details; plate bounds intentionally unchanged.')

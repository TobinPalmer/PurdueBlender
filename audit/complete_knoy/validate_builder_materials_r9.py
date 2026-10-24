import bpy, ast, json
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
source_path=ROOT/'modular/buildings/build_knoy_hall.py'
tree=ast.parse(source_path.read_text(encoding='utf-8-sig'))
needed={'setup_brick_material','setup_concrete_material','setup_glass_material'}
funcs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in needed]
assert {n.name for n in funcs}==needed
namespace={'bpy':bpy}
exec(compile(ast.Module(body=funcs,type_ignores=[]),str(source_path),'exec'),namespace)
created=[]
for name in ['setup_brick_material','setup_concrete_material','setup_glass_material']:
 m=namespace[name](); created.append(m)
 assert m.use_nodes and len(m.node_tree.nodes)>=2
 assert any(n.type=='OUTPUT_MATERIAL' for n in m.node_tree.nodes)
 assert len(m.node_tree.links)>0
 if 'Brick' in m.name:
  b=next(n for n in m.node_tree.nodes if n.type=='TEX_BRICK')
  assert abs(b.inputs['Brick Width'].default_value-.23)<1e-5
  assert abs(b.inputs['Row Height'].default_value-.076)<1e-5
  assert tuple(round(v,2) for v in b.inputs['Mortar'].default_value[:3])==(0.38,0.34,0.29)
  assert abs(b.inputs['Mortar Size'].default_value-.006)<1e-5
  assert m.get('measurement_limit')
 if 'Concrete' in m.name: assert abs(next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Roughness'].default_value-.82)<1e-5
 if 'Glass' in m.name:
  p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  assert abs(p.inputs['IOR'].default_value-1.5)<1e-5
  assert abs(p.inputs['Transmission Weight'].default_value-.85)<1e-5
report={'builder_material_functions':'PASS','tested_functions':sorted(needed),'node_graphs_created_and_linked':True,'brick_render_scale_dimensions_m':[0.23,0.076],'brick_mortar_render_scale_m':0.006,'brick_mortar_color_render_estimate':[0.38,0.34,0.29],'concrete_roughness':0.82,'glass_ior':1.5,'glass_transmission':0.85,'no_building_geometry_created':True,'notes':'Material setup functions were AST-extracted and run in Blender in the unsaved audit scene. They were not used to regenerate or overwrite the saved asset.'}
(ROOT/'audit/complete_knoy/builder_material_validation_r9.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))




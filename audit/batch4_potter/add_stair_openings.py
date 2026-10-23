import bpy,json,shutil,bmesh
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
shutil.copy2(P,D/'round2.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
cores=[(49.8,1.5),(49.9,53.4),(10.5,35.2)]
levels=['POTR_Interior_Slab_Level_1_EstimatedElevation','POTR_Interior_Slab_Level_2_EstimatedElevation','POTR_Interior_Slab_Level_3_EstimatedElevation','POTR_Official_864_Roof']
for name in levels:
 slab=c.objects[name]
 for i,(x,y) in enumerate(cores,1):
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,6))
  cut=bpy.context.object;cut.name=f'TEMP_Cut_{name}_{i}';cut.dimensions=(4.6,3.6,25);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  mod=slab.modifiers.new(f'Historic stair opening {i}','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
  bpy.context.view_layer.objects.active=slab;slab.select_set(True)
  try: bpy.ops.object.modifier_apply(modifier=mod.name)
  except Exception as e: print('BOOL_FAILED',name,i,repr(e))
  bpy.data.objects.remove(cut,do_unlink=True)
 slab['stair_openings']='Three rectangular openings added from approximate S01-S03 centers on 2016 plans; 4.6 x 3.6 m estimated, verify before architectural use.'
# basement-to-first-floor opening omitted until basement plan stair locations reconciled.
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];dg=bpy.context.evaluated_depsgraph_get();res=[]
for n in levels:
 o=c.objects[n];eo=o.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);res.append({'name':n,'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)});bm.free();eo.to_mesh_clear()
print(json.dumps({'reopened':True,'root':list(c.objects['AssetRoot_potter_engineering'].location),'shell_xy':list(c.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]),'openings':res},indent=2))

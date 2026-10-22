import bpy,json,pathlib
from mathutils import Matrix
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');path=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(path));col=bpy.data.collections['Asset_hovde_hall'];sy=14.63/18.8;sx=3.58/7.2;T=Matrix(((0,-sx,0,10.8-35.5*sx),(sy,0,0,-.255),(0,0,1,0),(0,0,0,1)));extra=[]
for o in col.all_objects:
 if o.name.startswith(('HOVD_Balustrade_','HOVD_Urn_','HOVD_Gold_Letters')):o.matrix_basis=T@o.matrix_basis;extra.append(o.name)
 elif o.name.startswith(('HOVD_Plaza_','HOVD_Planter_','HOVD_Bench_','HOVD_Bike_','HOVD_Lantern_')):o.location.x-=2.085834
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));print('ACTUAL_OBJECTS',len(bpy.data.collections['Asset_hovde_hall'].all_objects));p=P/'audit/walc_north/hovde_correction.json';r=json.loads(p.read_text());r['followup']='Moved previously missed gold letters, balustrades and urns with entrance. Closed2.086m paving/stair gap by shifting plaza+site furniture toward steps; plaza now contacts stair outer edge in local frame.';r['changed_objects']+=extra;r['actual_exported_objects']=len(bpy.data.collections['Asset_hovde_hall'].all_objects);p.write_text(json.dumps(r,indent=2))

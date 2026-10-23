import bpy, math
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_hovde_hall']
# Set apart the portico panel from the central glazing and keep the complete six-column line under the narrower entablature.
for n in ['HOVD_Portico_Entablature','HOVD_Portico_Cornice','HOVD_Portico_Pediment_Base','HOVD_Portico_Pediment_Crown']:
 o=bpy.data.objects[n];o.location.x+=.60
# Tighten fascia and cornice to an 8.8 m frontage; keep the gable proportion coherent with the column line.
for n,factor in [('HOVD_Portico_Entablature',.75),('HOVD_Portico_Cornice',.75),('HOVD_Portico_Pediment_Base',.78),('HOVD_Portico_Pediment_Crown',.74)]:
 bpy.data.objects[n].scale.x*=factor
# Reduce projection and make the architrave a slimmer lintel. Maintain contact with column capitals.
ent=bpy.data.objects['HOVD_Portico_Entablature'];ent.scale.y*=.82;ent.scale.z*=.72;ent.location.z=11.02
corn=bpy.data.objects['HOVD_Portico_Cornice'];corn.scale.y*=.82;corn.scale.z*=.78;corn.location.z=11.77
ped=bpy.data.objects['HOVD_Portico_Pediment_Base'];ped.scale.y*=.88;ped.scale.z*=.80;ped.location.z=12.67
crown=bpy.data.objects['HOVD_Portico_Pediment_Crown'];crown.scale.y*=.82;crown.scale.z*=.85;crown.location.z=13.68
# Bring the six columns in as a group; retain 6 supports, round shafts and existing root/local frame.
center_y=-.255
for i in range(1,7):
 for prefix in ['HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_','HOVD_Column_FluteCollar_Base_','HOVD_Column_FluteCollar_Capital_']:
  o=bpy.data.objects.get(prefix+str(i))
  if not o:continue
  o.location.y=center_y+(o.location.y-center_y)*.85
  if prefix.startswith('HOVD_Classical_Column_'):
   o.scale.x*=.72;o.scale.y*=.72
   me=o.data
   for v in me.vertices:
    # Deepen the twelve flutes slightly so the shafts catch side light at human scale.
    rr=math.hypot(v.co.x,v.co.y)
    if rr>0:
     a=math.atan2(v.co.y,v.co.x);g=max(0.0,math.cos(12*a))**12
     old=.018*g;new=.045*g;fac=(rr-new)/(rr-old) if rr>old else 1.0;v.co.x*=fac;v.co.y*=fac
   me.update()
  elif 'Base_' in prefix or 'Capital_' in prefix:
   o.scale.x*=.74;o.scale.y*=.74
  else:
   o.scale.x*=.72;o.scale.y*=.72
# Reduce the oversaturated pale stone value while retaining opaque limestone.
stone=bpy.data.materials['Bedford_Indiana_Limestone'];stone.diffuse_color=(.50,.46,.39,1)
bs=stone.node_tree.nodes.get('Principled BSDF')
if bs:bs.inputs['Base Color'].default_value=(.50,.46,.39,1)
ramp=next((n for n in stone.node_tree.nodes if n.bl_idname=='ShaderNodeValToRGB'),None)
if ramp:ramp.color_ramp.elements[0].color=(.44,.41,.35,1);ramp.color_ramp.elements[1].color=(.53,.49,.41,1)
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('round4 refinement saved: smaller, projecting portico; six narrower fluted supports; stone value balanced')

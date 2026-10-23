import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
f=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(f))

# Replace the heavy, window-covering stack with a narrow architrave, separate cornice,
# and a compact triangular tympanum centered over the six-column bay.
ent=bpy.data.objects['HOVD_Portico_Entablature']
ent.scale.x*=.86; ent.scale.y*=.52; ent.scale.z*=.68; ent.location.z=10.71
corn=bpy.data.objects['HOVD_Portico_Cornice']
corn.scale.x*=.84; corn.scale.y*=.52; corn.scale.z*=.58; corn.location.z=10.99
ped=bpy.data.objects['HOVD_Portico_Pediment_Base']
ped.scale.x*=.80; ped.scale.y*=.59; ped.scale.z*=.95; ped.location.z=11.74
crown=bpy.data.objects['HOVD_Portico_Pediment_Crown']
crown.scale.x*=.80; crown.scale.y*=.58; crown.scale.z*=.70; crown.location.z=12.62

# Align all supports under the smaller pediment while leaving visible brick and glazing
# at the adjacent bays. Keep the six support count and source asset local frame.
for i in range(1,7):
    for prefix in ('HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_',
                   'HOVD_Column_FluteCollar_Base_','HOVD_Column_FluteCollar_Capital_'):
        o=bpy.data.objects.get(prefix+str(i))
        if o: o.location.y=-.255+(o.location.y+.255)*.87

# Keep the name readable on the fascia without spanning or colliding with the pediment face.
plaque=bpy.data.objects['HOVD_Sign_Plaque']; text=bpy.data.objects['HOVD_Gold_Letters']
plaque.scale.x*=.75; plaque.scale.z*=.55
text.scale.x*=.80; text.scale.z*=.90
plaque.location=(13.64,-.255,10.72)
text.location=(13.68,-.255,10.72)

bpy.ops.wm.save_as_mainfile(filepath=str(f))
print('Round 5 portico revision saved: narrow fascia/cornice, smaller triangular panel, six supports aligned, compact fascia inscription.')

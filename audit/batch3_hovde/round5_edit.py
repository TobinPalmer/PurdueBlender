import bpy
from pathlib import Path

P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
f=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(f))

# Fit the stone assembly to a narrower central bay so the brick window rhythm remains legible.
for name,factor in [
    ('HOVD_Portico_Entablature',.78),
    ('HOVD_Portico_Cornice',.78),
    ('HOVD_Portico_Pediment_Base',.84),
    ('HOVD_Portico_Pediment_Crown',.82),
]:
    bpy.data.objects[name].scale.x*=factor
ped=bpy.data.objects['HOVD_Portico_Pediment_Base']
ped.scale.y*=.68
ped.scale.z*=.80
ped.location.z=12.10
crown=bpy.data.objects['HOVD_Portico_Pediment_Crown']
crown.location.z=13.00
# Adjust the fascia stack to meet the shortened pediment without gaps.
bpy.data.objects['HOVD_Portico_Entablature'].scale.z*=.86
bpy.data.objects['HOVD_Portico_Cornice'].location.z=11.12

# Compress six supports symmetrically toward the centerline; retain all six bays.
for i in range(1,7):
    for prefix in ('HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_',
                   'HOVD_Column_FluteCollar_Base_','HOVD_Column_FluteCollar_Capital_'):
        o=bpy.data.objects.get(prefix+str(i))
        if o:
            o.location.y=-.255+(o.location.y+.255)*.78

# Move the display name onto a compact, centered plaque that fits the new fascia width.
plaque=bpy.data.objects['HOVD_Sign_Plaque']
text=bpy.data.objects['HOVD_Gold_Letters']
plaque.scale.x*=.50
text.scale.x*=.60
plaque.location.x=13.64
text.location.x=13.68

# Refit the interpretive office seating to the modeled room boundary and reduce the dominant rug.
for name in ('HOVD_Chesterfield_Sofa_Seat','HOVD_Chesterfield_Sofa_Back'):
    o=bpy.data.objects[name]
    o.location.x+=3.5
rug=bpy.data.objects['HOVD_Pres_Rug']
rug.scale.x*=.78
rug.scale.y*=.78

bpy.ops.wm.save_as_mainfile(filepath=str(f))
print('Saved round 5: narrower portico, compact centered sign, six supports retained, office sofa moved inside room and rug reduced.')

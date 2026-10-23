import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
f=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(f))

# Give the brick facade a larger visible margin around the entry while keeping six columns.
for name,factor in [
    ('HOVD_Portico_Entablature',.90),
    ('HOVD_Portico_Cornice',.90),
    ('HOVD_Portico_Pediment_Base',.96),
    ('HOVD_Portico_Pediment_Crown',.96),
]: bpy.data.objects[name].scale.x*=factor
for i in range(1,7):
    for prefix in ('HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_',
                   'HOVD_Column_FluteCollar_Base_','HOVD_Column_FluteCollar_Capital_'):
        o=bpy.data.objects.get(prefix+str(i))
        if o: o.location.y=-.255+(o.location.y+.255)*.90

# Move plaque and type in front of the entablature so the inscription is actually visible.
plaque=bpy.data.objects['HOVD_Sign_Plaque']; text=bpy.data.objects['HOVD_Gold_Letters']
plaque.location.x=14.10; plaque.location.z=10.72
text.location.x=14.14; text.location.z=10.72
plaque.scale.z*=.75

# Place the interpretive sofa fully inside the modeled office footprint along the west wall.
sofa=bpy.data.objects['HOVD_Chesterfield_Sofa_Seat']; sofa.location=(-3.0,-25.0,sofa.location.z)
back=bpy.data.objects['HOVD_Chesterfield_Sofa_Back']; back.location=(-3.6,-25.0,back.location.z)

bpy.ops.wm.save_as_mainfile(filepath=str(f))
print('Saved round 5 fit refinement: reduced portico width, six supports retained, plaque moved forward, sofa aligned inside office.')

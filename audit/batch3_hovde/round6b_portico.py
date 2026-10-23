import bpy
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
# Re-space six shafts to leave the three door leaves legible through the colonnade.
centers=[-5.3,-4.0,-1.5,1.0,3.48,5.3]
for i,y in enumerate(centers,1):
    for prefix in ('HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_','HOVD_Column_FluteCollar_Base_','HOVD_Column_FluteCollar_Capital_'):
        o=bpy.data.objects.get(prefix+str(i))
        if o: o.location.y=y
# Broaden roof-level classical frame/pediment to correspond to the now-readable six-column spacing.
for name,factor in [('HOVD_Portico_Entablature',2.35),('HOVD_Portico_Cornice',2.35),('HOVD_Portico_Pediment_Base',2.55),('HOVD_Portico_Pediment_Crown',2.55)]:
    o=bpy.data.objects[name]; o.scale.x*=factor
# Plaque/sign remains compact, centered on the entry instead of spanning the entire entablature.
bpy.ops.wm.save_as_mainfile(filepath=p)
print('Round6b: six columns positioned around 3 existing door openings',centers,'pediment broadened; root unchanged',tuple(bpy.data.objects['HOVD_Root'].location))

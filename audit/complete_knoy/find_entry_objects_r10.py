import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
c=bpy.data.collections.get('Asset_knoy_hall')
for o in sorted(c.objects,key=lambda o:o.name):
 if any(k in o.name.lower() for k in ['entr','portal','canopy','sign','letter','curb','stair','planter','plaza']):print(o.name,o.type,tuple(round(v,3) for v in o.location),tuple(round(v,3) for v in o.dimensions))

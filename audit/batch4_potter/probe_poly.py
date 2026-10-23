import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');bpy.ops.wm.open_mainfile(filepath=str(P));o=bpy.data.objects['POTR_2016_StairCore3_Level0_Flight'];print('type',o.type,'polys',len(o.data.polygons));print([(tuple(round(x,2) for x in p.normal),round(p.area,3)) for p in o.data.polygons[:40]])
